import myparamiko
import threading
from datetime import datetime
from scp import SCPClient
def backup(router):
    # Make a copy of the router dictionary and remove the 'hostname' key
    router_copy = router.copy()
    hostname = router_copy.pop('hostname', None)  # Remove 'hostname' key

    try:
        client = myparamiko.connect(**router_copy)  # Now it won't have the 'hostname' key
        shell = myparamiko.get_shell(client)

        # Switch user if necessary
        myparamiko.send_command(shell, 'su')
        myparamiko.send_command(shell, router_copy['passwd'], 2)

        # Check NTP status
        cmd = 'if [[ $(timedatectl status | grep -i "NTP service" | awk \'{print $3}\') == "active" ]]; then echo "NTP is running"; else echo "NTP is not running"; fi'
        myparamiko.send_command(shell, cmd)

        # Set hostname using the extracted value
        if hostname:
            hostname_cmd = f'hostnamectl set-hostname {hostname}'
            myparamiko.send_command(shell, hostname_cmd)

        # Additional commands and operations
        output = myparamiko.show(shell)
        print(f"Output from {router_copy['server_ip']}:\n{output}")
        output_list = output.splitlines()
        count = len(output_list)
        print(f"The number of elements in the list is: {count}")
        output_list = output_list[7:count - 1]
        output = '\n'.join(output_list)
        # print(output)
        now = datetime.now()
        year = now.year
        mounth = now.month
        day = now.day

        file_name = f'{router["server_ip"]}_{year}-{mounth}-{day}.txt'
        print(file_name)
        if 'NTP is running' in output:
            print("NTP is running as the expected.")
            # Do something based on the condition
        else:
            print("Configre NTP First.")
            raise RuntimeError("NTP is not running. Execution halted.")

        with open(file_name, 'w') as f:
            f.write(output)
        myparamiko.close(client)

    except Exception as e:
        print(f"Error occurred on {router_copy['server_ip']}: {e}")



router1 = {'server_ip': '10.0.0.20', 'server_port': '22', 'user':'bilge', 'passwd':'123', 'hostname': 'rke21'}
router2 = {'server_ip': '10.0.0.21', 'server_port': '22', 'user':'bilge', 'passwd':'123', 'hostname': 'rke22'}
router3 = {'server_ip': '10.0.0.22', 'server_port': '22', 'user':'bilge', 'passwd':'123', 'hostname': 'rke23'}

routers = [router1, router2,  router3]
threads = list()
for router in routers:
    th = threading.Thread(target=backup, args=(router,))
    threads.append(th)
    print(th)

for th in threads:
    th.start()


for th in threads:
    th.join()