import os
import stat
import datetime, time
import pycurl
import json
from StringIO import StringIO

class Ipamodule():
    def epoch(self):
        now=datetime.datetime.now()
        return int(time.mktime(now.timetuple()))


    def mtime(self,filepath):
        try:
                return int(os.stat(filepath).st_mtime)
        except:
                return 0


    def check_cookiejar(self,COOKIEJAR,MAX_FILEAGE,IPAHOSTNAME,IPACERT,LOGINDATA):
	print "CHECKING COOKIEJAR"
	print  str(self.epoch()) + " "+   str(self.mtime(COOKIEJAR)) + " " + str(MAX_FILEAGE)
	if (self.mtime(COOKIEJAR) + MAX_FILEAGE) < self.epoch():
		try:
			os.remove(COOKIEJAR)
		except:
			pass
		print "Creating CookieJar"
		curl = pycurl.Curl()
	
		curl.setopt(pycurl.HTTPHEADER, ['referer:https://'+IPAHOSTNAME+'/ipa',
			'Content-Type:application/x-www-form-urlencoded',
        		'Accept:text/plain'])
		curl.setopt(pycurl.CAINFO, IPACERT)
		curl.setopt(pycurl.SSL_VERIFYPEER, 1)
		curl.setopt(pycurl.SSL_VERIFYHOST, 2)

		curl.setopt(pycurl.COOKIEJAR, COOKIEJAR)
		curl.setopt(pycurl.COOKIEFILE, COOKIEJAR)
		curl.setopt(pycurl.URL, "https://"+IPAHOSTNAME+"/ipa/session/login_password")
		curl.setopt(pycurl.POSTFIELDS, LOGINDATA)
		curl.perform()
		curl.close()


    def resolve_email_address(self,username,COOKIEJAR,IPAHOSTNAME,IPACERT):
	QUERYDATA=json.dumps({"method":"user_find","params":[[username],{}],"id":0})
    	storage=StringIO()
	curl = pycurl.Curl()
	curl.setopt(pycurl.HTTPHEADER, ['referer:https://'+IPAHOSTNAME+'/ipa',
			'Content-Type:application/json',
        		'Accept:applicaton/json'])
	
	curl.setopt(pycurl.CAINFO, IPACERT)
	curl.setopt(pycurl.SSL_VERIFYPEER, 1)
	curl.setopt(pycurl.SSL_VERIFYHOST, 2)
	
	curl.setopt(pycurl.COOKIEJAR, COOKIEJAR)
	curl.setopt(pycurl.COOKIEFILE, COOKIEJAR)
	curl.setopt(pycurl.URL, "https://"+IPAHOSTNAME+"/ipa/session/json")
	curl.setopt(pycurl.POST, 1)
	
	curl.setopt(pycurl.POSTFIELDS, QUERYDATA)
	
	curl.setopt(pycurl.WRITEFUNCTION, storage.write)
	curl.perform()
	content = storage.getvalue()
	curl.close()
	print content
	email_address=json.loads(content)['result']['result'][0]['mail']
	return email_address

    def reset_password(self,username,password,COOKIEJAR,IPAHOSTNAME,IPACERT):
    	storage=StringIO()
	RESETDATA=json.dumps({"method":"passwd","params":[[username],{"password":password}]})

	curl = pycurl.Curl()
	curl.setopt(pycurl.HTTPHEADER, ['referer:https://'+IPAHOSTNAME+'/ipa',
		'Content-Type:application/json',
        	'Accept:applicaton/json'])

	curl.setopt(pycurl.CAINFO, IPACERT)
	curl.setopt(pycurl.SSL_VERIFYPEER, 1)
	curl.setopt(pycurl.SSL_VERIFYHOST, 2)

	curl.setopt(pycurl.COOKIEJAR, COOKIEJAR)
	curl.setopt(pycurl.COOKIEFILE, COOKIEJAR)
	curl.setopt(pycurl.URL, "https://"+IPAHOSTNAME+"/ipa/session/json")
	curl.setopt(pycurl.POST, 1)

	curl.setopt(pycurl.POSTFIELDS, RESETDATA)

	curl.setopt(pycurl.WRITEFUNCTION, storage.write)
	curl.perform()
	content = storage.getvalue()
	curl.close()
	return content

