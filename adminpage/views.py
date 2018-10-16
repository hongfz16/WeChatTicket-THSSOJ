from django.shortcuts import render
from django.http import HttpResponse
from adminpage.models import *
from codex.baseview import APIView
from codex.baseerror import *
from wechat.models import Activity
from wechat.models import Ticket
from datetime import datetime
from wechat.views import CustomWeChatView

# Create your views here.


def getCurrentTime():
    return int( datetime.now().timestamp() )


def get_index(id, buttons):
    book_header = CustomWeChatView.event_keys['book_header']
    for i in range(len(buttons)):
        if buttons['key'] == book_header+str(id):
            return i+1
    return 0


class loginPage(APIView):

    def get(self):
        pass

    def post(self):
        pass

class logoutPage(APIView):
    def post(self):
        pass

class activityList(APIView):

    def get(self):
        if self.request.auth.is_authenticated():
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
            if act['status'] == Activity.STATUS_PUBLISHED:
                re['status'] = 1
            else: re['status'] = 0
            ret.append(re)

        return ret

class activityDelete(APIView):
    def post(self):
        if self.request.auth.is_authenticated():
            raise LogicError('Your are offline!')

        self.check_input('id')
        try:
            Activity.remove_by_id(self.input['id'])
        except:
            raise LogicError('delete activity error!')
        return


class activityCreate(APIView):
    def post(self):
        pass

class imageUpload(APIView):
    def post(self):
        pass

class activityDetail(APIView):
    def get(self):
        if self.request.auth.is_authenticated():
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
        if self.request.auth.is_authenticated():
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
        pass


class activityMenu(APIView):
    def get(self):
        if self.request.auth.is_authenticated():
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
        if self.request.auth.is_authenticated():
            raise LogicError('Your are offline!')

        self.check_input('id')
        try:
            CustomWeChatView.update_menu(self.input['id'])
        except:
            raise LogicError('add Menu failed!')
        return

