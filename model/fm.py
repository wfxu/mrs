# utf-8

import pandas as pd
import numpy as np
import sqlalchemy
import time


ENGINE = sqlalchemy.create_engine('sqlite:///../sqlite/wfxu.db')
step = 0.001
reg_w = 0.001
reg_v = 0.001
K = 8
N = 4000
W0 = 0
W = np.random.randn(N)*0.1
V = np.random.standard_normal((N, K))*0.1


def now():
    return time.strftime("%Y-%m-%d %X", time.localtime())


def loadData():
    """
    0-999     用户id
    1000-1019 用户年龄
    1020-1021 用户性别
    1030-1050 用户职业
    1100-1481 用户区域
    1000-3000 电影id
    3000-3018 电影标签（19个标签）
    """
    sql = """
        select a.rating, a.user_id, a.item_id, b.age, b.gender, b.occupation, substr(b.zip_code, 1, 3) as zcode
        from tb_data a
            left join tb_user b on a.user_id = b.user_id
    """
    data = pd.read_sql(sql, ENGINE)
    data['age'] = pd.cut(data.age, range(0, 101, 5), labels=range(1000, 1020))
    data['gender'] = data.gender.map({'M':1020, 'F':1021})
    oc_list = data.occupation.drop_duplicates().sort_values().to_list()
    oc_dict = {o:1030+i for i, o in enumerate(oc_list)}
    data['occupation'] = data.occupation.map(oc_dict)
    zcode_list = data.zcode.drop_duplicates().sort_values().to_list()
    zcode_dict = {z:1100+i for i, z in enumerate(zcode_list)}
    data['zcode'] = data.zcode.map(zcode_dict)
    data['item_id'] = data.item_id.map(lambda x: x+1000)
    return data


def loadUser():
    sql = """
        select b.user_id,b.age, b.gender, b.occupation, substr(b.zip_code, 1, 3) as zcode
        from tb_user b
    """
    data = pd.read_sql(sql, ENGINE)
    data['age'] = pd.cut(data.age, range(0, 101, 5), labels=range(1000, 1020))
    data['gender'] = data.gender.map({'M':1020, 'F':1021})
    oc_list = data.occupation.drop_duplicates().sort_values().to_list()
    oc_dict = {o:1030+i for i, o in enumerate(oc_list)}
    data['occupation'] = data.occupation.map(oc_dict)
    zcode_list = data.zcode.drop_duplicates().sort_values().to_list()
    zcode_dict = {z:1100+i for i, z in enumerate(zcode_list)}
    data['zcode'] = data.zcode.map(zcode_dict)
    return data


def getRating(feat):
    r = W0
    for i in range(len(feat)-1):
        r += W[feat[i]]
        for j in range(i, len(feat)):
            r += sum(V[feat[i]]*V[feat[j]])
    return np.round(r, 6)


def predict(data)->pd.Series:
    pred = []
    for ind in data.index:
        feat = data.loc[ind,:].to_list()[1:]
        pred.append(getRating(feat))
    return pred


def train(data):
# loss = 1/2*(p-r)^2 + 1/2*reg_w*sum(W[i]^2) + 1/2*reg_v*sum(<V[i],V[i]>)
# d0 = p - r
# dW0 = d0
# dWi = d0 + reg_w * W[i]
# dVi = d0 * sum_{j!=i}V[j] + reg_v * V[i]
    global W0
    for ind in data.index:
        feat = data.iloc[ind,:].to_list()
        r = feat.pop(0)
        pred = getRating(feat)
        d0 = pred-r
        W0 -= d0*step
        sum_Vj = 0
        for f in feat:
            dWi = d0 + reg_w*W[f]
            W[f] -= dWi*step
            sum_Vj += V[f]
        for f in feat:
            dVi = d0*(sum_Vj-V[f]) + reg_v*V[f]
            V[f] -= dVi*step


def rmse(data, pred):
    return np.round(np.sqrt(np.sum(np.square(data.rating - pred))/data.shape[0]), 6)


def optimization(data, iters=10):
    for i in range(iters):
        train(train_data)
        train_pred = predict(train_data)
        test_pred = predict(test_data)
        train_rmse = rmse(train_data, train_pred)
        test_rmse = rmse(test_data, test_pred)
        print(now(), i, train_rmse, test_rmse)


def getUFR(data):
    # get user features recall
    user_features = pd.concat((data.age.drop_duplicates(), data.gender.drop_duplicates(),
                              data.occupation.drop_duplicates(), 
                              data.zcode.drop_duplicates())).to_list()
    user_features.sort()
    features_recall = {}
    for f in user_features:
        f_rating = {}
        for i in range(1000, 1681):
            feat = [f, i]
            f_rating[i] = getRating(feat)
        f_rating_sort = sorted(f_rating.items(), key=lambda x: x[1], reverse=True)
        top_10 = [tp[0] for tp in f_rating_sort[:10]]
        features_recall[f] = set(top_10)
    return features_recall


def getUR(features_recall):
    # get user reacall
    users = loadUser()
    user_recall = {}
    for i in users.index:
        user_id, age, gender, occupation, zcode = users.loc[i, :]
        user_recall[user_id] = set.union(features_recall[age], features_recall[gender],
                                         features_recall[occupation], features_recall[zcode])
    return user_recall


if __name__ == '__main__':
    data = loadData()
    train_data = data[:80000].copy()
    test_data = data[80000:].copy()
    optimization(data, iters=20)
    features_recall = getUFR(data)
    user_recall = getUR(features_recall)
    df_user_recall = pd.DataFrame({'user_id':list(user_recall.keys()),
                                   'recall':list(user_recall.values())})
    df_user_recall['recall'] = df_user_recall.recall.map(
            lambda x: ','.join([str(r) for r in x]))
    df_user_recall.to_sql('user_recall', ENGINE, index=False, if_exists='replace')