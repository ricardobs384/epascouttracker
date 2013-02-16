#!/usr/bin/env python
# 
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import cgi
import datetime
import webapp2
import logging
import os
from google.appengine.ext.webapp import template

from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.ext import blobstore
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers


RANKS = ["Tender Foot", "Second Class" , "First Class", "Star", "Life", "Eagle"]

def admin_only(function):
  def auth_func(self):
    if users.is_current_user_admin():
      return function(self)
    else:
      self.redirect(users.create_login_url(self.request.url))

  return auth_func 


def authenticated(function):
  def auth_func(self):
    user = users.get_current_user()
    if user:
      return function(self)
    else:
      self.redirect(users.create_login_url(self.request.url))

  return auth_func 


class Scout (db.Model):
  name = db.StringProperty()
  start_date = db.DateProperty()
  picture = blobstore.BlobReferenceProperty()
  def get_url(self):
    url = "/scout?id="+str(self.key())
    return url
  def image_url(self):
    url ="/scout_image?id="+str(self.key())
    return url

class Rank (db.Model):
  name = db.StringProperty()
  signature = db.StringProperty()
  date = db.DateProperty()
  scout = db.ReferenceProperty(Scout)

class MainPage(webapp2.RequestHandler):
  @authenticated
  def get(self):
    scouts =  db.GqlQuery("SELECT * FROM Scout").run()
    user = users.get_current_user()
    path = os.path.join(os.path.dirname(__file__),'mainpage.html')
    self.response.out.write(template.render(path,{
            'logout_url':users.create_logout_url("/"),
            'user':user,
            'scouts':scouts
            }))
    


class ScoutForm(webapp2.RequestHandler):
  def get(self):
    path = os.path.join(os.path.dirname(__file__),'addscoutpage.html')
    self.response.out.write(template.render(path,{}))
   
  @admin_only
  def post(self):
    name = self.request.get("scout_name")
    date = self.request.get("date_started")
    logging.info("name: " +name + " date: " + date)
    scout = Scout()
    scout.name = name
    scout.start_date = datetime.datetime.strptime(date,'%x').date()
    scout.put()
    self.redirect("/")
   
class ScoutPage (webapp2.RequestHandler):
  @authenticated
  def get(self):
    scout = Scout.get(self.request.get("id"))
    upload_url = blobstore.create_upload_url('/upload')
    path = os.path.join(os.path.dirname(__file__),'scoutpage.html')
    self.response.out.write(template.render(path,{
      'scout':scout,
      'all_ranks':RANKS,
      'upload_url':upload_url}))

class ImageUploadHandler (blobstore_handlers.BlobstoreUploadHandler):
  def post(self):
    uploads = self.get_uploads('file')
    scout = Scout.get(self.request.get("scout_key"))
    if uploads:
      image = uploads [0]
      scout.picture = image
      scout.put()
    self.redirect(scout.get_url())
    

class ServiceImageHandler (blobstore_handlers.BlobstoreDownloadHandler):
  def get(self):
    key = self.request.get("id")
    scout = Scout.get(key)
    self.send_blob(scout.picture)
    

class ScoutDeletePage (webapp2.RequestHandler):
  def post(self):
    k = self.request.get("scout_key")
    scout =  Scout.get(k)
    scout.delete()
    self.redirect("/")

class RankDeletePage (webapp2.RequestHandler):
  def post(self):
    k = self.request.get("rank_key")
    rank = Rank.get(k)
    rank.delete()
    self.redirect(rank.scout.get_url())

class AddRank (webapp2.RequestHandler):
  def post(self):
    #first create a rank 
    rank = Rank() 
    rank.name = self.request.get("rank_name")
    rank.date = datetime.datetime.strptime(self.request.get("date_earned"),'%x').date()
    rank.signature = self.request.get("signature") 
    rank.scout = Scout.get(self.request.get("scout_key"))
    rank.put()
    self.redirect(rank.scout.get_url())
                        
logging.getLogger().setLevel(logging.DEBUG)
app = webapp2.WSGIApplication([
  ('/', MainPage),
  ('/add', ScoutForm),
  ('/scout',ScoutPage),
  ('/delete_scout',ScoutDeletePage),
  ('/rank',AddRank),
  ('/delete_rank',RankDeletePage),
  ('/upload',ImageUploadHandler),
  ('/scout_image',ServiceImageHandler)

], debug=True)
