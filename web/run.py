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
    if 'user' in session:
        movies_age, movies_gender = getMovies(session['user'])
    else:
        movies_age, movies_gender = getMovies(random.randint(1, 943))
    return render_template('movie.html', movies_age=movies_age, movies_gender=movies_gender)


def getMoviesRecall(num):
    sql1 = """
        select user_id, rating
        from tb_data a
        where item_id = {num}
    """
    sql2 = """
        select a.user_id, a.item_id, b.movie_title, a.rating
        from tb_data a
            left join tb_item b on a.item_id = b.movie_id
        where a.item_id <> {num}
    """
    data1 = pd.read_sql(sql1.format(num=num), ENGINE)
    data2 = pd.read_sql(sql2.format(num=num), ENGINE)
    data1 = data1[data1.rating == data1.rating.max()]
    data2 = pd.merge(data1, data2, how='inner', on='user_id', suffixes=('_', ''))
    data2 = data2[(data2.rating == data2.rating.max()) & data2.item_id.isin(image_list)]
    if data2.shape[0] <= 5:
        data3 = data2.copy()
    else:
        data3 = data2.sample(5).copy()
    movies = {}
    for i in data3.index:
        movies[data3.loc[i, 'item_id']] = data3.loc[i, 'movie_title']
    return movies


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
    movies = getMoviesRecall(num)
    return render_template('movie_detail.html', detail=detail, movies=movies)


def getUserMovies(recall):
    movie_list = recall.split(',')
    movie_list = [im for im in movie_list if int(im) in image_list]
    random.shuffle(movie_list)
    sql = "select movie_title as title from tb_item where movie_id = {m}"
    movies = {}
    for m in movie_list[:5]:
        title = pd.read_sql(sql.format(m=m), ENGINE).title[0]
        movies[m] = title
    return movies


@app.route('/user/', methods=['GET', 'POST'])
def user():
    sql1 = """
        select a.age, a.gender, a.occupation, a.zip_code, b.recall
        from tb_user a
            left join user_recall b on a.user_id = b.user_id
        where a.user_id = {user}
    """
    sql2 = """
        select * 
        from tb_data a
            left join tb_item b on a.item_id = b.movie_id
        where user_id = {user} 
        order by rating desc
    """
    if 'user' in session:
        user = session['user']
        data = pd.read_sql(sql1.format(user=user), ENGINE)
        age, gender, occupation, zip_code, recall = data.loc[0, ['age', 'gender', 'occupation', 'zip_code', 'recall']]
        data1 = pd.read_sql(sql2.format(user=user), ENGINE)
        cnt = data1.shape[0]
        love_movies = {}
        licensed = data1[(data1.rating == data1.rating.max()) & data1.item_id.isin(image_list)].shape[0]
        if licensed >= 5:
            for i in data1[(data1.rating == data1.rating.max()) & data1.item_id.isin(image_list)].sample(5).index:
                love_movies[data1.loc[i, 'item_id']] = data1.loc[i, 'movie_title']
        else:
            for i in data1[(data1.rating == data1.rating.max()) & data1.item_id.isin(image_list)].sample(licensed).index:
                love_movies[data1.loc[i, 'item_id']] = data1.loc[i, 'movie_title']
        classification = ['Action', 'Adventure', 'Animation', 'Children', 
                           'Comedy', 'Crime', 'Documentary', 'Drama', 'Fantasy', 'Film-Noir', 
                           'Horror', 'Musical', 'Mystery', 'Romance', 'Sci-Fi', 'Thriller', 
                           'War', 'Western']
        love_label_dict = {}
        for col in classification:
            love_label_dict[col] = data1.loc[data1.rating >= 3, col].sum()
        love_label = sorted(love_label_dict.items(), key = lambda x: x[1], reverse=True)
        love_label = '；'.join([col[0] for col in love_label[:5]])
        users = {'user':user, 'age':age, 'gender':gender, 'occupation':occupation, 
                 'zip_code':zip_code, 'cnt':cnt, 'love_label':love_label}
        movies = getUserMovies(recall)
        return render_template('user.html', users=users, love_movies=love_movies, movies=movies)
    else:
        return redirect(url_for('login'))


@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form['user']
        try:
            int(user)
        except ValueError:
            return render_template('login.html', prompt="输入用户不合法！</br>您可以输入1-943的任意数字")
        result = pd.read_sql("select 1 from tb_user where user_id = {user}".format(user=user), ENGINE)
        if result.shape[0] == 0:
            return render_template('login.html', prompt="用户不存在，请重新登录！</br>您可以输入1-943的任意数字")
        else:
            session['user'] = user
            return redirect(url_for('user'))
    else:
        return render_template('login.html', prompt="请登录！</br>您可以输入1-943的任意数字")


@app.route('/logout/')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=80, debug=True)
