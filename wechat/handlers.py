# -*- coding: utf-8 -*-
#
from datetime import datetime
from django.utils import timezone
from wechat.wrapper import WeChatHandler
from wechat.models import *
from django.db import transaction
import uuid
from WeChatTicket import settings


class ErrorHandler(WeChatHandler):

    def check(self):
        return True

    def handle(self):
        return self.reply_text('对不起，服务器现在有点忙，暂时不能给您答复 T T')


class DefaultHandler(WeChatHandler):

    def check(self):
        return True

    def handle(self):
        return self.reply_text('对不起，没有找到您需要的信息:(')


class HelpOrSubscribeHandler(WeChatHandler):

    def check(self):
        return self.is_text('帮助', 'help') or self.is_event('scan', 'subscribe') or \
               self.is_event_click(self.view.event_keys['help'])

    def handle(self):
        return self.reply_single_news({
            'Title': self.get_message('help_title'),
            'Description': self.get_message('help_description'),
            'Url': self.url_help(),
        })


class UnbindOrUnsubscribeHandler(WeChatHandler):

    def check(self):
        return self.is_text('解绑') or self.is_event('unsubscribe')

    def handle(self):
        self.user.student_id = ''
        self.user.save()
        return self.reply_text(self.get_message('unbind_account'))


class BindAccountHandler(WeChatHandler):

    def check(self):
        return self.is_text('绑定') or self.is_event_click(self.view.event_keys['account_bind'])

    def handle(self):
        return self.reply_text(self.get_message('bind_account'))


class BookEmptyHandler(WeChatHandler):

    def check(self):
        return self.is_event_click(self.view.event_keys['book_empty'])

    def handle(self):
        return self.reply_text(self.get_message('book_empty'))


class BookTicketsHandler(WeChatHandler):

    def check(self):
        print("BookTicketsHandler check")
        for button in self.view.menu['button'][-1]['sub_button']:
            if self.is_event_click(button['key']):
                self.id = int(button['key'][len(self.view.event_keys['book_header']):])
                return True
        return False

    def handle(self):
        print("BookTicketsHandler handle")
        # print()
        if self.user.student_id is None:
            return self.reply_text("请先绑定学号！")
        student_id = int(self.user.student_id)

        with transaction.atomic():
            try:
                activity = Activity.objects.select_for_update().get(id=self.id,
                                                                    status=Activity.STATUS_PUBLISHED)
            except:
                return self.reply_text('未找到该活动!')

            if int(activity.book_start.timestamp()) > int(self.input['CreateTime']):
                return self.reply_text('抢票未开始!')
            if int(activity.book_end.timestamp()) < int(self.input['CreateTime']):
                return self.reply_text('抢票已结束!')

            ticket = Ticket.objects.filter(student_id=student_id,
                                           activity=activity)
            if len(ticket) > 0:
                return self.reply_text('你已经抢到票了，请不要重复抢票！')
            if activity.remain_tickets <= 0:
                return self.reply_text('抱歉，没票啦！')
            activity.remain_tickets -= 1
            activity.save()

        Ticket.objects.create(student_id=student_id,
                              unique_id=str(uuid.uuid1()),
                              activity=activity,
                              status=Ticket.STATUS_VALID)
        return self.reply_text('恭喜你！抢到《'+activity.name+'》的票啦~')


class CheckTicketHandler(WeChatHandler):
    def check(self):

        return self.is_event_click(self.view.event_keys['get_ticket']) or self.is_text('查票')

    def handle(self):
        print('check ticket')
        if self.user.student_id is None:
            return self.reply_text("请先绑定学号！")
        opn_id=self.user.open_id
        stu_id=self.user.student_id#User.objects.get(open_id=opn_id).student_id
        info_menu = []
        print(len(stu_id))
        if len(stu_id)==10:

            chosen_tickets=Ticket.objects.filter(student_id=stu_id)
            for ticket in chosen_tickets:
                print(ticket.unique_id)
                info_menu.append({'Title':ticket.activity.name,
                                  'Description':ticket.activity.description,
                                  'Url':self.url_ticket(opn_id, ticket.unique_id)})
        return self.reply_news(info_menu)

    def url_ticket(self, opn_id, unq_id):
        print("url_ticket")
        print(opn_id)
        print(unq_id)
        return settings.get_url('u/ticket', {'openid':opn_id, 'ticket':unq_id})


class BookWhatHandler(WeChatHandler):

    def check(self):
        return self.is_event_click(self.view.event_keys['book_what'])

    def handle(self):
        # return self.reply_text('click book what')
        dateNow = timezone.now()

        objs = Activity.objects.filter(
            book_end__gt = dateNow,
            status=Activity.STATUS_PUBLISHED
        ).order_by('start_time')
        arts = []
        for obj in objs:
            arts.append({
                'Title': obj.name,
                'Description': obj.description,
                'Url': self.url_activity(obj.id)
            })
        return self.reply_news(arts)

