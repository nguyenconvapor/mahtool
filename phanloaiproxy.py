import socket
import time
import datetime

def check_proxy(proxy):
    """Checks the type of a proxy by attempting connections.

    Args:
        proxy (str): The proxy in the format 'ip:port'.

    Returns:
        str: The proxy type (http, socks4, socks5) or None if connection fails.
    """
    ip, port = proxy.split(':')
    port = int(port)

    def check_http(ip, port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.settimeout(5)  # Set a timeout for connection attempts
                s.connect((ip, port))
                s.sendall(b"GET / HTTP/1.1\r\nHost: www.example.com\r\n\r\n")
                response = s.recv(1024)
                if b"HTTP/" in response:
                    return "http"
            except (socket.timeout, ConnectionRefusedError, OSError):
                pass # Ignore connection errors
            return None

    def check_socks4(ip, port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.settimeout(5)
                s.connect((ip, port))
                # SOCKS4 handshake (very basic example)
                # For more robust checks, use a proper SOCKS4 library.
                s.sendall(b"\x04\x01\x50" + port.to_bytes(2, 'big') + socket.inet_aton(ip) + b"\x00")
                response = s.recv(8)  # Expect 8 bytes response
                if response and response[0] == 0x00:  # Check for success
                    return "socks4"
            except (socket.timeout, ConnectionRefusedError, OSError):
                pass

            return None


    def check_socks5(ip, port):
      with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
          s.settimeout(5)
          s.connect((ip, port))

          # SOCKS5 initial handshake (no auth)
          s.sendall(b"\x05\x01\x00")
          response = s.recv(2)

          if response == b"\x05\x00":  # Check for success
            return "socks5"
        except (socket.timeout, ConnectionRefusedError, OSError):
          pass

        return None



    if check_http(ip, port):
        return "http"
    elif check_socks4(ip, port):
        return "socks4"
    elif check_socks5(ip, port):
        return "socks5"


    return None


def main():
    filepath = input("Enter the path to the proxy file (ip:port format): ")

    try:
        with open(filepath, 'r') as f:
            proxies = [line.strip() for line in f]
    except FileNotFoundError:
        print(f"Error: File not found at {filepath}")
        return

    total_proxies = len(proxies)
    print(f"Found {total_proxies} proxies to check.")

    results = {
        "http": [],
        "socks4": [],
        "socks5": [],
        "invalid": []
    }

    print("Starting proxy check...")

    for i, proxy in enumerate(proxies):
        proxy_type = check_proxy(proxy)

        if proxy_type:
            results[proxy_type].append(proxy)
        else:
            results["invalid"].append(proxy)

        print(f"Checked {i+1}/{total_proxies} proxies", end='\r')  # Print progress

    print("\nProxy check complete.")

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    for proxy_type, proxy_list in results.items():
        if proxy_list:
            filename = f"{timestamp}_{proxy_type}.txt"
            with open(filename, "w") as f:
                f.writelines("\n".join(proxy_list))
            print(f"Saved {len(proxy_list)} {proxy_type} proxies to {filename}")


if __name__ == "__main__":
    main()