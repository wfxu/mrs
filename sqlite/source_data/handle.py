# utf-8
'''
将文件处理至数据库中
'''
import os
import pandas as pd
import sqlalchemy


ENGINE = sqlalchemy.create_engine('sqlite:///../wfxu.db')


def load(columns, files, table_name, sep='/t', if_exists='append'):
    data = pd.read_csv(files, sep=sep, engine='python', header=None, names=columns)
    data.to_sql(table_name, ENGINE, if_exists=if_exists, index=False, chunksize=1000)


def main():
    # u.data
    data_col = ['user_id', 'item_id', 'rating', 'timestamp']
    load(data_col, 'u.data', 'tb_data')
    # u.item
    itme_col = ['movie_id', 'movie_title', 'release_date', 'video_release_date', 
               'IMDb_URL', 'unknown', 'Action', 'Adventure', 'Animation', 'Children', 
               'Comedy', 'Crime', 'Documentary', 'Drama', 'Fantasy', 'Film-Noir', 
               'Horror', 'Musical', 'Mystery', 'Romance', 'Sci-Fi', 'Thriller', 
               'War', 'Western']
    load(itme_col, 'u.item', 'tb_itme', sep='|')
    # u.user
    user_col = 'user_id', 'age', 'gender', 'occupation', 'zip_code'
    load(user_col, 'u.user', 'tb_user', sep='|')



