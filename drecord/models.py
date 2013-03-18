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


class Form(OrderedModel):
	"""form model"""
	
	title = models.CharField(u'问卷标题', max_length=80)
	deadline = models.DateField(u'过期时间')
	submit_datetime = models.DateTimeField(u'添加时间', auto_now_add=True)
	
	def __unicode__(self):
		return self.title
	
	class Meta:
		db_table = 'form'
		verbose_name = verbose_name_plural = u'问卷'
		ordering = ['-order']

class Ans(models.Model):
	"""ans model"""
	
	title = models.CharField(u'答案', max_length=80)
	#question = models.ManyToManyField(Question)
	
	def __unicode__(self):
		return self.title
	
	class Meta:
		db_table = 'ans'
		verbose_name = verbose_name_plural = u'答案'

class Question(models.Model):
	"""question model"""
	
	title = models.CharField(u'问题', max_length=80)
	form = models.ForeignKey(Form)
	ans = models.ManyToManyField(Ans)
	
	def __unicode__(self):
		return self.title
	
	class Meta:
		db_table = 'question'
		verbose_name = verbose_name_plural = u'问题'

class Submit(models.Model):
    """docstring for Submit"""
    
    form = models.ForeignKey(Form)
    user = models.ForeignKey(User)
    submit_datetime = models.DateTimeField(u'添加时间', auto_now_add=True)

    def __unicode__(self):
        return self.form.title+self.user.username
    
    class Meta:
        db_table = 'submit'
        verbose_name = verbose_name_plural = u'问卷提交'

class Subitem(models.Model):
    """Subitem model"""
    
    submit = models.ForeignKey(Submit)
    question = models.ForeignKey(Question)
    ans = models.ForeignKey(Ans)
    
    def __unicode__(self):
        return self.question.title+self.ans.title
    
    class Meta:
        db_table = 'subitem'
        verbose_name = verbose_name_plural = u'提交项'



