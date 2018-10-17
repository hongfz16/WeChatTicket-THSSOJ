# # Create your tests here.
#
from datetime import datetime
from django.test import TestCase
from django.test import Client
from wechat.models import *


class TryTest(TestCase):
    def setUp(self):
        User.objects.create(open_id = 'ojM6q1V-l8RyGrzjrirdOdkcwmKQ', student_id = '1234567890')
        Activity.objects.create(
            name='ycdfwzy',
            key='wzy',
            description='zyw',
            start_time=datetime(2018, 10, 20, 2, 31, 0),
            end_time=datetime(2018, 11, 8, 23, 59, 59),
            place='zsdechuangshang',
            book_start=datetime(2018, 10, 10, 8, 8, 8),
            book_end=datetime(2018, 10, 19, 0, 0, 0),
            total_tickets=100,
            status=Activity.STATUS_PUBLISHED,
            pic_url='https://www.pornhub.com/ycdfwzy.png',
            remain_tickets=50
        )

    def testBind(self):
        c = Client()
        # b'<xml><ToUserName><![CDATA[gh_5e0443904265]]></ToUserName>\n<FromUserName><![CDATA[ojM6q1V-l8RyGrzjrirdOdkcwmKQ]]></FromUserName>\n<CreateTime>1539793148</CreateTime>\n<MsgType><![CDATA[text]]></MsgType>\n<Content><![CDATA[\xe6\x8a\xa2\xe7\xa5\xa8 \xe6\xa8\xa1\xe6\x8b\x9f\xe8\xb5\x9b]]></Content>\n<MsgId>6613361214134013343</MsgId>\n</xml>'

        response = c.post('wechat/??signature=b632388bc042d3d0dc6e490ef43e053d4dd5db95&timestamp=1539793148&nonce=1217778196&openid=ojM6q1V-l8RyGrzjrirdOdkcwmKQ',
                          b'<xml><ToUserName><![CDATA[gh_5e0443904265]]></ToUserName>\n<FromUserName><![CDATA[ojM6q1V-l8RyGrzjrirdOdkcwmKQ]]></FromUserName>\n<CreateTime>1539793148</CreateTime>\n<MsgType><![CDATA[text]]></MsgType>\n<Content><![CDATA[\xe6\x8a\xa2\xe7\xa5\xa8 wzy]]></Content>\n<MsgId>6613361214134013343</MsgId>\n</xml>',
                          content_type='text/xml')
        self.assertEqual(Activity.objects.get(name = 'ycdfwzy').remain_tickets, 49)
#        response = c.get('/api/u/user/bind', {'openid': 'xyz'})
#        self.assertEqual(response.status_code, 200)
#        self.assertEqual(response.json()['data'], '')
#         response = c.post('/api/u/user/bind',
#                {
#                     'openid': 'ycdfwzy',
#                     'student_id': '1234567890',
#                     'password': 'zstql'
#                 })
#         self.assertEqual(response.json()['code'], 0)
#         response = c.get('/api/u/user/bind',
#                          {
#                              'openid': 'ycdfwzy'
#                          })
#         self.assertEqual(response.json()['code'], 0)
#         self.assertEqual(response.json()['data'], '1234567890')
