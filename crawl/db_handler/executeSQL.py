# 向数据库中插入数据
import pymysql
import os
import re
import xml.etree.ElementTree as ET
import crawl.tool.util as util
import traceback
import time

db_name = 'weibo'


# 把信息插入到数据库中
def execute_data_sql(data_list, table_name):
    conn = pymysql.connect(host='127.0.0.1',  user='root', passwd='Ryan', db=db_name,charset='UTF8')
    cur = conn.cursor()
    for item in data_list:
        try:
            try:
                sql_str = "insert into {0} (id,userid,content,passageUrl,terminal,forwardNum,commentNum,LikeNum,date,time) values ('{1}',{2},'{3}','{4}','{5}',{6},{7},{8},'{9}','{10}');".format(table_name, item[0], item[1], item[2], item[3], item[4], item[5], item[6], item[7], item[8], item[9])
                cur.execute(sql_str)
            except(pymysql.err.ProgrammingError):
                with open("sql_error.txt", "a",encoding='utf8') as file:
                    traceback.print_exc()
                    file.write(sql_str + '\n')
                    print('正常数据')
                    print(sql_str)

        except(pymysql.err.IntegrityError):
            pass

    cur.close()                                    #关闭游标
    conn.commit()                                  #向数据库中提交任何未解决的事务，对不支持事务的数据库不进行任何操作
    conn.close()                                   #关闭到数据库的连接，释放数据库资源


# 处理文件返回有效数据list，错误数据list，处理的url0
def process_file(text):
    root = ET.fromstring(text)
    # url = root.find('url').text
    # 获取数据列表
    data_list = util.get_item_list(root)
    # print(len(data_list))
    # 插入正常数据
    if len(data_list) != 0:
        execute_data_sql(data_list, 'data')


def process_xml(xml_text):
    try:
        process_file(xml_text)
    except(ET.ParseError):
        with open('./error/err_file_record.txt', 'a') as record_file1:
            record_file1.write(str(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())))+'\n')
            record_file1.write(xml_text+'\n')


