import unittest

from common.variables import RESPONSE, ERROR, ACTION, PRESENCE, TIME, \
    USER, ACCOUNT_NAME
from server import control_of_protocol_compliance


class TestControlFunction(unittest.TestCase):
    """Тест функции control_of_protocol_compliance сервера"""
    ANY_FAIL = 'qwerty_йцукен'
    dicts = {
        'answer_bad': {
            RESPONSE: 400,
            ERROR: 'Request is not compliance to protocol'
        },
        'answer_ok': {RESPONSE: 200},
        'correct_msg': {
            ACTION: PRESENCE,
            TIME: 1607158202.201626,
            USER: {ACCOUNT_NAME: 'Guest'}
        },
        'no_action_msg': {
            TIME: 1607158202.201626,
            USER: {ACCOUNT_NAME: 'Guest'}
        },
        'fail_action_msg': {
            ACTION: ANY_FAIL,
            TIME: 1607158202.201626,
            USER: {ACCOUNT_NAME: 'Guest'}
        },
        'no_time_msg': {
            ACTION: PRESENCE,
            USER: {ACCOUNT_NAME: 'Guest'}
        },
        'fail_time_msg': {
            ACTION: PRESENCE,
            TIME: ANY_FAIL,
            USER: {ACCOUNT_NAME: 'Guest'}
        },
        'no_user_msg': {
            ACTION: PRESENCE,
            TIME: 1607158202.201626,
        },
        # 'fail_user_msg': {
        #     ACTION: PRESENCE,
        #     TIME: 1607158202.201626,
        #     USER: {True: ANY_FAIL}
        # },
        'no_guest_user_msg': {
            ACTION: PRESENCE,
            TIME: 1607158202.201626,
            USER: {ACCOUNT_NAME: ANY_FAIL}
        }
    }

    def test_correct_msg(self):
        """Получение правильного сообщения"""
        self.assertEqual(control_of_protocol_compliance(
            self.dicts['correct_msg']), self.dicts['answer_ok']
        )

    def test_no_action_msg(self):
        """отсутствие действия"""
        self.assertEqual(control_of_protocol_compliance(
            self.dicts['no_action_msg']), self.dicts['answer_bad']
        )

    def test_fail_action_msg(self):
        """Неправильная запись действия"""
        self.assertEqual(control_of_protocol_compliance(
            self.dicts['fail_action_msg']), self.dicts['answer_bad']
        )

    def test_no_time_msg(self):
        """отсутствие времени"""
        self.assertEqual(control_of_protocol_compliance(
            self.dicts['no_time_msg']), self.dicts['answer_bad']
        )

    def test_fail_time_msg(self):
        """Неправильная запись времени"""
        self.assertEqual(control_of_protocol_compliance(
            self.dicts['fail_time_msg']), self.dicts['answer_bad']
        )

    def test_no_user_msg(self):
        """отсутствие пользователя"""
        self.assertEqual(control_of_protocol_compliance(
            self.dicts['no_user_msg']), self.dicts['answer_bad'])

    # def test_fail_user_msg(self):
    #     """Неправильная запись пользователя"""
    #     self.assertEqual(control_of_protocol_compliance(
    #         self.dicts['fail_user_msg']), self.dicts['answer_bad']
    #     )

    def test_no_guest_user_msg(self):
        """Пользователь не является - 'Гость' """
        self.assertEqual(control_of_protocol_compliance(
            self.dicts['no_guest_user_msg']), self.dicts['answer_bad']
        )

    # def test_(self):
    #     """"""
    #     self.assertEqual(control_of_protocol_compliance(
    #         self.dicts['']), self.dicts['answer_bad']
    #         )


if __name__ == '__main__':
    unittest.main()
