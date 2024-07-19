
import os
from database import Database

def db_exists():
    return os.path.exists('data.sdb')

def create_db():
    Database('data.sdb', {
        'spots': int,
    })
