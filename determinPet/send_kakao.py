import json
import time
from selenium_init import driver
from selenium.webdriver import ActionChains

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
import requests

REST_API_KEY = "1dcc5cb6841f71bbdf5438b9e73efcc7"
REDIRECT_URI = "https://www.naver.com"

def kakao_init():
    code = get_token()
    access_token = get_access_token(code)
    return access_token

def get_token():
    oauth_url = f"https://kauth.kakao.com/oauth/authorize?response_type=code&client_id={REST_API_KEY}&redirect_uri={REDIRECT_URI}"
    driver.get(oauth_url)
    access_code = False

    while True:
        print(driver.current_url)
        if("https://www.naver.com/?code=" in  driver.current_url) :
            access_code = driver.current_url.split("code=")[-1]
            print(access_code)
            break
        time.sleep(1)

    driver.close()
    return access_code

def get_access_token(access_code):
    url = 'https://kauth.kakao.com/oauth/token'

    data = {
        'grant_type':'authorization_code',
        'client_id':REST_API_KEY,
        'redirect_uri':REDIRECT_URI,
        'code': access_code,
    }

    response = requests.post(url, data=data)
    tokens = response.json()
    print(tokens)
    return tokens["access_token"]


def send_kakaotalk(ACCESS_TOKEN) :
    url="https://kapi.kakao.com/v2/api/talk/memo/default/send"
    # kapi.kakao.com/v2/api/talk/memo/default/send 

    print("Bearer" + ACCESS_TOKEN)

    headers={
        "Authorization" : "Bearer " + ACCESS_TOKEN,
        "Content-Type" : "application/x-www-form-urlencoded"
    }

    data= {
        "template_object":  json.dumps({
        	"object_type": "text",
            "text": "test",
            "link": {
                "web_url" : "lorem ipsum",
                "mobile_web_url" : "lorem ipsum"
            },
            "button_title" : "lorem ipsum"
        })
    }

    response = requests.post(url, headers=headers, data=data)
    print(response.content)
