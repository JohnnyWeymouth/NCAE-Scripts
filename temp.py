import paramiko

# Connect to the SSH server
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.16.5.1', username='blueteam', password='abc123')

# Execute the command
stdin, stdout, stderr = ssh.exec_command('ls /home')




# Wait for the command to complete and get the exit status
exit_status = stdout.channel.recv_exit_status()

if exit_status == 0:
    print("Command executed successfully")
else:
    print("Command failed with exit status:", exit_status)

# Close the SSH connection
ssh.close()
























# import sys
# import select

# # Assuming stdout is already set up properly, e.g., sys.stdout

# # Set a timeout of 1 second
# timeout = 1

# # List of file descriptors to monitor (in this case, just sys.stdout)
# read_list = [sys.stdout]

# # Use select to wait for data or timeout
# ready_to_read, _, _ = select.select(read_list, [], [], timeout)

# if ready_to_read:
#     # If there is data available to read, read it
#     data = sys.stdout.read()
#     print("Data received:", data)
# else:
#     # If timeout occurs, print a message
#     print("Timeout occurred. No data received within the specified time.")
