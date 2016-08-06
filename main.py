from flask import Flask, render_template, request, redirect, flash, session
from mysqlconnection import MySQLConnector
import os
import re
import hashlib
import binascii
import datetime

# key features: sha256 encryption for password with randomly generated salt, full SQL queries written,
# utilizes session and regex

app = Flask(__name__)
mysql = MySQLConnector(app, 'the_wall')
app.secret_key = 'hushhush'
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9\.\+_-]+@[a-zA-Z0-9\._-]+\.[a-zA-Z]*$')
PASS_REGEX = re.compile(r'^[A-Z0-9]')
NAME_REGEX = re.compile(r'[0-9]')


@app.route('/')
def load_index():
	if 'id' not in session:
		return render_template('index.html')
	return redirect ('/wall')

@app.route('/login', methods=['POST'])
def handle_login():
	data = {'email':request.form['email']}
	user = mysql.query_db("SELECT * FROM users WHERE email=:email",data)
	isvalid = True
	if EMAIL_REGEX.match(data['email']) == None:
		flash('Email formatted incorrectly. Please try again.')
		isvalid = False
	elif len(user) == 0:
		flash('The email address that you entered is not in our database.')
		isvalid = False
	elif hashlib.sha256(user[0]['pw_salt'] + request.form['password']).hexdigest() != user[0]['password']:
		flash('The password you entered is not correct.')
		isvalid = False
	else:
		isvalid = True
	if isvalid == True:
		session['id'] = user[0]['id']
		session['first_name'] = user[0]['first_name']
		return redirect('/wall')
	else:
		print 'login failed'
		return render_template('index.html',type='login')

@app.route('/register', methods=['POST'])
def handle_register():
	data = {'email':request.form['email']}
	user = mysql.query_db("SELECT * FROM users WHERE email=:email",data)
	if len(user) == 1:
		flash('The email address you entered is already registered in our system.')
		isvalid = False
	elif len(request.form['first_name']) < 2 or len(request.form['last_name']) < 2:
		flash('Names must be longer than one character.')
		isvalid = False
	elif len(request.form['password']) < 8:
		flash('Passwords must be at least 8 characters in length.')
		isvalid = False
	elif request.form['password'] != request.form['confirm-password']:
		flash('Passwords do not match.')
		isvalid = False
	else:
		verif_query = "SELECT * FROM users WHERE email=:email"
		verif_data = {"email":request.form['email']}
		verify = mysql.query_db(verif_query, verif_data)
		if len(verify) > 0:
			flash('The email you entered is already in our system.  Please use a different email address.')
			return render_template('index.html', type='register')
		salt = binascii.hexlify(os.urandom(16))
		password = hashlib.sha256(salt + request.form['password']).hexdigest()
		data = {
			"first_name":request.form['first_name'],
			"last_name":request.form['last_name'],
			'email':request.form['email'],
			'password':password,
			'pw_salt':salt
		}
		query = "INSERT INTO users (id, first_name, last_name, email, password, pw_salt, created_at, updated_at) VALUES (DEFAULT,:first_name, :last_name, :email, :password, :pw_salt, NOW(), NOW())"
		id = mysql.query_db(query,data)
		isvalid = True
		
	if isvalid == True:
		session['user_id'] = id
		session['first_name'] = data['first_name']
		return redirect('/wall/')
	return render_template('index.html')

@app.route('/wall/')
def load_wall():
	data = {
		'id':session['id'],
	}
	wall_posts = mysql.query_db('SELECT messages.id AS "m.id", messages.message AS "m.message", messages.message_title AS "m.title" , messages.created_at AS "m.created_at", messages.created_at AS "m.date", users.id AS "u.id", users.first_name AS "u.first", users.last_name AS "u.last", comments.message AS "comment", comments.user_id AS "commenter" FROM messages LEFT JOIN users ON messages.user_id=users.id LEFT JOIN comments ON messages.id=comments.message_id ORDER BY messages.created_at DESC', data)
	users = mysql.query_db('SELECT * FROM users')
	if len(wall_posts) != 0:
		m_id = wall_posts[0]['m.id']
		length = len(wall_posts)
		for post in wall_posts:
			for user in users:
				if user['id'] == post['commenter']:
					post['commenter'] = user['first_name']
			date = post['m.date']
			date = date.strftime('%B %d, %Y')
			post['m.date'] = date

	return render_template('wall.html', posts=wall_posts, len=length)

@app.route('/logoff')
def logoff():
	session['id'] = ''
	session['first_name'] = ''
	return render_template('index.html')

@app.route('/post', methods=['POST'])
def postMessage():
	data = {
	'id':session['id'],
	'post':request.form['post'],
	'title':request.form['title']
	}
	mysql.query_db("INSERT INTO messages (id, user_id, message, created_at, updated_at, message_title) VALUES (DEFAULT, :id, :post, NOW(), NOW(), :title)", data)
	return redirect('/wall')

@app.route('/comment', methods=['POST'])
def postComment():
	data = {
	'id':session['id'],
	'comment':request.form['comment'],
	'message_id':request.form['message_id']
	}
	print data
	mysql.query_db("INSERT INTO comments (id, user_id, message_id, message, created_at, updated_at) VALUES (DEFAULT, :id,:message_id, :comment, NOW(), NOW())", data)
	return redirect('/wall')

@app.route('/delete/<id>')
def delete(id):
	data = {
	'id':id
	}
	mysql.query_db('DELETE FROM messages WHERE id=:id', data)
	return redirect('/wall')

app.run(debug=True)

