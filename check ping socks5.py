import asyncio
import aiohttp
import time
import re

async def check_proxy(proxy):
    """Kiểm tra proxy và trả về thời gian ping nếu thành công, None nếu thất bại."""
    try:
        start_time = time.time()
        async with aiohttp.ClientSession() as session:
             async with session.get('http://www.google.com', proxy=proxy, timeout=10) as response: #timeout tùy chỉnh
                if response.status == 200:
                    return time.time() - start_time
    except Exception as e:
        #print(f"Proxy {proxy} lỗi: {e}") # Bỏ comment nếu muốn xem chi tiết lỗi
        pass
    return None

async def main():
    filename = input("Nhập tên file chứa proxy: ")
    try:
        with open(filename, "r") as f:
            proxies = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"Không tìm thấy file {filename}.")
        return

    total_proxies = len(proxies)
    print(f"Số lượng proxy cần kiểm tra: {total_proxies}")

    fast_proxies = []
    medium_proxies = []
    slow_proxies = []
    bad_proxies = []


    checked_count = 0
    for proxy in proxies:
        ping = await check_proxy(proxy)
        checked_count += 1
        print(f"Đã kiểm tra {checked_count}/{total_proxies} proxy.", end="\r")

        if ping is not None:
            if ping < 0.5:  # Điều chỉnh ngưỡng theo nhu cầu
                fast_proxies.append(proxy)
            elif ping < 1:
                medium_proxies.append(proxy)
            else:
                slow_proxies.append(proxy)
        else:
            bad_proxies.append(proxy)
    print("\nHoàn thành kiểm tra.")

    def save_proxies(proxies, filename):
        with open(filename, "w") as f:
            for proxy in proxies:
                f.write(proxy + "\n")


    save_proxies(fast_proxies, "fast_proxies.txt")
    save_proxies(medium_proxies, "medium_proxies.txt")
    save_proxies(slow_proxies, "slow_proxies.txt")
    save_proxies(bad_proxies, "bad_proxies.txt")
    print("Đã lưu danh sách proxy đã phân loại.")




if __name__ == "__main__":
    asyncio.run(main())
