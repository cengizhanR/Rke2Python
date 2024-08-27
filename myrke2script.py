import myparamiko
import threading
from scp import SCPClient
def backup(router):
    client = myparamiko.connect(**router)
    shell = myparamiko.get_shell(client)

    myparamiko.send_command(shell, 'uname -a')

    cmd = 'su'
    myparamiko.send_command(shell, cmd)
    myparamiko.send_command(shell, '123', 2)
    # myparamiko.show(shell)
    myparamiko.send_command(shell, 'whoami')
    output = myparamiko.show(shell)
    # print(output)
    output_list = output.splitlines()
    count = len(output_list)
    print(f"The number of elements in the list is: {count}")
    output_list = output_list[7:count - 1]
    output = '\n'.join(output_list)
    # print(output)
    from datetime import datetime
    now = datetime.now()
    year = now.year
    mounth = now.month
    day = now.day
    hour = now.hour
    minute = now.minute

    file_name = f'{router["server_ip"]}_{year}-{mounth}-{day}.txt'
    print(file_name)
    if 'root' in output:
        print("The command output contains the expected string.")
        # Do something based on the condition
    else:
        print("The command output does not contain the expected string.")

    with open(file_name, 'w') as f:
        f.write(output)

    myparamiko.close(client)

router1 = {'server_ip': '10.0.0.20', 'server_port': '22', 'user':'bilge', 'passwd':'123'}
router2 = {'server_ip': '10.0.0.21', 'server_port': '22', 'user':'bilge', 'passwd':'123'}
router3 = {'server_ip': '10.0.0.22', 'server_port': '22', 'user':'bilge', 'passwd':'123'}

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