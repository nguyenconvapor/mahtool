import asyncio
import random
import ssl
import json
import time
import uuid
import requests
import backoff
from loguru import logger
from websockets_proxy import Proxy, proxy_connect
from fake_useragent import UserAgent
from datetime import datetime, timezone

# List to keep track of active proxies
active_proxies = set()

async def connect_to_wss(socks5_proxy, user_id):
    user_agent = UserAgent(os=['windows', 'macos', 'linux'], browsers='chrome')
    random_user_agent = user_agent.random
    device_id = str(uuid.uuid3(uuid.NAMESPACE_DNS, socks5_proxy))

    # Add the proxy to active proxies set
    active_proxies.add(socks5_proxy)
    logger.info(f"Using proxy: {socks5_proxy}, device_id: {device_id}, Active proxies: {len(active_proxies)}")

    urilist = ["wss://proxy2.wynd.network:4444/", "wss://proxy2.wynd.network:4650/", "wss://proxy2.wynd.network:443/"]
    server_hostname = "proxy2.wynd.network"
    custom_headers = {"User-Agent": random_user_agent}
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    @backoff.on_exception(backoff.expo, Exception, max_tries=3)
    async def send_websocket_message(message):
        async with proxy_connect(random.choice(urilist), proxy=Proxy.from_url(socks5_proxy), ssl=ssl_context, server_hostname=server_hostname, extra_headers=custom_headers) as websocket:
            await websocket.send(json.dumps(message))

    async def send_ping(websocket):
        while True:
            send_message = {"id": str(uuid.uuid4()), "version": "1.0.0", "action": "PING", "data": {}}
            logger.debug(f"Sending PING: {send_message}")
            await websocket.send(json.dumps(send_message))
            await asyncio.sleep(5)

    while True:
        try:
            proxy = Proxy.from_url(socks5_proxy)
            async with proxy_connect(random.choice(urilist), proxy=proxy, ssl=ssl_context, server_hostname=server_hostname, extra_headers=custom_headers) as websocket:
                logger.info(f"Connected to {random.choice(urilist)} using {socks5_proxy}")

                asyncio.create_task(send_ping(websocket))

                async for response in websocket:
                    try:
                        message = json.loads(response)
                        logger.info(f"Received message: {message}")

                        now = datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S GMT')

                        if message.get("action") == "AUTH":
                            auth_response = {
                                "id": message["id"],
                                "origin_action": "AUTH",
                                "result": {
                                    "browser_id": device_id,
                                    "user_id": user_id,
                                    "user_agent": custom_headers['User-Agent'],
                                    "timestamp": int(time.time()),
                                    "device_type": "desktop",
                                    "version": "4.29.0",
                                }
                            }
                            await websocket.send(json.dumps(auth_response))

                        elif message.get("action") == "HTTP_REQUEST":
                            httpreq_response = {
                                "id": message["id"],
                                "origin_action": "HTTP_REQUEST",
                                "result": {
                                    "url": message["url"],
                                    "status": 200,
                                    "status_text": "OK",
                                    "headers": {
                                        "content-type": "application/json; charset=utf-8",
                                        "date": now,
                                        "keep-alive": "timeout=5",
                                        "proxy-connection": "keep-alive",
                                        "x-powered-by": "Express",
                                    }
                                }
                            }
                            await websocket.send(json.dumps(httpreq_response))

                        elif message.get("action") == "PONG":
                           pong_response = {"id": message["id"], "origin_action": "PONG"}
                           logger.debug(pong_response)
                           await websocket.send(json.dumps(pong_response))

                        else:
                           logger.warning(f"Unexpected message: {message}. Removing proxy {socks5_proxy}")
                           raise Exception("Unexpected message")

                    except json.JSONDecodeError:
                        logger.error(f"Invalid JSON received: {response}")


        except Exception as e:
            logger.error(f"Error with proxy {socks5_proxy}: {e}")
            await asyncio.sleep(random.uniform(1, 5))

def remove_proxy(proxy):
    if proxy in active_proxies:
        active_proxies.remove(proxy)
        logger.info(f"Proxy {proxy} removed. Active proxies: {len(active_proxies)}")


async def main():
    _user_id = '2owgypvuaDXDxUN3gDdVcCwbxYj' # Replace with your user ID
    try:
       r = requests.get("https://api.proxyscrape.com/v4/free-proxy-list/get?request=display_proxies&proxy_format=protocolipport&format=text", stream=True)
       r.raise_for_status()  # Raise an exception for bad status codes
       with open('auto_proxies.txt', 'wb') as f:
           for chunk in r:
               f.write(chunk)
       with open('auto_proxies.txt', 'r') as file:
           auto_proxy_list = [f"socks5://{proxy}" for proxy in file.read().splitlines()] # Add socks5:// prefix
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching proxies: {e}")
        return


    tasks = [asyncio.ensure_future(connect_to_wss(i, _user_id)) for i in auto_proxy_list]
    await asyncio.gather(*tasks)


if __name__ == '__main__':
    logger.add(lambda msg: print(msg, end='')) # print to console
    asyncio.run(main())
