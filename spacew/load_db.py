
import os
from datetime import date
from database import Database

def db_exists():
    return os.path.exists('data.sdb')

def create_db():
    db = Database('data.sdb', {
        'spots': int,
    }, date)
    db.save()
