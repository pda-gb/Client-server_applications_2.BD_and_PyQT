import inspect
import select
import socket
import sys
import traceback
from argparse import ArgumentParser
from logging import getLogger

# import log.configs.server_log_config - должна быть для
# инициализации логирования
import log.configs.server_log_config

from common.utils import get_message, send_message
from common.variables import DEFAULT_PORT, MAX_CONNECTIONS, ACTION, \
    PRESENCE, TIME, ACCOUNT_NAME, USER, ERROR, DEFAULT_IP_ADDRESS, \
    MESSAGE, MESSAGE_TEXT, SENDER, CODE_400, CODE_200, DESTINATION, EXIT

# Инициализация логирования сервера.
LOGGER = getLogger('server')


# декоратор на классе
class Log():
    """Декоратор - пример использования для дебаг-логирования функций"""

    def __call__(self, decorated_func):
        def log_wrap(*args, **kwargs):
            """Обертка"""
            result = decorated_func(*args, **kwargs)
            LOGGER.debug(f'\n+ + +\n__doc__: {decorated_func.__doc__}'
                         f'\n+ + +\n'
                         f'Функция {decorated_func.__name__} c параметрами '
                         f'{args}, {kwargs}. \n'
                         f'Вызов из модуля {decorated_func.__module__} из '
                         f'функции '
                         f'{traceback.format_stack()[0].strip().split()[-1]}\n'
                         f'Вызов из функции {inspect.stack()[1][3]}')

            # traceback, inspect - помогают через логирование узнать имя
            # функции, модуля откуда вызвана логируемая функция.
            return result

        return log_wrap


@Log()
def control_of_protocol_compliance(message_of_client, list_messages, _client,
                                   _clients, _names):
    """
    Обработка принятого сообщения.
    Проверка на соответствие протоколу  сообщения от клиента.
    Отпраляет клиенту, если это сообщение о присутствии. Если это сообщение
    клиента - только добавить в список сообщений.
    """
    # LOGGER.debug(f'Проверка на соответствие протоколу  сообщения '
    #              f'от клиента: {message_of_client}')

    # Проверка на сообщение о присутствии
    if ACTION in message_of_client and message_of_client[ACTION] == PRESENCE \
            and TIME in message_of_client and USER in message_of_client and \
            type(message_of_client[TIME]) is float:
        # если клиент ещё не зарегистрирован в общем списке имён клиентов
        if message_of_client[USER][ACCOUNT_NAME] not in _names.keys():
            # добавляем в список имён клиентов
            _names[message_of_client[USER][ACCOUNT_NAME]] = _client
            LOGGER.debug(f'Регистрация клиента '
                         f'{message_of_client[USER][ACCOUNT_NAME]} на сервере')
        else:
            # если клент с таким именем есть, то сообщаем и удаляем из списка
            # общей очереди, отключаем пользователя
            LOGGER.error(f'Ошибка. Данное имя - '
                         f'{message_of_client[USER][ACCOUNT_NAME]} уже '
                         f'занято.')
            bad_name = CODE_400
            bad_name[ERROR] = 'Ошибка. Данное имя уже занято.'
            send_message(_client, bad_name)
            _clients.remove(_client)
            _client.close()
        send_message(_client, CODE_200)  # Говорим клиенту ОК
    # Проверка на сообщение от клиента
    elif ACTION in message_of_client and message_of_client[ACTION] == MESSAGE \
            and MESSAGE_TEXT in message_of_client and TIME in \
            message_of_client and SENDER in message_of_client and DESTINATION \
            in message_of_client:
        # Добавялем в общий список сообщений.
        list_messages.append(message_of_client)
    # Пришло сообщение о выходе
    elif ACTION in message_of_client and message_of_client[ACTION] == EXIT \
            and ACCOUNT_NAME in message_of_client:
        _clients.remove(_names[message_of_client[ACCOUNT_NAME]])
        del _names[message_of_client[ACCOUNT_NAME]]
    # Сообщение не соответствует критериям. Вернуть ошибку
    else:
        send_message(_clients, CODE_400)


@Log()
def find_connections_parameters():
    """
    Функция парсер. Запуск сервера с заданными параметрами или по дефолту.
    пример: server.py -a XXX.XXX.XXX.XXX -p XXXX

    """

    find_parameters = ArgumentParser()
    # добавляем в класс аргументы-параметры по ключам
    find_parameters.add_argument('-a', '--address', default=DEFAULT_IP_ADDRESS,
                                 nargs='?', dest='a')
    find_parameters.add_argument('-p', '--port', default=DEFAULT_PORT,
                                 type=int, nargs='?', dest='p')
    # парсим начиная после первого элемента(server.py)
    parameters = find_parameters.parse_args(sys.argv[1:])
    ip_for_client_connect = parameters.a
    port_for_client_connect = parameters.p
    if 1024 > port_for_client_connect or port_for_client_connect > 65535:
        print('Порт д.б. в диапазоне 1024-65535')
        LOGGER.critical(f'Запуск сервера с портом {port_for_client_connect} '
                        f'недопустимо. Порт д.б. в диапазоне 1024-65535.')
        sys.exit(1)
    return ip_for_client_connect, port_for_client_connect


# @Log()
# def send_responses(message, list_clients_to_send, list_clients):
#     """
#     Отправка сообщения списку клиентов ожидающих получения сообщения и
#     удаления из списка клиентов
#     """
#     for client in list_clients_to_send:
#         try:
#             send_message(client, message)
#         except OSError:
#             LOGGER.info(f'Неудалось прочитать сообщение, клиент '
#                         f'{client.getpeername()} не в сети')
#         client.close()
#         # удаляем из общего списка, т.к. клиент получил ответ или не в сети
#         list_clients.remove(client)


def send_msg_to_destinations(_msg, _all_user_names, _clients_to_send):
    """
    Функция из списка принятых сообщений рассылает ожидающим адресатам.
    :param _msg:
    :param _all_user_names:
    :param _clients_to_send:
    :return:
    """
    # если имя получателя в списке и его сокет в списке ожидания
    if _msg[DESTINATION] in _all_user_names and \
            _all_user_names[_msg[DESTINATION]] in _clients_to_send:
        # отправляем получателю
        send_message(_all_user_names[_msg[DESTINATION]], _msg)
        LOGGER.info(f'От:{_msg[SENDER]} \n'
                    f'сообщение:{_msg[MESSAGE_TEXT]}\n'
                    f'отправлено в {_msg[TIME]}')
    # если зарег. пользользователь не в сети
    elif _msg[DESTINATION] in _all_user_names and \
            _all_user_names[_msg[DESTINATION]] not in _clients_to_send:
        # выдать ошибку соединения
        raise ConnectionError
    # если нет такого получателя
    else:
        LOGGER.error(f'Пользователь{_msg[DESTINATION]} не зарегистрирован  '
                     f'на сервере')
        try:
            # сообщим отправителю
            fail_send = CODE_400
            fail_send[ERROR] = f'Пользователь{_msg[DESTINATION]} не ' \
                               f'зарегистрирован на сервере, сообщение не ' \
                               f'доставлено.'
            send_message(_all_user_names[_msg[SENDER]])
        except (ConnectionError, ConnectionResetError,
                ConnectionRefusedError, ConnectionAbortedError):
            LOGGER.error(f'Потеря связи! c отправителем {_msg[SENDER]} ')


def main():
    # запуск сервера с заданными параметрами или по дефолту.
    ip_for_client_connect, port_for_client_connect = \
        find_connections_parameters()
    LOGGER.info(f'Запущен сервер с параметрами: {ip_for_client_connect} '
                f'{port_for_client_connect}.')
    print(f'Сервер запущен! ({ip_for_client_connect}:'
          f'{port_for_client_connect})')
    # создаём сокет, соединяемся, слушаем
    client_connect = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_connect.bind((ip_for_client_connect, port_for_client_connect))
    client_connect.listen(MAX_CONNECTIONS)
    # прерываемся, что бы проверить новые подключения или получение данных
    client_connect.settimeout(1)

    all_clients = []  # общ список клиентов
    all_user_names = {}  # общ список имён клиентов: {имя: клиент}
    messages_of_clients = []  # общ список сообщений: [{клиент: сообщение},]

    while True:
        try:
            # подключение клиента
            client, address_of_client = client_connect.accept()
        except OSError:
            # settimeout время вышло
            pass
        else:
            # Успешное подключение
            print(f'Подключен клиент с параметрами: {address_of_client}')
            LOGGER.info(f'Подключен клиент {address_of_client}')
            all_clients.append(client)  # добавляем в общий список

        # список клиентов, для получения от них сообщения
        clients_to_recv = []
        # список клиентов, для отправки им сообщения
        clients_to_send = []
        # список ошибок
        errors = []

        try:
            # сортируем клиентов на принимающих и отправляющих
            clients_to_recv, clients_to_send, errors = \
                select.select(all_clients, all_clients, [], 0)
        except OSError:
            # Клиент отключился
            print('Клиент отключился')

        #
        # Приём сообщения, создаем словарь: {клиент: сообщение}
        if clients_to_recv:  # клиенты отправившие сообщения и в очереди ожид.
            for waiting_client in clients_to_recv:
                try:
                    # проверим на соотв протоколу, добавим сообщ-е в общ список
                    control_of_protocol_compliance(get_message(waiting_client),
                                                   messages_of_clients,
                                                   waiting_client, all_clients,
                                                   all_user_names
                                                   )
                except(ConnectionError, ConnectionResetError,
                       ConnectionRefusedError, ConnectionAbortedError):
                    # удалить отключенных из общего списка
                    LOGGER.info(f'Клиент {waiting_client.getpeername()} не в '
                                f'сети')
                    print('Нет связи с клиентом')
                    waiting_client.close()
                    all_clients.remove(waiting_client)

        # Если есть сообщение и клиенты ожидающие приём сообщения
        if messages_of_clients and clients_to_send:
            # из каждого сообщение из списка
            for msg in messages_of_clients:
                send_msg_to_destinations(msg, all_user_names, clients_to_send)

            # после отправки всех сообщений очищаем список сообщений
            messages_of_clients = []


if __name__ == '__main__':
    main()
