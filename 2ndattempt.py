import paramiko
import os

def copy_file_with_sudo(local_file, remote_host, remote_user, remote_file_path, sudo_password):
    # Create an SSH client instance
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # Connect to the remote server
    ssh.connect(remote_host, username=remote_user, password=sudo_password)

    # Create an SFTP client instance
    sftp = ssh.open_sftp()

    # Transfer the local file to a temporary location on the remote server
    temp_remote_file_path = f"/tmp/{os.path.basename(local_file)}"
    sftp.put(local_file, temp_remote_file_path)

    # Execute sudo command to move the file to the final destination
    stdin, stdout, stderr = ssh.exec_command(f"sudo -S -p '' mv {temp_remote_file_path} {remote_file_path}")
    stdin.write(f'{sudo_password}\n')
    stdin.flush()

    output = stdout.read().decode()
    errors = stderr.read().decode()

    # Print the output and errors
    if output:
        print("Output:")
        print(output)
    if errors:
        print("Errors:")
        print(errors)

    # Close the SFTP and SSH connections
    sftp.close()
    ssh.close()

# Example usage
keys_dir = os.path.join(os.getcwd(), 'SSHKeys')
remote_host = '172.16.5.1'
remote_user = 'blueteam'
sudo_password = 'abc123'

import os

# Loop through each file in the directory
for filename in os.listdir(keys_dir):
    # Construct the full file path
    file_path = os.path.join(keys_dir, filename)
    
    # Check if the current item is a file and ends with .pub
    if os.path.isfile(file_path) and filename.endswith('.pub'):
        user = filename[:-8]
        print("Public Key File:", filename)
        remote_file = f'/home/{user}/.ssh/'
        copy_file_with_sudo(file_path, remote_host, remote_user, remote_file, sudo_password)
