from django.test import TestCase
# Create your tests here.
import re


class UserValidator:
    # 表示类方法
    @classmethod
    def valid_phone(cls, value):
        if not re.match(r'1[1-57-9]\d{9}', value):
            print('手机格式错误')
        return True


if __name__ == '__main__':
    value = '159'
    UserValidator.valid_phone(value)