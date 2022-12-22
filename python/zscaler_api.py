import httpx
from ratelimit import limits, sleep_and_retry
from const import OAUTH_SERVER, OAUTH_SCOPE, OAUTH_CLIENT_ID, OAUTH_CLIENT_SECRET, OAUTH_TOKEN_PATH
from const import ZIA_CLOUD, RATE_LIMIT


def get_oauth_token() -> str:
    """Collect oAuth token from Authorization server and return access token"""
    payload = {"grant_type": "client_credentials",
               "scope": OAUTH_SCOPE}
    transport = httpx.HTTPTransport(retries=3)
    auth = (OAUTH_CLIENT_ID, OAUTH_CLIENT_SECRET)
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    http_client = httpx.Client(http2=True, auth=auth, base_url=OAUTH_SERVER, headers=headers, transport=transport, timeout=60)
    
    with http_client as client:
        response = client.post(OAUTH_TOKEN_PATH, data=payload)
    
    try:
        token = response.json()['access_token']
    except (ValueError, TypeError) as error:
        print(response.status_code)
        print(response.content)
        print(error)
    
    return token

def create_http_client() -> httpx.Client:
    """
    Create a http client instance to re-use across API calls
    The client is created separate from the API call then passed in as a parameter
    to the api call function so that the cookie set by the zscaler api is maintained.
    I found that the api will set a cookie first time it sees the oAuth bearer token,
    and expects this same cookie to be maintained. If the same bearer token is used across
    multiple calls without retaining the cookie the api returns a 403 'Unauthorized'
    """
    token = get_oauth_token()
    transport = httpx.HTTPTransport(retries=3)
    headers = {'content-type': 'application/json',
               'authorization': f'Bearer {token}',
               'cache-control': 'no-cache'}
    http_client = httpx.Client(http2=True, base_url=ZIA_CLOUD, headers=headers, transport=transport)
    
    return http_client

@sleep_and_retry
@limits(1, RATE_LIMIT)
def zs_api_call(method:str, path:str, http_client:httpx.Client, payload:dict|list=None) -> dict:
    """Call Zscaler API and return response"""

    if method == 'GET':
        response = http_client.get(path)
    if method == 'POST':
        response = http_client.post(path, json=payload)
    if method == 'PUT':
        response = http_client.put(path, json=payload)
    if method == 'DELETE':
        response = http_client.delete(path)
    
    try:
        # Delete operations return a 204 with no content
        if response.status_code == 204:
            result = {'result':'SUCCESS'}
    
        elif response.status_code == 200:
            result = response.json()
        
        else:
            print(response.text)
            print(response.status_code)
            raise SystemExit(1)
            
    except (ValueError, TypeError) as error:
        print(response.status_code)
        print(response.content)
        print(error)
    
    return result