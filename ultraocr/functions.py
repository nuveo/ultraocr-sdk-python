from requests import Session, post

class Client:
    API_TIMEOUT = 30
    BASE_URL = "https://ultraocr.apis.nuveo.ai/v2/"
    AUTH_BASE_URL = "https://auth.apis.nuveo.ai/v2/"

    def __init__(
        self,
        client_id,
        client_secret,
        auth_base_url=AUTH_BASE_URL,
        base_url=BASE_URL,
        timeout=API_TIMEOUT,
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.auth_base_url = auth_base_url
        self.base_url = base_url
        self.timeout = timeout
        self._session = Session()

    def authenticate(self):
        """Authenticate on UltraOCR

        Authenticate on UltraOCR and save the token to use on future requests.
        """
        url = f'{self.auth_base_url}/token'
        data = {
            "ClientID": self.client_id,
            "ClientSecret": self.client_secret,
        }

        resp = post(url, json=data)
        self.token = resp.json()["token"]