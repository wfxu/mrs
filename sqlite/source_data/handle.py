# utf-8
'''
将文件处理至数据库中
'''
import os
import pandas as pd
import sqlalchemy


ENGINE = sqlalchemy.create_engine('sqlite:///../wfxu.db')


def load_item():
    columns = ['movie id', 'movie title', 'release date', 'video release date', 
               'IMDb URL', 'unknown', 'Action', 'Adventure', 'Animation', 'Children', 
               'Comedy', 'Crime', 'Documentary', 'Drama', 'Fantasy', 'Film-Noir', 
               'Horror', 'Musical', 'Mystery', 'Romance', 'Sci-Fi', 'Thriller', 
               'War', 'Western']
    data = pd.read_csv('u.item', sep='|', engine='python', header=None, names=columns)
    data.to_sql('tb_item', ENGINE, if_exists='append', index=False, chunksize=100)