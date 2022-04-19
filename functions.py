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

def addAddrToDatabase(conn,database):
    sql = 'UPDATE users Set addr=? WHERE chatid=?'
    cur = conn.cursor()
    cur.execute(sql,database)
    conn.commit()

def rmAddrFromDatabase(conn, database):
	print('hi')
	sql = 'DELETE FROM users WHERE chatid=?'
	cur = conn.cursor()
	cur.execute(sql,database)
	conn.commit()

def addDateToDatabase(conn,database):
	sql = 'UPDATE users Set date=? WHERE chatid=?'
	cur = conn.cursor()
	cur.execute(sql,database)
	conn.commit()

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

def returnChatId(conn,addr):
    cur = conn.cursor()
    sql='select chatid from users where addr=?'
    cur.execute(sql)
    rows = cur.fetchone()[0]
    return rows

def returnAddress(conn,chatid):
	cur = conn.cursor()
	sql='select addr from users where chatid=?'
	cur.execute(sql,(chatid,))
	rows = cur.fetchone()[0]
	return rows

def returnAllChatIds(conn):
	cur = conn.cursor()
	arra = []
	sql ='select chatid from users'
	cur.execute(sql)
	rows = cur.fetchall()
	print(rows)
	return rows
	'''for row in rows:
		arra.append(row[0])
		print(arra)
		return arra'''

def returnDateFromId(conn,chatid):
	cur = conn.cursor()
	sql='select date from users where chatid=?'
	cur.execute(sql,(chatid,))
	rows = cur.fetchone()[0]
	return rows

def returnAddresses(conn):
    cur = conn.cursor()
    arra = []
    sql ='select addr from users'
    cur.execute(sql)
    rows = cur.fetchall()
    for row in rows:
        arra.append(row[0])
    return arra