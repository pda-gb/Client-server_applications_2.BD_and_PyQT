"""Extend of errors"""

class EmptyOrFailDataRecv(Exception):
    """ Исключение: из сокета получено пустое или неправильное сообщение"""
    def __str__(self):
        return 'Из сокета получено пустое или неправильное сообщение'