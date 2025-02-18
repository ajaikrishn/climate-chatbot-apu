import paramiko
from secrets import remote_host,remote_user,remote_password
from scp import SCPClient
import os
import time
from paramiko.ssh_exception import SSHException

# Define connection details    
local_folder = "/home/ajai-krishna/Downloads/extracted_models-20250130T045853Z-001" 
remote_folder = "/home/cccs/Documents/Anjishnu/India_Climate_Report/data/India_netcdf" 

# Connection settings
MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds
TIMEOUT = 30     # seconds

def create_scp_client():
    for attempt in range(MAX_RETRIES):
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            # Add timeout parameter to the connection
            ssh.connect(
                remote_host, 
                username=remote_user, 
                password=remote_password,
                timeout=TIMEOUT,
                banner_timeout=TIMEOUT
            )
            
            # Configure keep-alive settings
            transport = ssh.get_transport()
            transport.set_keepalive(30)
            
            scp = SCPClient(transport, socket_timeout=TIMEOUT)
            return ssh, scp
            
        except (paramiko.SSHException, TimeoutError, ConnectionError) as e:
            print(f"Connection attempt {attempt + 1} failed: {str(e)}")
            if attempt < MAX_RETRIES - 1:
                print(f"Retrying in {RETRY_DELAY} seconds...")
                time.sleep(RETRY_DELAY)
            else:
                print("Max retries reached. Could not establish connection.")
                return None, None
        except Exception as e:
            print(f"Unexpected error while connecting: {str(e)}")
            return None, None

def upload_folder(local_path, remote_path):
    if not os.path.exists(local_path):
        print(f"Error: Local path '{local_path}' does not exist")
        return

    ssh, scp = create_scp_client()
    if scp:
        try:
            print(f"Starting upload from '{local_path}' to '{remote_path}'...")
            scp.put(local_path, recursive=True, remote_path=remote_path)
            print(f"Folder '{local_path}' successfully uploaded to '{remote_path}'")
        except Exception as e:
            print(f"Error transferring folder: {str(e)}")
        finally:
            try:
                scp.close()
                ssh.close()
            except Exception as e:
                print(f"Error closing connections: {str(e)}")

# Run the upload
if __name__ == "__main__":
    upload_folder(local_folder, remote_folder)
