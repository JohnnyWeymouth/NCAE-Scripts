from dotenv import load_dotenv
import os
from all_functions import add_user_if_necessary, reset_user_password, recursively_create_dir, create_blank_file_with_path, ssh_connection, sftp_connection
import paramiko

def main():
    load_dotenv()
    remote_host = os.getenv('REMOTE_HOST')
    remote_user = os.getenv('REMOTE_USER')
    sudo_password = os.getenv('SUDO_PASSWORD')
    
def set_up_ssh_for_user(ssh:paramiko.SSHClient, designated_user:str, sudo_password:str):
    # Add the user, if needed, to the remote host
    add_user_if_necessary(ssh, designated_user, sudo_password)

    # Reset the password for that user to something strong
    reset_user_password(ssh, designated_user, sudo_password)

    # Add the necessary dirs if not already created
    dir_path = f'/home/{designated_user}/.ssh/'
    recursively_create_dir(ssh, dir_path, sudo_password)

    # Recreates the known_hosts and authorized_keys files from scratch
    path = f'/home/{designated_user}/.ssh/known_hosts'
    create_blank_file_with_path(ssh, path, sudo_password)

    path = f'/home/{designated_user}/.ssh/authorized_keys'
    create_blank_file_with_path(ssh, path, sudo_password)


    




    
if __name__ == '__main__':
    main()
