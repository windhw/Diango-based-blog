# Create your views here.
#!/usr/bin/env python
# -*- coding: utf-8 -*-
from google.appengine.ext import db
from google.appengine.api import users
from django.template import Context, loader
from blog.models import Article
from blog.models import Comment
from blog.models import Tag
from blog.views import gen_archive_list
from django.http import HttpResponse, HttpResponseRedirect
from google.appengine.api import mail
import datetime
import time
import cgi
from datetime import tzinfo, timedelta



def index(request):
    query = db.GqlQuery("SELECT * FROM Article ORDER BY id DESC")
    pop_article = query.get()
    latest_articles = query.fetch(9,1)
    query2= db.GqlQuery("SELECT * FROM Comment ORDER BY comment_id DESC")
    latest_comments = query2.fetch(5)
    
    archive_list = gen_archive_list()

    user = users.get_current_user()
    is_admin=users.is_current_user_admin()
       
    t = loader.get_template('index.html')
    c = Context({
        'pop_article': pop_article,
        'latest_articles': latest_articles,
        'latest_comments': latest_comments,
        'archive_list': archive_list,
        'user' : user, 'user' : user , 'is_admin' : is_admin,
    })
    return HttpResponse(t.render(c))