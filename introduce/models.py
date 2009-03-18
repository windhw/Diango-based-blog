from google.appengine.ext import db
import datetime 
class Article(db.Model): 
#
    id = db.StringProperty()
    title = db.StringProperty(multiline=True)
    author = db.StringProperty(multiline=True)
    content = db.TextProperty()
    tags = db.StringProperty(multiline=True)
    date = db.StringProperty(multiline=True)
    gmtdate = db.StringProperty(multiline=True)
    year = db.StringProperty(multiline=True)
    month = db.StringProperty(multiline=True)

class Comment(db.Model): 
#
    article_id = db.StringProperty()
    comment_id = db.StringProperty()
    title = db.StringProperty(multiline=True)
    author = db.StringProperty(multiline=True)
    content = db.StringProperty(multiline=True)
    date = db.StringProperty(multiline=True)

class Tag(db.Model): 
    article_id = db.StringProperty()
    tag = db.StringProperty()


