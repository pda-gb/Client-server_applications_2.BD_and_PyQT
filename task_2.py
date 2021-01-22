"""
2. Написать функцию host_range_ping() для перебора ip-адресов из заданного
 диапазона.
Меняться должен только последний октет каждого адреса.
По результатам проверки должно выводиться соответствующее сообщение.
"""

from ipaddress import ip_address
from platform import system
from socket import gethostbyname
from subprocess import Popen, PIPE


def host_range_ping():

    # =====================
    def host_ping(host):
        args = ['ping', '-n', '2']

        # для linux нужно явно указать количество запроса, иначе зациклится
        # для унивесальности, всё в нижнем регистре принудительно
        os_name = system().lower()

        if os_name == 'windows':
            pass
        else:
            args.pop(1)
            args.insert(1, '-c')

        try:
            ip_adr = str(ip_address(host))
        except ValueError:
            # если это не ip, а домен, то преобразуем в ip
            ip_adr = gethostbyname(host)
        args.append(ip_adr)
        # запускаем процесс пингования и ждём код выхода
        ping_host_proc = Popen(args, stdout=PIPE, shell=False)
        ping_host_proc.wait()
        args.pop()  # удаляем адрес из аргументов

        if ping_host_proc.returncode == 0:
            print(f'{host}     Узел доступен')
        else:
            print(f'{host}     Узел не доступен')
    # =====================

    begin_ip = input('Введите начальный адрес: ')
    try:
        tail = int(begin_ip.split('.')[3])
    except Exception as e:
        print(e)

    # Добиваемся введения подходящей цифры и пингуем, выводя результат
    while True:
        count_ip = input('Введите количество ip для проверки: ')
        if (int(count_ip) + tail) > 256:
            print('Проверка адресов только последнего октета, он не должен '
                  'превышать 255')
        elif not count_ip.isnumeric():
            print(' Введите число!')
        else:
            count_ip = int(count_ip)
            begin_ip = ip_address(begin_ip)
            end_ip = begin_ip + count_ip
            for i in range(0, count_ip):
                end_ip = begin_ip + i
                host_ping(end_ip)
            break







if __name__ == '__main__':
    host_range_ping()
