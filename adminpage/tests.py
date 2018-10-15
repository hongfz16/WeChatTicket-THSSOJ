from django.test import TestCase
from django.test import Client
from django.contrib.auth import get_user_model
from wechat.models import Activity
from wechat.models import User as wechatuser
from datetime import datetime
import base64

class LoginTest(TestCase):
    def setUp(self):
        User = get_user_model()
        User.objects.create_superuser('admin', 'admin@myproject.com', 'thisispassword')

    def testPost(self):
        c = Client()
        trueresponse = c.post('/api/a/login',
                          {
                              'username': 'admin',
                              'password': 'thisispassword'
                          })
        c.post('/api/a/logout',{})
        self.assertEqual(trueresponse.json()['code'], 0)
        falsepwdresponse = c.post('/api/a/login',
                               {
                                   'username': 'admin',
                                   'password': 'thisisnotpassword'
                               })
        c.post('/api/a/logout',{})
        self.assertNotEqual(falsepwdresponse.json()['code'], 0)
        falseunresponse = c.post('/api/a/login',
                                 {
                                     'username': 'notadmin',
                                     'password': 'thisispassword'
                                 })
        c.post('/api/a/logout',{})
        self.assertNotEqual(falseunresponse.json()['code'], 0)

    def testGet(self):
        c = Client()
        c.post('/api/a/login',
               {
                   'username': 'admin',
                   'password': 'thisispassword'
               })
        loginresponse = c.get('/api/a/login',{})
        self.assertEqual(loginresponse.json()['code'], 0)
        c.post('/api/a/logout',{})
        logoutresponse = c.get('api/a/login',{})
        self.assertNotEqual(logoutresponse.json()['code'], 0)

class LogoutTest(TestCase):
    def setUp(self):
        User = get_user_model()
        User.objects.create_superuser('admin', 'admin@myproject.com', 'thisispassword')

    def testPost(self):
        c = Client()
        c.post('/api/a/login',
               {
                   'username': 'admin',
                   'password': 'thisispassword'
               })
        succresponse = c.post('/api/a/logout',{})
        self.assertEqual(succresponse.json()['code'], 0)
        failresponse = c.post('api/a/logout',{})
        self.assertNotEqual(failresponse.json()['code'], 0)

class ActivityListTest(TestCase):
    def setUp(self):
        self.starttime = datetime.now()
        self.endtime = datetime.now()
        self.bookstart = datetime.now()
        self.bookend = datetime.now()
        User = get_user_model()
        User.objects.create_superuser('admin', 'admin@myproject.com', 'thisispassword')
        Activity.objects.create(name = 'testac1',
                                key = 'thisisamaxlengthof64key',
                                description = 'testdesc1',
                                start_time = self.starttime,
                                end_time = self.endtime,
                                place = 'testplace1',
                                book_start = self.bookstart,
                                book_end = self.bookend,
                                total_tickets = 100,
                                status = 0,
                                pic_url = 'http://thisisaurl.com',
                                remain_tickets = 99
                                )
        Activity.objects.create(name='testac2',
                                key='thisisamaxlengthof64key',
                                description='testdesc2',
                                start_time=self.starttime,
                                end_time=self.endtime,
                                place='testplace2',
                                book_start=self.bookstart,
                                book_end=self.bookend,
                                total_tickets=200,
                                status=1,
                                pic_url='http://thisisaurl.com',
                                remain_tickets=199
                                )
    def testGet(self):
        c = Client()
        response = c.get('/api/a/activity/list', {})
        self.assertNotEqual(response.json()['code'], 0)
        c.post('/api/a/login',
               {
                   'username': 'admin',
                   'password': 'thisispassword'
               })
        response = c.get('/api/a/activity/list', {})
        self.assertEqual(response.json()['code'], 0)
        for i in range(2):
            activity = response.json()['data'][i]
            self.assertEqual(activity['id'], i+1)
            self.assertEqual(activity['name'], 'testac'+str(i+1))
            self.assertEqual(activity['description'], 'testdesc'+str(i+1))
            self.assertEqual(activity['startTime'], self.starttime.timestamp())
            self.assertEqual(activity['endTime'], self.endtime.timestamp())
            self.assertEqual(activity['place'], 'testplace'+str(i+1))
            self.assertEqual(activity['bookStart'], self.bookstart.timestamp())
            self.assertEqual(activity['bookEnd'], self.bookend.timestamp())
            self.assertAlmostEqual(activity['currentTime'], datetime.now().timestamp(), delta = 5)
            self.assertEqual(activity['status'], i)

class ActivityDeleteTest(TestCase):
    def setUp(self):
        self.starttime = datetime.now()
        self.endtime = datetime.now()
        self.bookstart = datetime.now()
        self.bookend = datetime.now()
        User = get_user_model()
        User.objects.create_superuser('admin', 'admin@myproject.com', 'thisispassword')
        Activity.objects.create(name = 'testac1',
                                key = 'thisisamaxlengthof64key',
                                description = 'testdesc1',
                                start_time = self.starttime,
                                end_time = self.endtime,
                                place = 'testplace1',
                                book_start = self.bookstart,
                                book_end = self.bookend,
                                total_tickets = 100,
                                status = 0,
                                pic_url = 'http://thisisaurl.com',
                                remain_tickets = 99
                                )
        Activity.objects.create(name='testac2',
                                key='thisisamaxlengthof64key',
                                description='testdesc2',
                                start_time=self.starttime,
                                end_time=self.endtime,
                                place='testplace2',
                                book_start=self.bookstart,
                                book_end=self.bookend,
                                total_tickets=200,
                                status=1,
                                pic_url='http://thisisaurl.com',
                                remain_tickets=199
                                )

    def testPost(self):
        c = Client()
        logoutresponse = c.post('/api/a/activity/delete',
                              {
                                  'id': 0
                              })
        self.assertNotEqual(logoutresponse.json()['code'], 0)
        c.post('/api/a/login',
               {
                   'username': 'admin',
                   'password': 'thisispassword'
               })
        succresponse = c.post('/api/a/activity/delete',
                              {
                                  'id': 0
                              })
        self.assertEqual(succresponse.json()['code'], 0)
        failresponse = c.post('/api/a/activity/delete',
                              {
                                  'id': 100
                              })
        self.assertNotEqual(failresponse.json()['code'], 0)
        succ2response = c.post('/api/a/activity/delete',
                              {
                                  'id': 1
                              })
        self.assertEqual(succ2response.json()['code'], 0)

class ActivityCreateTest(TestCase):
    def setUp(self):
        self.url = '/api/a/activity/create'
        User = get_user_model()
        User.objects.create_superuser('admin', 'admin@myproject.com', 'thisispassword')
        self.starttime = datetime.now().timestamp()
        self.endtime = datetime.now().timestamp()
        self.bookstart = datetime.now().timestamp()
        self.bookend = datetime.now().timestamp()

    def testPost(self):
        c = Client()
        postjson = {
            'name': 'testac1',
            'key': 'thisisaxiajibabiandekey',
            'place': 'testplace1',
            'description': 'testdesc1',
            'picUrl': 'http://ycdfwzy.avi',
            'startTime': self.starttime,
            'endTime': self.endtime,
            'bookStart': self.bookstart,
            'bookEnd': self.bookend,
            'totalTickets': 100,
            'status': 0
        }
        logoutresponse = c.post(self.url, postjson)
        self.assertNotEqual(logoutresponse.json()['code'], 0)
        c.post('/api/a/login',
               {
                   'username': 'admin',
                   'password': 'thisispassword'
               })
        succresponse = c.post(self.url, postjson)
        self.assertEqual(succresponse.json()['code'], 0)

class ImageUploadTest(TestCase):
    def setUp(self):
        self.url = '/api/a/image/upload'
        User = get_user_model()
        User.objects.create_superuser('admin', 'admin@myproject.com', 'thisispassword')
        self.imgpath = '../static/img/good.png'

    def testPost(self):
        c = Client()
        imgf = open(self.imgpath, 'rb')
        imgstr = base64.b64encode(imgf.read())
        postjson = {
            'image': imgstr
        }
        logoutresponse = c.post(self.url, postjson)
        self.assertNotEqual(logoutresponse.json()['code'], 0)
        c.post('/api/a/login',
               {
                   'username': 'admin',
                   'password': 'thisispassword'
               })
        succresponse = c.post(self.url, postjson)
        self.assertEqual(succresponse.json()['code'], 0)

class ActivityDetailTest(TestCase):
    def setUp(self):
        self.url = '/api/a/activity/detail'
        self.starttime = datetime.now()
        self.endtime = datetime.now()
        self.bookstart = datetime.now()
        self.bookend = datetime.now()
        User = get_user_model()
        User.objects.create_superuser('admin', 'admin@myproject.com', 'thisispassword')
        Activity.objects.create(name = 'testac1',
                                key = 'thisisamaxlengthof64key',
                                description = 'testdesc1',
                                start_time = self.starttime,
                                end_time = self.endtime,
                                place = 'testplace1',
                                book_start = self.bookstart,
                                book_end = self.bookend,
                                total_tickets = 100,
                                status = 0,
                                pic_url = 'http://thisisaurl.com',
                                remain_tickets = 99
                                )
        Activity.objects.create(name='testac2',
                                key='thisisamaxlengthof64key',
                                description='testdesc2',
                                start_time=self.starttime,
                                end_time=self.endtime,
                                place='testplace2',
                                book_start=self.bookstart,
                                book_end=self.bookend,
                                total_tickets=200,
                                status=1,
                                pic_url='http://thisisaurl.com',
                                remain_tickets=199
                                )
        self.tickets = [100, 200]

    def testGet(self):
        c = Client()
        getjson = {
            'id': 1
        }
        logoutresponse = c.get(self.url, getjson)
        self.assertNotEqual(logoutresponse.json()['code'], 0)
        c.post('/api/a/login',
               {
                   'username': 'admin',
                   'password': 'thisispassword'
               })
        for i in range(2):
            getjson = {
                'id': i+1
            }
            response = c.get(self.url, getjson)
            activity = response.json()['data']
            self.assertEqual(activity['name'], 'testac'+str(i+1))
            self.assertEqual(activity['key'], 'thisisamaxlengthof64key')
            self.assertEqual(activity['description'], 'testdesc'+str(i+1))
            self.assertEqual(activity['startTime'], self.starttime.timestamp())
            self.assertEqual(activity['endTime'], self.endtime.timestamp())
            self.assertEqual(activity['place'], 'testplace'+str(i+1))
            self.assertEqual(activity['bookStart'], self.bookstart.timestamp())
            self.assertEqual(activity['bookEnd'], self.bookend.timestamp())
            self.assertEqual(activity['totalTickets'], self.tickets[i])
            self.assertEqual(activity['picUrl'], 'http://thisisaurl.com')
            self.assertEqual(activity['usedTickets'], self.tickets[i]-1)
            self.assertAlmostEqual(activity['currentTime'], datetime.now().timestamp(), delta = 5)
            self.assertEqual(activity['status'], i)
        c.post('/api/a/logout',{})

    def testPost(self):
        c = Client()
        postjson = {
            'id': 1,
            'name': 'testac1',
            'place': 'testplace1',
            'description': 'changedesc1',
            'picUrl': 'http://ycdfwzychange.avi',
            'startTime': self.starttime.timestamp(),
            'endTime': self.endtime.timestamp(),
            'bookStart': self.bookstart.timestamp(),
            'bookEnd': self.bookend.timestamp(),
            'totalTickets': 100,
            'status': 0
        }
        logoutresponse = c.post(self.url, postjson)
        self.assertNotEqual(logoutresponse.json()['code'], 0)
        c.post('/api/a/login',
               {
                   'username': 'admin',
                   'password': 'thisispassword'
               })
        succresponse = c.post(self.url, postjson)
        self.assertEqual(logoutresponse.json()['code'], 0)
        c.post('/api/a/logout',{})

class ActivityMenuTest(TestCase):
    def setUp(self):
        self.url = '/api/a/activity/menu'
        User = get_user_model()
        User.objects.create_superuser('admin', 'admin@myproject.com', 'thisispassword')
        self.starttime = datetime.now()
        self.endtime = datetime.now()
        self.bookstart = datetime.now()
        self.bookend = datetime.now()
        Activity.objects.create(name = 'testac1',
                                key = 'thisisamaxlengthof64key',
                                description = 'testdesc1',
                                start_time = self.starttime,
                                end_time = self.endtime,
                                place = 'testplace1',
                                book_start = self.bookstart,
                                book_end = self.bookend,
                                total_tickets = 100,
                                status = 1,
                                pic_url = 'http://thisisaurl.com',
                                remain_tickets = 99
                                )
    def testGet(self):
        c = Client()
        logoutresponse = c.get(self.url, {})
        self.assertNotEqual(logoutresponse.json()['code'], 0)
        c.post('/api/a/login',
               {
                   'username': 'admin',
                   'password': 'thisispassword'
               })
        succresponse = c.get(self.url, {})
        self.assertEqual(succresponse.json()['code'], 0)
        activity = succresponse.json()['data']
        for i in range(1):
            ac = activity[i]
            self.assertEqual(ac['id'], i+1)
            self.assertEqual(ac['name'], 'testac1')
        c.post('/api/a/logout',{})

    def testPost(self):
        c = Client()
        logoutresponse = c.post(self.url, {'id':1})
        self.assertNotEqual(logoutresponse.json()['code'], 0)
        c.post('/api/a/login',
               {
                   'username': 'admin',
                   'password': 'thisispassword'
               })
        succresponse = c.post(self.url, {'id':1})
        self.assertEqual(succresponse.json()['code'], 0)

class CheckinTest(TestCase):
    def setUp(self):
        self.url = '/api/a/activity/checkin'
        User = get_user_model()
        User.objects.create_superuser('admin', 'admin@myproject.com', 'thisispassword')
        self.starttime = datetime.now()
        self.endtime = datetime.now()
        self.bookstart = datetime.now()
        self.bookend = datetime.now()
        Activity.objects.create(name = 'testac1',
                                key = 'thisisamaxlengthof64key',
                                description = 'testdesc1',
                                start_time = self.starttime,
                                end_time = self.endtime,
                                place = 'testplace1',
                                book_start = self.bookstart,
                                book_end = self.bookend,
                                total_tickets = 100,
                                status = 1,
                                pic_url = 'http://thisisaurl.com',
                                remain_tickets = 99
                                )
        wechatuser.objects.create(open_id = 'ycdfwzy')

    def testPost(self):
        c = Client()
        response = c.post('/api/u/user/bind',
               {
                    'openid': 'ycdfwzy',
                    'student_id': '1234567890',
                    'password': 'zstql'
                })
        self.assertEqual(response.json()['code'], 0)
        postjson = {
            'actId': 1,
            'studentId': '1234567890'
        }
        logoutresponse = c.post(self.url, postjson)
        self.assertNotEqual(logoutresponse.json()['code'], 0)
        c.post('/api/a/login',
               {
                   'username': 'admin',
                   'password': 'thisispassword'
               })
        succresponse = c.post(self.url, postjson)
        self.assertEqual(succresponse.json()['code'], 0)
        self.assertEqual(succresponse.json()['data']['studentId'], '1234567890')
