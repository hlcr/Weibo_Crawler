import pymysql
from pymysql import IntegrityError

db_name="weibo"

# 把用户信息插入数据库中
def add_user(py):
    conn = pymysql.connect(host='127.0.0.1',  user='root', passwd='Ryan', db=db_name,charset='UTF8')
    cur = conn.cursor()
    sql="select id from {0}".format(py)
    print(sql)
    cur.execute(sql)
    id_list = []
    for ii in cur:
        id_list.append(ii[0])
    print(len(id_list))
    id_set = set(id_list)
    print(len(id_set))

    for id in id_set:
        sql=r"delete from data where id='{0}';".format(id)
        # print(sql)
        cur.execute(sql)
    cur.close()  # 关闭游标
    conn.commit()  # 向数据库中提交任何未解决的事务，对不支持事务的数据库不进行任何操作
    conn.close()  # 关闭到数据库的连接，释放数据库资源


Pyl=["jd","qz","gj","hp","mh","nl","wl","xh","xw"]
Pyl=["wl"]
for py in Pyl:
    add_user(py)