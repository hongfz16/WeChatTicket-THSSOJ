from django.shortcuts import render
from django.http import HttpResponse
from adminpage.models import *
from codex.baseview import APIView
from wechat.models import Activity
from wechat.models import Ticket
from datetime import datetime
from wechat.views import CustomWeChatView
from django.contrib import auth
from wechat.models import User, Activity, Ticket
from codex.baseerror import *
from WeChatTicket.settings import get_url
from django.utils import timezone
import uuid
import base64
import os
import json
import pickle

# Create your views here.


def getCurrentTime():
    return int( timezone.now().timestamp() )


def get_index(id, buttons):
    book_header = CustomWeChatView.event_keys['book_header']
    for i in range(len(buttons)):
        if buttons[i]['key'] == book_header+str(id):
            return i+1
    return 0


class loginPage(APIView):
    def get(self):
        print("loginPage get")
        if self.request.user.is_authenticated():
            return ''
        else:
            raise ValidateError('user not logged')
    def post(self):
        print("loginPage post")
        self.check_input('username', 'password')
        usr_name=self.input['username']
        pass_wrd=self.input['password']
        user=auth.authenticate(username=usr_name, password=pass_wrd, request=self.request)
        if user is not None:
            auth.login(self.request, user)
        else:
            raise ValidateError('invalid username or password!')

class logoutPage(APIView):
    def post(self):
        print("logoutPage post")
        # print(self.request.user)
        if not self.request.user.is_authenticated():
            raise LogicError('logout error!')
        auth.logout(self.request)

class activityList(APIView):

    def get(self):
        print("activityList get")
        if not self.request.user.is_authenticated():
            raise LogicError('Your are offline!')

        try:
            actived_activities = Activity.get_nonegtive_status()
        except:
            raise LogicError('get error when status')

        ret = []
        for act in actived_activities:
            re = {}
            re['id'] = act.id
            re['name'] = act.name
            re['description'] = act.description
            re['startTime'] = int(act.start_time.timestamp())
            re['endTime'] = int(act.end_time.timestamp())
            re['place'] = act.place
            re['bookStart'] = int(act.book_start.timestamp())
            re['bookEnd'] = int(act.book_end.timestamp())
            re['currentTime'] = getCurrentTime()
            if act.status == Activity.STATUS_PUBLISHED:
                re['status'] = 1
            else: re['status'] = 0
            ret.append(re)
        return ret

class activityDelete(APIView):
    def post(self):
        print("activityDelete post")
        if not self.request.user.is_authenticated():
            raise LogicError('Your are offline!')

        self.check_input('id')
        try:
            Activity.remove_by_id(self.input['id'])
        except:
            raise LogicError('delete activity error!')


class activityCreate(APIView):
    def post(self):
        print("activityCreate post")
        if self.request.user.is_authenticated():
            self.check_input('name', 'key', 'place', 'description', 'picUrl', 'startTime',
                             'endTime', 'bookStart', 'bookEnd', 'totalTickets', 'status')
            if int(self.input['bookEnd']) < int(self.input['bookStart']):
                raise InputError("bookEnd < bookStart")
            if int(self.input['endTime']) < int(self.input['startTime']):
                raise InputError("endTime < startTime")
            if int(self.input['totalTickets']) < 0:
                raise InputError("totalTickets < 0")
            if len(self.input['key'])>64:
                raise InputError('key is too long')
            if int(self.input['status'])<-1 or int(self.input['status'])>1:
                raise InputError('status error')
            try:
                print(self.input['name'])
                print(self.input['name'].encode('gbk').decode('gbk'))
                new_activity=Activity.objects.create(name=self.input['name'], key=self.input['key'], place=self.input['place'],
                                                     description=self.input['description'], pic_url=self.input['picUrl'],
                                                     start_time=datetime.fromtimestamp(float(self.input['startTime'])),
                                                     end_time=datetime.fromtimestamp(float(self.input['endTime'])),
                                                     book_start=datetime.fromtimestamp(float(self.input['bookStart'])),
                                                     book_end=datetime.fromtimestamp(float(self.input['bookEnd'])),
                                                     total_tickets=int(self.input['totalTickets']),
                                                     remain_tickets=int(self.input['totalTickets']),
                                                     status=int(self.input['status']))
                return new_activity.id
            except Exception as e:
                print("activityCreate fail!")
                raise BaseError(4, str(e))
                # raise InputError('error when write new activity item')
        else:
            raise ValidateError('user not logged')

class imageUpload(APIView):
    def post(self):
        print("imageUpload post")
        if self.request.user.is_authenticated():
            self.check_input('image')
            ori_content=self.input['image']

            cur_path=os.getcwd()
            tgt_path=cur_path+'/static/images'
            if not os.path.exists(tgt_path):
                try:
                    os.makedirs(tgt_path)
                except:
                    raise ValidateError('create image path error')
            try:
                unique_str = str(uuid.uuid1())
                return_path = '/images/'+unique_str+'.png'
                image_path = tgt_path + '/' + unique_str + '.png'
                img_file = open(image_path, 'wb')
                img_file.write(ori_content[0].read())
                img_file.close()
                total_url = get_url(return_path)
                return total_url
            except:
                raise ValidateError('save image error')
        else:
            raise ValidateError('user not logged')

class activityDetail(APIView):
    def get(self):
        print("activityDetail get")
        if not self.request.user.is_authenticated():
            # print("detail offline!")
            raise LogicError('Your are offline!')

        self.check_input('id')
        try:
            res = Activity.get_by_id(int(self.input['id']))
        except:
            raise LogicError("get activity by id")
        ret = {}
        ret['name'] = res.name
        ret['key'] = res.key
        ret['description'] = res.description
        ret['startTime'] = int(res.start_time.timestamp())
        ret['endTime'] = int(res.end_time.timestamp())
        ret['place'] = res.place
        ret['bookStart'] = int(res.book_start.timestamp())
        ret['bookEnd'] = int(res.book_end.timestamp())
        ret['totalTickets'] = res.total_tickets
        ret['picUrl'] = res.pic_url
        ret['bookedTickets'] = res.total_tickets-res.remain_tickets
        ret['currentTime'] = getCurrentTime()
        if res.status == Activity.STATUS_PUBLISHED:
            ret['status'] = 1
        else: ret['status'] = 0

        cnt = 0
        ress = Ticket.get_by_activity(res)
        for res in ress:
            if res.status == Ticket.STATUS_USED:
                cnt = cnt+1
        ret['usedTickets'] = cnt

        return ret

    def post(self):
        print("activityDetail post")
        if not self.request.user.is_authenticated():
            raise LogicError('Your are offline!')

        self.check_input('id', 'name', 'place', 'description',
                         'picUrl', 'startTime', 'endTime', 'bookStart',
                         'bookEnd', 'totalTickets', 'status')
        try:
            res = Activity.get_by_id(int(self.input['id']))
        except:
            raise LogicError("get activity by id error!")

        if res.status != Activity.STATUS_PUBLISHED:
            if res.name != self.input['name']:
                raise LogicError('can\'t  modify name')
            if res.place != self.input['place']:
                raise LogicError('can\'t  modify place')
            # print("self.input['bookStart="+str(self.input['bookStart']))
            # print("res.book_start="+str(res.book_start))
            if int(res.book_start.timestamp()) != int(float(self.input['bookStart'])):
                raise LogicError('can\'t  modify book_start')
            if res.status != int(self.input['status']) and int(self.input['status']) == 0:
                raise LogicError('can\'t  modify status')

        curTime = getCurrentTime()
        if curTime > int(res.start_time.timestamp()):
            if int(res.book_end.timestamp()) != int(float(self.input['bookEnd'])):
                raise LogicError('can\'t  modify book_end')
            if res.total_tickets != int(self.input['totalTickets']):
                raise LogicError('can\'t  modify total_tickets')

        if curTime > int(res.end_time.timestamp()):
            if int(res.start_time.timestamp()) != int(float(self.input['startTime'])):
                raise LogicError('can\'t  modify start_time')
            if int(res.end_time.timestamp()) != int(float(self.input['endTime'])):
                raise LogicError('can\'t  modify end_time')

        res.name = self.input['name']
        res.place = self.input['place']
        res.description = self.input['description']
        res.pic_url = self.input['picUrl']
        res.start_time = datetime.fromtimestamp(float(self.input['startTime']))
        res.end_time = datetime.fromtimestamp(float(self.input['endTime']))
        res.book_start = datetime.fromtimestamp(float(self.input['bookStart']))
        res.book_end = datetime.fromtimestamp(float(self.input['bookEnd']))
        res.total_tickets = int(self.input['totalTickets'])
        res.status = int(self.input['status'])
        res.save()
        return


class activityCheckin(APIView):
    def post(self):
        print("activityCheckin get")
        ticket_info={}
        if self.request.user.is_authenticated():
            self.check_input('actId')
            try:
                activity=Activity.objects.get(id=self.input['actId'])
            except:
                raise ValidateError('activity not found')
            if 'ticket' in self.input:
                try:
                    ticket=Ticket.objects.get(unique_id=self.input['ticket'])
                    if ticket.activity.name==activity.name:
                        ticket_info['ticket']=ticket.unique_id
                        ticket_info['studentId']=ticket.student_id
                        return ticket_info
                    else:
                        raise LogicError('not match')
                except:
                    raise ValidateError('no valid ticket')
            elif 'studentId' in self.input:
                try:
                    ticket=Ticket.objects.get(student_id=self.input['studentId'])
                    if ticket.activity.name==activity.name:
                        ticket_info['ticket']=ticket.unique_id
                        ticket_info['studentId']=ticket.student_id
                        return ticket_info
                    else:
                        raise LogicError('not match')
                except:
                    raise ValidateError('no valid ticket')
            else:
                raise InputError('inadequate input')
        else:
            raise ValidateError('user not logged')


class activityMenu(APIView):
    def get(self):
        print("activityMenu get")
        if not self.request.user.is_authenticated():
            raise LogicError('Your are offline!')

        try:
            res = Activity.get_status_published()
        except:
            raise LogicError('get activity by status=1 error!')

        buttons = CustomWeChatView.menu['button'][1]['sub_button']

        ret = []
        for re in res:
            RET = {}
            RET['id'] = re.id
            RET['name'] = re.name
            RET['menuIndex'] = get_index(re.id, buttons)
            ret.append(RET)
        return ret

    def post(self):
        print("activityMenu post")
        if not self.request.user.is_authenticated():
            raise LogicError('Your are offline!')

        if isinstance(self.input, list):
            acts = self.input
        elif isinstance(self.input['idarr'], str):
            acts = [int(self.input['idarr']), ]
        else:
            raise LogicError('logical error!')

        try:
            res = []
            for act in acts:
                res.append(Activity.get_by_id(int(act)))
        except:
            raise LogicError('get activity by id error!')

        try:
            print(res)
            CustomWeChatView.update_menu(res)
        except:
            raise LogicError('update Menu failed!')
        return
