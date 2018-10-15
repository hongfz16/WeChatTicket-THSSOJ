from django.shortcuts import render
from django.http import HttpResponse
from adminpage.models import *
from codex.baseview import APIView

# Create your views here.

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
        return HttpResponse("F**K")

class activityDelete(APIView):
    def post(self):
        pass

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

