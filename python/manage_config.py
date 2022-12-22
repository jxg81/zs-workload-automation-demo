import os
import json
import csv

from const import USER_DEPARTMENT
from zscaler_api import zs_api_call, create_http_client

http_client = create_http_client()

def resolve_user_department(department:str=USER_DEPARTMENT) -> dict:
    """Get ID's for already created department name"""
    user_department: list = zs_api_call('GET', f'/departments?search={department}', http_client)
    return user_department[0]

def resolve_user_groups(groups:list):
    """Get ID's for already created group names"""
    current_groups: list = zs_api_call('GET', '/groups', http_client)
    target_groups = [group for group in current_groups if group['name'] in groups]
    return target_groups

def get_users():
    """Get ID's for already created group names"""
    users: list = zs_api_call('GET', '/users', http_client)
    return users

def get_target_user_config() -> list[dict]:
    """Get target user config"""
    target_user_config = []
    with open('./config/users.csv', newline='') as input:
        input_reader = csv.DictReader(input)
        for user in input_reader:
            user['groups'] = [group for group in user['groups'].split(':')]
            target_user_config.append(user)
    return target_user_config

def get_target_app_config() -> list[dict]:
    """Get target app config"""
    app_list = os.listdir('./config/apps')
    target_app_config = []
    for app in app_list:
        with open(f'./config/apps/{app}') as file:
            target_app_config.append(json.load(file))
    return target_app_config

def get_state() -> dict:
    """Retrieve state of managed configuration"""
    with open(f'./config/state.json') as file:
            state = json.load(file)
    return state['user_state'], state['app_state']

def create_user(user: dict):
    """
    {"name": user['name'],
    "email": user['email'],
    "groups": user['groups'],
    "department": user['department'],
    "password": user['password']}
    """
    result = zs_api_call('POST', '/users', http_client, payload=user)
    
def delete_user(user: dict):
    """
    {"name": user['name'],
    "email": user['email'],
    "groups": user['groups'],
    "department": user['department'],
    "password": user['password']}
    """
    result = zs_api_call('DELETE', f'/users{user["id"]}', http_client)

def create_url_cat(urls: list):
    """
    {
    "id": "ANY",
    "configuredName": "string",
    "urls": [
        "string"
    ],
    "customCategory": True,
    "type": "URL_CATEGORY"
    }
    """
    formatted_payload = {'superCategory': 'USER_DEFINED',
                        "configuredName": "testcat4",
                        "urls": [".zscaler.com",
                                ".github.com"],
                        "customCategory": True,
                        "type": "URL_CATEGORY"}
    result = zs_api_call('POST', '/urlCategories', http_client, payload=formatted_payload)
    return result

pre_format_users = [{'name': 'testing_user_1',
                   'email': 'testing_user_1@zphyrs.com',
                   'password': 'P@ssw0rd123*',
                   'groups': ['package_management', 'security_services']},
                    {'name': 'testing_user_2',
                   'email': 'testing_user_2@zphyrs.com',
                   'password': 'P@ssw0rd123*',
                   'groups': ['package_management', 'security_services']},
                    {'name': 'testing_user_3',
                   'email': 'testing_user_3@zphyrs.com',
                   'password': 'P@ssw0rd123*',
                   'groups': ['package_management', 'security_services']}]

def process_config(users:list[dict]=pre_format_users):
    user_state, app_state = get_state()
    department = resolve_user_department()
    for user in users:
        if user in user_state:
            print(f'skipping - {user}')
            continue
        user['groups'] = resolve_user_groups(user['groups'])
        user['department'] = department
        print(result)
    for app in app_state:
        pass

#print(zs_api_call('GET', '/urlCategories?customOnly=True', http_client))
print(create_url_cat('blah'))
http_client.close()
#user = {'name': 'test_user',
#        'email': 'test_user@zphyrs.com',
#        'groups': [{'id': 63108494, 'name': 'package_management'},
#                   {'id': 63108602, 'name': 'security_services'}],
#        'department': {'id': 63108466, 'name': 'workloads'},
#        'password': 'P@ssw0rd123*'}
#result = zs_api_call('POST', '/users', AUTH_TOKEN, payload=user)
#user.update('id': result)
#print(result)
#print(get_target_user_state())
#print(get_target_app_state())

formatted_payload = {
  "id": "ANY",
  "configuredName": "string",
  "urls": [
    "string"
  ],
  "customCategory": True,
  "type": "URL_CATEGORY"
}