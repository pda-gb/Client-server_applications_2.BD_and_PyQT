import unittest

from client import create_massage_a_presence, parsing_response
from common.variables import RESPONSE, ERROR, TIME, ACTION, PRESENCE, \
    ACCOUNT_NAME, USER


class TestParsingResponse(unittest.TestCase):
    """Тест функции parsing_response клента"""

    test_dict = {
        'answer_ok': 'code : 200. OK, you are connected.',
        'answer_bad': 'code :400. Error: Request is not compliance to '
                      'protocol',
        'true_request': {
            ACTION: PRESENCE,
            TIME: 1607158202.201626,
            USER: {ACCOUNT_NAME: 'Guest'}
        },
        'server_response_ok': {RESPONSE: 200},
        'server_response_bad': {
            RESPONSE: 400,
            ERROR: 'Request is not compliance to protocol'
        }
    }

    def test_massage_a_presence(self):
        """
        Тест правильного создания запроса серверу. Принудительно выставляем
        значение времени, т.к. в ф. create_massage_a_presence, время
        вычисляется текущее время в момент проверки
        """
        test_msg = create_massage_a_presence()
        test_msg[TIME] = 1607158202.201626
        self.assertEqual(test_msg, self.test_dict['true_request'])

    def test_answer_ok(self):
        """Проверка получения положительного ответа"""
        self.assertEqual(
            parsing_response(self.test_dict['server_response_ok']),
            self.test_dict['answer_ok']
        )

    def test_answer_bad(self):
        """Проверка получения отрицательного ответа"""
        self.assertEqual(
            parsing_response(self.test_dict['server_response_bad']),
            self.test_dict['answer_bad']
        )

    def test_server_response_empty(self):
        """Тест на отсутствие RESPONSE"""
        self.assertRaises(ValueError, parsing_response,
                          self.test_dict['answer_bad'])

    # def test_(self):
    #     """"""
    #     self.assertEqual(
    #         parsing_response(self.test_dict['']),
    #         self.test_dict[''])


if __name__ == '__main__':
    unittest.main()
