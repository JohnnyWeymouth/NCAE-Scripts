import paramiko

def create_remote_directory(hostname, username, password, remote_dir):
    # Connect to the remote server
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname, username=username, password=password)
    
    # Check if the directory exists
    stdin, stdout, stderr = ssh.exec_command(f"test -d {remote_dir} && echo 'Exists' || echo 'Not exists'")
    directory_status = stdout.read().decode().strip()

    # If directory doesn't exist, create it
    if directory_status == 'Not exists':
        ssh.exec_command(f"mkdir -p {remote_dir}")
        print(f"Created directory: {remote_dir}")
    else:
        print(f"Directory already exists: {remote_dir}")

    # Close the SSH connection
    ssh.close()

# Example usage
hostname = '172.16.5.1'
username = 'blueteam'
password = 'abc123'
remote_dir = '/blueteam/hi/imhere'

create_remote_directory(hostname, username, password, remote_dir)
