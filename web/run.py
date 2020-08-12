from flask import Flask, render_template, session, request, url_for, redirect
import sqlite3


app = Flask(__name__)
app.secret_key = 'T\x08;C\xb6A)\xcdE\xa2>\xacW\xa3\x8d\xb8\xe1\xb4\xc4i d\x15\xf8'
DATABASE = '../sqlite/wfxu.db'


@app.route('/')
def index():
	return render_template('index.html')


@app.route('/movie/', methods=['GET', 'POST'])
def movie():
	return render_template('movie.html')


@app.route('/user/', methods=['GET', 'POST'])
def user():
	if 'user' in session:
		return render_template('user.html', user=session['user'])
	else:
		return redirect(url_for('login'))


@app.route('/login/', methods=['GET', 'POST'])
def login():
	if request.method == 'POST':
		user = request.form['user']
		session['user'] = user
		db = connectDB().cursor()
		result = db.execute("select 1 from users where name=?", (user,))
		r = result.fetchall()
		db.close()
		if len(r) == 0:
			return render_template('login.html', prompt="用户不存在，请重新登录！")
		else:
			return redirect(url_for('user'))
	else:
		return render_template('login.html', prompt="用户未登录，请登录！")


@app.route('/logout/')
def logout():
	session.pop('user', None)
	return render_template('login.html', prompt="已注销，请登录其他账号！")


def connectDB():
	return sqlite3.connect(DATABASE)


if __name__ == '__main__':
	app.run(host='127.0.0.1', port=80, debug=True)
