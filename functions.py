import sqlite3
from sqlite3 import Error

#creates a row whit the user chad id (that will be used as index to find the user when needed)
def createUser(conn,chatid):
	cur=conn.cursor()
	sql='INSERT INTO users(chatid) VALUES(?)'
	cur.execute(sql,(chatid,))
	conn.commit()

def checkUserExistence(conn,chatid):
	cur=conn.cursor()
	check = cur.execute('SELECT chatid FROM users WHERE chatid=?',(chatid,)).fetchone()
	print(check)
	if check:
		print('Table exists')
		return True
	else:
		print('Table doesn\'t exist')
		return False



def createConnection(database):
	conn = None
	try:
		conn = sqlite3.connect(database,check_same_thread=False)
	except Error as e:
		print(e)
	return conn

def createTableSql(conn,createUserTable):
	cur = conn.cursor()
	cur.execute(createUserTable)
	conn.commit()