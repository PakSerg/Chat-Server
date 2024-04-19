#TODO доделать этот файл, доделать .env, доделать utilities, заменить все низкоуровневые функции в functions на send_json_to_client и
import os
from dotenv import load_dotenv 


load_dotenv()


HOST = os.environ.get('HOST')
PORT = int(os.environ.get('PORT')) 

MSG_SIZE = int(os.environ.get('MSG_SIZE'))
DB_URL = os.environ.get('DB_URL')