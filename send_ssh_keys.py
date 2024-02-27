from dotenv import load_dotenv
import os
from all_functions import add_user_if_necessary

def main():
    load_dotenv()
    remote_host = os.getenv('REMOTE_HOST')
    remote_user = os.getenv('REMOTE_USER')
    sudo_password = os.getenv('SUDO_PASSWORD')

    
def set_up_ssh_for_user(username:str):
    add_user_if_necessary(username)
    

if __name__ == '__main__':
    main()
