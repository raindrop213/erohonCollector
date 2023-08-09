from fake_useragent import UserAgent
import requests


def chosen_headers(random_headers):  # 选headers
    if random_headers:
        return {'User-Agent': UserAgent().random}
    else:
        ua = UserAgent()
        headers = {'User-Agent': ua.random}
        response = requests.get('https://httpbin.org/user-agent', headers=headers)
        user_agent = response.json()['user-agent']
        return user_agent

print(chosen_headers(False))