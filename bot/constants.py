import os
import json

from pathlib import Path
from dotenv import load_dotenv

load_dotenv(override=True)

_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
ABI_PATH = _DIR / 'abi'

BASE_HTTPS_URL = os.getenv('BASE_HTTPS_URL')
BASE_ALCHEMY_URL = os.getenv('BASE_ALCHEMY_URL')
BASE_WSS_URL = os.getenv('BASE_WSS_URL')

PRIVATE_KEY = os.getenv('PRIVATE_KEY')

FT_ADDRESS = os.getenv('FT_ADDRESS')
FT_ABI = json.load(open(ABI_PATH / 'FriendtechSharesV1.json', 'r'))

TWITTER_EMAIL = os.getenv('TWITTER_EMAIL')
TWITTER_USERNAME = os.getenv('TWITTER_USERNAME')
TWITTER_PASSWORD = os.getenv('TWITTER_PASSWORD')