import os
import json
import csv

from const import USER_DEPARTMENT, USER_PASSWORD
from zscaler_api import create_http_client, resolve_user_department, resolve_user_groups
from zscaler_api import get_user, get_all_users, create_user, update_user, delete_user
from zscaler_api import get_url_cat, create_url_cat, update_url_cat, delete_url_cat
from zscaler_api import get_url_pol, create_url_pol, delete_url_pol, update_url_pol



def get_state() -> dict:
    """Retrieve state of managed configuration"""
    with open(f'./state/state.json') as file:
            state = json.load(file)
    return state['user_state'], state['app_state']

def store_state(user_state:list[dict], app_state:list[dict]) -> None:
    """Store state back to file"""
    # Format the state file
    state_file_content = {'user_state': user_state,
                        'app_state': app_state}
    # Write the state file to JSON
    with open('./state/state.json', 'w') as state_file:
        json.dump(state_file_content, state_file)

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

def process_user_config(user_state:list[dict]) -> list[dict]:
    """Process the user configuration by comparing target config to current state and perform adds, updates, deletes"""
    # Pre-process target users for later matching
    target_users = get_target_user_config()
    for user in target_users:
        user['groups'].sort()


    # Format the user state to essential fields for comparison with target
    user_state_summary = []
    if user_state:
        for user in user_state:
            summary_user = {k:v for (k,v) in user.items() if k in ['name', 'email', 'groups']}
            summary_user['groups'] = [group['name'] for group in summary_user['groups']]
            summary_user['groups'].sort()
            user_state_summary.append(summary_user)
    user_state_name_list = [user['name'] for user in user_state_summary]
    
    # Create containers to hold user change data for later state updates
    created_user_configs = []
    modified_user_configs = []
    modified_user_ids = []
    deleted_user_ids = []
    
    # Remove users that have been deleted from user config 
    for existing_user in user_state_summary:
        if existing_user['name'] not in [user['name'] for user in target_users]:
            user_id = [user['id'] for user in user_state if user['name'] == existing_user['name']][0]
            print(f'deleting user {existing_user}')
            result = delete_user(user_id, HTTP_CLIENT)
            deleted_user_ids.append(user_id)
    
    # Create new users or modify existing users based on user config
    for target_user in target_users:
        if target_user in user_state_summary:
            print(f'skipping user - {target_user}')
            continue
        elif target_user['name'] in user_state_name_list:
            target_user['id'] = [user['id'] for user in user_state if user['name'] == target_user['name']][0]
            target_user['department'] = USER_DEPARTMENT_RESOLVED
            target_user['groups'] = resolve_user_groups(target_user['groups'], HTTP_CLIENT)
            print(f'modifying user {target_user}')
            target_user.update({'password': USER_PASSWORD})
            result = update_user(target_user, HTTP_CLIENT)
            modified_user_configs.append(result)
            modified_user_ids.append(target_user['id'])
        else:
            print(f'creating user {target_user}')
            target_user['department'] = USER_DEPARTMENT_RESOLVED
            target_user['groups'] = resolve_user_groups(target_user['groups'], HTTP_CLIENT)
            result = create_user(target_user, HTTP_CLIENT)
            target_user.update({'password': USER_PASSWORD})
            created_user_configs.append(result)

    # Remove deleted and modified users from user state
    user_state = [user for user in user_state if user['id'] not in deleted_user_ids and user['id'] not in modified_user_ids]
    
    # Update user state with new and modified user details
    user_state = user_state + created_user_configs + modified_user_configs
    
    # Get rid of any password information in the user state store before writing
    for user in user_state:
        user.pop('password', None)

    return user_state

def process_app_config(app_state:list[dict]) -> list[dict]:
    """Process the app configuration by comparing target config to current state and perform adds, updates, deletes"""

    # Pre-process target app for later matching
    target_apps = get_target_app_config()
    for target_app in target_apps:
        target_app['urls'].sort()
        target_app['users'].sort()

    # Format the app state to essential fields for comparison with target
    app_state_summary = []
    if app_state:
        for target_app in app_state:
            summary_app = {'name': target_app['name'], 'users': target_app['policy']['users'], 'urls': target_app['category']['urls']}
            summary_app['users'] = [user['name'] for user in summary_app['users']]
            summary_app['urls'].sort()
            summary_app['users'].sort()
            app_state_summary.append(summary_app)
    app_state_name_list = [app['name'] for app in app_state_summary]
    
    # Create containers to hold app change data for later state updates
    created_app_configs = []
    deleted_app_configs = []
    modified_app_configs =[]
    
    # Remove apps that have been deleted from app config 
    for existing_app in app_state:
        if existing_app['name'] not in [app['name'] for app in target_apps]:
            print(f'deleting app - {existing_app}')
            delete_url_pol(existing_app['policy']['id'], HTTP_CLIENT)
            delete_url_cat(existing_app['category']['id'], HTTP_CLIENT)
            deleted_app_configs.append(existing_app)
    
    # Create new url cats or modify existing url cats based on app config
    for target_app in target_apps:
        if target_app in app_state_summary:
            print(f'skipping app - {target_app}')
            continue
        elif target_app['name'] in app_state_name_list:
            print(f'modifying app {target_app}')
            for existing_app in app_state:
                if existing_app['name'] == target_app['name']:
                    category_config = existing_app['category']
                    category_config['urls'] = target_app['urls']
                    policy_config = existing_app['policy']
                    user_content = []
                    for user in target_app['users']:
                        user_content.append(get_user(user, HTTP_CLIENT)[0])
                    policy_config['users'] = user_content
                    result_cat = update_url_cat(category_config, HTTP_CLIENT)
                    result_pol = update_url_pol(policy_config, HTTP_CLIENT)
                    modified_app_configs.append({'name': target_app['name'], 'category': result_cat, 'policy': result_pol,})
        else:
            print(f'creating app {target_app}')
            url_cat = create_url_cat(target_app['name'], target_app['urls'], HTTP_CLIENT)
            url_pol = create_url_pol(target_app['name'], target_app['users'], url_cat['id'], HTTP_CLIENT)
            created_app_configs.append({'name': target_app['name'], 'category': url_cat, 'policy': url_pol,})
    
       
    # Remove deleted and modified apps from app state
    state_remove_list = [app['name'] for app in deleted_app_configs] + [app['name'] for app in modified_app_configs]
    app_state = [app for app in app_state if app['name'] not in state_remove_list]
        
    # Update user state with new and modified user details
    app_state = app_state + created_app_configs + modified_app_configs

    return app_state

if __name__ == "__main__":
    # Create an HTTP client instance for all requests
    HTTP_CLIENT = create_http_client()
    
    # Resolve the ID of the department that new users will be place into
    USER_DEPARTMENT_RESOLVED = resolve_user_department(USER_DEPARTMENT, HTTP_CLIENT)
    
    # Get current user state from state store
    user_state, app_state = get_state()

    # Process configuration updates
    user_state = process_user_config(user_state)
    app_state = process_app_config(app_state)

    # Store the new state information
    store_state(user_state, app_state)

    HTTP_CLIENT.close()