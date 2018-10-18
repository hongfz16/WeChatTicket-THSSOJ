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
#        response = c.get('/api/u/user/bind', {'openid': 'xyz'})
#        self.assertEqual(response.status_code, 200)
#        self.assertEqual(response.json()['data'], '')
        response = c.post('/api/u/user/bind',
               {
                    'openid': 'ycdfwzy',
                    'student_id': '1234567890',
                    'password': 'zstql'
                })
        self.assertEqual(response.json()['code'], 0)
        response = c.get('/api/u/user/bind',
                         {
                             'openid': 'ycdfwzy'
                         })
        self.assertEqual(response.json()['code'], 0)
        self.assertEqual(response.json()['data'], '1234567890')