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

# Create your views here.


def getCurrentTime():
    return int( timezone.now().timestamp() )


def get_index(id, buttons):
    book_header = CustomWeChatView.event_keys['book_header']
    for i in range(len(buttons)):
        if buttons['key'] == book_header+str(id):
            return i+1
    return 0


class loginPage(APIView):
    def get(self):
        if self.request.user.is_authenticated():
            pass
        else:
            raise ValidateError('user not logged')
    def post(self):
        self.check_input('username', 'password')
        usr_name=self.input['username']
        pass_wrd=self.input['password']
        user=auth.authenticate(username=usr_name, password=pass_wrd)
        if user is not None:
            auth.login(self.request, user)
        else:
            raise ValidateError('invalid username or password!')

class logoutPage(APIView):
    def post(self):
        if self.request.user.is_authenticated():
            auth.logout(self.request)
        else:
            raise LogicError('logout error!')

class activityList(APIView):

    def get(self):
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
            re['startTime'] = act.start_time
            re['endTime'] = act.end_time
            re['place'] = act.place
            re['bookStart'] = act.book_start
            re['bookEnd'] = act.book_end
            re['currentTime'] = getCurrentTime()
            if act.status == Activity.STATUS_PUBLISHED:
                re['status'] = 1
            else: re['status'] = 0
            ret.append(re)

        return ret

class activityDelete(APIView):
    def post(self):
        if not self.request.user.is_authenticated():
            raise LogicError('Your are offline!')

        self.check_input('id')
        try:
            Activity.remove_by_id(self.input['id'])
        except:
            raise LogicError('delete activity error!')


class activityCreate(APIView):
    def post(self):
        if self.request.user.is_authenticated():
            self.check_input('name', 'key', 'place', 'description', 'picUrl', 'startTime',
                             'endTime', 'bookStart', 'bookEnd', 'totalTickets', 'status')
            print("self.input['bookEnd']="+str(self.input['bookEnd']))
            print("self.input['bookStart']=" + str(self.input['bookStart']))
            if int(self.input['bookEnd']) < int(self.input['bookStart']):
                raise InputError("bookEnd < bookStart")
            if int(self.input['endTime']) < int(self.input['startTime']):
                raise InputError("endTime < startTime")
            try:
                new_activity=Activity.objects.create(name=self.input['name'], key=self.input['key'], place=self.input['place'],
                                                     description=self.input['description'], pic_url=self.input['picUrl'],
                                                     start_time=datetime.fromtimestamp(float(self.input['startTime'])),
                                                     end_time=datetime.fromtimestamp(float(self.input['endTime'])),
                                                     book_start=datetime.fromtimestamp(float(self.input['bookStart'])),
                                                     book_end=datetime.fromtimestamp(float(self.input['bookEnd'])),
                                                     total_tickets=self.input['totalTickets'],
                                                     remain_tickets=self.input['totalTickets'],
                                                     status=self.input['status'])
                return new_activity.id
            except Exception as e:
                print("activityCreate fail!")
                raise BaseError(4, str(e))
                # raise InputError('error when write new activity item')
        else:
            raise ValidateError('user not logged')

class imageUpload(APIView):
    def post(self):
        if self.request.user.is_authenticated():
            self.check_input('image')
            ori_content=base64.b64decode(self.input['image'])
            cur_path=os.getcwd()
            tgt_path=cur_path+'/static/images'
            if not os.path.exists(tgt_path):
                try:
                    os.makedirs(tgt_path)
                    image_path=tgt_path+'/'+uuid.uuid1()+'.png'
                    img_file=open(image_path, 'w')
                    img_file.write(ori_content)
                    img_file.close()
                    total_url=get_url(image_path)
                    return total_url
                except:
                    raise ValidateError('save image error')
        else:
            raise ValidateError('user not logged')

class activityDetail(APIView):
    def get(self):
        if not self.request.user.is_authenticated():
            # print("detail offline!")
            raise LogicError('Your are offline!')

        self.check_input('id')
        try:
            res = Activity.get_by_id(self.input['id'])
        except:
            raise LogicError("get activity by id")
        ret = {}
        ret['name'] = res.name
        ret['key'] = res.key
        ret['description'] = res.description
        ret['startTime'] = res.start_time
        ret['endTime'] = res.end_time
        ret['place'] = res.place
        ret['bookStart'] = res.book_start
        ret['bookEnd'] = res.book_end
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
        if not self.request.user.is_authenticated():
            raise LogicError('Your are offline!')

        self.check_input('id', 'name', 'place', 'description',
                         'picUrl', 'startTime', 'endTime', 'bookStart',
                         'bookEnd', 'totalTickets', 'status')
        try:
            res = Activity.get_by_id(self.input['id'])
        except:
            raise LogicError("get activity by id error!")

        if res.status != Activity.STATUS_PUBLISHED:
            if res.name != self.input['name']:
                raise LogicError('can\'t  modify name')
            if res.place != self.input['place']:
                raise LogicError('can\'t  modify place')
            if res.book_start != self.input['bookStart']:
                raise LogicError('can\'t  modify book_start')
            if res.status != self.input['status'] and self.input['status'] == 0:
                raise LogicError('can\'t  modify status')

        curTime = getCurrentTime()
        if curTime > res.start_time:
            if res.book_end != self.input['bookEnd']:
                raise LogicError('can\'t  modify book_end')

        if curTime > res.end_time:
            if res.start_time != self.input['startTime']:
                raise LogicError('can\'t  modify start_time')
            if res.end_time != self.input['endTime']:
                raise LogicError('can\'t  modify end_time')

        if curTime > res.totalTickets:
            if res.total_tickets != self.input['totalTickets']:
                raise LogicError('can\'t  modify total_tickets')

        res.name = self.input['name']
        res.place = self.input['place']
        res.description = self.input['description']
        res.pic_url = self.input['picUrl']
        res.start_time = self.input['startTime']
        res.end_time = self.input['endTime']
        res.book_start = self.input['bookStart']
        res.book_end = self.input['bookEnd']
        res.total_tickets = self.input['totalTickets']
        res.status = self.input['status']
        res.save()
        return


class activityCheckin(APIView):
    def post(self):
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
        if not self.request.user.is_authenticated():
            raise LogicError('Your are offline!')

        self.check_input('id')
        try:
            CustomWeChatView.update_menu(self.input['id'])
        except:
            raise LogicError('add Menu failed!')
        return

