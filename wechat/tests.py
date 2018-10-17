# # Create your tests here.
#
from django.test import TestCase
from django.test import Client
from wechat.models import User


class TryTest(TestCase):
    def setUp(self):
        User.objects.create(open_id = 'ycdfwzy', student_id = '1234567890')

    def testBind(self):
        c = Client()
        response = c.post('POST /wechat?signature=7663baee57ea9c91c8b5056f20afd1cef722b961&timestamp=1539789722&nonce=422928425&openid=ojM6q1V-l8RyGrzjrirdOdkcwmKQ',
                          b'<xml><ToUserName><![CDATA[gh_5e0443904265]]></ToUserName>\n<FromUserName><![CDATA[ojM6q1V-l8RyGrzjrirdOdkcwmKQ]]></FromUserName>\n<CreateTime>1539789722</CreateTime>\n<MsgType><![CDATA[text]]></MsgType>\n<Content><![CDATA[\xe6\x8a\xa2\xe7\xa5\xa8 \xe6\xa8\xa1\xe6\x8b\x9f\xe8\xb5\x9b]]></Content>\n<MsgId>6613346499576056535</MsgId>\n</xml>')
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