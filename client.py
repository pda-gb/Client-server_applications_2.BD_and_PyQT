import inspect
import json
import socket
import sys
import threading
import time
import traceback
from argparse import ArgumentParser
from logging import getLogger

# import log.configs.client_log_config - должна быть для
# инициализации логирования
import log.configs.client_log_config

from common.utils import send_message, get_message
from common.variables import DEFAULT_IP_ADDRESS, DEFAULT_PORT, ACTION, \
    PRESENCE, TIME, USER, ACCOUNT_NAME, RESPONSE, ERROR, MESSAGE, SENDER, \
    MESSAGE_TEXT, DESTINATION, EXIT
from errors import EmptyOrFailDataRecv

# Инициализация логирования клиента.
LOGGER = getLogger('client')


# декоратор на функции
def log(decorated_func):
    """Декоратор - пример использования для дебаг-логирования функций"""

    def log_wrap(*args, **kwargs):
        """Обертка"""
        result = decorated_func(*args, **kwargs)
        LOGGER.debug(f'\n+ + +\n__doc__: {decorated_func.__doc__}\n+ + +\n'
                     f'Функция {decorated_func.__name__} c параметрами '
                     f'{args}, {kwargs}. \n'
                     f'Вызов из модуля {decorated_func.__module__} из '
                     f'функции '
                     f'{traceback.format_stack()[0].strip().split()[-1]}\n'
                     f'Вызов из функции {inspect.stack()[1][3]}')

        # traceback, inspect - помогают через логирование узнать имя
        # функции, модуля откуда вызвана логируемая функция.
        return result

    # для сообщения от конкретной точки для лога сначала получим описание
    # логируемой функции и передадим в качестве доп. сообщения
    log_wrap.__doc__ = decorated_func.__doc__
    return log_wrap


@log
def create_massage_a_presence(_account='Guest'):
    """
    Создаёт сообщение о присутствии клиента в сети, по умолчанию c аккантом -
    Гость.
    """
    _message = {
        ACTION: PRESENCE,
        TIME: time.time(),
        USER: {
            ACCOUNT_NAME: _account
        }
    }
    # LOGGER.debug(f'Создание сообщения о присутствии от клиента: '
    #             f'{_message}')
    return _message


@log
def create_message_disconnect(_account):
    """
    Создаёт сообщение об отключении клиента от сети.
    """
    return {
        ACTION: EXIT,
        TIME: time.time(),
        ACCOUNT_NAME: _account
    }


@log
def parsing_response_of_presence(_server_response):
    """Разбор ответа сервера на сообщение о присутствии клиента в сети"""

    # LOGGER.debug(f'разбор ответа сервера: {_server_response}')
    # Проверка на сообщение о присутствии
    if RESPONSE in _server_response:
        if _server_response[RESPONSE] == 200:
            return 'code : 200. OK, you are connected.'
        return f'code :{_server_response[RESPONSE]}. Error: ' \
               f'{_server_response[ERROR]}'
    raise ValueError


@log
def parsing_response_of_users_message(_server_response, _user_name):
    """Разбор ответа сервера на сообщение от пользователя"""
    # Проверка на сообщение от клиента
    if ACTION in _server_response and _server_response[ACTION] == MESSAGE \
            and MESSAGE_TEXT in _server_response and TIME in _server_response\
            and _server_response[DESTINATION] == _user_name:
        # отдаём текс сообщения
        # return _server_response[MESSAGE_TEXT]
        return True

    raise ValueError


@log
def find_connections_parameters():
    """
    Функция парсер. Запуск клиента с заданными параметрами или по дефолту.
    пример: client.py -a XXX.XXX.XXX.XXX -p XXXX -m listen/sender

    """

    find_parameters = ArgumentParser()
    # добавляем в класс аргументы-параметры по ключам
    find_parameters.add_argument('-a', '--address', default=DEFAULT_IP_ADDRESS,
                                 nargs='?', dest='a')
    find_parameters.add_argument('-p', '--port', default=DEFAULT_PORT,
                                 type=int, nargs='?', dest='p')
    # парсим начиная после первого элемента(client.py)
    parameters = find_parameters.parse_args(sys.argv[1:])
    ip_for_server_connect = parameters.a
    port_for_server_connect = parameters.p
    if 1024 > port_for_server_connect or port_for_server_connect > 65535:
        print('Порт д.б. в диапазоне 1024-65535')
        LOGGER.critical(f'Запуск клиента с портом {port_for_server_connect} '
                        f'недопустимо. Порт д.б. в диапазоне 1024-65535.')
        sys.exit(1)
    return ip_for_server_connect, port_for_server_connect


@log
def get_users_message(user_socket, _user_name):
    """
    Постоянное получение сообщений, так как для этого запускается в отдельном
    потоке.
    Проверка сообщений от пользователей, приходящих с сервера, на
    соответствие протоколу JIM.
    """
    while True:
        try:
            # получение сообщения из сокета
            user_msg_from_server = get_message(user_socket)
            # валидация
            if parsing_response_of_users_message(user_msg_from_server,
                                                 _user_name):
                LOGGER.debug(f'\nПолучено сообщение:'
                             f'{user_msg_from_server[MESSAGE_TEXT]}\n'
                             f' от пользователя:'
                             f'{user_msg_from_server[SENDER]}\n'
                             f'отправлено в {user_msg_from_server[TIME]}\n'
                             f'получено через '
                             f'{time.time() - user_msg_from_server[TIME]} '
                             f'сек.')
                print(f'От:{user_msg_from_server[SENDER]} \n'
                      f'сообщение:{user_msg_from_server[MESSAGE_TEXT]}\n'
                      f'отправлено в {time.ctime(user_msg_from_server[TIME])}')

        except (ConnectionError, ConnectionResetError, ConnectionRefusedError,
                ConnectionAbortedError):
            LOGGER.error(f'Потеря связи! Сервер '
                         f'{user_socket.getpeername()} '
                         f'не доступен.')
            sys.exit(1)


@log
def create_users_message(account='Guest'):
    """
    Функция заправшивает текст сообщения пользователя для отправки, запрашивает
    получателя формирует словарь для отправки на сервер.

    """
    user_to_recv = input('Имя получателя:\n')
    text_msg = input('Напишите своё сообщение:\n')

    message_to_server = {
        ACTION: MESSAGE,
        SENDER: account,
        DESTINATION: user_to_recv,
        TIME: time.time(),
        # ACCOUNT_NAME: account,
        MESSAGE_TEXT: text_msg
    }
    LOGGER.debug(f'Сформирован слоаврь для отправки:{message_to_server}')
    return message_to_server


@log
def console_interface(sock_of_conn, account='Guest'):
    """
    Функция - интерфейс меню, создания и отправки сообщения
    """
    while True:
        cmd = input('Команды: m - написать сообщение, e - выход.\n Введите '
                    'команду')
        if cmd == 'm':
            try:
                send_message(sock_of_conn, create_users_message(account))
                LOGGER.debug('Собщение отправлено')
            except (ConnectionError, ConnectionResetError,
                    ConnectionRefusedError, ConnectionAbortedError):
                LOGGER.error(f'Потеря связи! Сервер '
                             f'{sock_of_conn.getpeername()} '
                             f'не доступен.')
                sys.exit(1)
        elif cmd == 'e':
            send_message(sock_of_conn, create_message_disconnect(account))
            print('Завершение соединения.')
            LOGGER.info('Пользователь завершил работу приложения по команде '
                        'exit.')
            # Пауза для того, чтобы сообщение о выходе успело придти на сервер
            time.sleep(0.5)
            sock_of_conn.close()
            sys.exit(0)
            # break
        else:
            print('Неправильная команда ! ! !.')
            LOGGER.debug(f'Неправильная команда:{cmd}')


def main():
    print('+++ Launched the client module of the messenger. +++')

    # запуск клиента с заданными параметрами или по дефолту.
    ip_for_server_connect, port_for_server_connect = \
        find_connections_parameters()
    LOGGER.info(f'Запущен клиент с параметрами: {ip_for_server_connect} '
                f'{port_for_server_connect}.')
    print(f'Запущен клиент с параметрами: {ip_for_server_connect} '
          f'{port_for_server_connect}.')

    # Задаём имя пользователю
    user_name = None
    while not user_name:
        user_name = input('Введите обязательное имя пользователя или команду '
                          '\"exit\" - для выхода:')
        if user_name == 'exit':
            print('Закрытие программы.')
            LOGGER.info('Пользователь завершил работу приложения по команде '
                        'exit.')
            sys.exit(0)
            # break

    try:
        # создаём сокет, соединяемся
        server_connect = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_connect.connect((ip_for_server_connect,
                                port_for_server_connect))
        LOGGER.debug(f'создаём сокет, соединяемся c сервером: '
                     f'{(ip_for_server_connect, port_for_server_connect)}')
        print(f'Соединение c сервером: '
              f'{(ip_for_server_connect, port_for_server_connect)} '
              f'установлено.')

        # создаём и отправляем сообщение о присутствии серверу
        message_to_server = create_massage_a_presence(user_name)
        send_message(server_connect, message_to_server)
        LOGGER.debug(f'создаём и отправляем сообщение о присутствии серверу: '
                     f'{message_to_server}')
        # Получаем сообщения от сервера
        response_of_server = parsing_response_of_presence(get_message(
            server_connect))
        LOGGER.debug(f'Ответ сервера на отправку сообщения о присутствии:'
                     f'{response_of_server}')
        print(f'Ответ сервера: {response_of_server}')
    except (ConnectionError, ConnectionResetError, ConnectionRefusedError,
            ConnectionAbortedError):
        LOGGER.error(f'Потеря связи! Сервер '
                     f'{(ip_for_server_connect, port_for_server_connect)} '
                     f'не доступен.')
        sys.exit(1)
    except json.JSONDecodeError:
        print('Не удалось декодировать данные.')
        LOGGER.critical('Не удалось декодировать данные.')
    except EmptyOrFailDataRecv:
        LOGGER.error('Из сокета получено пустое или неправильное сообщение')
    else:
        # Если есть связь с сервером и удался обмен данными о присутствии,
        # то можем начать обмениваться сообщениями (основной цикл работы).

        # Приём. Создаём отдельный поток
        thread_recv = threading.Thread(target=get_users_message,
                                       args=(server_connect, user_name)
                                       )
        thread_recv.daemon = True
        thread_recv.start()

        # Передача. Создаём отдельный поток
        thread_send = threading.Thread(target=console_interface,
                                       args=(server_connect, user_name)
                                       )
        thread_send.daemon = True
        thread_send.start()

        LOGGER.debug('Запущены процессы приёма и передачи клиента.')

        # Отслеживать каждую секунду что все потоки работают. Если кто то по
        # какой то причине отваливается. Выйти из цикла(завершить прокрамму
        # клиент)
        while True:
            time.sleep(1)
            if thread_send.is_alive() and thread_recv.is_alive():
                continue
            break


if __name__ == '__main__':
    main()
