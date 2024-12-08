import requests

url = "https://api.proxyscrape.com/v4/free-proxy-list/get?request=display_proxies&proxy_format=protocolipport&format=text"
response = requests.get(url)

with open('proxies.txt', 'w') as f:
    f.write(response.text)