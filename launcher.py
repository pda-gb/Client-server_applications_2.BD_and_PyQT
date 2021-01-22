"""
Запуск сервера и заданное количество клиентов
"""
import os
import signal
import subprocess
import sys
from os.path import dirname

all_servers = []
all_clients = []
# полный текущий путь заущенного скрипта launcher
work_dir = dirname(os.path.abspath(__file__))
while True:
    ask = input('Выход - q, запустить сервер и клиент - x, '
                'завершить работу серверов - w, завершить работу клиентов - e,'
                ' завершить все запущенные процессы - k\n')

    # выход
    if ask == 'q':
        break

    # Запуск
    if ask == 'x':
        # выбор порта
        port = input('Укажите порт подключения (1024-65535) или оставить'
                     ' по умолчанию - d\n')
        if port == 'd':
            port = ''
        else:
            port = f'-p {port}'
        # выбор адреса
        address = input('Укажите адпес подключения (ХХХ.ХХХ.ХХХ.ХХХ) '
                        'или оставить по умолчанию - d\n')
        if address == 'd':
            address = ''
        else:
            address = f'-a {address}'
        ask = None

        # запуск сервера ------
        # для linux .CREATE_NEW_CONSOLE не работает
        if sys.platform == 'Windows':
            all_servers.append(
                subprocess.Popen(f'python {work_dir}\server.py {port} '
                                 f'{address}',
                                 creationflags=subprocess.CREATE_NEW_CONSOLE)
            )
        else:
            all_servers.append(
                subprocess.Popen(f'x-terminal-emulator -e python3 '
                                 f'{work_dir}/server.py {port} {address}',
                                 shell=True, start_new_session=True)
            )

        # запуск клиента ------
        count_client = int(input('Укажите какое количество клиентов '
                                 'запустить (0-20)\n'))
        if count_client != 0:  # запускать клиенты, если их больше 0
            for i in range(count_client):
                # для linux .CREATE_NEW_CONSOLE не работает
                if sys.platform == 'Windows':
                    all_clients.append(
                        subprocess.Popen(
                            f'python {work_dir}\client.py {port} {address}',
                            creationflags=subprocess.CREATE_NEW_CONSOLE
                        )
                    )
                else:
                    all_clients.append(
                        subprocess.Popen(f'x-terminal-emulator -e python3 '
                                         f'{work_dir}/client.py {port} '
                                         f'{address}', shell=True,
                                         start_new_session=True
                                         )
                    )
        print('готово!')

    # "убить" все сервера
    if ask == 'w' or ask == 'k':
        count = len(all_servers)
        while all_servers:
            item = all_servers.pop()
            if sys.platform == 'Windows':
                item.kill()
            else:
                os.killpg(os.getpgid(item.pid), signal.SIGTERM)
        print(f'серверов \"убито\": {count}')

    # "убить" все клиенты
    if ask == 'e' or ask == 'k':
        count = len(all_clients)
        while all_clients:
            item = all_clients.pop()
            if sys.platform == 'Windows':
                item.kill()
            else:
                os.killpg(os.getpgid(item.pid), signal.SIGTERM)
        print(f'клиентов \"убито\": {count}')
