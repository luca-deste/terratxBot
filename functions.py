import sqlite3
from sqlite3 import Error
#___________________________
#creates a row whit the user chad id (that will be used as index to find the user when needed)
def createUser(conn,chatid): #USED
	cur=conn.cursor()
	sql='INSERT INTO users(chatid) VALUES(?)'
	cur.execute(sql,(chatid,))
	conn.commit()
#___________________________
#check if the user already exist inside the database
def checkUserExistence(conn,chatid): #USED
	cur=conn.cursor()
	check = cur.execute('SELECT chatid FROM users WHERE chatid=?',(chatid,)).fetchone()
	print(check)
	if check:
		print('Table exists')
		return True
	else:
		print('Table doesn\'t exist')
		return False
#___________________________
#add an address to the database based on the chat id
def addAddrToDatabase(conn,database): #USED
    sql = 'UPDATE users Set addr=? WHERE chatid=?'
    cur = conn.cursor()
    cur.execute(sql,database)
    conn.commit()
#___________________________
#remove an address from the database based on the chat id
def rmAddrFromDatabase(conn, database): #USED
	print('hi')
	sql = 'DELETE FROM users WHERE chatid=?'
	cur = conn.cursor()
	cur.execute(sql,database)
	conn.commit()
#___________________________
#add date to the database
#this helps the bot to track the latest transactions
def addDateToDatabase(conn,database): #USED
	sql = 'UPDATE users Set date=? WHERE chatid=?'
	cur = conn.cursor()
	cur.execute(sql,database)
	conn.commit()
#___________________________
#connects to the database
def createConnection(database): #USED
	conn = None
	try:
		conn = sqlite3.connect(database,check_same_thread=False)
	except Error as e:
		print(e)
	return conn
#___________________________
#creates the sql table if it doesn't exist
def createTableSql(conn,createUserTable): #USED
	cur = conn.cursor()
	cur.execute(createUserTable)
	conn.commit()
#___________________________
#return the address that correspons to a chat id
def returnAddress(conn,chatid): #USED
	cur = conn.cursor()
	sql='select addr from users where chatid=?'
	cur.execute(sql,(chatid,))
	rows = cur.fetchone()[0]
	return rows
#___________________________
#returns all the chat id's inside the users table
#used to iterate trough the users
def returnAllChatIds(conn): #USED
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
#___________________________
#returns the timestamp based on the chat id
def returnDateFromId(conn,chatid): #USED
	cur = conn.cursor()
	sql='select date from users where chatid=?'
	cur.execute(sql,(chatid,))
	rows = cur.fetchone()[0]
	return rows
#___________________________
