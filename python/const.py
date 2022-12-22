from os import getenv

try:
    from dotenv import load_dotenv
    load_dotenv()
except ModuleNotFoundError:
    pass

RATE_LIMIT: float = float(getenv('ZIA_RATE_LIMIT')) if getenv('ZIA_RATE_LIMIT') else 2
ZIA_USERNAME: str = getenv('ZIA_USERNAME')
ZIA_PASSWORD: str = getenv('ZIA_PASSWORD')
ZIA_API_KEY: str = getenv('ZIA_API_KEY')
ZIA_CLOUD: str = getenv('ZIA_CLOUD')
OAUTH_SERVER: str = getenv('OAUTH_SERVER')
OAUTH_SCOPE: str = getenv('OAUTH_SCOPE')
OAUTH_TOKEN_PATH: str = getenv('OAUTH_TOKEN_PATH')
OAUTH_CLIENT_ID: str = getenv('OAUTH_CLIENT_ID')
OAUTH_CLIENT_SECRET: str = getenv('OAUTH_CLIENT_SECRET')

USER_DEPARTMENT = 'workloads'