import sqlite3 

DATABASE = 'test.db'

DEF_INSERT = '''INSERT INTO SUBMISSION (CREATED,EMAIL,CODE) VALUES(?,?,?)'''
DEF_CREATE = '''CREATE TABLE IF NOT EXISTS SUBMISSION
	(CREATED TIMESTAMP PRIMARY KEY NOT NULL,
	EMAIL   CHAR(50) NOT NULL,
	CODE 	CHAR(20) NOT NULL, 
	DONE 	BOOLEAN NOT NULL DEFAULT 0);'''
DEF_SELECT = '''SELECT * FROM SUBMISSION WHERE EMAIL=? 
	ORDER BY CREATED DESC LIMIT 1'''
DEF_LOCKOUT = """UPDATE SUBMISSION SET DONE=1 WHERE EMAIL=? AND CODE=?  """


class Sqlite3module():
    def initialise(self,db=DATABASE, command=DEF_CREATE):
	try:
        	conn = sqlite3.connect(db)
		RESULT=conn.execute(command)
		conn.close()
		conn.commit()
		return 1;
	except:
		conn.close()
		return -1


    def register(self,TIMESTAMP,USER,TOKEN,db=DATABASE,command=DEF_INSERT):
	try:
		conn = sqlite3.connect(db)
		conn.execute(command, (TIMESTAMP,USER,TOKEN))
		conn.commit()
		conn.close()
		return 1
	except:
		conn.close()
		return -1

    def match_against_last_registration(self,USER,db=DATABASE,command=DEF_SELECT):
	try:
		conn = sqlite3.connect(db)
		RESULT=conn.execute(command,(USER,))
		TOPRESULT=RESULT.fetchone()
		if TOPRESULT is not None:
			CREATED=TOPRESULT[0]
			CODE=TOPRESULT[2]
			DONE=TOPRESULT[3]
		conn.close()
		return CREATED,CODE,DONE
	except:
		print "EXCEPTION:"
		conn.close()
		return -1,-1,-1

    def lockout_token(self,username,code,db=DATABASE,command=DEF_LOCKOUT):
	try:
		conn = sqlite3.connect(db)
		conn.execute(command,(username, code))
		conn.commit()
		conn.close()
		return 1
	except:
		conn.rollback()
		return -1
