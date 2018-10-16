# -*- coding: utf-8 -*-
from django.test import TestCase
from django.test import Client
from django.contrib.auth import get_user_model
from wechat.models import Activity
from wechat.models import User as wechatuser
from datetime import datetime
from django.utils import timezone
import base64
from copy import deepcopy

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
    # 2 client (session)
        c1 = Client()
        response1 = c1.post('/api/a/login',
               {
                   'username': 'admin',
                   'password': 'thisispassword'
               })
        self.assertEqual(response1.json()['code'], 0)
        response1 = c1.get('/api/a/login', {})
        self.assertEqual(response1.json()['code'], 0)
        c2 = Client()
        response2 = c2.get('/api/a/login', {})
        self.assertNotEqual(response2.json()['code'], 0)
        response2 = c2.post('/api/a/login',
               {
                   'username': 'admin',
                   'password': 'thisispassword'
               })
        self.assertEqual(response2.json()['code'], 0)
        response2 = c2.get('/api/a/login', {})
        self.assertEqual(response2.json()['code'], 0)


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
        # default status test
        c2 = Client()
        response2 = c2.post('/api/a/logout', {})
        self.assertNotEqual(response2.json()['code'], 0)

class ActivityListTest(TestCase):
    def setUp(self):
        self.starttime = timezone.now()
        self.endtime = timezone.now()
        self.bookstart = timezone.now()
        self.bookend = timezone.now()
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
            self.assertAlmostEqual(activity['currentTime'], timezone.now().timestamp(), delta = 5)
            self.assertEqual(activity['status'], i)

class ActivityDeleteTest(TestCase):
    def setUp(self):
        self.starttime = timezone.now()
        self.endtime = timezone.now()
        self.bookstart = timezone.now()
        self.bookend = timezone.now()
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
                                  'id': 1
                              })
        self.assertNotEqual(logoutresponse.json()['code'], 0)
        c.post('/api/a/login',
               {
                   'username': 'admin',
                   'password': 'thisispassword'
               })
        succresponse = c.post('/api/a/activity/delete',
                              {
                                  'id': 1
                              })
        self.assertEqual(succresponse.json()['code'], 0)
        failresponse = c.post('/api/a/activity/delete',
                              {
                                  'id': 100
                              })
        self.assertNotEqual(failresponse.json()['code'], 0)
        succ2response = c.post('/api/a/activity/delete',
                              {
                                  'id': 2
                              })
        self.assertEqual(succ2response.json()['code'], 0)
    # another
        response2 = c.post('/api/a/activity/delite',
                           {
                               'id': -1
                           })
        self.assertNotEqual(response2.json()['code'], 0)
        response2 = c.post('/api/a/activity/delite',
                           {
                               'id': 0
                           })
        self.assertNotEqual(response2.json()['code'], 0)
        response2 = c.post('/api/a/activity/delite',
                           {
                               'id': '0'
                           })
        self.assertNotEqual(response2.json()['code'], 0)

class ActivityCreateTest(TestCase):
    def setUp(self):
        self.url = '/api/a/activity/create'
        User = get_user_model()
        User.objects.create_superuser('admin', 'admin@myproject.com', 'thisispassword')
        # self.starttime = timezone.now().timestamp()
        # self.endtime = timezone.now().timestamp()
        # self.bookstart = timezone.now().timestamp()
        # self.bookend = timezone.now().timestamp()
        self.mstarttime = datetime(1999, 9, 11, 2, 31, 0)
        self.mendtime = datetime(2000, 11, 8, 23, 59, 59)
        self.mbookstart = datetime(1997, 12, 9, 8, 8, 8)
        self.mbookend = datetime(2000, 11, 8, 0, 0, 0)

        self.starttime = int(self.mstarttime.timestamp())
        self.endtime = int(self.mendtime.timestamp())
        self.bookstart = int(self.mbookstart.timestamp())
        self.bookend = int(self.mbookend.timestamp())
        # already an activity in db
        Activity.objects.create(name='testac2',
                                key='thisisamaxlengthof64key',
                                description='testdesc2',
                                start_time=self.mstarttime,
                                end_time=self.mendtime,
                                place='testplace2',
                                book_start=self.mbookstart,
                                book_end=self.mbookend,
                                total_tickets=200,
                                status=1,
                                pic_url='http://thisisaurl.com',
                                remain_tickets=199
                                )


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
        #test data field
        self.assertEqual(succresponse.json()['data'], 2)
        # check db
        obj = Activity.objects.get(id = succresponse.json()['data'])
        self.assertNotEqual(obj, None)
        self.assertEqual(postjson['name'], obj.name)
        self.assertEqual(postjson['key'], obj.key)
        self.assertEqual(postjson['description'], obj.description)
        self.assertEqual(postjson['place'], obj.place)
        self.assertEqual(postjson['totalTickets'], obj.total_tickets)
        self.assertEqual(postjson['picUrl'], obj.pic_url)
        self.assertEqual(postjson['startTime'], int(obj.start_time.timestamp()))
        self.assertEqual(postjson['endTime'], int(obj.end_time.timestamp()))
        self.assertEqual(postjson['bookStart'], int(obj.book_start.timestamp()))
        self.assertEqual(postjson['bookEnd'], int(obj.book_end.timestamp()))

    # some more tests
        postjsonbs = {
            'name': 'sitest0',
            'key': 'thisisaxiajibabiandekey',
            'place': 'testplace1',
            'description': 'testdesc1',
            'picUrl': 'http://ycdfwzy.avi',
            'startTime': self.endtime,
            'endTime': self.starttime,
            'bookStart': self.bookstart,
            'bookEnd': self.bookend,
            'totalTickets': 100,
            'status': 0
        }
        # endtime < starttime: should return false
        postjson2 = deepcopy(postjsonbs)
        postjson2['startTime'] = self.endtime
        postjson2['endTime'] = self.starttime
        response2 = c.post(self.url, postjson2)
        self.assertNotEqual(response2.json()['code'], 0)
        # bookend < bookstart: should return false
        postjson2 = deepcopy(postjsonbs)
        postjson2['bookStart'] = self.bookend
        postjson2['bookEnd'] = self.bookstart
        response2 = c.post(self.url, postjson2)
        self.assertNotEqual(response2.json()['code'], 0)
        # totalTickets < 0: should return false
        postjson2 = deepcopy(postjsonbs)
        postjson2['totalTickets'] = -1
        response2 = c.post(self.url, postjson2)
        self.assertNotEqual(response2.json()['code'], 0)
        # length of [key] exceed
        postjson2 = deepcopy(postjsonbs)
        postjson2['key'] = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
        response2 = c.post(self.url, postjson2)
        self.assertNotEqual(response2.json()['code'], 0)
        # timestamp test
        postjson2 = deepcopy(postjsonbs)
        postjson2['startTime'] = 100000
        postjson2['endTime'] = 100000000.1415926
        response2 = c.post(self.url, postjson2)
        self.assertNotEqual(response2.json()['code'], 0)
        # invalid value of status field
        postjson2 = deepcopy(postjsonbs)
        postjson2['status'] = 2
        response2 = c.post(self.url, postjson2)
        self.assertNotEqual(response2.json()['code'], 0)
        # multiple language test
            # 1
        postjson2 = deepcopy(postjsonbs)
        postjson2['name'] = '讲中文'
        postjson2['description'] = '讲中文'
        response2 = c.post(self.url, postjson2)
        self.assertEqual(response2.json()['code'], 0)
        self.assertEqual(response2.json()['data'], 3)
            # 2
        postjson2 = deepcopy(postjsonbs)
        postjson2['name'] = '日本語で話す'
        postjson2['description'] = '日本語で話す'
        response2 = c.post(self.url, postjson2)
        self.assertEqual(response2.json()['code'], 0)
        self.assertEqual(response2.json()['data'], 4)


class ImageUploadTest(TestCase):
    def setUp(self):
        self.url = '/api/a/image/upload'
        User = get_user_model()
        User.objects.create_superuser('admin', 'admin@myproject.com', 'thisispassword')
        self.imgpath = 'static/img/good.png'

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
        self.starttime = timezone.now()
        self.endtime = timezone.now()
        self.bookstart = timezone.now()
        self.bookend = timezone.now()
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
        siresponse = c.post('/api/a/login',
               {
                   'username': 'admin',
                   'password': 'thisispassword'
               })
        self.assertEqual(siresponse.json()['code'], 0)
        for i in range(2):
            getjson = {
                'id': i+1
            }
            response = c.get(self.url, getjson)
            self.assertEqual(response.json()['code'], 0)
            activity = response.json()['data']
            self.assertIsInstance(activity, dict)
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
            self.assertAlmostEqual(activity['currentTime'], timezone.now().timestamp(), delta = 5)
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
        self.assertEqual(succresponse.json()['code'], 0)
        c.post('/api/a/logout',{})

class ActivityMenuTest(TestCase):
    def setUp(self):
        self.url = '/api/a/activity/menu'
        User = get_user_model()
        User.objects.create_superuser('admin', 'admin@myproject.com', 'thisispassword')
        self.starttime = timezone.now()
        self.endtime = timezone.now()
        self.bookstart = timezone.now()
        self.bookend = timezone.now()
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
        self.starttime = timezone.now()
        self.endtime = timezone.now()
        self.bookstart = timezone.now()
        self.bookend = timezone.now()
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
