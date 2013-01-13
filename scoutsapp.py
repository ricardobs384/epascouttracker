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

from google.appengine.ext import db
from google.appengine.api import users

RANKS = ["TenderFoot", "Second Class" , "First Class", "Star", "Life", "Eagle"]

class Scout (db.Model):
  name = db.StringProperty()
  start_date = db.DateProperty()
  def get_url(self):
    url = "/scout?id="+str(self.key())
    return url
  
class Rank (db.Model):
  name = db.StringProperty()
  signature = db.StringProperty()
  date = db.DateProperty()
  scout = db.ReferenceProperty(Scout)

class MainPage(webapp2.RequestHandler):
  def get(self):
    self.response.out.write("<a href='/add'>Click to add a scout</a>")
    self.response.out.write("<br>")
    self.response.out.write("These are the scouts in the troop so far.")
    self.response.out.write("<br>")

    scouts =  db.GqlQuery("SELECT * FROM Scout").run()

    for scout in scouts:
      self.response.out.write("<a href='" + scout.get_url() + "'>" + scout.name + "</a>" ) 
      self.response.out.write("<br>")



class ScoutForm(webapp2.RequestHandler):
  def get(self):
    self.response.out.write("""
<form method='post'>
  <div>Scout Name</div>
  <input type='text' name='scout_name'/>
  <div>Start Date (mm/dd/yy)</div>
  <input type='text' name='date_started'/>
  <button type='submit'>Add Scout</button>
</form>
""")
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
  def get(self):
    scout = Scout.get(self.request.get("id"))
    self.response.out.write(scout.name + " joined on " + str(scout.start_date)) 
    
    self.response.out.write("""
<form method='post' action='/delete'>
<input type='hidden' name='scout_key' value='""" + str(scout.key()) + """'/>
<button type='submit'>Delete</button>
</form>""")

    self.response.out.write("""
<form method='post' action='/rank'>
<input type='hidden' name='scout_key' value='""" + str(scout.key()) + """'/>
<div>Rank</div><select name='rank_name'>""")
    for rank in RANKS:
      self.response.out.write("<option value='"+rank+"'>"+rank+"</option>")
    self.response.out.write("""</select>
<div>Date Earned(mm/dd/yy)</div>
<input type='text' name='date_earned'/>
<div>Signature</div>
<input type='text' name='signature'/>
<button type='submit'>Create Rank</button>
</form>""")

    for rank in scout.rank_set.run():
      self.response.out.write(rank.name)
      self.response.out.write("<br>")

class DeletePage (webapp2.RequestHandler):
  def post(self):
    k = self.request.get("scout_key")
    scout =  Scout.get(k)
    scout.delete()
    self.redirect("/")

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
  ('/delete',DeletePage),
  ('/rank',AddRank)
], debug=True)
