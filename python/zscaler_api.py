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
    All timeouts have been set to 20.0 seconds
    """
    token = get_oauth_token()
    transport = httpx.HTTPTransport(retries=3)
    headers = {'content-type': 'application/json',
               'authorization': f'Bearer {token}',
               'cache-control': 'no-cache'}
    timeout = httpx.Timeout(20.0)
    http_client = httpx.Client(http2=True, base_url=ZIA_CLOUD, headers=headers, transport=transport, timeout=timeout)
    
    return http_client

@sleep_and_retry
@limits(1, RATE_LIMIT)
def zs_api_call(method:str, path:str, http_client:httpx.Client, payload:dict|list=None) -> list|dict:
    """Call Zscaler API and return response
    
    Args:
        method: HTTP request method for request [GET, POST, PUT, DELETE]
        path: API path to call. This should be the relative path excluding the base.
        http_client: httpx client instance used to send request. This client instance must include the base url and auth headers
        payload: Payload as dict or list to be sent for POST and PUT operations
    
    Returns:
        JSON response data from API formatted as a list or dict
    """

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

def resolve_user_department(department:str, http_client:httpx.Client) -> dict:
    """Get ID for already created department name
    
    Args:
        department: Department name to retrieve
        http_client: httpx client instance used to send request
        
    Returns:
        Dict holding department name and corresponding ID
        
        Example output:
        {'id': 98765432, 'name': 'department_name'}
    """
    user_department: list = zs_api_call('GET', f'/departments?search={department}', http_client)
    return user_department[0]

def resolve_user_groups(groups:list[str], http_client:httpx.Client) ->list:
    """Get ID's for already created group names
    
    Args:
        groups: List of group names to retrieve
        http_client: httpx client instance used to send request
        
    Returns:
        List of dicts containing group names and corresponding IDs
        
        Example output:
        [{'id': 23456789, 'name': 'group1'}, {'id': 87654321, 'name': 'group2'}]
    """
    current_groups: list = zs_api_call('GET', '/groups', http_client)
    target_groups = [group for group in current_groups if group['name'] in groups]
    return target_groups

def get_user(name:str, http_client:httpx.Client) -> dict:
    """Get config for a specific named user
    
    Args:
        name: Name of user to retrieve
        http_client: httpx client instance used to send request
    
    Returns:
        User configuration as dict
        
        Example output:
        {'id': 12345678,
        'name': 'user1',
        'email': 'user1@domain.com',
        'groups': [{'id': 23456789, 'name': 'group1'}, {'id': 87654321, 'name': 'group2'}],
        'department': {'id': 98765432, 'name': 'department_name'},
        'password': 'password',
        'deleted': False}
    """
    users: str = zs_api_call('GET', f'/users?name={name}', http_client)
    return users

def get_all_users(http_client:httpx.Client) -> list[dict]:
    """Get config for all existing users
    
    Args:
        http_client: httpx client instance used to send request
    
    Returns:
        User configurations as a list of dicts
        
        Example output:
        [{'id': 12345678,
        'name': 'user1',
        'email': 'user1@domain.com',
        'groups': [{'id': 23456789, 'name': 'group1'}, {'id': 87654321, 'name': 'group2'}],
        'department': {'id': 98765432, 'name': 'department_name'},
        'password': 'password',
        'deleted': False},
        {'id': 12345679,
        'name': 'user2',
        'email': 'user2@domain.com',
        'groups': [{'id': 23456789, 'name': 'group1'}, {'id': 87654321, 'name': 'group2'}],
        'department': {'id': 98765432, 'name': 'department_name'},
        'password': 'password',
        'deleted': False},
        ...]
    """
    users: str = zs_api_call('GET', f'/users', http_client)
    return users

def create_user(user_config: dict, http_client:httpx.Client) -> dict:
    """Create a new user

    Args:
        user: Formatted configuration data to send to API
        http_client: httpx client instance used to send request
        
        Example input:
        {'id': 12345678,
        'name': 'user1',
        'email': 'user1@domain.com',
        'groups': [{'id': 23456789, 'name': 'group1'}, {'id': 87654321, 'name': 'group2'}],
        'department': {'id': 98765432, 'name': 'department_name'},
        'password': 'password',
        'deleted': False}
    
    Returns:
        User configuration as dict; format of response will match input format
    """
    result = zs_api_call('POST', '/users', http_client, payload=user_config)
    return result

def update_user(user_config: dict, http_client:httpx.Client) -> dict:
    """Update an existing URL category
    
    Args:
        user_config: Formatted configuration data to send to API
        http_client: httpx client instance used to send request
        
        Example input:
        {"id": 64846403,
        "name": "my_user",
        "email": "my_user@example.com",
            "groups": [{"id": 63108494,
            "name": "package_management"},
            {"id": 63108602,
            "name": "security_services"}],
        "department": {"id": 63108466, "name": "infra"},
        "deleted": false
        
    Returns:
        User configuration as dict; format of response will match input format
    """
    result = zs_api_call('PUT', f'/users/{user_config["id"]}', http_client, payload=user_config)
    # For some reason the API obfuscates the name and email in the response to updates. Correcting that here so response is readable
    result['name'] = user_config['name']
    result['email'] = user_config['email']
    return result

def delete_user(user_id: dict, http_client:httpx.Client) -> None:
    """delete config for user
    
    Args:
        user_id: ID value for the user to be deleted
        http_client: httpx client instance used to send request
    
    Returns:
        None
    """
    result = zs_api_call('DELETE', f'/users/{user_id}', http_client)

def get_url_cat(cat_id:str, http_client:httpx.Client) -> dict:
    """Get config for existing url category
    
    Args:
        cat_id: ID value of the url category to be retrieved
        http_client: httpx client instance used to send request
    
    Returns:
        Category configuration as dict
        
        Example output:
        {"id": "CUSTOM_08",
        "configuredName": "infra_access",
        "superCategory": "USER_DEFINED",
        "keywords": [],
        "keywordsRetainingParentCategory": [],
        "urls": [".zscaler.com",".github.com"],
        "dbCategorizedUrls": [],
        "customCategory": true,
        "editable": true,
        "type": "URL_CATEGORY",
        "val": 135,
        "customUrlsCount": 2,
        "urlsRetainingParentCategoryCount": 0,
        "customIpRangesCount": 0,
        "ipRangesRetainingParentCategoryCount": 0}
    """
    result = zs_api_call('GET', f'/urlCategories/{cat_id}', http_client)
    return result

def create_url_cat(name:str, urls: list, http_client:httpx.Client) -> dict:
    """Create a new custom URL category and add URLs (not retaining parent category)
    
    Args:
        name: Friendly name to be assigned to the URL category
        urls: List of URLS to add to category
        http_client: httpx client instance used to send request
    
    Returns:
        API response including ID assigned to category
        
        Example output:
        {'id': 'CUSTOM_08',
        'configuredName': 'My Custom Category',
        'superCategory': 'USER_DEFINED',
        'keywords': [],
        'keywordsRetainingParentCategory': [],
        'urls': ['.zscaler.com', '.example.com'],
        'dbCategorizedUrls': [],
        'customCategory': True,
        'editable': True,
        'type': 'URL_CATEGORY',
        'val': 135,
        'customUrlsCount': 2,
        'urlsRetainingParentCategoryCount': 0,
        'customIpRangesCount': 0,
        'ipRangesRetainingParentCategoryCount': 0}
    """
    formatted_payload = {'superCategory': 'USER_DEFINED',
                        'configuredName': name,
                        'urls': urls,
                        'customCategory': True,
                        'type': 'URL_CATEGORY'}
    result = zs_api_call('POST', '/urlCategories', http_client, payload=formatted_payload)
    return result

def update_url_cat(cat_config, http_client:httpx.Client) -> dict:
    """Update an existing URL category
    
    Args:
        cat_config: Formatted configuration data to send to API
        http_client: httpx client instance used to send request
        
        Example input:
        {'id': 'CUSTOM_08',
        'configuredName': 'My Custom Category',
        'superCategory': 'USER_DEFINED',
        'keywords': [],
        'keywordsRetainingParentCategory': [],
        'urls': ['.zscaler.com', '.example.com'],
        'dbCategorizedUrls': [],
        'customCategory': True,
        'editable': True,
        'type': 'URL_CATEGORY',
        'val': 135,
        'customUrlsCount': 2,
        'urlsRetainingParentCategoryCount': 0,
        'customIpRangesCount': 0,
        'ipRangesRetainingParentCategoryCount': 0}
        
    Returns:
        Category configuration as dict; format of response will match input format
    """
    result = zs_api_call('PUT', f'/urlCategories/{cat_config["id"]}', http_client, payload=cat_config)
    return result

def delete_url_cat(cat_id:str, http_client:httpx.Client) -> None:
    """delete config for existing url cat
    Args:
        cat_id: ID value for the URL cat to be deleted
        http_client: httpx client instance used to send request
    
    Returns:
        None
    """
    result = zs_api_call('DELETE', f'/urlCategories/{cat_id}', http_client)

def get_url_pol(pol_id:int, http_client:httpx.Client) -> dict:
    """Get config for existing url filtering policy element
    
    Args:
        pol_id: ID value of the policy element to be retrieved
        http_client: httpx client instance used to send request
    
    Returns:
        Policy configuration as dict
        
        Example output:
        {'id': 617899,
        'accessControl': 'READ_WRITE',
        'name': 'my_filtering_rule',
        'order': 1,
        'protocols': ['ANY_RULE'],
        'users': [{'id': 64846403, 'name': 'joe_blogs(joe_blogs@example.com)'}],
        'urlCategories': ['CUSTOM_09'],
        'state': 'ENABLED',
        'rank': 7,
        'requestMethods': ['OPTIONS', 'GET', 'HEAD', 'POST', 'PUT', 'DELETE', 'TRACE', 'CONNECT', 'OTHER'],
        'blockOverride': False,
        'description': 'joe blogs access rule',
        'enforceTimeValidity': False,
        'cbiProfileId': 0,
        'action': 'ALLOW'}
    """
    result = zs_api_call('GET', f'/urlFilteringRules/{pol_id}', http_client)
    return result

def create_url_pol(name:str, users:list, url_cat:str, http_client:httpx.Client, order:int = 1) -> dict:
    """Create a new URL filtering rule for one or more users and a single URL category
    
    Args:
        name: Name of policy element
        users: Users to add to policy
        url_cat: URL category to add to policy
        http_client: httpx client instance used to send request
        order: [optional] Order in policy list, defaults to one
    
        Returns:
        Policy configuration as dict
        
        Example output:
        {'id': 617899,
        'accessControl': 'READ_WRITE',
        'name': 'my_filtering_rule',
        'order': 1,
        'protocols': ['ANY_RULE'],
        'users': [{'id': 64846403, 'name': 'joe_blogs(joe_blogs@example.com)'}],
        'urlCategories': ['CUSTOM_09'],
        'state': 'ENABLED',
        'rank': 7,
        'requestMethods': ['OPTIONS', 'GET', 'HEAD', 'POST', 'PUT', 'DELETE', 'TRACE', 'CONNECT', 'OTHER'],
        'blockOverride': False,
        'description': 'joe blogs access rule',
        'enforceTimeValidity': False,
        'cbiProfileId': 0,
        'action': 'ALLOW'}
    """
    user_content = []
    for user in users:
        user_content.append(get_user(user, http_client)[0])
    formatted_payload = {'name': name,
                         'order': order,
                         'rank': 7,
                         'protocols': ['ANY_RULE'],
                         'users': user_content,
                         ## This should be the ID (i.e CUSTOM07)
                         'urlCategories': [url_cat],
                         'state': 'ENABLED',
                         'requestMethods': ['CONNECT', 'DELETE', 'GET', 'HEAD', 'OPTIONS', 'OTHER', 'POST', 'PUT', 'TRACE'],
                         'description': f'allow {name} destinations',
                         'action': 'ALLOW'}
    result = zs_api_call('POST', '/urlFilteringRules', http_client, payload=formatted_payload)
    return result

def update_url_pol(pol_config, http_client:httpx.Client) -> dict:
    """Update existing URL filtering policy
    
    Args:
        pol_config
        http_client: httpx client instance used to send request
    
        Example input:
        {'id': 617899,
        'accessControl': 'READ_WRITE',
        'name': 'my_filtering_rule',
        'order': 1,
        'protocols': ['ANY_RULE'],
        'users': [{'id': 64846403, 'name': 'joe_blogs(joe_blogs@example.com)'}],
        'urlCategories': ['CUSTOM_09'],
        'state': 'ENABLED',
        'rank': 7,
        'requestMethods': ['OPTIONS', 'GET', 'HEAD', 'POST', 'PUT', 'DELETE', 'TRACE', 'CONNECT', 'OTHER'],
        'blockOverride': False,
        'description': 'joe blogs access rule',
        'enforceTimeValidity': False,
        'cbiProfileId': 0,
        'action': 'ALLOW'}
    
    Returns:
        Policy configuration as dict; format will match input format
    """
    result = zs_api_call('PUT', f'/urlFilteringRules/{pol_config["id"]}', http_client, payload=pol_config)
    return result

def delete_url_pol(pol_id:int, http_client:httpx.Client) -> None:
    """delete config for existing filtering policy
    
    Args:
        pol_id: ID value for the URL policy to be deleted
        http_client: httpx client instance used to send request
    
    Returns:
        None
    """
    result = zs_api_call('DELETE', f'/urlFilteringRules/{pol_id}', http_client)