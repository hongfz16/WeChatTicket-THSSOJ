from django.shortcuts import render
from django.http import HttpResponse
from adminpage.models import *
from codex.baseview import APIView
from codex.baseerror import *
from wechat.models import Activity
from datetime import datetime

# Create your views here.

def getCurrentTime():
    return int( datetime(datetime.now()).timestamp() )

class loginPage(APIView):

    def get(self):
        return HttpResponse("F**K")

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
            re['id'] = act['id']
            re['name'] = act['name']
            re['description'] = act['description']
            re['startTime'] = act['start_time']
            re['endTime'] = act['end_time']
            re['place'] = act['place']
            re['bookStart'] = act['book_start']
            re['bookEnd'] = act['book_end']
            re['currentTime'] = getCurrentTime()
            if act['status'] == Activity.STATUS_PUBLISHED:
                re['status'] = 1
            else: re['status'] = 0
            ret.append(re)

        return ret
        # return HttpResponse("F**K")

class activityDelete(APIView):
    def post(self):
        if self.request.auth.is_authenticated():
            raise LogicError('Your are offline!')

        self.check_input('id')
        Activity.remove_by_id(self.input['id'])

        return BaseError(0, '')


class activityCreate(APIView):
    def post(self):
        pass

class imageUpload(APIView):
    def post(self):
        pass

class activityDetail(APIView):
    def get(self):
        pass

    def post(self):
        pass

class activityCheckin(APIView):
    def post(self):
        pass

class activityMenu(APIView):
    def get(self):
        pass

    def post(self):
        pass

