import os
import pymongo

from typing import Any, Dict
from dotenv import load_dotenv

load_dotenv(override=True)

MONGODB_HOST = os.getenv('MONGODB_HOST')
MONGODB_PORT = int(os.getenv('MONGODB_PORT'))
MONGODB_USERNAME = os.getenv('MONGODB_USERNAME')
MONGODB_PASSWORD = os.getenv('MONGODB_PASSWORD')


class DB:
    
    def __init__(self):
        url = f'mongodb://{MONGODB_USERNAME}:{MONGODB_PASSWORD}@{MONGODB_HOST}:{MONGODB_PORT}/'
        self.conn = pymongo.MongoClient(url)
        self.db = self.conn.friendtech
        self.subject = self.db.subject
        
    def set(self, data: Dict[str, Any]) -> str:
        return self.subject.insert_one(data).inserted_id
    
    def get(self, subject: str):
        return self.subject.find_one({'subject': subject})
        
    
if __name__ == '__main__':
    from web_data import get_cached_trades_array
    
    trades_array = get_cached_trades_array()
    
    db = DB()
    data = db.get('subject')
    print(data)