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
image_list = [int(im.split('.')[0]) for im in os.listdir(r'static/image')]


@app.route('/')
def index():
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


def getMovies(user):
    sql = """
        select 1000+age/5 as age, case when gender = 'M' then 1020 else 1021 end as gender
        from tb_user where user_id = {user}
    """
    data = pd.read_sql(sql.format(user=user), ENGINE)
    sql1 = "select recall from features_recall where features = {f}"
    sql2 = "select movie_title as title from tb_item where movie_id = {mi}"
    movies_age = {}
    movies_gender = {}
    age_recall = pd.read_sql(sql1.format(f=data.loc[0, 'age']), ENGINE).recall[0].split(',')
    age_recall = [im for im in age_recall if int(im) in image_list]
    random.shuffle(age_recall)
    for mi in age_recall[:5]:
        movies_age[mi] = pd.read_sql(sql2.format(mi=mi), ENGINE).title[0]
    gender_recall = pd.read_sql(sql1.format(f=data.loc[0, 'gender']), ENGINE).recall[0].split(',')
    gender_recall = [im for im in gender_recall if int(im) in image_list]
    random.shuffle(gender_recall)
    for mi in gender_recall[:5]:
        movies_gender[mi] = pd.read_sql(sql2.format(mi=mi), ENGINE).title[0]
    return movies_age, movies_gender


@app.route('/movie/', methods=['GET', 'POST'])
def movie():
    # 1.如果没有用户登录则按照电影类别进行召回然后随机选取10个
    # 2.如果有用户登录则按照找回表随机抽取10个
    if 'user' in session:
        movies_age, movies_gender = getMovies(session['user'])
    else:
        movies_age, movies_gender = getMovies(random.randint(1, 943))
    return render_template('movie.html', movies_age=movies_age, movies_gender=movies_gender)


@app.route('/movie/<int:num>', methods=['GET', 'POST'])
def movieDetail(num):
    sql = """
        select a.*, count(1) as cnt, round(avg(rating), 2) as avg_rating, 
            max(rating) as max_rating, min(rating) as min_rating
        from tb_item a
            inner join tb_data b on a.movie_id = b.item_id
        where movie_id = {num}
    """
    data = pd.read_sql(sql.format(num=num), ENGINE)
    use_col = ['movie_title', 'release_date', 'cnt', 'avg_rating', 'max_rating', 'min_rating']
    title, release_date, cnt, avg_rating, max_rating, min_rating = data.loc[0, use_col]
    label = []
    classification = ['Action', 'Adventure', 'Animation', 'Children', 
                       'Comedy', 'Crime', 'Documentary', 'Drama', 'Fantasy', 'Film-Noir', 
                       'Horror', 'Musical', 'Mystery', 'Romance', 'Sci-Fi', 'Thriller', 
                       'War', 'Western']
    for col in classification:
        if data.loc[0, col] == 1:
            label.append(col)
    detail = [num, title, release_date, '；'.join(label), cnt, avg_rating, max_rating, min_rating]
    movies = {'1':'one', '2':'two', '3':'three', '4':'four', '5':'five'}
    return render_template('movie_detail.html', detail=detail, movies=movies)


def getUserMovies(user):
    recall = pd.read_sql("select recall from user_recall where user_id = {user}".format(user=user), ENGINE).recall[0]
    movie_list = recall.split(',')
    sql = "select movie_tittle as title from tb_item where movie_id = {m}"
    movies = {}
    for m in movie_list:
        title = pd.read_sql(sql.format(m=m), ENGINE).title[0]
        movies[m] = title
    return movies


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
