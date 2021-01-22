from logging import DEBUG as LOGGING_LEVEL_DEBUG
# from logging import INFO as LOGGING_LEVEL_INFO
# from logging import WARNING as LOGGING_LEVEL_WARNING
# from logging import ERROR as LOGGING_LEVEL_ERROR
# from logging import CRITICAL as LOGGING_LEVEL_CRITICAL

"""Константы"""

# Порт по умолчанию для сетевого ваимодействия
DEFAULT_PORT = 7847
# IP адрес по умолчанию для подключения клиента
DEFAULT_IP_ADDRESS = '127.0.0.1'
# IP адрес по умолчанию для прослушивания сервером
DEFAULT_IP_ADDRESS_FOR_LISTEN = ''
# Максимальная очередь подключений
MAX_CONNECTIONS = 10
# Максимальная длинна сообщения в байтах
MAX_PACKAGE_LENGTH = 2048
# Кодировка проекта
ENCODING = 'utf-8'
# Задание уровна логирования
LOGGER_LEVEL = LOGGING_LEVEL_DEBUG


# =====================================

# Прококол JIM основные ключи:
ACTION = 'action'
TIME = 'time'
USER = 'user'
ACCOUNT_NAME = 'account_name'
SENDER = 'from'
DESTINATION = 'to'

# =====================================

# Прочие ключи
PRESENCE = 'presence'
RESPONSE = 'response'
ERROR = 'error'
MESSAGE = 'message'
MESSAGE_TEXT = 'message_text'
EXIT = 'exit'

# =====================================

# Сдлвари - заготовки для ответов
CODE_400 = {
            RESPONSE: 400,
            ERROR: 'Request is not compliance to protocol'
        }
CODE_200 = {RESPONSE: 200}
