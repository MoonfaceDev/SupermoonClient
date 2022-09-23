import pickle
import time

import requests
from starlette.testclient import TestClient

from supermoon_client.app import app
from supermoon_client.consts import INITIAL_POLL_INTERVAL, SERVER_GET_REQUEST_URL, SERVER_SEND_RESPONSE_URL


def start_polling():
    polling_interval = INITIAL_POLL_INTERVAL
    while True:
        time.sleep(polling_interval)

        server_request = requests.get(SERVER_GET_REQUEST_URL)
        try:
            key, value = server_request.content.split(b'=')
            if key == 'interval':
                polling_interval = float(value)
        except ValueError:
            pass

        request: requests.PreparedRequest = pickle.loads(server_request.content)

        with TestClient(app) as client:
            response = client.send(request)

        response.headers['action-id'] = request.headers['action-id']
        requests.post(SERVER_SEND_RESPONSE_URL, pickle.dumps(response))
