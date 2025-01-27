import hashlib
import os
import requests
from datetime import datetime

MLX_LAUNCHER = "https://launcher.mlx.yt:45001/api/"
MLX_BASE = "https://api.multilogin.com"

HEADERS = {
    'Accept': 'application/json',
    'Content-Type': 'application/json'
}

#TODO: Insert your account information in both variables below.
USERNAME = ""
PASSWORD = ""
OS = "windows" #Choose your OS: windows, linux or macos. 

# TODO: Please, fill the required variable
COUNT = 5 #[OPTIONAL] Specify the number of IPs to generate.
COUNTRY = "INSERT_HERE_THE_COUNTRY" #[REQUIRED] Specify the country code. Use ISO 3166-1 alpha-2 country codes. Send "any" to genereate a random proxy.
REGION = "" #[OPTIONAL] Specify the region or leave as empty string. Use snake_case for specifying the region. Example: "some_region"
CITY = "" #[OPTIONAL] Specify the city or leave as empty string. Use snake_case for specifying the city.

def signin() -> str:

    payload = {
        'email': USERNAME,
        'password': hashlib.md5(PASSWORD.encode()).hexdigest()
    }
    
    r = requests.post(f'{MLX_BASE}/user/signin', json=payload)

    if(r.status_code != 200):
        print(f'\nError during login: {r.text}\n')

    response = r.json()['data']

    token = response['token']

    return token

def get_proxy(session_type="sticky", protocol="socks5"):
    payload = {
        "country": COUNTRY,
        "protocol": protocol,
        "sessionType": session_type,
        "region": REGION,
        "city": CITY,
        "count": COUNT
    }

    r = requests.post(f'https://profile-proxy.multilogin.com/v1/proxy/connection_url', headers=HEADERS, json=payload)

    if r.status_code == 201:
        #print(f"\nInformation: {r.text}\n")
        print(r.status_code)

        response_data = r.json()
        proxy_list = response_data["data"]
        print("The proxy list was successfully get.")
        return proxy_list

    else:
        print(f"Error: {r.status_code}, {r.text}")
        return []


def check_proxy(proxy_json):
    print(f"\nTestando dentro do check_proxy: {proxy_json}")

    payload = {
        "type": proxy_json["type"],
        "host": proxy_json["host"],
        "port": int(proxy_json["port"]),
        "username": proxy_json["username"],
        "password": proxy_json["password"]
    }
    
    print(f"\nPayload for proxy: {payload}")

    try: 
        resp = requests.post(f'{MLX_LAUNCHER}v1/proxy/validate', headers=HEADERS, json=payload, timeout=15)
        if resp.status_code == 200:
            print(f"\nPayload for proxy: {resp.status_code}")
            print("\nProxy checked successfully.")
            return True, resp
        
        else:
            print(f"Unexpected error: {resp.status_code}")
            return False, resp
    
    except requests.RequestException as e:
        print(f"Error validating proxy {proxy_json}, error: {e}")
        return False, None

def main():
    token = signin()
    HEADERS.update({"Authorization": f'Bearer {token}'})

    print("Starting script...")
    proxy_list = get_proxy()
    print(f"\nLista de proxies: {proxy_list}")

    valid_proxies = []
    invalid_proxies = []
    proxy_checked_count = 0
    proxy_failed_count = 0

    for proxy in proxy_list:
        parts = proxy.split(":")
        print(f"\nParts: {parts}")
    
        if len(parts) == 4:
            protocol = "http" if parts[1] == "8080" else "socks5"

            proxy_json = {
                "host": parts[0],
                "port": parts[1],
                "username": parts[2],
                "password": parts[3],
                "type": protocol
            }

            print(f"\nProxy_json is: {proxy_json}")

        sucess, resp = check_proxy(proxy_json)

        print(f"\nThe response is AFTER check proxy: {resp}") 
        if sucess and resp.status_code == 200:
            valid_proxies.append(proxy)
            proxy_checked_count += 1
            print(f"Current check: {proxy_checked_count}")

        else:
            invalid_proxies.append(proxy)
            proxy_failed_count += 1
            print(f"Number of fails: {proxy_failed_count}")

    timestamp = datetime.now()
    date_created = timestamp.strftime("%d-%m-%Y_%H-%M-%S")
    print("date_created")
    file_name = f"proxy_checked_{date_created}.txt"


    with open(file_name, 'a') as file:
        for proxy in valid_proxies:
            file.write(f"{proxy_json['host']}:{proxy_json['port']}:{proxy_json['username']}:{proxy_json['password']}\n")

    print(f"\nTotal proxies checked: {proxy_checked_count}")
    print(f"Valid proxies: {len(valid_proxies)}")
    print(f"Invalid proxies: {len(invalid_proxies)}")

    try:
        if OS == "windows":
            os.system(f"notepad {file_name}")
            print("\nProxies checked and ready to be used.")

        elif OS == "macos":
            os.system(f"open {file_name}")
            print("\nProxies checked and ready to be used.")

        else: 
            os.system(f"xdg-open {file_name}") #for linux OS.
            print("\nProxies checked and ready to be used.")
    
    except Exception as e:
        print(f"Unexpected error opening the file {e}")


if __name__ == "__main__":
    main()