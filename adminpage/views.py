from django.shortcuts import render
from codex.baseview import APIView
from django.contrib import auth


from wechat.models import User, Activity, Ticket
from codex.baseerror import *
from WeChatTicket.settings import get_url
import datetime
import uuid
import base64
import os
# Create your views here.

class Login(APIView):
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

class Logout(APIView):
    def post(self):
        if self.request.user.is_authenticated():
            auth.logout(self.request)
        else:
            raise LogicError('logout error!')

class ActivityCreate(APIView):
    def post(self):
        if self.request.user.is_authenticated():
            self.check_input('name', 'key', 'place', 'description', 'picUrl', 'startTime',
                             'endTime', 'bookStart', 'bookEnd', 'totalTickets', 'status')
            try:
                new_activity=Activity.objects.create(name=self.input['name'], key=self.input['key'], place=self.input['place'],
                                        description=self.input['description'], pic_url=self.input['picUrl'],
                                        start_time=datetime.datetime.fromtimestamp(self.input['startTime']),
                                        end_time=datetime.datetime.fromtimestamp(self.input['endTime']),
                                        book_start=datetime.datetime.fromtimestamp(self.input['bookStart']),
                                        book_end=datetime.datetime.fromtimestamp(self.input['bookEnd']),
                                        total_tickets=self.input['totalTickets'],
                                        remain_tickets=self.input['totalTickets'],
                                        status=self.input['status'])
                return new_activity.id
            except:
                raise InputError('error when write new activity item')
        else:
            raise ValidateError('user not logged')

class ImageUpload(APIView):
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

class ActivityCheckin(APIView):
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
