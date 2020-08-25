-- 用户数量
select count(1) from tb_user;
-- 职业数量
select count(distinct occupation) from tb_user;
-- 区域数量
select count(distinct substr(zip_code, 1, 3)) from tb_user;

-- 电影数量
select count(1) from tb_item;

用户 943； 年龄 20；性别 2； 职业 21； 区域 382；
电影 1682； 标签 19；

1-943     用户id
1000-1019 用户年龄
1020-1021 用户性别
1030-1050 用户职业
1100-1481 用户区域

1000-1681 电影id
3000-3018 电影标签（19个标签）