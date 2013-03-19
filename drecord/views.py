#-*- coding: utf-8 -*-

import os
import time

from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, render, redirect
from django.utils import simplejson as json
from django.contrib.auth.decorators import permission_required
from django.core.paginator import Paginator
from django.utils.decorators import method_decorator
from django.core.servers.basehttp import FileWrapper
from django.contrib.contenttypes.models import ContentType

from django.template import RequestContext
from django.db import transaction
from django.core.context_processors import csrf
from django.utils import timezone
from django.contrib.auth.models import User

from models import Record


def home(request):
	records = Record.list()
	total_times = int(0)
	for x in records:
		total_times += x['times']
	summary = {'user_num':User.objects.all().count,
	'total_times':total_times}
	context = {'records':records,'summary':summary,}
	return render_to_response('index_list.html', context,context_instance=RequestContext(request))

def record_user(request,user):
	user = User.objects.get(id=user)
	summary = Record.summary_by_user(user)
	records = Record.list_by_user(user)

	context = {'records':records,
		'summary':summary,}
	
	return render_to_response('user.html', context,context_instance=RequestContext(request))


def record_user_road(request,user,road):
	user = User.objects.get(id=user)
	records = Record.objects.filter(user=user,road=road)
	summary = Record.summary_by_user_road(user,road)
	context = {'user':user,
		'records':records,
		'summary':summary,}
	return render_to_response('record-user-road.html', context,context_instance=RequestContext(request))

