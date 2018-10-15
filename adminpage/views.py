from django.shortcuts import render
from codex.baseview import APIView

from wechat.models import User, Activity, Ticket
from codex.baseerror import *
import datetime
# Create your views here.

class Login(APIView):
    def get(self):
        pass
    def post(self):
        pass
