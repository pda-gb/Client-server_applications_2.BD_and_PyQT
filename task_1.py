"""
1. Написать функцию host_ping(), в которой с помощью утилиты ping
будет проверяться доступность сетевых узлов.
Аргументом функции является список, в котором каждый сетевой узел
должен быть представлен именем хоста или ip-адресом.
В функции необходимо перебирать ip-адреса и проверять
их доступность с выводом соответствующего сообщения
(«Узел доступен», «Узел недоступен»). При этом ip-адрес
сетевого узла должен создаваться с помощью функции ip_address().
"""
from ipaddress import ip_address
from platform import system
from socket import gethostbyname
from subprocess import Popen, PIPE


def host_ping(list_hosts):
    args = ['ping', '-n', '2']

    # для linux нужно явно указать количество запроса, иначе зациклится
    # для унивесальности, всё в нижнем регистре принудительно
    os_name = system().lower()

    if os_name == 'windows':
        pass
    else:
        args.pop(1)
        args.insert(1, '-c')

    for itm in list_hosts:
        try:
            ip_adr = str(ip_address(itm))
        except ValueError:
            # если это не ip, а домен, то преобразуем в ip
            ip_adr = gethostbyname(itm)
        args.append(ip_adr)
        # запускаем процесс пингования и ждём код выхода
        ping_host_proc = Popen(args, stdout=PIPE, shell=False)
        ping_host_proc.wait()
        args.pop()  # удаляем адрес из аргументов

        if ping_host_proc.returncode == 0:
            print(f'{itm}     Узел доступен')
        else:
            print(f'{itm}     Узел не доступен')


if __name__ == '__main__':
    hosts = ['yandex.ru', 'youtube.com', '10.0.0.1', '192.168.0.1', '1.1.1.1']
    host_ping(hosts)
