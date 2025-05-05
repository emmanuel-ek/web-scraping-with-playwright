#this function will bypass the capcha by using
# zenrows api

import requests

url = "https://www.scrapingcourse.com/antibot-challenge"
api_key = "8d52a81b3ca57cdc829963a7b6b17851e192a30b"

params = {
    "url": url,
    "apikey": api_key   ,
    "js_render": "true",
    "premium_proxy": "true",
}

response = requests.get("https://api.zenrows.com/v1/", params=params)
print(response.text)
