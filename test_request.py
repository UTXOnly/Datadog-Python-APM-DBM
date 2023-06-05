import requests
import time
from ddtrace import tracer

tracer.configure(hostname='127.0.0.1', port=8126)

def test_make_requests():
    url = 'http://127.0.0.1:5000/apm-dbm'
    while True:
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raises an exception if status code is >= 400
            data = response.json()
            for line in data:
                print(f'{line}')
            assert response.status_code == 200, f'Request failed with status code {response.status_code}'
        except requests.exceptions.RequestException as e:
            print(f'Error making request: {e}')
            # Optionally, you can raise the exception to stop the script at this point
            # raise e
        time.sleep(1)

test_make_requests()




