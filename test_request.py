import requests
import time
from ddtrace import tracer

tracer.configure(hostname='127.0.0.1', port=8126)

def test_make_requests():
    url = 'http://127.0.0.1:5000/apm-dbm'
    while True:
        response = requests.get(url)
        data = response.json()
        for line in data:
            print(f'{line}')
        assert response.status_code == 200, f'Request failed with status code {response.status_code}'
        time.sleep(1)

test_make_requests()



