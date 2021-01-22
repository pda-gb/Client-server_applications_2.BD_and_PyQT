"""
Написать функцию host_range_ping_tab(), возможности которой основаны на
функции из примера 2.
Но в данном случае результат должен быть итоговым по всем ip-адресам,
представленным в табличном формате
(использовать модуль tabulate). Таблица должна состоять из двух колонок
"""

from ipaddress import ip_address
from platform import system
from socket import gethostbyname
from subprocess import Popen, PIPE
from re import match
from tabulate import tabulate

def host_range_ping_tab():

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
            result = (host, 'Узел доступен')
        else:
            result = (host, 'Узел не доступен')
        return result


    # =====================

    while True:
        begin_ip = input('Введите начальный адрес: ')
        # Проверка регуляркой на соответствие
        if match(r'\d{0,255}\.\d{0,255}\.\d{0,255}\.\d{0,255}', begin_ip):
            # получаем последний октет
            tail = int(begin_ip.split('.')[3])
            break
        else:
            print('Неправильно введены данные, введите в формате '
                  'ХХХ.ХХХ.ХХХ.ХХХ, где ХХХ - от 0 до 255 !\n')

    # Добиваемся введения подходящей цифры и пингуем, выводя результат
    while True:
        count_ip = input('Введите количество ip для проверки: ')
        if (int(count_ip) + tail) > 256:
            print('Проверка адресов только последнего октета, он не должен '
                  'превышать 255')
        elif not count_ip.isnumeric():
            print(' Введите число!')
        else:
            # для сбора в табл., ('Host', 'Result') - первый элемент для шапки
            end_result = [('Host', 'Result'), ]
            count_ip = int(count_ip)
            # задаём объекты ipv4
            begin_ip = ip_address(begin_ip)
            end_ip = begin_ip + count_ip
            # пингуем каждый ip
            print('Подождите, выполняется операция...')
            for i in range(0, count_ip):
                end_ip = begin_ip + i
                # собираем в список результат пинга
                end_result.append(host_ping(end_ip))
            print('Готово!\n')
            print(tabulate(end_result, headers='firstrow', tablefmt='presto',
                           stralign="center"))
            break

if __name__ == '__main__':
    host_range_ping_tab()
