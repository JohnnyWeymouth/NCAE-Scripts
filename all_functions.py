import paramiko
import os
from dotenv import load_dotenv
from typing import Generator
from contextlib import contextmanager

class UnexpectedRemoteHostError(Exception):
    """Custom exception for representing errors generated on the remote server."""
    def __init__(self, message):
        super().__init__(message)
        self.message = message

class UsefulStrings():
    """Grabs passwords from the env file, avoiding global variables"""    
    def __init__(self) -> None:
        load_dotenv()
        self.strongPassword1 = os.getenv('STRONG_PASSWORD_1')
        self.strongPassword2 = os.getenv('STRONG_PASSWORD_2')

@contextmanager
def ssh_connection(host_ip:str, username:str, password:str=None, path_to_priv_key:str=None) -> Generator[paramiko.SSHClient, None, None]:
    """Sets up an ssh context that will automatically close if an error occurs.

    Args:
        host_ip (str): the designated ip to connect to
        username (str): the username on the host
        password (str, optional): said user's password. Required unless path_to_priv_key is specified. Defaults to None.
        path_to_priv_key (str, optional): said user's local path to their private key. Required unless password is specified. Defaults to None.

    Raises:
        ValueError: Only specify a password or a private key, not both

    Yields:
        Generator[paramiko.SSHClient, None, None]: the ssh client session
    """    
    if (password is None and path_to_priv_key is None) or (password is not None and path_to_priv_key is not None):
        raise ValueError('Specify a private key OR a password')
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(host_ip, username=username, password=password)
        yield ssh
    finally:
        ssh.close()

@contextmanager
def sftp_connection(ssh:paramiko.SSHClient) -> Generator[paramiko.SFTPClient, None, None]:
    """Given that an ssh session has already been initialized, sets up a secure file
    transfer protocol session context. If an error occurs, the session will
    automatically close.

    Args:
        ssh (paramiko.SSHClient): the ssh client session

    Yields:
        Generator[paramiko.SFTPClient, None, None]: the sftp client session
    """    
    sftp = ssh.open_sftp()
    try:
        yield sftp
    finally:
        sftp.close()

def execute_command(ssh:paramiko.SSHClient, command:str, necessary_inputs:list[str]=None) -> tuple[str, str]:
    """Executes an unprivileged command on a remote host using an ssh session

    Args:
        ssh (paramiko.SSHClient): the ssh client session
        command (str): the command to be executed
        necessary_input (str, optional): any additions that need to be added after 
        the command is executed. Defaults to None.

    Returns:
        tuple[str, str]: output (empty if none) and errors (empty if none)
    """  
    stdin, stdout, stderr = ssh.exec_command(command)
    if necessary_inputs:
        for n_input in necessary_inputs:
            stdin.write(f'{n_input}\n')
            stdin.flush()
    output = stdout.read().decode()
    errors = stderr.read().decode()
    return output, errors

def execute_privileged_command(ssh:paramiko.SSHClient, command:str, sudo_password:str, necessary_inputs:list[str]=None) -> tuple[str, str]:
    """Executes an unprivileged command on a remote host using an ssh session

    Args:
        ssh (paramiko.SSHClient): the ssh client session
        command (str): the command to be executed
        sudo_password (str): the password of the sudoer on the remote host
        necessary_input (str, optional): any additions that need to be added after 
        the command is executed. Defaults to None.

    Returns:
        tuple[str, str]: output (empty if none) and errors (empty if none)
    """  
    stdin, stdout, stderr = ssh.exec_command(f"sudo -S -p '' {command}")
    stdin.write(f'{sudo_password}\n')
    stdin.flush()
    if necessary_inputs:
        for n_input in necessary_inputs:
            stdin.write(f'{n_input}\n')
            stdin.flush()
    output = stdout.read().decode()
    errors = stderr.read().decode()
    return output, errors

def add_user_if_necessary(ssh:paramiko.SSHClient, user_to_add:str, sudo_password:str) -> bool:
    """Adds a user to the remote host if they are not already added

    Args:
        ssh (paramiko.SSHClient): the ssh client session
        user_to_add (str): the name of the user in question
        sudo_password (str): the sudo password of the connected client

    Raises:
        UnexpectedRemoteHostError: Should the remote host not run as expected,
        this error with the error's message will be raised.

    Returns:
        bool: whether the user was added. If false, the remote host already had 
        the user
    """    
    # Check if the user is already added to the remote host
    id_command = f'id {user_to_add}'
    output, errors = execute_command(ssh, id_command)

    # If user already added to remote host, return false
    if not errors:
        return False
    
    # Otherwise, add the user, set password, give them a dir, and return true
    else:
        # Add the user
        command = f'useradd -m -s /bin/bash {user_to_add}'
        output, errors = execute_privileged_command(ssh, command, sudo_password)
        if errors:
            if 'already exists' not in errors:
                raise UnexpectedRemoteHostError(errors)

        # Set the user password
        reset_user_password(ssh, user_to_add, sudo_password)

        # Change the ownership of the user's home directory
        command = f'chown -R {user_to_add}:{user_to_add} /home/{user_to_add}'
        output, errors = execute_privileged_command(ssh, command, sudo_password)
        if errors:
            raise UnexpectedRemoteHostError(errors)

        # Added
        return True
    
def reset_user_password(ssh:paramiko.SSHClient, user:str, sudo_password:str):
    command = f'passwd {user}'
    new_password = UsefulStrings().strongPassword1
    output, errors = execute_privileged_command(ssh, command, sudo_password, [new_password, new_password])
    if 'updated successfully' not in errors:
        raise UnexpectedRemoteHostError(errors)
    
def recursively_create_dir(ssh:paramiko.SSHClient, dir_path:str, sudo_password:str):
    command = f'mkdir -p {dir_path}'
    output, errors = execute_privileged_command(ssh, command, sudo_password)
    if errors:
        raise UnexpectedRemoteHostError(errors)
    
def create_blank_file_with_path(ssh:paramiko.SSHClient, path:str, sudo_password:str):
    # Delete the file (if it exists)
    command = f'rm {path}'
    output, errors = execute_privileged_command(ssh, command, sudo_password)
    if 'No such file' not in errors:
        raise UnexpectedRemoteHostError(errors)
    
    # Recreate it
    command = f'touch {path}'
    output, errors = execute_privileged_command(ssh, command, sudo_password)
    if errors:
        raise UnexpectedRemoteHostError(errors)
        
def copy_file_to_remote_host(path_to_local_file:str, host_ip:str, username:str, sudo_password:str) -> str:
    """Copies a file from the client's computer to the temp folder of the remote host.

    Args:
        path_to_local_file (str): the path on the client's computer
        host_ip (str): the ip of the remote host
        username (str): the username on the remote host
        sudo_password (str): the sudoer's password on the remote host

    Returns:
        str: the remote host file path of the copied file
    """    
    with ssh_connection(host_ip, username, sudo_password) as ssh:
        with sftp_connection(ssh) as sftp:
            file_name = os.path.basename(path_to_local_file)
            temp_remote_file_path = f"/tmp/{file_name}"
            sftp.put(path_to_local_file, temp_remote_file_path)
            return temp_remote_file_path