from codex.baseview import APIView

from wechat.models import User, Activity, Ticket
from codex.baseerror import *
import datetime
from django.utils import timezone


class UserBind(APIView):

    def validate_user(self):
        """
        input: self.input['student_id'] and self.input['password']
        raise: ValidateError when validating failed
        """
        if len(self.input['student_id']) != 10:
            raise ValidateError('Invialidated student id!')
        # raise NotImplementedError('You should implement UserBind.validate_user method')

    def get(self):
        self.check_input('openid')
        # print(self.input['openid'])
        return User.get_by_openid(self.input['openid']).student_id

    def post(self):
        print("UserBind post")
        self.check_input('openid', 'student_id', 'password')
        user = User.get_by_openid(self.input['openid'])
        self.validate_user()
        user.student_id = self.input['student_id']
        user.save()

class ActivityDetail(APIView):
    def get(self):
        try:
            target_activity=Activity.objects.get(id=self.input['id'])
            try:
                if target_activity.status==1:
                    activity_detail={}
                    activity_detail['name']=target_activity.name
                    activity_detail['key']=target_activity.key
                    activity_detail['description']=target_activity.description
                    activity_detail['startTime']=int(target_activity.start_time.timestamp())
                    activity_detail['endTime'] = int(target_activity.end_time.timestamp())
                    activity_detail['place'] = target_activity.place
                    activity_detail['bookStart'] = int(target_activity.book_start.timestamp())
                    activity_detail['bookEnd'] = int(target_activity.book_end.timestamp())
                    activity_detail['totalTickets']=target_activity.total_tickets
                    activity_detail['picUrl'] = target_activity.pic_url
                    activity_detail['remainTickets'] = target_activity.remain_tickets
                    activity_detail['currentTime'] = int(timezone.now().timestamp())
                    return activity_detail
                else:
                    raise BaseError(code=4, msg='activity not published')
            except:
                raise ValidateError('cannot get activity status')
        except:
            raise ValidateError('cannot get activity via id')

class TicketDetail(APIView):
    def get(self):
        self.check_input('openid', 'ticket')
        try:
            opn_id=self.input['openid']
            unq_id=self.input['ticket']
            ticket_detail={}
            if not isinstance(unq_id, str):
                raise InputError('wrong input type')
            try:
                ticket = Ticket.objects.get(unique_id=unq_id)
                activity = Activity.get_by_id(ticket.activity_id)
                std_id = User.objects.get(open_id=opn_id).student_id
                # if self.input['openid']=='':
                #     print('why this works ', User.objects.get(open_id=opn_id))

                # if ticket.student_id == std_id:
                #     ticket_detail['activityName'] = ticket.activity.name
                #     ticket_detail['place'] = ticket.activity.place
                #     ticket_detail['activityKey'] = ticket.activity.key
                #     ticket_detail['uniqueId'] =ticket.unique_id
                #     ticket_detail['startTime'] = int(ticket.activity.start_time.timestamp())
                #     ticket_detail['endTime'] = int(ticket.activity.end_time.timestamp())
                #     ticket_detail['currentTime'] = int(timezone.now().timestamp())
                #     ticket_detail['status'] = ticket.status
                #     return ticket_detail
                # else:
                #     raise BaseError(code=4, msg='not match')
                if ticket.student_id == std_id:
                    ticket_detail['activityName'] = activity.name
                    ticket_detail['place'] = activity.place
                    ticket_detail['activityKey'] = activity.key
                    ticket_detail['uniqueId'] =ticket.unique_id
                    ticket_detail['startTime'] = int(activity.start_time.timestamp())
                    ticket_detail['endTime'] = int(activity.end_time.timestamp())
                    ticket_detail['currentTime'] = int(timezone.now().timestamp())
                    ticket_detail['status'] = ticket.status
                    return ticket_detail
                else:
                    raise BaseError(code=4, msg='not match')
            except:
                raise ValidateError('not valid ticket')
        except:
            raise InputError('input message error')
