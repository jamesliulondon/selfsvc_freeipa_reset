# selfsvc_freeipa_reset

sudo yum install python python-pip supervisor
pip install --upgrade pip
pip install -r requirements.txt


in /etc/supervisord.conf, add:

[program:resetter]
command=/usr/bin/python /vagrant/selfsvc_freeipa_reset/run.py
directory=/vagrant/selfsvc_freeipa_reset
redirect_stderr=true
startsecs=5
autorestart=true
stdout_logfile=/tmp/log.log


in run.py, change:
[...]
s_username='CHANGEME'
s_password='CHANGEME'
IPAHOSTNAME='ldapserver.site.performgroup.com'
[...]

service supervisor restart
