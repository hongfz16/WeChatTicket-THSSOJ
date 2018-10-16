from django.db import models

from codex.baseerror import LogicError


class User(models.Model):
    open_id = models.CharField(max_length=64, unique=True, db_index=True)
    student_id = models.CharField(max_length=32, unique=True, db_index=True, null=True, blank=True)

    @classmethod
    def get_by_openid(cls, openid):
        try:
            return cls.objects.get(open_id=openid)
        except cls.DoesNotExist:
            raise LogicError('User not found')


class Activity(models.Model):
    name = models.CharField(max_length=128)
    key = models.CharField(max_length=64, db_index=True)
    description = models.TextField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    place = models.CharField(max_length=256)
    book_start = models.DateTimeField(db_index=True)
    book_end = models.DateTimeField(db_index=True)
    total_tickets = models.IntegerField()
    status = models.IntegerField()
    pic_url = models.CharField(max_length=256)
    remain_tickets = models.IntegerField()

    STATUS_DELETED = -1
    STATUS_SAVED = 0
    STATUS_PUBLISHED = 1

    @classmethod
    def get_nonegtive_status(cls):
        try:
            return cls.objects.filter(status__gte=0)
        except:
            raise LogicError('get activity by status error!')

    @classmethod
    def get_status_published(cls):
        try:
            return cls.objects.filter(status=cls.STATUS_PUBLISHED)
        except:
            raise LogicError('get activity by status=1 error!')

    @classmethod
    def get_by_id(cls, id):
        try:
            # print("id=" + str(id))
            return cls.objects.get(id=id)
        except:
            raise LogicError('get activity by id error!')

    @classmethod
    def remove_by_id(cls, id):
        try:
            cls.objects.get(id=id).delete()
        except:
            raise LogicError('delete activity error!')



class Ticket(models.Model):
    student_id = models.CharField(max_length=32, db_index=True)
    unique_id = models.CharField(max_length=64, db_index=True, unique=True)
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
    status = models.IntegerField()

    STATUS_CANCELLED = 0
    STATUS_VALID = 1
    STATUS_USED = 2

    @classmethod
    def get_by_activity(cls, act):
        try:
            return cls.objects.filter(activity=act)
        except:
            raise LogicError('get ticket by activity error!')
