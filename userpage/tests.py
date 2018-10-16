# Create your tests here.

from datetime import datetime
from django.utils import timezone
from django.test import TestCase
from django.test import Client
from wechat.models import User, Activity, Ticket

class TestUBind(TestCase):
    def setUp(self):
        self.url = '/api/u/user/bind'
        User.objects.create(open_id = 'ycdfwzy')
        User.objects.create(open_id = 'wzsxzjl')
        User.objects.create(open_id = 'klsshfz')

    def testUserNotExist(self):
# test nobody
        c = Client()
        response = c.get(self.url,
                         {
                             'openid': ''
                         })
        self.assertNotEqual(response.json()['code'], 0)

        c = Client()
        response = c.get(self.url,
                         {
                             'open_id': 'wzsxzjl'
                         })
        self.assertNotEqual(response.json()['code'], 0)

        c = Client()
        response = c.get(self.url,
                         {
                             'openid': 'somebodynotexist'
                         })
        self.assertNotEqual(response.json()['code'], 0)

    def testBind(self):
# test lrj
    # get: user not found
        c = Client()
        response = c.get(self.url,
                         {
                             'openid': 'bjdxlrj'
                         })
        self.assertNotEqual(response.json()['code'], 0)
    # post: user not found
        response = c.c.post(self.url,
                        {
                            'openid': 'bjdxlrj',
                            'student_id': '1234567890',
                            'password': 'rjtcl'
                        })
        self.assertNotEqual(response.json()['code'], 0)

# test hfz
    # unbind user
        c = Client()
        response = c.get(self.url,
                         {
                             'openid': 'klsshfz'
                         })
        self.assertEqual(response.json()['data'], '')

# test zjl
    # invalid student id
        c = Client()
        response = c.post(self.url,
                    {
                        'openid': 'wzsxzjl',
                        'student_id': '12345',
                        'password': 'jltql'
                    })
        self.assertNotEqual(response.json()['code'], 0)

        response = c.post(self.url,
                          {
                              'openid': 'wzsxzjl',
                              'student_id': '',
                              'password': 'jltql'
                          })
        self.assertNotEqual(response.json()['code'], 0)

        response = c.post(self.url,
                          {
                              'openid': 'wzsxzjl',
                              'student_id': None,
                              'password': 'jltql'
                          })
        self.assertNotEqual(response.json()['code'], 0)

        response = c.post(self.url,
                          {
                              'openid': 'wzsxzjl',
                              'password': 'jltql'
                          })
        self.assertNotEqual(response.json()['code'], 0)

        response = c.post(self.url,
                          {
                              'openid': 'wzsxzjl',
                              'student_id': '1234567890',
                          })
        self.assertNotEqual(response.json()['code'], 0)

        response = c.post(self.url,
                          {
                              'student_id': '1234567890',
                              'password': 'jltql'
                          })
        self.assertNotEqual(response.json()['code'], 0)

        response = c.get(self.url,
                         {
                             'openid': 'wzsxzjl'
                         })
        self.assertEqual(response.json()['data'], '')

# test wzy
    # success
        response = c.post(self.url,
                          {
                              'openid': 'ycdfwzy',
                              'student_id': '1234567890',
                              'password': 'zstql'
                          })
        self.assertEqual(response.json()['code'], 0)

        response = c.post(self.url,
                          {
                               'openid': 'ycdfwzy'
                          })
        self.assertEqual(response.json()['code'], 0)
        self.assertEqual(response.json()['data'], '1234567890')

class TestUActivity(TestCase):
    def setUp(self):
        self.url = '/api/u/activity/detail'
    # act 1
        Activity.objects.create(
            name = 'ycdfwzy',
            key = 'wzy',
            description = 'zyw',
            start_time = datetime(1999, 9, 11, 2, 31, 0),
            end_time = datetime(2000, 11, 8, 23, 59, 59),
            place = 'zsdechuangshang',
            book_start = datetime(1997, 12, 9, 8, 8, 8),
            book_end = datetime(2000, 11, 8, 0, 0, 0),
            total_tickets = 100,
            status = 1,
            pic_url = 'https://www.pornhub.com/ycdfwzy.png',
            remain_tickets = 50
        )
    # act 2
        Activity.objects.create(
            name = 'wzsxzjl',
            key = 'zjl',
            description = 'jlz',
            start_time = datetime(1999, 9, 11, 2, 31, 0),
            end_time = datetime(2000, 11, 8, 23, 59, 59),
            place = 'jldechuangshang',
            book_start = datetime(1997, 12, 9, 8, 8, 8),
            book_end = datetime(2000, 11, 8, 0, 0, 0),
            total_tickets = 100,
            status = 0,
            pic_url = 'https://www.pornhub.com/ycdfwzy.png',
            remain_tickets = 50
        )
    # act 3
        Activity.objects.create(
            name = 'klsxhfz',
            key = 'hfz',
            description = 'fzh',
            start_time = datetime(1999, 9, 11, 2, 31, 0),
            end_time = datetime(2000, 11, 8, 23, 59, 59),
            place = 'fzdechuangshang',
            book_start = datetime(1997, 12, 9, 8, 8, 8),
            book_end = datetime(2000, 11, 8, 0, 0, 0),
            total_tickets = 100,
            status = -1,
            pic_url = 'https://www.pornhub.com/hfz.png',
            remain_tickets = 50
        )
        self.id1 = Activity.objects.get(name = 'ycdfwzy').id
        self.id2 = Activity.objects.get(name = 'wzsxzjl').id
        self.id3 = Activity.objects.get(name = 'klsxhfz').id

    def testFail(self):
        c = Client()
        response = c.get(self.url,
                         {
                             'id': self.id2
                         })
        self.assertNotEqual(response.json()['code'], 0)

        response = c.get(self.url,
                         {
                             'id': self.id3
                         })
        self.assertNotEqual(response.json()['code'], 0)

        response = c.get(self.url,
                         {
                             'id': 4000
                         })
        self.assertNotEqual(response.json()['code'], 0)

        response = c.get(self.url,
                         {
                             'id': -1
                         })
        self.assertNotEqual(response.json()['code'], 0)

        response = c.get(self.url,
                         {
                             'id': None
                         })
        self.assertNotEqual(response.json()['code'], 0)

        response = c.get(self.url,
                         {
                             'id': '1'
                         })
        self.assertNotEqual(response.json()['code'], 0)

        response = c.get(self.url,
                         {
                             'id': 'zjl'
                         })
        self.assertNotEqual(response.json()['code'], 0)

    def testSuccess(self):
        c = Client()
        curTime = int(timezone.now().timestamp())
        obj = Activity.objects.get(id = self.id1)
        response = c.get(self.url,
                         {
                            'id': self.id1
                         })
        js = response.json()['data']
        self.assertEqual(js['name'], obj.name)
        self.assertEqual(js['key'], obj.key)
        self.assertEqual(js['description'], obj.description)
        self.assertEqual(js['startTime'], int(obj.start_time.timestamp()))
        self.assertEqual(js['endTime'], int(obj.end_time.timestamp()))
        self.assertEqual(js['place'], obj.place)
        self.assertEqual(js['bookStart'], int(obj.book_start.timestamp()))
        self.assertEqual(js['bookEnd'], int(obj.book_end.timestamp()))
        self.assertEqual(js['totalTickets'], obj.tot_tickets)
        self.assertEqual(js['picUrl'], obj.pic_url)
        self.assertEqual(js['remainTickets'], obj.remain_tickets)
        self.assertAlmostEqual(js['currentTime'], curTime, delta = 5)

class TestUTicket(TestCase):
    def setUp(self):
        self.url = '/api/u/ticket/detail'
        User.objects.create(open_id = 'ycdfwzy')
    # act 1
        Activity.objects.create(
            name = 'ycdfwzy',
            key = 'wzy',
            description = 'zyw',
            start_time = datetime(1999, 9, 11, 2, 31, 0),
            end_time = datetime(2000, 11, 8, 23, 59, 59),
            place = 'zsdechuangshang',
            book_start = datetime(1997, 12, 9, 8, 8, 8),
            book_end = datetime(2000, 11, 8, 0, 0, 0),
            total_tickets = 100,
            status = 1,
            pic_url = 'https://www.pornhub.com/ycdfwzy.png',
            remain_tickets = 50
        )
    # act 2
        Activity.objects.create(
            name = 'wzsxzjl',
            key = 'zjl',
            description = 'jlz',
            start_time = datetime(1999, 9, 11, 2, 31, 0),
            end_time = datetime(2000, 11, 8, 23, 59, 59),
            place = 'jldechuangshang',
            book_start = datetime(1997, 12, 9, 8, 8, 8),
            book_end = datetime(2000, 11, 8, 0, 0, 0),
            total_tickets = 100,
            status = 0,
            pic_url = 'https://www.pornhub.com/ycdfwzy.png',
            remain_tickets = 50
        )
    # act 3
        Activity.objects.create(
            name = 'klsxhfz',
            key = 'hfz',
            description = 'fzh',
            start_time = datetime(1999, 9, 11, 2, 31, 0),
            end_time = datetime(2000, 11, 8, 23, 59, 59),
            place = 'fzdechuangshang',
            book_start = datetime(1997, 12, 9, 8, 8, 8),
            book_end = datetime(2000, 11, 8, 0, 0, 0),
            total_tickets = 100,
            status = -1,
            pic_url = 'https://www.pornhub.com/hfz.png',
            remain_tickets = 50
        )
        self.id1 = Activity.objects.get(name = 'ycdfwzy').id
        self.id2 = Activity.objects.get(name = 'wzsxzjl').id
        self.id3 = Activity.objects.get(name = 'klsxhfz').id


    # ticket1: success, a = 1, s = 0
        Ticket.objects.create(
            student_id = '1234567890',
            unique_id = '123',
            activity = Activity.objects.get(id = self.id1),
            status = 0
        )
    # ticket2: success, a = 2, s = 0
        Ticket.objects.create(
            student_id = '1234567890',
            unique_id = '123',
            activity = Activity.objects.get(id = self.id2),
            status = 0
        )
    # ticket3: success, a = 3, s = 0
        Ticket.objects.create(
            student_id = '1234567890',
            unique_id = '123',
            activity = Activity.objects.get(id = self.id3),
            status = 0
        )
    # ticket4: success, a = 1, s = 1
        Ticket.objects.create(
            student_id = '1234567890',
            unique_id = '123',
            activity = Activity.objects.get(id = self.id1),
            status = 1
        )
    # ticket5: success, a = 1, s = 2
        Ticket.objects.create(
            student_id = '1234567890',
            unique_id = '123',
            activity = Activity.objects.get(id = self.id1),
            status = 2
        )

    def testUserNotExist(self):
    # test nobody
        c = Client()
        response = c.get(self.url,
                         {
                             'openid': '',
                             'ticket': '123'
                         })
        self.assertNotEqual(response.json()['code'], 0)

        response = c.get(self.url,
                         {
                             'open_id': 'wzsxzjl',
                             'ticket': '123'
                         })
        self.assertNotEqual(response.json()['code'], 0)

        response = c.get(self.url,
                         {
                             'openid': 'somebodynotexist',
                             'ticket': '123'
                         })
        self.assertNotEqual(response.json()['code'], 0)

    def testFailed(self):
        c = Client()
        response = c.get(self.url,
                         {
                             'openid': 'ycdfwzy',
                             'ticket': 'fakeid'
                         })
        self.assertNotEqual(response.json()['code'], 0)
        response = c.get(self.url,
                         {
                             'openid': 'ycdfwzy'
                         })
        self.assertNotEqual(response.json()['code'], 0)
        response = c.get(self.url,
                         {
                             'openid': 'ycdfwzy',
                             'ticket': 123
                         })
        self.assertNotEqual(response.json()['code'], 0)

    def testSuccess(self):
        c = Client()
        curTime = int(timezone.now().timestamp())
        response = c.get(self.url,
                         {
                             'openid': 'ycdfwzy',
                             'ticket': '123'
                         })
        js = response.json()['data']
        objT = Ticket.objects.get(unique_id = '123')
        objA = objT.activity
        self.assertEqual(js['activityName'], objA.name)
        self.assertEqual(js['place'], objA.place)
        self.assertEqual(js['activityKey'], objA.key)
        self.assertEqual(js['uniqueId'], objT.unique_id)
        self.assertEqual(js['startTime'], int(objA.start_time.timestamp()))
        self.assertEqual(js['endTime'], int(objA.end_time.timestamp()))
        self.assertEqual(js['status'], objT.status)
        self.assertAlmostEqual(js['currentTime'], curTime, delta = 5)
