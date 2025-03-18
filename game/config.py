import os

from dotenv import load_dotenv

load_dotenv('.env')

class Config:
    SERVER_ADDRESS = os.environ.get('SERVER_ADDRESS', None)
    SERVER_PORT = os.environ.get('SERVER_PORT', None)

