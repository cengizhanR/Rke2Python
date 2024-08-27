import paramiko
import time
import threading
from scp import SCPClient


def connect(server_ip, server_port, user, passwd):
    """
    Establishes an SSH connection to the server.

    :param server_ip: IP address of the server.
    :param server_port: SSH port number.
    :param user: SSH username.
    :param passwd: SSH password.
    :return: An active SSHClient object.
    """
    ssh_client = paramiko.SSHClient()
    ssh_client.load_system_host_keys()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        print(f'Connecting to {server_ip}')
        ssh_client.connect(hostname=server_ip, port=server_port, username=user, password=passwd,
                           look_for_keys=False, allow_agent=False)
        print(f'Connected to {server_ip}')
        return ssh_client
    except paramiko.AuthenticationException:
        print(f"Authentication failed for {server_ip}")
    except paramiko.SSHException as e:
        print(f"SSH connection error to {server_ip}: {e}")
    except Exception as e:
        print(f"Failed to connect to {server_ip}: {e}")
    return None

def scpfile(ssh_client, files, remote_path):
    """
    Transfers files to a remote server using SCP.

    :param ssh_client: An active SSHClient object.
    :param files: Path to the local file or list of files to transfer.
    :param remote_path: Destination path on the remote server.
    """
    try:
        scp = SCPClient(ssh_client.get_transport())
        scp.put(files, remote_path)
        print(f"Transferred {files} to {remote_path}")
    except Exception as e:
        print(f"Failed to transfer files: {e}")
    finally:
        scp.close()

def get_shell(ssh_client):
    """
    Opens an interactive shell session over SSH.

    :param ssh_client: An active SSHClient object.
    :return: The interactive shell channel or None if invocation fails.
    """
    try:
        shell = ssh_client.invoke_shell()
        print("Interactive shell session established.")
        return shell
    except paramiko.SSHException as sshException:
        print(f"Failed to invoke shell: {sshException}")
    except Exception as e:
        print(f"An unexpected error occurred while invoking shell: {e}")
    return None

def send_command (shell, command, timeout=1):
    try:
        print(f"Sending command: {command}")
        shell.send(command + '\n')
        time.sleep(timeout)
    except paramiko.SSHException as sshException:
        print(f"Failed to send command '{command}': {sshException}")
    except Exception as e:
        print(f"An unexpected error occurred while sending command '{command}': {e}")
    return ""
def show (shell,n=10000):
    output=shell.recv(n)
    return output.decode()

def close(ssh_client):
    if ssh_client.get_transport().is_active() == True:
        print('Closing connection...')
        ssh_client.close()
def send_from_list(shell,content):
    for cmd in content:
        print(f'Sending command: {cmd}')
        send_command(shell,cmd)
def send_from_file(shell,file):
    with open(file, 'r') as f:
        content = f.read().splitlines()
    for cmd in content:
        print(f'Sending command: {cmd}')
        send_command(shell,cmd)
def target_function(router):
    ssh_client = connect(server_ip=router['server_ip'], server_port=router['server_port'], user=router['user'],
                             passwd=router['passwd'])

    shell = get_shell(ssh_client)
    send_from_file(shell, router['config'])
    output = show(shell)
    print(output)

if __name__ == '__main__':
    router1 = {'server_ip': '10.1.1.10', 'server_port': '22', 'user':'u1', 'passwd':'cisco', 'config':'ospf.txt'}
    router2 = {'server_ip': '10.1.1.20', 'server_port': '22', 'user': 'u1', 'passwd': 'cisco', 'config':'eigrp.txt'}
    router3 = {'server_ip': '10.1.1.30', 'server_port': '22', 'user': 'u1', 'passwd': 'cisco', 'config':'router3.conf'}


    devices = [router1, router2, router3]

    my_threads = list()
    for router in devices:
        th = threading.Thread(target=target_function, args=(router,))
        my_threads.append(th)

    for th in my_threads:
        th.start()

    for th in my_threads:
        th.join()

