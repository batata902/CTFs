from flask import Flask, jsonify, request, make_response, redirect, url_for
from functools import wraps
from contextlib import contextmanager
import sqlite3
import hashlib
import uuid
import random

app = Flask(__name__)
app.json.sort_keys = False

schema: str = '''
CREATE TABLE IF NOT EXISTS users(
	id INTEGER PRIMARY KEY,
	username TEXT NOT NULL UNIQUE,
	password TEXT NOT NULL,
	cc TEXT UNIQUE,
	token TEXT
);
'''

numbers = '01234567890123456789'
users = [
	("admin", "admin123", "".join(random.sample(numbers, 16))),
	("alice", "alice123", "5555555555554444"),
	("bob", "bob123", None),
	("charlie", "charlie123", "4000000000000002"),
	("david", "david123", None),
	("eve", "eve123", "378282246310005"),
	("frank", "frank123", "6011111111111117"),
	("grace", "grace123", None),
	("heidi", "heidi123", "3530111333300000"),
	("ivan", "ivan123", None),
	("judy", "judy123", "3566002020360505"),
	("mallory", "mallory123", None),
	("oscar", "oscar123", "5105105105105100"),
	("peggy", "peggy123", None),
	("trent", "trent123", "4012888888881881"),
	("victor", "victor123", None),
	("walter", "walter123", "4222222222222"),
	("sybil", "sybil123", None),
	("olivia", "olivia123", "5555555555554444"),
	("zoe", "zoe123", None),
	("nathan", "nathan123", "4532015112830366"),
	("laura", "laura123", None),
	("bruno", "bruno123", "2223000048400011"),
	("camila", "camila123", None),
	("felipe", "felipe123", "5555555555554444"),
	("isabela", "isabela123", "4111111111111111"),
	("lucas", "lucas123", None),
	("marina", "marina123", "5200828282828210"),
	("rafael", "rafael123", None),
	("beatriz", "beatriz123", "340000000000009"),
]

@contextmanager
def db():
	conn = sqlite3.connect('apidb.db')
	cur = conn.cursor()

	try:
		yield conn, cur
	finally:
		conn.close()


def populate():
	with db() as (conn, _):
		for username, password, cc in users:
			password = hashlib.sha256(password.encode()).hexdigest()
			conn.execute('INSERT OR IGNORE INTO users(username, password, cc) VALUES(?, ?, ?)', (username, password, cc))
			conn.commit()

def login_required(f):
	@wraps(f)
	def wrapper(*args, **kwargs):
		token = request.cookies.get("token")
		with db() as (_, cur):
			query = cur.execute('SELECT id FROM users WHERE token=?;', (token,)).fetchone()
			if query:
				return f(*args, **kwargs)
		return jsonify({'error': 'forbidden'}), 403
	return wrapper


def is_logged(token: str) -> tuple[bool, str | None]:
	with db() as (_, cur):
		query = cur.execute('SELECT username FROM users WHERE token=?;', (token,)).fetchone()
		return (query != None, query[0] if query else None)


@app.route('/')
def home():
	return '''<!DOCTYPE html>
<html lang="pt-BR">
<head>
	<meta charset="UTF-8">
	<meta name="viewport" content="width=device-width, initial-scale=1.0">
	<title>PotAPI</title>
</head>
<body>
	<h1>PotAPI - v5.0.1</h1>
	<p>Use essas credenciais na rota /login -> bob:bob123</p>
	<p>Ao fazer login você será redirecionado para /users/{seu id} para visualizar seus dados</p>
	<button id="loginBtn" style="padding: 10px 20px; font-size: 16px; cursor: pointer;">
		Entrar como Bob
	</button>

	<script>
	document.getElementById('loginBtn').addEventListener('click', function() {
		fetch('/login', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify({
				'username': 'bob',
				'password': 'bob123'
			})
		})
		.then(response => response.json())
		.then(data => {
			if (data.status === 'success') {
				window.location.href = `/users/${data.user_id}`;
			} else {
				alert('Erro no login: ' + data.status);
			}
		})
		.catch(error => {
			console.error('Erro:', error);
			alert('Erro ao processar a requisição.');
		});
	});
	</script>
</body>
</html>
'''

@app.route('/login', methods=['GET', 'POST'])
def login():
	if request.method == 'GET':
		token = request.cookies.get('token')
		is_l = is_logged(token)
		if not is_l[0]:
			return jsonify({'status': 'not logged in'})
		return jsonify({'status': f'welcome {is_l[1]}'})
	else:
		data = request.get_json() # {'username': ..., 'password': ...}

		with db() as (conn, cur):
			try:
				user = cur.execute('SELECT id FROM users WHERE username=? AND password=?;', (data['username'], hashlib.sha256(data['password'].encode()).hexdigest())).fetchone()
			except KeyError:
				return jsonify({'error': 'invalid json'})
			if not user:
				return jsonify({'status': 'wrong username or password'})

			new_token = str(uuid.uuid4())

			cur.execute('UPDATE users SET token=? WHERE username=?;', (new_token, data['username']))
			conn.commit()

			response = make_response(jsonify({'status': 'success', 'user_id': user[0]}))
			response.set_cookie(key='token', value=new_token, httponly=True)

			return response


@app.route('/users/<int:user_id>')
@login_required
def user(user_id: int):
	with db() as (_, cur):
		query = cur.execute('SELECT * FROM users WHERE id=?;', (user_id,))
		user = query.fetchone()

		if not user:
			return jsonify({'error': 'not found'}), 404
		return jsonify({'id':user[0], 'username':user[1], 'password':user[2], 'cc':user[3]})



if __name__ == '__main__':
	conn = sqlite3.connect('apidb.db')
	conn.executescript(schema)
	populate()

	conn.close()

	app.run()
