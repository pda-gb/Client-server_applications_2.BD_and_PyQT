import logging.handlers
from logging import Formatter, getLogger
from os import chdir, getcwd, path, pardir
from sys import stderr

from common.variables import LOGGER_LEVEL

# +++ определяем путь файла для логирования +++
# если запускаем конфинг напрямую, то сменяем папку на 1 шаг выше
if __name__ == '__main__':
    chdir(pardir)
# получаем путь
path_to_app = getcwd()
if __name__ == '__main__':  # если запускаем конфинг напрямую
    path_to_app = path.join(path_to_app, 'logs', 'client.log')
else:
    path_to_app = path.join(path_to_app, 'log', 'logs', 'client.log')

# +++ задаём формат логов +++
format_msg = Formatter('%(asctime)s %(levelname)s %(filename)s '
                       '%(message)s \n module: %(module)s function: '
                       '%(funcName)s str_line: %(lineno)d ')

# +++ обработчик потока логов +++
handler_log_file = logging.handlers.TimedRotatingFileHandler(path_to_app,
                                                             encoding='utf-8',
                                                             backupCount=10,
                                                             interval=1,
                                                             when='D')
handler_log_file.setFormatter(format_msg)
handler_log_file.setLevel(LOGGER_LEVEL)
# вывод в поток ошибок (для теста)
handler_log_stream = logging.StreamHandler(stderr)

# +++ регистратор лога +++
# создаём регистратор
logger = getLogger('client')
# добавляем к нему обработчики
logger.addHandler(handler_log_file)
logger.addHandler(handler_log_stream)
# устанавливаем уровень логов
logger.setLevel(LOGGER_LEVEL)

# +++ тест лога +++
if __name__ == '__main__':
    logger.debug('Отладочная информация')
    logger.info('Информационное сообщение')
    logger.warning('Предупреждения')
    logger.error('Ошибка')
    logger.critical('Критическая ошибка')
