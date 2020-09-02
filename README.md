---
author:
- 徐文汾
date: '2018-08-28'
title: 电影推荐系统说明文档
---

\maketitle
\pagenumbering{gobble}
\newpage
\pagenumbering{arabic}
概览
====

系统架构
--------

![系统架构](image/系统架构.png){width="\linewidth"}

对movielens数据进行FM模型训练，使用梯度下降优化算法，损失函数为RMSE，训练后的结果保存至数据库中。用户访问页面时，从数据库中获取FM模型和规则的多路召回结果，然后再排序取TOP10推荐并展示给用户。

项目结构
--------

![项目文档结构](image/项目结构.png){width="\linewidth"}

项目文档主要包含了三个部分：模型、数据和网页文件夹。**模型文件夹**中包含了模型训练的脚本和对样本数据进行统计的脚本。**数据文件夹**包含了sqlite3的安装文件（sqlite3.\*)、数据库文件（wfxu.db）、爬虫文件夹（crawler）、数据处理文件夹（source\_data)，其中爬虫文件夹中包含了爬虫脚本和爬虫获取的电影展示图片的网页链接，数据处理文件夹包含了movielens原始数据和数据处理脚本。**网页文件夹**主要包含了Flask框架的前端静态文件和后端脚本，其中static主要保存了爬虫获取的电影展示图片，templates中全都是前端页面，**run.py为服务启动脚本，运行该脚本即可启动网页服务，输入127.0.0.1:80即可访问电影推荐系统**。

\newpage
成果展示
========

项目地址在：https://github.com/wfxu/mrs，clone项目后可以本地直接运行run.py文件后在浏览器中输入127.0.0.1:80就可以使用电影推荐系统了。

数据
----

### 采集和处理的数据

\centering
![u.data](image/data.png){width="\linewidth"}

![u.user](image/user.png){width="\linewidth"}

![u.item](image/item.png){width="\linewidth"}

\centering
![tb\_data](image/tb_data.png){width="\linewidth"}

![tb\_user](image/tb_user.png){width="\linewidth"}

![tb\_item](image/tb_item.png){width="\linewidth"}

原始数据都是文件形式，每次读取都需要处理后才能使用，为方便使用所以处理后统一保存至数据库，这样也可以在数据库中进行一些特征的统计和观察。

![爬取的电影展示图片](image/movie_image.png){width="\linewidth"}

为了推荐系统页面的展示，所以从imdb获取了电影的展示图片，并且图片的名称与数据中的movie\_id是一一对应的，这样在页面展示的时候就可以直接使用movie\_id调用。

### 模型训练后的召回数据

\centering
![用户特征召回数据](image/features_recall.png){width="\linewidth"}

![用户召回数据](image/user_recall.png){width="\linewidth"}

使用FM模型的召回结果主要是保存用户或用户特征对应的movie\_id，这样在页面展示的时候直接查询取数就可以了。

模型
----

![模型训练过程](image/model.png){width="\linewidth"}

页面
----

![首页（热门电影）](image/index.png){width="\linewidth"}

![推荐电影](image/movie.png){width="\linewidth"}

![电影详情](image/movie_detail.png){width="\linewidth"}

![用户登录](image/login.png){width="\linewidth"}

![用户](image/html_user.png){width="\linewidth"}

\newpage
数据
====

数据的搜集
----------

#### 源数据

源数据来自于网上的movielens 数据
（[下载地址](http://files.grouplens.org/datasets/movielens/ml-100k/)）

#### 采集数据

使用Python的selenium模块建立爬虫，对[互联网电影资料库](https://www.imdb.com)网站查询、爬取各个电影对应的展示图片，用于前端页面的展示。

数据的处理
----------

首先将movielens的所有文件数据处理后保存到sqlite数据库中，然后训练的时候再从数据库中读取该数据，最后将模型训练后的结构保存至数据库中。这样处理的目的是将所有的数据包括基础数据、模型的训练数据、模型训练后的数据、召回结果、精排结果等数据都存储在数据库中，使用时也统一从数据库中查询调用，方便后端的调用和调优。

\newpage
模型
====

此次推荐系统采用的算法比较简单和单一，数据的训练和样本的召回使用功能的都是FM模型。

FM模型
------

$$y = f(w_0 + \sum\nolimits_{n}w_i x_i +\sum\nolimits_{n}\sum\nolimits_{n}<u_i, u_j>x_i x_j)$$
对用户id和电影id以及四个用户特征（性别、年龄、职业、区域）进行FM模型训练，使用梯度下降进行优化，得到隐特征矩阵。

召回
----

#### 基于用户特征的召回

根据FM模型训练得到的隐特征矩阵和上面（1）式计算四个用户特征隐特征向量对应的电影评分，排序后选取TOP10就得到该用户特征对应的召回结果。

#### 基于用户的召回

对用户四个特征的召回结果求并集，然后取TOP10就得到用户的召回结果。

#### 基于电影的召回

对于电影的召回并没有使用算法，而是采用规则进行过滤和选取。规则就是找到看过该电影并且评分高的用户，然后查询该用户看过且评分高的其它电影，就得到了该电影的召回结果。

\newpage
网页
====

使用Flask + HTML + CSS纯手工打造的推荐页面。

前端
----

前端仅仅使用了HTML和CSS两种技术，没有使用jquery和ajax等JS相关技术。
前端页面主要分为四个页面：热门电影、推荐电影、电影详情、用户

### 热门电影

该页面也是推荐系统的首页，筛选出大多数评价为高分的电影并随机抽取一部分展示为热门电影，没有针对用户进行特殊调整，属于大众化的推荐。

### 推荐电影

该页面分为两部分，一部分是针对用户登录后的电影推荐，一部分是针对未登录用户的电影推荐。

#### 针对已登录用户

获取该用户的年龄和性别特征的召回结果，然后随机抽取其中5个电影进行展示。

#### 针对未登录用户

随机获取一位用户的年龄和性别特征的召回结果，然后随机抽取其中5个电影进行展示。

### 电影详情

该页面展示了电影的详细信息，包括电影名称、上映时间、电影类别、历史观影人数、平均评分、最高评分和最低评分，并且还获取了该电影的召回结果，随机抽取其中5个电影展示，用于电影推荐。

### 用户

用户未登录时会转至用户登录页面，用户登录后会展示用户的详细信息，包括用户ID、性别、年龄、职业、邮政编码、喜欢观看的电影类型、观看电影的统计、评分最高的5部电影。而且还获取了改用户的召回结果，随机抽取其中5个电影进行推荐展示。

后端
----

后端使用Python的Flask框架，一个页面对应一个视图函数，另外还有用户登录、用户注销、用户召回结果获取和电影召回结果获取函数，默认地址为127.0.0.1，端口号80。

\newpage
总结
====

待完善的地方
------------

#### 数据

考虑到模型训练的复杂度和本次使用的模型较为简单所以只是使用了100000小批量的数据和4个用户特征，数据的样本量和特征的多样性还有待提高。

#### 模型

此次只采用了FM算法，没有使用其协同过滤等传统算法，也没有使用功能Deep
FM等深度模型。

#### 页面

纯手工打造的页面过于简单，这方面有很大提高的地方，比如的登录页面，用户页面、导航栏等

感谢
----

在这里感谢七月的各位老师和同学，老师们的谆谆教诲依旧在耳旁萦绕，无论是anch3or老师的详细严谨的推导过程还是seven老师"跟着我的节奏走"的自信都给我留下了深刻的学习印象，今后的学习也会以他们教授的方法为基础层层递进。还有同学们热烈的讨论，让我深切感受到了氛围的力量，你想不到的总会有人能想到。\
\
感谢各位老师的耐心讲解！\
感谢各位同学的陪伴！\
感谢这段时间的付出！\
且行且珍惜！学习的脚步不会停止！
