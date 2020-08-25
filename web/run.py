# utf-8

from flask import Flask, render_template, session, request, url_for, redirect
import sqlite3
import pandas as pd
import sqlalchemy
import os
import random


app = Flask(__name__)
app.secret_key = 'T\x08;C\xb6A)\xcdE\xa2>\xacW\xa3\x8d\xb8\xe1\xb4\xc4i d\x15\xf8'
DATABASE = '../sqlite/wfxu.db'
ENGINE = sqlalchemy.create_engine('sqlite:///../sqlite/wfxu.db')


@app.route('/')
def index():
    image_list = [int(im.split('.')[0]) for im in os.listdir(r'static/image')]
    sql = """
        select item_id as id, b.movie_title as title
        from tb_data a
            left join tb_item b on a.item_id = b.movie_id
        where rating = 5
        group by item_id having (count(1) >= 100)
    """
    data = pd.read_sql(sql, ENGINE)
    data = data[data['id'].isin(image_list)].sample(10)
    movies1 = {}
    movies2 = {}
    for i in data.index:
        id_, title = data.loc[i, :]
        if len(movies1) <= 4:
            movies1[id_] = title
        else:
            movies2[id_] = title
    return render_template('index.html', movies1=movies1, movies2=movies2)


@app.route('/movie/', methods=['GET', 'POST'])
def movie():
    # 1.如果没有用户登录则按照电影类别进行召回然后随机选取10个
    # 2.如果有用户登录则按照找回表随机抽取10个
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
