# Create your views here.
#!/usr/bin/env python
# -*- coding: utf-8 -*-
from google.appengine.ext import db
from google.appengine.api import users
from django.template import Context, loader
from blog.models import Article
from blog.models import Comment
from blog.models import Tag
from django.http import HttpResponse, HttpResponseRedirect
from google.appengine.api import mail
import datetime
import time
import cgi
from datetime import tzinfo, timedelta



def index(request):
    '''
    query = db.GqlQuery("SELECT * FROM Article ORDER BY id DESC")
    pop_article = query.get()
    latest_articles = query.fetch(9,1)
    query2= db.GqlQuery("SELECT * FROM Comment ORDER BY comment_id DESC")
    latest_comments = query2.fetch(5)
    
    archive_list = gen_archive_list()

    user = users.get_current_user()
    is_admin=users.is_current_user_admin()
    '''
       
    t = loader.get_template('survey/index.html')
    '''
    c = Context({
        'pop_article': pop_article,
        'latest_articles': latest_articles,
        'latest_comments': latest_comments,
        'archive_list': archive_list,
        'user' : user, 'user' : user , 'is_admin' : is_admin,
    })
    '''
    c = Context({})    
    return HttpResponse(t.render(c))

def feed(request):
    query = db.GqlQuery("SELECT * FROM Article ORDER BY id DESC")
    latest_articles = query.fetch(15)
    s = (datetime.datetime.now()+timedelta(hours=+8)).ctime()   
    pub_date = "%s, %s %s %s %s GMT" % (s[:3] ,s[8:10], s[4:7] ,s[-4:] ,s[11:19])
    t = loader.get_template('blog/rss.xml')
    c = Context({
        'latest_articles': latest_articles,
        'pub_date': pub_date,
    })
    res =  HttpResponse(t.render(c))
    res.headers['Content-Type'] = 'application/rss+xml; charset=utf-8'
    return res


def archive(request,archive_id):
    query= db.GqlQuery("SELECT * FROM Comment ORDER BY comment_id DESC")
    latest_comments = query.fetch(5)
    query = db.GqlQuery("SELECT * FROM Article ORDER BY id DESC")
    latest_articles = query.fetch(8)
    archive_list = gen_archive_list()

    query = db.GqlQuery("SELECT * FROM Article WHERE year = :1 and month = :2 ORDER BY id DESC",archive_id[:4],archive_id[-2:])
    archive_articles = query.fetch(40)
    
    user = users.get_current_user()
    is_admin=users.is_current_user_admin()
       
    t = loader.get_template('blog/archive.html')
    c = Context({
        'latest_articles': latest_articles,
        'latest_comments': latest_comments,
        'archive_list': archive_list,
        'archive_articles': archive_articles,
        'archive_id' : (archive_id[:4],archive_id[-2:]),
        'user' : user, 'user' : user , 'is_admin' : is_admin,
    })
    return HttpResponse(t.render(c))


def login(request):
    return HttpResponseRedirect(users.create_login_url(''))

def logout(request):
    return HttpResponseRedirect(users.create_logout_url(''))

def article(request, article_id):
    query = db.GqlQuery("SELECT * FROM Article ORDER BY id DESC")
    latest_articles = query.fetch(8)
    query= db.GqlQuery("SELECT * FROM Comment ORDER BY comment_id DESC")
    latest_comments = query.fetch(5)
    archive_list = gen_archive_list()
    ar = Article.all()
    ar.filter("id =", article_id)
    tags = []
    this_article = None
    for t in ar:
        this_article = t
        if this_article:
            tags = filter(None,this_article.tags.split(' '))
    co = Comment.all()
    co.filter("article_id =", article_id)
    co.order("comment_id")
    user = users.get_current_user()
    is_admin=users.is_current_user_admin()
    t = loader.get_template('blog/article.html')
    if this_article:
        c = Context({
            'article': this_article,
            'now_comments':co,
            'tags':tags,
            'latest_articles': latest_articles,
            'latest_comments': latest_comments,
            'archive_list' : archive_list,
            'user' : user , 'is_admin' : is_admin,
        })
        
        return HttpResponse(t.render(c))
    else:
        return HttpResponseRedirect("/")

def admin(request):
    t = loader.get_template('blog/admin.html')
    user = users.get_current_user()
    is_admin=users.is_current_user_admin()
    if is_admin:
        c = Context({
             'user' : user , 'user' : user , 'is_admin' : is_admin,
             })
        return HttpResponse(t.render(c))
    else:
        return HttpResponseRedirect("/")

def edit(request, article_id):
    user = users.get_current_user()
    is_admin=users.is_current_user_admin()        
    if is_admin:
        if request.POST.has_key('article_id'):
            query = db.GqlQuery("SELECT * FROM Article WHERE id = :1",
                                 cgi.escape(request.POST['article_id'].decode('utf-8')))
            article = query.get()
            query = db.GqlQuery("SELECT * FROM Tag WHERE article_id = :1",
                                 article.id)
            tags = query.fetch(20)
            for tag in tags:
                tag.delete()

            article.author = cgi.escape(request.POST['author'].decode('utf-8'))
            article.content = request.POST['content'].decode('utf-8')
            article.tags = request.POST['tags'].decode('utf-8')
            article.title = cgi.escape(request.POST['title'].decode('utf-8'))
            article.put()
            for tag_name in filter(None,(request.POST['tags'].decode('utf-8')).split(' ')):
                tag = Tag()
                tag.tag = tag_name
                tag.article_id = article.id
                tag.put()
            return HttpResponseRedirect("/blog/article/"+cgi.escape(request.POST['article_id'].decode('utf-8')))
        else:
            query = db.GqlQuery("SELECT * FROM Article WHERE id = :1",article_id)
            article = query.get()    
            t = loader.get_template('blog/edit.html')
            c = Context({
                 'user' : user , 'user' : user , 'is_admin' : is_admin,
                 'article':article
                 })
            return HttpResponse(t.render(c))
    else:
        return HttpResponseRedirect("/")

def delete(request, article_id):
    user = users.get_current_user()
    if users.is_current_user_admin() and article_id:
        query = db.GqlQuery("SELECT * FROM Article WHERE id = :1",article_id)
        article = query.get()
        article.delete()
        query2 = db.GqlQuery("SELECT * FROM Comment WHERE article_id = :1",article_id)
        comments = query2.fetch(500)
        for comment in comments:
            comment.delete()
        query = db.GqlQuery("SELECT * FROM Tag WHERE article_id = :1",article_id)
        tags = query.fetch(20)
        for tag in tags:
            tag.delete()
        return HttpResponseRedirect("/blog")
    return HttpResponseRedirect("/blog")

def post(request):

    now=time.localtime()
    article =Article()
    if request.POST.has_key('content'):
        article.author = cgi.escape(request.POST['author'].decode('utf-8'))
        article.content = request.POST['content'].decode('utf-8')
        article.tags = request.POST['tags'].decode('utf-8')
        article.title = cgi.escape(request.POST['title'].decode('utf-8'))
        now_date = datetime.datetime.now()+timedelta(hours=+8)        
        s = now_date.ctime()
        article.date = str(now_date)[:-7] 
        article.gmtdate = "%s, %s %s %s %s GMT" % (s[:3] ,s[8:10], s[4:7] ,s[-4:] ,s[11:19])
        article.year = str(datetime.datetime.now()+timedelta(hours=+8))[:4]
        article.month = str(datetime.datetime.now()+timedelta(hours=+8))[5:7]
        if not article.title:
            if len(article.content) > 11:
                article.title = article.content[:12] + '...'
            else:
                article.title=article.content

        article.id=time.strftime('%Y%m%d%H%M%S',now)
        if article.content:
            article.put()
            for tag_name in filter(None,article.tags.split(' ')):
                tag = Tag()
                tag.tag = tag_name
                tag.article_id = article.id
                tag.put()
    return HttpResponseRedirect("/blog/")

def comment(request):
    now=time.localtime()
    comment =Comment()
    if request.POST.has_key('content') and request.POST.has_key('article_id'):
        comment.author = cgi.escape(request.POST['author'].decode('utf-8'))
        comment.content = request.POST['content'].decode('utf-8')
        comment.title = cgi.escape(request.POST['title'].decode('utf-8'))
        comment.date = str(datetime.datetime.now()+timedelta(hours=+8))[:-7]
        comment.comment_id=time.strftime('%Y%m%d%H%M%S',now)
        comment.article_id = cgi.escape(request.POST['article_id'].decode('utf-8'))
        comment.put()
    return HttpResponseRedirect("/blog/article/"+comment.article_id+"#"+comment.comment_id)

def gen_archive_list():
    query = db.GqlQuery("SELECT * FROM Article ORDER BY id DESC")
    top_article = query.get()
    query = db.GqlQuery("SELECT * FROM Article ORDER BY id ASC")
    bot_article = query.get()
    if (not top_article):
        return []
    start = [int(bot_article.id[:4]),int(bot_article.id[4:6])]
    end = [int(top_article.id[:4]),int(top_article.id[4:6])]
    archive_list=[]
    while(start[0]<= end[0] and start[1]<=end[1]):
        archive_list.append([str(start[0]),str(start[1])])
        if (end[1] == 1):
            end[0] -= 1
            end[1] = 12
        else:
            end[1] -= 1
    return archive_list

def contact(request):       
    t = loader.get_template('contact.html')
    c = Context({})
    return HttpResponse(t.render(c))
def about(request):       
    t = loader.get_template('about.html')
    c = Context({})
    return HttpResponse(t.render(c))

def announce(request):       
    t = loader.get_template('announce.html')
    c = Context({})
    return HttpResponse(t.render(c))

def service(request):       
    t = loader.get_template('service.html')
    c = Context({})
    return HttpResponse(t.render(c))
    
def notexist(requestt):       
    t = loader.get_template('notexist.html')
    c = Context({})
    return HttpResponse(t.render(c))