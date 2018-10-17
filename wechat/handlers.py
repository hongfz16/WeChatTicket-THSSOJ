# -*- coding: utf-8 -*-
#
from wechat.wrapper import WeChatHandler
from wechat.models import User, Activity, Ticket
from WeChatTicket import settings
__author__ = "Epsirom"


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

class CheckTicketHandler(WeChatHandler):
    def check(self):
        return self.is_event_click(self.view.event_keys['get_ticket']) or self.is_text('查票')

    def handle(self):
        opn_id=self.user.open_id
        stu_id=User.objects.get(open_id=opn_id)
        if len(stu_id)!=10:
            chosen_tickets=Ticket.objects.filter(student_id=stu_id)
            info_menu=[]
            for ticket in chosen_tickets:
                info_menu.append({'Title':ticket.activity.name,
                                  'Description':ticket.activity.description,
                                  'Url':self.url_ticket(opn_id, ticket.unique_id)})
            return self.reply_news(info_menu)

    def url_ticket(self, opn_id, unq_id):
        return settings.get_url('u/ticket', {'openid':opn_id, 'ticket':unq_id})
