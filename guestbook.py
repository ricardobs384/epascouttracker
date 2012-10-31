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

from google.appengine.ext import db
from google.appengine.api import users

class Calculation(db.Model):
  firstNum = db.FloatProperty()
  secondNum = db.FloatProperty() 
  operation = db.StringProperty()
  result = db.FloatProperty()
  date = db.DateTimeProperty(auto_now_add=True)


class MainPage(webapp2.RequestHandler):
  def get(self):
    self.response.out.write('<html><body>')

    calculations = db.GqlQuery("SELECT * "
                            "FROM Calculation "
                            "ORDER BY date ASC LIMIT 10")

    for calc in calculations:
      self.response.out.write("<div>%s %s %s = %s</div>" % (calc.firstNum,calc.operation,
                                                            calc.secondNum,calc.result))

#        self.response.out.write('An anonymous person wrote:')
#      self.response.out.write('<blockquote>%s</blockquote>' %
#                              cgi.escape(greeting.content))
#

    self.response.out.write("""
          <form action="/add" method="post">
            <div><input name ="firstNum" type="text"/></div>
            <div><input name="secondNum" type="text"/></div>
            <div><input name="addButton" type="submit" value="Add Values"></div>
            <div><input name="subtractButton" type="submit" value="Subtract Values"></div>
          </form>
        </body>
      </html>""")


class Adder(webapp2.RequestHandler):
  def post(self):

    newCalc = Calculation()
    addButtonClicked = self.request.get('addButton')
    try:
      firstNum = float (self.request.get('firstNum'))
      secondNum = float (self.request.get('secondNum'))
    except ValueError:
      self.response.out.write('Please use only umbers!')
    newCalc.firstNum = firstNum
    newCalc.secondNum = secondNum
    if addButtonClicked:
      newCalc.operation = "+"
      newCalc.result = firstNum+secondNum
    else:
     
      newCalc.operation = "-"
      newCalc.result = firstNum-secondNum

    newCalc.put()
    self.redirect('/')
# Cool story bro.

app = webapp2.WSGIApplication([
  ('/', MainPage),
  ('/add', Adder)
], debug=True)
