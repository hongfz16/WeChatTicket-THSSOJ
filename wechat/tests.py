# # Create your tests here.
#
from datetime import datetime
from django.test import TestCase, TransactionTestCase
from django.test import Client
from django.contrib.auth import get_user_model
from wechat.models import *
from wechat.views import CustomWeChatView
from WeChatTicket import settings
import threading
from copy import deepcopy
# import xml


def trans_dict_to_xml(data):
    """
    将 dict 对象转换成微信支付交互所需的 XML 格式数据

    :param data: dict 对象
    :return: xml 格式数据 bytes
    """
    xml = []
    for k in sorted(data.keys()):
        v = data.get(k)
        if not v.startswith('<![CDATA['):
            v = '<![CDATA[{}]]>'.format(v)
        xml.append('<{key}>{value}</{key}>'.format(key=k, value=v))
    return '<xml>{}</xml>'.format(''.join(xml)).encode('utf8')

def getDict(userid, content):
    return {
                'ToUserName': 'gh_5e0443904265',
                'FromUserName': userid,
                'CreateTime': '1539793148',
                'MsgType': 'text',
                'Content': content,
                'MsgId': '6613361214134013343',
            }


class BookTicketTest(TestCase):
    def setUp(self):
        self.Url = '/wechat'
        User.objects.create(open_id = 'thisisopenid', student_id = '1234567890')
        self.userid = 'thisisopenid'
        self.stuid = '1234567890'
        user = get_user_model()
        user.objects.create_superuser('admin', 'admin@myproject.com', 'thisispassword')
        Activity.objects.create(
            name='ycdfwzy',
            key='wzy',
            description='zyw',
            start_time=datetime(2019, 10, 22, 2, 31, 0),
            end_time=datetime(2019, 11, 8, 23, 59, 59),
            place='zsdechuangshang',
            book_start=datetime(2018, 10, 10, 8, 8, 8),
            book_end=datetime(2018, 12, 31, 0, 0, 0),
            total_tickets=100,
            status=Activity.STATUS_PUBLISHED,
            pic_url='https://www.pornhub.com/ycdfwzy.png',
            remain_tickets=50
        )
        self.postTextMsg = {'ToUserName': 'gh_5e0443904265',
                            'FromUserName': 'thisisopenid',
                            'CreateTime': '1539793148',
                            'MsgType': 'text',
                            'Content': '抢票 wzy',
                            'MsgId': '6613361214134013343',
                            }
        self.postClickMsg = {'ToUserName': 'gh_5e0443904265',
                            'FromUserName': 'thisisopenid',
                            'CreateTime': '1539793148',
                            'MsgType': 'event',
                            'Event': 'CLICK',
                            'EventKey': 'BOOKING_ACTIVITY_1',
                            }
        Activity.objects.create(
            name='act_remain0',
            key='act_remain0',
            description='act_remain0',
            start_time=datetime(2019, 10, 22, 2, 31, 0),
            end_time=datetime(2019, 11, 8, 23, 59, 59),
            place='jsdechuangshang',
            book_start=datetime(2018, 10, 10, 8, 8, 8),
            book_end=datetime(2018, 12, 31, 0, 0, 0),
            total_tickets=100,
            status=Activity.STATUS_PUBLISHED,
            pic_url='https://www.pornhub.com/ycdfwzy.png',
            remain_tickets=0
        )
        Activity.objects.create(
            name='act_deleted',
            key='act_deleted',
            description='act_deleted',
            start_time=datetime(2019, 10, 22, 2, 31, 0),
            end_time=datetime(2019, 11, 8, 23, 59, 59),
            place='jsdechuangshang',
            book_start=datetime(2018, 10, 10, 8, 8, 8),
            book_end=datetime(2018, 12, 31, 0, 0, 0),
            total_tickets=100,
            status=Activity.STATUS_DELETED,
            pic_url='https://www.pornhub.com/ycdfwzy.png',
            remain_tickets=10
        )
        Activity.objects.create(
            name='act_saved',
            key='act_saved',
            description='act_saved',
            start_time=datetime(2019, 10, 22, 2, 31, 0),
            end_time=datetime(2019, 11, 8, 23, 59, 59),
            place='jsdechuangshang',
            book_start=datetime(2018, 10, 10, 8, 8, 8),
            book_end=datetime(2018, 12, 31, 0, 0, 0),
            total_tickets=100,
            status=Activity.STATUS_SAVED,
            pic_url='https://www.pornhub.com/ycdfwzy.png',
            remain_tickets=100
        )
        Activity.objects.create(
            name='act_overdue',
            key='act_overdue',
            description='act_overdue',
            start_time=datetime(2019, 10, 22, 2, 31, 0),
            end_time=datetime(2019, 11, 8, 23, 59, 59),
            place='jsdechuangshang',
            book_start=datetime(2018, 10, 10, 8, 8, 8),
            book_end=datetime(2018, 10, 11, 0, 0, 0),
            total_tickets=100,
            status=Activity.STATUS_PUBLISHED,
            pic_url='https://www.pornhub.com/ycdfwzy.png',
            remain_tickets=10
        )
        Activity.objects.create(
            name='act_nstart',
            key='act_nstart',
            description='act_nstart',
            start_time=datetime(2019, 10, 22, 2, 31, 0),
            end_time=datetime(2019, 11, 8, 23, 59, 59),
            place='zsdechuangshang',
            book_start=datetime(2018, 10, 20, 8, 8, 8),
            book_end=datetime(2018, 10, 21, 0, 0, 0),
            total_tickets=100,
            status=Activity.STATUS_PUBLISHED,
            pic_url='https://www.pornhub.com/ycdfwzy.png',
            remain_tickets=10
        )

    def test(self):
        c = Client()

        c.post('/api/a/login',
               {
                   'username': 'admin',
                   'password': 'thisispassword'
               })

        addMenuUrl = '/api/a/activity/menu'
        id = Activity.objects.get(name='ycdfwzy').id
        c.post(addMenuUrl, {'idarr': id})

        button = CustomWeChatView.get_book_btn()['sub_button']
        self.assertEqual(len(button), 1)    # check add menu

        self.postClickMsg['EventKey'] = CustomWeChatView.event_keys['book_header']+str(id)
        response = c.post(self.Url,
                          trans_dict_to_xml(self.postClickMsg),
                          content_type='text/xml')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'text.xml')
        self.assertEqual(Activity.objects.get(name = 'ycdfwzy').remain_tickets, 49)
        tkt = Ticket.objects.get(student_id = self.stuid)
        self.assertNotEqual(tkt, None)
        self.assertEqual(tkt.status, Ticket.STATUS_VALID)

        response = c.post(self.Url,
                          trans_dict_to_xml(self.postTextMsg),
                          content_type='text/xml')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'text.xml')
        self.assertContains(response, '你已经抢到票了，请不要重复抢票！')

        #remain = 0
        response = c.post(self.Url,
                          trans_dict_to_xml(getDict(self.userid, '抢票 act_remain0')),
                          content_type = 'text/xml')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'text.xml')
        self.assertContains(response, '抱歉，没票啦！')

        #deleted
        response = c.post(self.Url,
                          trans_dict_to_xml(getDict(self.userid, '抢票 act_deleted')),
                          content_type = 'text/xml')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'text.xml')
        self.assertContains(response, '未找到该活动')

        #saved
        response = c.post(self.Url,
                          trans_dict_to_xml(getDict(self.userid, '抢票 act_saved')),
                          content_type='text/xml')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'text.xml')
        self.assertContains(response, '未找到该活动!')

        #act not exsist
        response = c.post(self.Url,
                          trans_dict_to_xml(getDict(self.userid, '抢票 act_absent')),
                          content_type='text/xml')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'text.xml')
        self.assertContains(response, '未找到该活动!')

        #overdue
        response = c.post(self.Url,
                          trans_dict_to_xml(getDict(self.userid, '抢票 act_overdue')),
                          content_type='text/xml')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'text.xml')
        self.assertContains(response, '抢票已结束!')

        #haven't start
        response = c.post(self.Url,
                          trans_dict_to_xml(getDict(self.userid, '抢票 act_nstart')),
                          content_type='text/xml')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'text.xml')
        self.assertContains(response, '抢票未开始!')


class CheckTicketTest(TestCase):
    def setUp(self):
        self.Url = '/wechat'
        User.objects.create(open_id='thisisopenid', student_id='1234567890')
        # user = get_user_model()
        # user.objects.create_superuser('admin', 'admin@myproject.com', 'thisispassword')
        Activity.objects.create(
            name='gansita',
            key='gansita',
            description='gansita',
            start_time=datetime(2018, 10, 20, 2, 31, 0),
            end_time=datetime(2018, 11, 8, 23, 59, 59),
            place='zsdechuangshang',
            book_start=datetime(2018, 10, 10, 8, 8, 8),
            book_end=datetime(2018, 10, 20, 0, 0, 0),
            total_tickets=100,
            status=Activity.STATUS_PUBLISHED,
            pic_url='https://www.pornhub.com/ycdfwzy.png',
            remain_tickets=50
        )
        self.postTextMsg = {'ToUserName': 'gh_5e0443904265',
                            'FromUserName': 'thisisopenid',
                            'CreateTime': '1539793148',
                            'MsgType': 'text',
                            'Content': '抢票 gansita',
                            'MsgId': '6613361214134013343',
                            }
        self.postClickMsg = {'ToUserName': 'gh_5e0443904265',
                             'FromUserName': 'thisisopenid',
                             'CreateTime': '1539793148',
                             'MsgType': 'event',
                             'Event': 'CLICK',
                             'EventKey': 'SERVICE_GET_TICKET',
                             }

    def test(self):
        c = Client()
        response = c.post(self.Url,
                          trans_dict_to_xml(self.postClickMsg),
                          content_type='text/xml')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'text.xml')
        self.assertContains(response, '你还没有票！')

        response = c.post(self.Url,
                          trans_dict_to_xml(self.postTextMsg),
                          content_type='text/xml')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'text.xml')
        self.assertEqual(Activity.objects.get(name='gansita').remain_tickets, 49)
        unique_id = Ticket.objects.get(student_id='1234567890').unique_id

        response = c.post(self.Url,
                          trans_dict_to_xml(self.postClickMsg),
                          content_type='text/xml')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'news.xml')
        # print("what the hell",str(response))
        # self.assertContains(response,
        #                     [{
        #                         'Title':'gansita',
        #                         'Description':'gansita',
        #                         'Url':settings.get_url('u/ticket',{'openid':'ojM6q1V-l8RyGrzjrirdOdkcwmKQ',
        #                                                            'ticket':unique_id})
        #                     },])


class BookWhatTest(TestCase):
    def setUp(self):
        self.Url = '/wechat'
        User.objects.create(open_id='thisisopenid', student_id='1234567890')
        self.postTextMsg = {'ToUserName': 'gh_5e0443904265',
                            'FromUserName': 'thisisopenid',
                            'CreateTime': '1539793148',
                            'MsgType': 'text',
                            'Content': '抢啥',
                            'MsgId': '6613361214134013343',
                            }
        self.postClickMsg = {'ToUserName': 'gh_5e0443904265',
                             'FromUserName': 'thisisopenid',
                             'CreateTime': '1539793148',
                             'MsgType': 'event',
                             'Event': 'CLICK',
                             'EventKey': 'SERVICE_BOOK_WHAT',
                             }

    def test(self):
        c = Client()
        response = c.post(self.Url,
                          trans_dict_to_xml(self.postClickMsg),
                          content_type='text/xml')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'text.xml')
        self.assertContains(response, '没有可以订票的活动！')

        Activity.objects.create(
            name='gansita',
            key='gansita',
            description='gansita',
            start_time=datetime(2018, 10, 20, 2, 31, 0),
            end_time=datetime(2018, 11, 8, 23, 59, 59),
            place='hell',
            book_start=datetime(2018, 10, 10, 8, 8, 8),
            book_end=datetime(2018, 10, 20, 0, 0, 0),
            total_tickets=100,
            status=Activity.STATUS_PUBLISHED,
            pic_url='https://www.pornhub.com/ycdfwzy.png',
            remain_tickets=2
        )

        response = c.post(self.Url,
                          trans_dict_to_xml(self.postTextMsg),
                          content_type='text/xml')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'news.xml')
        # self.assertContains(response, "")


class BookTicketTestThread(threading.Thread):
    def __init__(self, threadID, client, Url, postMsg):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.client = client
        self.url = Url
        self.postMsg = postMsg
        self.open_id = self.postMsg['FromUserName'] + str(threadID)
        self.postMsg['FromUserName']  = self.open_id
        self.student_id = ('aaaaaaaaa' if self.threadID < 10 else 'aaaaaaaa') + str(self.threadID)
        User.objects.create(open_id=self.open_id, student_id=self.student_id)


    def run(self):
        # self.bindres = self.client.post('/api/u/user/bind',
        #                        {
        #                            'openid': self.open_id,
        #                            'student_id': self.student_id,
        #                            'password': 'cnm'
        #                        })
        self.response = self.client.post(self.url,
                                         trans_dict_to_xml(self.postMsg),
                                         content_type='text/xml')




class BookTicketTestConcurrent(TransactionTestCase):
    def setUp(self):
        self.Url = '/wechat'
        User.objects.create(open_id='thisisopenid', student_id='1234567890')
        # user = get_user_model()
        # user.objects.create_superuser('admin', 'admin@myproject.com', 'thisispassword')
        Activity.objects.create(
            name='shadowiterator',
            key='shadowiterator',
            description='shadowiterator',
            start_time=datetime(2019, 10, 22, 2, 31, 0),
            end_time=datetime(2019, 11, 8, 23, 59, 59),
            place='shadowiterator',
            book_start=datetime(2018, 10, 10, 8, 8, 8),
            book_end=datetime(2018, 12, 31, 0, 0, 0),
            total_tickets=50,
            status=Activity.STATUS_PUBLISHED,
            pic_url='https://www.pornhub.com/ycdfwzy.png',
            remain_tickets=10
        )
        self.postTextMsg = {'ToUserName': 'gh_5e0443904265',
                            'FromUserName': 'thisisopenid',
                            'CreateTime': '1539793148',
                            'MsgType': 'text',
                            'Content': '抢票 shadowiterator',
                            'MsgId': '6613361214134013343',
                            }

    def test(self):
        c = Client()
        threadpool = []
        for i in range(50):
            thread = BookTicketTestThread(i, deepcopy(c), self.Url, deepcopy(self.postTextMsg))
            threadpool.append(thread)
            thread.start()
        for t in threadpool:
            t.join()

        count = 0
        for t in threadpool:
            self.assertEqual(t.response.status_code, 200)
            self.assertTemplateUsed(t.response, 'text.xml')
            if t.response.content.decode('utf8').find('恭喜你') == -1:
                self.assertContains(t.response, '抱歉，没票啦！')
            else:
                count = count + 1
        self.assertEqual(count, 10)
        self.assertEqual(Activity.objects.get(name="shadowiterator").remain_tickets, 0)