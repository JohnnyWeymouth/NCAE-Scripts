from dotenv import load_dotenv
import os
from all_functions import add_user_if_necessary, recursively_create_dir
from all_functions import create_blank_file_with_path, ssh_connection, recursively_change_owner
from all_functions import change_permissions, copy_file_to_remote_host, copy_file_to_other_file
import paramiko

#TODO test using the private key to log into ssh instead of the password
def main():
    load_dotenv()
    remote_host_ip = os.getenv('REMOTE_HOST')
    remote_user = os.getenv('REMOTE_USER')
    sudo_password = os.getenv('SUDO_PASSWORD')

    designated_user = 'andrewanderson'
    local_path_of_pub_ssh_key = r'C:\Users\johnn\OneDrive\Desktop\School\NCAE-Scripts\SSHKeys\andrewanderson_key.pub'

    with ssh_connection(remote_host_ip, remote_user, sudo_password) as ssh:
        set_up_ssh_for_user(ssh, designated_user, local_path_of_pub_ssh_key, 'abc123')

def set_up_ssh_for_user(ssh:paramiko.SSHClient, designated_user:str, local_path_of_pub_ssh_key:str, sudo_password:str):
    # Add the user, if needed, to the remote host
    add_user_if_necessary(ssh, designated_user, sudo_password)

    # Add the necessary dirs if not already created
    dir_path = f'/home/{designated_user}/.ssh/'
    recursively_create_dir(ssh, dir_path, sudo_password)

    # Recreates the known_hosts files from scratch
    file_path = f'/home/{designated_user}/.ssh/known_hosts'
    create_blank_file_with_path(ssh, file_path, sudo_password)

    # Send the pub file from client to /home/username/.ssh/authorized_keys
    tmp_path_on_remote = copy_file_to_remote_host(ssh, local_path_of_pub_ssh_key)
    file_path = f'/home/{designated_user}/.ssh/authorized_keys'
    copy_file_to_other_file(ssh, tmp_path_on_remote, file_path, sudo_password)

    # Change the files' and dirs' owner
    dir_path = f'/home/{designated_user}/'
    recursively_change_owner(ssh, dir_path, designated_user, sudo_password)

    # Change the files' and dirs' permissions
    dir_path = f'/home/{designated_user}/'
    change_permissions(ssh, dir_path, 755, sudo_password)
    dir_path = f'/home/{designated_user}/.ssh'
    change_permissions(ssh, dir_path, 700, sudo_password)
    file_path = f'/home/{designated_user}/.ssh/authorized_keys'
    change_permissions(ssh, file_path, 600, sudo_password)
    file_path = f'/home/{designated_user}/.ssh/known_hosts'
    change_permissions(ssh, file_path, 644, sudo_password)

    
if __name__ == '__main__':
    main()
