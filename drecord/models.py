# -*- coding: utf-8 -*-
from django.db import models

import datetime
import json

from django.db import models, connection
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse

class OrderedModel(models.Model):
    order = models.PositiveIntegerField(editable=False)

    def save(self):
        if not self.id:
            try:
                self.order = self.__class__.objects.all().order_by("-order")[0].order + 1
            except IndexError:
                self.order = 0
        super(OrderedModel, self).save()
        

    def order_link(self):
        model_type_id = ContentType.objects.get_for_model(self.__class__).id
        model_id = self.id
        kwargs = {"direction": "up", "model_type_id": model_type_id, "model_id": model_id}
        url_up = reverse("admin-move", kwargs=kwargs)
        kwargs["direction"] = "down"
        url_down = reverse("admin-move", kwargs=kwargs)
        return '<a href="%s">up</a> | <a href="%s">down</a>' % (url_up, url_down)
    order_link.allow_tags = True
    order_link.short_description = 'Move'
    order_link.admin_order_field = 'order'


    @staticmethod
    def move_down(model_type_id, model_id):
        try:
            ModelClass = ContentType.objects.get(id=model_type_id).model_class()

            lower_model = ModelClass.objects.get(id=model_id)
            higher_model = ModelClass.objects.filter(order__gt=lower_model.order)[0]
            
            lower_model.order, higher_model.order = higher_model.order, lower_model.order

            higher_model.save()
            lower_model.save()
        except IndexError:
            pass
        except ModelClass.DoesNotExist:
            pass
                
    @staticmethod
    def move_up(model_type_id, model_id):
        try:
            ModelClass = ContentType.objects.get(id=model_type_id).model_class()

            higher_model = ModelClass.objects.get(id=model_id)
            lower_model = list(ModelClass.objects.filter(order__lt=higher_model.order))[-1]

            lower_model.order, higher_model.order = higher_model.order, lower_model.order

            higher_model.save()
            lower_model.save()
        except IndexError:
            pass
        except ModelClass.DoesNotExist:
            pass

    class Meta:
        ordering = ["order"]
        abstract = True

class Record(models.Model):
    """docstring for Record"""
    
    user = models.ForeignKey(User)
    road = models.CharField(u'路段ID', max_length=80)
    start_time = models.DateTimeField(u'开始时间')
    end_time = models.DateTimeField(u'结束时间')
    submit_datetime = models.DateTimeField(u'添加时间', auto_now_add=True)

    def __unicode__(self):
        return self.user.username+self.road

    def delta(self):
        return int((self.end_time-self.start_time).total_seconds()/60)
    
    @staticmethod
    def summary_by_user_road(user,road):
        record = {}
        record['road'] = road
        total_time = int(0)
        _list = Record.objects.filter(user=user,road=road)
        record['times'] = _list.count()
        for item in _list:
            total_time += item.delta()
        record['total_time'] = total_time
        return record
    @staticmethod
    def list_by_user(user):
        _list = []
        _records = Record.objects.filter(user=user)
        s = set()
        for item in _records:
            if item.road not in s:
                _list.append(Record.summary_by_user_road(user,item.road))
                s.add(item.road)
        return _list
    @staticmethod
    def summary_by_user(user):
        result = {}
        result['user'] = user
        result['username'] = user.username
        records = Record.objects.filter(user=user)
        result['times'] = int(records.count())
        result['total_time'] = int(0)
        for item in records:
            result['total_time'] += item.delta()
        return result
    @staticmethod
    def list():
        _list = []
        users = User.objects.all()
        for user in users:
            _list.append(Record.summary_by_user(user))
        return _list

    class Meta:
        db_table = 'record'
        verbose_name = verbose_name_plural = u'行车记录'
        ordering = ['-submit_datetime']


