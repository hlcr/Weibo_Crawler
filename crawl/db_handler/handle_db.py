import pymysql
from pymysql import IntegrityError
import random

db_name="weibo"

# 把用户信息插入数据库中
def add_user(user_list):
    conn = pymysql.connect(host='127.0.0.1',  user='root', passwd='Ryan', db=db_name,charset='UTF8')
    cur = conn.cursor()
    for user,pwd in user_list:
        try:
            sql_str = "insert into weibo_user (user,password) values ('{0}','{1}');".format(user, pwd)
            cur.execute(sql_str)
        except IntegrityError:
            pass
    cur.close()                                    #关闭游标
    conn.commit()                                  #向数据库中提交任何未解决的事务，对不支持事务的数据库不进行任何操作
    conn.close()                                   #关闭到数据库的连接，释放数据库资源

# 取出用户信息
def get_user_list(num=None):
    user_list = []
    conn = pymysql.connect(host='127.0.0.1',  user='root', passwd='Ryan', db=db_name,charset='UTF8')
    cur = conn.cursor()
    if num:
        sql_str = "select user,password from weibo_user  where status='0' limit 0,{0};".format(num)
    else:
        sql_str = "select user,password from weibo_user  where status='0';"
    cur.execute(sql_str)
    for ii in cur:
        user_list.append((ii[0], ii[1]))

    for item in user_list:
        sql_str = "update weibo_user set status=1 where user='{0}';".format(item[0])
        cur.execute(sql_str)

    cur.close()                                    #关闭游标
    conn.commit()                                  #向数据库中提交任何未解决的事务，对不支持事务的数据库不进行任何操作
    conn.close()                                   #关闭到数据库的连接，释放数据库资源
    return user_list


# 把用户信息插入数据库中
def add_url(url_list):
    conn = pymysql.connect(host='127.0.0.1',  user='root', passwd='Ryan', db=db_name,charset='UTF8')
    cur = conn.cursor()
    for url in url_list:
        sql_str = "insert into url_record (url) values ('{0}');".format(url)
        cur.execute(sql_str)
    cur.close()                                    #关闭游标
    conn.commit()                                  #向数据库中提交任何未解决的事务，对不支持事务的数据库不进行任何操作
    conn.close()                                   #关闭到数据库的连接，释放数据库资源

def update_url():
    with open("./config/new_url.txt","r") as f:
        url_list = f.readlines()
    conn = pymysql.connect(host='127.0.0.1',  user='root', passwd='Ryan', db=db_name,charset='UTF8')
    cur = conn.cursor()
    for url in url_list:
        sql_str = "update url_record set num=0 where url='{0}';".format(url.strip())
        # print(sql_str)
        cur.execute(sql_str)
        conn.commit()
    cur.close()                                    #关闭游标
    conn.commit()                                  #向数据库中提交任何未解决的事务，对不支持事务的数据库不进行任何操作
    conn.close()                                   #关闭到数据库的连接，释放数据库资源


# 从数据库中取出url
def get_url_list(num):
    url_list = []
    conn = pymysql.connect(host='127.0.0.1',  user='root', passwd='Ryan', db=db_name,charset='UTF8')
    cur = conn.cursor()
    # sql_str = "select url from url_record  where num=0 limit 0,{0};".format(num)
    sql_str = "select url from url_record  where num<max_num limit 0,{0};".format(num)
    cur.execute(sql_str)
    if cur.rowcount < 10:
        sql_str = "select url from url_record  where num<max_num limit 0,{0};".format(num)
        cur.execute(sql_str)
    for ii in cur:
        url_list.append(ii[0])

    # for url in url_list:
    #     sql_str = "update url_record set num=-1 where url='{0}';".format(url)
    #     cur.execute(sql_str)

    cur.close()                                    #关闭游标
    conn.commit()                                  #向数据库中提交任何未解决的事务，对不支持事务的数据库不进行任何操作
    conn.close()                                   #关闭到数据库的连接，释放数据库资源
    random.shuffle(url_list)
    return url_list

# 更新url信息
def finish_url(url,num,max_num):
    conn = pymysql.connect(host='127.0.0.1',  user='root', passwd='Ryan', db=db_name,charset='UTF8')
    cur = conn.cursor()
    sql_str = "update url_record set num={0},max_num={1} where url='{2}';".format(num, max_num,url)
    cur.execute(sql_str)
    cur.close()                                    #关闭游标
    conn.commit()                                  #向数据库中提交任何未解决的事务，对不支持事务的数据库不进行任何操作
    conn.close()                                   #关闭到数据库的连接，释放数据库资源


# 更新user信息
def finish_user(user):
    conn = pymysql.connect(host='127.0.0.1',  user='root', passwd='Ryan', db=db_name,charset='UTF8')
    cur = conn.cursor()
    sql_str = "update weibo_user set status={0} where user='{1}';".format(0, user)
    cur.execute(sql_str)
    cur.close()                                    #关闭游标
    conn.commit()                                  #向数据库中提交任何未解决的事务，对不支持事务的数据库不进行任何操作
    conn.close()                                   #关闭到数据库的连接，释放数据库资源


def add_user_from_file():
    with open("./config/weibo","r") as f:
        file_list = f.readlines()
    user_list = []
    for item in file_list:
        user,pwd = item.split("----")
        user_list.append([user.strip(),pwd.strip()])
    add_user(user_list)

def add_url_from_file():
    with open("./config/url_list.txt","r") as f:
        file_list = f.readlines()
    user_list = []
    for item in file_list:
        user_list.append(item.strip())
    add_url(user_list)


def del_user(user):
    conn = pymysql.connect(host='127.0.0.1', user='root', passwd='Ryan', db=db_name, charset='UTF8')
    cur = conn.cursor()
    sql_str = "delete from weibo_user where user={0};".format(user)
    cur.execute(sql_str)
    cur.close()  # 关闭游标
    conn.commit()  # 向数据库中提交任何未解决的事务，对不支持事务的数据库不进行任何操作
    conn.close()  # 关闭到数据库的连接，释放数据库资源

def process_duplicate_id(py):
    conn = pymysql.connect(host='127.0.0.1',  user='root', passwd='Ryan', db=db_name,charset='UTF8')
    cur = conn.cursor()
    sql_str = "create table temp select * from {0} where id in (select id from {0} group by id,userid having count(*) > 1);".format(py)
    print(sql_str)
    cur.execute(sql_str)
    sql_str = "select id from temp"
    print(sql_str)
    cur.execute(sql_str)
    d_id_list = []
    for ii in cur:
        d_id_list.append(ii[0])
    for d_id in d_id_list:
        sql_str = r"delete from {0} where id='{1}'".format(py, d_id)
        cur.execute(sql_str)

    sql_str = "insert into {0} select * from temp;".format(py)
    print(sql_str)
    cur.execute(sql_str)

    sql_str = "ALTER TABLE `weibo`.`{0}` ADD PRIMARY KEY (`id`);".format(py)
    print(sql_str)
    cur.execute(sql_str)

    sql_str = "DROP TABLE `weibo`.`temp`;"
    print(sql_str)
    cur.execute(sql_str)

    cur.close()                                    #关闭游标
    conn.commit()                                  #向数据库中提交任何未解决的事务，对不支持事务的数据库不进行任何操作
    conn.close()                                   #关闭到数据库的连接，释放数据库资源


py_dict = {'扯淡': 'cd', '达人': 'dr', '淡定': 'dd', '腹黑': 'fh', '纠结': 'jj', '闷骚': 'ms',
          '山寨': 'sz', '完爆': 'wb', '接地气': 'jdq', '吐槽': 'tc', '正能量': 'znl', '自拍': 'zp',
          '努力': 'nl', '感觉': 'gj', '简单': 'jd', '无聊': 'wl', '希望': 'xw', '美好': 'mh', '气质': 'qz',
          '害怕': 'hp', '喜欢': 'xh'}

xc_dict = {'扯淡': 'cd', '达人': 'dr', '淡定': 'dd', '腹黑': 'fh', '纠结': 'jj', '闷骚': 'ms',
          '山寨': 'sz', '完爆': 'wb', '接地气': 'jdq', '吐槽': 'tc', '正能量': 'znl', '自拍': 'zp'}
# 获取data数据库里面含有各个关键词的条数
def get_sum():
    conn = pymysql.connect(host='127.0.0.1',  user='root', passwd='Ryan', db=db_name,charset='UTF8')
    cur = conn.cursor()

    for k,v in py_dict.items():
        print(k,end="\t")
        sql_str = r"select count(1) from data where content like '%{0}%'".format(k)
        cur.execute(sql_str)
        for ii in cur:
            print(ii[0])


    cur.close()                                    #关闭游标
    conn.commit()                                  #向数据库中提交任何未解决的事务，对不支持事务的数据库不进行任何操作
    conn.close()                                   #关闭到数据库的连接，释放数据库资源

# 获取各个数据库里面含有各个关键词的条数
def get_sum2():
    conn = pymysql.connect(host='127.0.0.1',  user='root', passwd='Ryan', db=db_name,charset='UTF8')
    cur = conn.cursor()

    for k,v in py_dict.items():
        print(k,end="\t")
        sql_str = r"select count(1) from {0}".format(v)
        cur.execute(sql_str)
        for ii in cur:
            print(ii[0])


    cur.close()                                    #关闭游标
    conn.commit()                                  #向数据库中提交任何未解决的事务，对不支持事务的数据库不进行任何操作
    conn.close()                                   #关闭到数据库的连接，释放数据库资源


def init_db():
    conn = pymysql.connect(host='127.0.0.1',  user='root', passwd='Ryan', db=db_name,charset='UTF8')
    cur = conn.cursor()

    sql_list = []
    sql_list.append("update weibo_user set status=0;")

    for sql_str in sql_list:
        print(sql_str)
        cur.execute(sql_str)
        conn.commit()  # 向数据库中提交任何未解决的事务，对不支持事务的数据库不进行任何操作

    cur.close()                                    #关闭游标
    conn.commit()                                  #向数据库中提交任何未解决的事务，对不支持事务的数据库不进行任何操作
    conn.close()                                   #关闭到数据库的连接，释放数据库资源

if __name__ == '__main__':
    # add_url_from_file()
    # add_user_from_file()
    init_db()
    # get_sum2()

