import paramiko

def test_sudo(remote_host, remote_user, sudo_password):
        # Create an SSH client instance
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # Connect to the remote server
    ssh.connect(remote_host, username=remote_user, password=sudo_password)

    # Create an SFTP client instance
    sftp = ssh.open_sftp()

    # Execute a sudo command to read the /etc/shadow file
    stdin, stdout, stderr = ssh.exec_command(f"sudo -S -p '' cat /etc/shadow >> /home/blueteam/hi/proof.txt")
    stdin.write(f'{sudo_password}\n')
    stdin.flush()

    output = stdout.read().decode()
    errors = stderr.read().decode()

    # Print the output and errors
    print("Output:")
    print(output)
    print("Errors:")
    print(errors)

    # Close the SFTP and SSH connections
    sftp.close()
    ssh.close()


# Example usage
remote_host = "172.16.5.1"
remote_user = "blueteam"
sudo_password = "abc123"

test_sudo(remote_host, remote_user, sudo_password)
