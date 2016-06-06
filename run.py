#!/usr/bin/python
import sys, os, random, re, datetime, time, stat, string, random
import pycurl,json
from flask import Flask, request, session, g,redirect, url_for, abort, render_template, flash,views, jsonify
from flask_restful import Resource, Api, reqparse
from flask_mail import Mail, Message
from StringIO import StringIO
from ipamodule import Ipamodule 
from sqlite3module import Sqlite3module

s_username='CHANGEME'
s_password='CHANGEME'
IPAHOSTNAME='perfelldap01.feltham.performgroup.com'
IPACERT="/etc/ipa/ca.crt"
COOKIEJAR='my.cookie.jar'
LOGINDATA="user="+s_username+"&password="+s_password
DATABASE = 'test.db'
MAX_DELAY=300
MAX_FILEAGE=300

app = Flask(__name__)
api = Api(app)
mail = Mail(app)


class Common():
    def verify_email_pattern(self,email_str):
	pattern=re.compile("[^@]+@[^@]+\.[^@]+")
	return pattern.match(email_str)

    def epoch(self):
	now=datetime.datetime.now()
	return int(time.mktime(now.timetuple()))

    def mtime(self,filepath):
	try:
		return int(os.stat(filepath).st_mtime)
	except:
		return 0

    def id_generator(self,size=8, chars=string.ascii_letters + string.digits):
	return ''.join(random.choice(chars) for _ in range(size))

    def send_token_by_mail(self,email,token):
	msg = Message(body="Hello, your token is: " + str(token),
                  sender="james.liu@performgroup.com",
                  recipients=[str(email)],
		  subject="Password Reset for IPA")
	mail.send(msg)


class Initialise(Resource):
    def get(self):
        conn = Sqlite3module()
	conn.initialise()


class Generate(Resource):
    def post(self):
        #json_data = request.get_json(force=True)

        #username = json_data['username']
	username=request.form['username']

	common = Common()
	ipamodule = Ipamodule()
	t = common.epoch()
	pw = common.id_generator()

    	ipamodule.check_cookiejar(COOKIEJAR,MAX_FILEAGE,IPAHOSTNAME,IPACERT,LOGINDATA)
	email=str(ipamodule.resolve_email_address(username,COOKIEJAR,IPAHOSTNAME,IPACERT)[0])
	
	if email:
        	conn = Sqlite3module()
		conn.register(t,username,pw)
		common.send_token_by_mail(email, pw)
	else:
		return "Didn't work"

        #return jsonify(u=email,p=pw)
	return redirect(url_for('redeem'))


class Validate(Resource):
    def post(self):
	common = Common()
	ipamodule = Ipamodule()
	t = common.epoch()
	conn = Sqlite3module()

        #json_data = request.get_json(force=True)
    	ipamodule.check_cookiejar(COOKIEJAR,MAX_FILEAGE,IPAHOSTNAME,IPACERT,LOGINDATA)

        #username = json_data['username']
        #code = json_data['code']
	username=request.form['username']
	code=request.form['code']

	created,recorded_token,completed=conn.match_against_last_registration(username)
	if created is None:
		return "Empty Response"
	elif ( code is None ):
		return "Please enter a code"
	elif ( code != recorded_token ):
		return "No valid entry found"
	elif (t - created ) > MAX_DELAY or completed != 0:
		return "too late"
	else:
		newpassword = common.id_generator()
		print "New Generated Password: " + newpassword
		newpassword = common.id_generator()
		result=ipamodule.reset_password(username, newpassword,COOKIEJAR,IPAHOSTNAME,IPACERT)
		if result is not None:
			conn = Sqlite3module()
			conn.lockout_token(username, code)
    			return render_template('form_complete.html',password=newpassword)
	conn.close()
	return "DEBUG: " + code + " " + str(CODE)  + " " + str(t)


@app.route('/register')
def register():
    return render_template('form_submit.html')

@app.route('/redeem')
def redeem():
	return render_template('form_validate.html')

@app.route('/dummy')
def dummy():
    return render_template('form_complete.html',password="newpassword")

api.add_resource(Validate, '/reset/v1.0/validate')
api.add_resource(Generate, '/reset/v1.0/generate')
api.add_resource(Initialise, '/reset/v1.0/initialise')

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')
