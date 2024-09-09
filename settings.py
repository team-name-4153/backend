
from os import environ
from dotenv import load_dotenv
load_dotenv()
DEBUG = bool(environ.get("DEBUG", 0))


