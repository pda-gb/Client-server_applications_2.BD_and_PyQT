import json
import unittest

from common.utils import send_message, get_message
from common.variables import ENCODING, ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, RESPONSE, ERROR


class DummySocket:
    """тестовый сокет - заглушка"""

    def __init__(self, dict_message):
        self.dict_message = dict_message  # принимаемый словарь сокетом
        # сохраняем закодированное сообщение тестовым сокетом как эталон
        self.control_message_to_send = None
        # то что должно быть отправлено в сокет. Это сообщение сохранено от
        # тестируемой функции
        self.message_to_send_of_test_func = None

    def send(self, sending_msg):
        """
        Кодирует в байты и сохраняет то что должно быть отправлено сокетом.
        sending_msg - то что отправляет в сокет тестируемая функция отпрвки
        """
        _msg_as_json = json.dumps(self.dict_message)
        self.control_message_to_send = _msg_as_json.encode(ENCODING)
        self.message_to_send_of_test_func = sending_msg

    def recv(self, max_connections):
        """
        Принимает из сокета сообщения . Отдаёт в тестируемую функуцю приёма
        байты
        """
        _json_msg = json.dumps(self.dict_message)
        control_message_to_receive = _json_msg.encode(ENCODING)
        return control_message_to_receive


class TestControlFunction(unittest.TestCase):
    """Тестовый класс"""
    sample_message = {
        ACTION: PRESENCE,
        TIME: 1607158202.201626,
        USER: {
            ACCOUNT_NAME: 'John_Doe'
        }
    }
    standart_answer_ok = {RESPONSE: 200}
    standart_answer_error = {
        RESPONSE: 400,
        ERROR: 'Request is not compliance to protocol'
    }

    def test_send_message(self):
        """тест отправки"""
        # создадим тестовый сокет, на основе загушки и передадим туда станд.
        # сообщение, что бы тестовый сокет сымтировал отправление станд.
        # байтовое сообщение из сокета
        testing_socket = DummySocket(self.sample_message)
        # вызываем тестуруемую функцию
        send_message(testing_socket, self.sample_message)
        # сравниваем результат с эталоном
        self.assertEqual(testing_socket.message_to_send_of_test_func,
                         testing_socket.control_message_to_send)
        # проверка исключения, если отправляемое сообщение с помощью
        # тестируемой функции будет не словарь
        # with self.assertRaises(Exception):
        #     send_message(testing_socket, testing_socket)
        # правильно ли так?
        self.assertRaises(Exception, send_message)

    def test_get_message(self):
        """тест приёма"""
        # создадим тестовый сокет, с разными ответами
        testing_socket_with_ok = DummySocket(self.standart_answer_ok)
        testing_socket_with_error = DummySocket(self.standart_answer_error)
        # тестируем функцию на приём ответа
        self.assertEqual(get_message(testing_socket_with_ok),
                         self.standart_answer_ok)
        self.assertEqual(get_message(testing_socket_with_error),
                         self.standart_answer_error)


if __name__ == '__main__':
    unittest.main()
