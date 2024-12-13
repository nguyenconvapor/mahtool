import requests
from bs4 import BeautifulSoup
import datetime

# Lấy thời gian hiện tại để đặt tên file
now = datetime.datetime.now()
filename = now.strftime("%Y-%m-%d_%H-%M-%S.txt")

url = "https://free-proxy-list.net/"
response = requests.get(url)
soup = BeautifulSoup(response.content, "html.parser")

proxies = []
for row in soup.find("table", class_="table").find_all("tr")[1:]:  # Bỏ qua hàng tiêu đề
    cells = row.find_all("td")
    ip = cells[0].text
    port = cells[1].text
    proxies.append(f"http://{ip}:{port}")

# Mở file để ghi, sử dụng 'with' để đảm bảo file tự động đóng
with open(filename, "w") as f:
    for proxy in proxies:
        f.write(proxy + "\n")  # Ghi mỗi proxy trên một dòng
        print(proxy)

print(f"Proxies đã được lưu vào file: {filename}")