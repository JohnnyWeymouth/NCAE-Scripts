import os
import subprocess

# List of servers
server = "172.16.5.1"
local_public_key = "./SSHKeys/"

# Directory containing public keys
keys_directory = "/practiceNCAE/files/SSHKeys/SSHKeys"

# Check if the directory exists
if not os.path.isdir(keys_directory):
    print(f"Error: Directory {keys_directory} not found.")
    exit(1)

# Loop through each public key file in the directory
for pubkey_file in os.listdir(keys_directory):
    if pubkey_file.endswith(".pub"):
        print(pubkey_file)
        target_username = pubkey_file[:-8]
        pubkey_path = os.path.join(keys_directory, pubkey_file)
        print(f"Pushing public key {pubkey_file} to server {server}")
        pubkey_path_full = os.path.join(keys_directory, pubkey_file)
        subprocess.run(["scp", local_public_key, f"blueteam@{server}:/home/{target_username}/.ssh/"])
        print("Done.")

print("All public keys pushed to all servers.")
