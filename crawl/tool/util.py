import os
import re
import pickle
from urllib import parse
from crawl.tool.gooseeker import GsExtractor
from lxml import etree


def html2xml(content):
    plExtra = GsExtractor()
    plExtra.setXsltFromFile("Xslt")
    # plExtra.setXsltFromAPI("9308b2a1ccf11e59d23c5d8b3022a904","local_wb")
    doc = etree.HTML(content)
    result = plExtra.extract(doc)
    return result
    # url_list = result.findall(".//url")

# 用于查找并且转换url中的关键词
def find_key_word(url):
    s_keyword = re.search(r"weibo/(\S*)&scope=ori", url).group(1)
    keyword = parse.unquote(s_keyword)
    keyword = parse.unquote(keyword)
    return keyword


# 用于生成微博地址的%关键词
def create_url_word(sword):
    string = parse.quote(sword)
    strArray = string.split('%')
    rword = ''
    for i in range(1, len(strArray)):
        rword += ('%25' + strArray[i])
    return rword


# 获取所有关键词的列表
def get_key_list():
    return ['山寨', '腹黑', '人艰不拆', '闷骚', '不明觉厉', '正能量', '完爆', '扯淡', '达人', '接地气', '纠结', '吐槽', '淡定', '自拍']


# 获取所有关键词的列表
def get_key_list2():
    return ['不约而同', '喜闻乐见', '努力', '感觉', '简单', '无聊', '希望', '美好', '气质', '害怕', '喜欢']


# 判断文字里面是否有keyword，简繁体
def isValid(keyword, content):
    word_dict = {'人艰不拆': '人艱不拆', '不明觉厉': '不明覺厲', '扯淡': '扯淡', '达人': '達人', '淡定': '淡定', '腹黑': '腹黑', '纠结': '糾結', '闷骚': '悶騷',
                 '山寨': '山寨', '十动然拒': '十動然拒', '完爆': '完爆', '接地气': '接地氣', '吐槽': '吐槽', '正能量': '正能量', '自拍': '自拍', '给力': '給力',
                 '不约而同': '不約而同', '喜闻乐见': '喜聞樂見', '努力': '努力', '感觉': '感覺', '简单': '簡單', '无聊': '無聊', '希望': '希望', '美好': '美好',
                 '气质': '氣質', '害怕': '害怕', '喜欢': '喜歡'}
    if keyword not in content and word_dict.get(keyword) not in content:
        return False
    return True


def getPY(keyword):
    pydict = {'不明觉厉': 'bmjl', '扯淡': 'cd', '达人': 'dr', '淡定': 'dd', '腹黑': 'fh', '纠结': 'jj', '闷骚': 'ms', '人艰不拆': 'rjbc',
              '山寨': 'sz', '完爆': 'wb', '接地气': 'jdq', '吐槽': 'tc', '正能量': 'znl', '自拍': 'zp', '给力': 'gl', '不约而同': 'byet',
              '喜闻乐见': 'xwlj', '努力': 'nl', '感觉': 'gj', '简单': 'jd', '无聊': 'wl', '希望': 'xw', '美好': 'mh', '气质': 'qz',
              '害怕': 'hp', '喜欢': 'xh'}
    return pydict.get(keyword)


# 获取dir下所有xml文件的名字
def get_file_list(dir, type='.xml'):
    currentDirFiles = os.listdir(dir+"/")
    return [xmlFile for xmlFile in currentDirFiles if type in xmlFile]


# 获取一个文件里面包含的所有有用信息
# 传入根节点
def get_item_list(root):
    item_list = root.findall(".//listItem/item")
    if len(item_list) <= 0:
        return []
    data_list = []
    for item in item_list:
        try:
            content = item.find('content').text.strip()
            content = encode_sql(content)
            passageUrl = item.find('passageId').text
            passageUrl = passageUrl.replace('?refer_flag=1001030103_', '')
        except AttributeError:
            print("AttributeError")
        try:
            passageUrl = re.search(r"(http://weibo.com/\S*)", passageUrl).group(1)

            id = re.search(r"http://weibo.com/\d*/(\S*)", passageUrl).group(1)
        except:
            print(passageUrl)
        user_id = item.find('id').text
        if user_id is None:
            user_id = 0
        terminal = item.find('terminal').text
        if terminal is not None:
            terminal = encode_sql(terminal)
        forwardNum = item.find('forwardNum').text
        if forwardNum is None:
            forwardNum = 0

        commentNum = item.find('commentNum').text
        if commentNum is None:
            commentNum = 0

        likeNum = item.find('likeNum').text
        if likeNum is None:
            likeNum = 0
        datetime = item.find('time').text
        date = datetime[0:10]
        time = datetime[11:]
        data_list.append([id, user_id, content, passageUrl, terminal, forwardNum, commentNum, likeNum, date, time])
    return data_list


w_dict = {chr(0): "\0", chr(39): r"\'", chr(34): "\"", chr(8): "\b", chr(10): "\n", chr(13): "\r", chr(9): "\t",
          chr(26): "\z", chr(37): "\%", chr(95): "\_"}

# 过滤表情
def filter_emoji(desstr, restr=''):
    try:
        co = re.compile(u'[\U00010000-\U0010ffff]')
    except re.error:
        co = re.compile(u'[\uD800-\uDBFF][\uDC00-\uDFFF]')
    return co.sub(restr, desstr)

#
def encode_sql(content):
    content = content.replace('\\', '\\\\')
    for k, v in w_dict.items():
        content = content.replace(k, v)
    content = filter_emoji(content)
    return content


def decode_sql(content):
    for k, v in w_dict.items():
        content = content.replace(v, k)
    return content





def infile_fh(temp):
    # 匹配符号
    return re.sub(
        "[\s+\.\!\/_,$%^*()\+\"\']+|[+—！，。？、~@#￥%…&*（）]+|[\':!),.;?\[\]}¢\"、。〉》」』】〕〗〞︰︱︳﹐､﹒﹔﹕﹖﹗﹚﹜﹞！），．：；？｜｝︴︶︸︺︼︾﹀﹂﹄﹏～￠々‖•·ˇˉ―-′’”({£¥‵〈《「『【〔〖（［｛￡￥〝︵︷︹︻︽︿﹁﹃﹙﹛﹝“‘—_…]",
        ' ', temp)


# 把一个list保存文件 utf-8 格式
def save_file(file_name, w_list, entire_line=False, code='utf-8'):
    with open(file_name, 'w', encoding=code) as f:
        for s in w_list:
            f.write(str(s) + '\n')
            if entire_line:
                f.write('\n')


# 读取文件，并且去空
def get_list_from_file(file_name, code='utf-8'):
    rr_list = []
    with open(file_name, 'r', encoding='utf-8') as r_file:
        r_list = r_file.readlines()
        for sentence in r_list:
            sentence = sentence.strip().rstrip('\n')
            if sentence is not None and sentence != '':
                rr_list.append(sentence)
    return rr_list


# 过滤微博中的无用字符,并且返回一个list
def input_filer(temp):
    # 匹配url
    temp = re.sub("(分享自@\S+)", '', temp)
    temp = re.sub("(@\S+)", '', temp)
    # 将正则表达式编译成Pattern对象
    pattern = re.compile(r'[\u4e00-\u9fa5]+')
    # 使用Pattern匹配文本，获得匹配结果，无法匹配时将返回None
    match = pattern.findall(temp)
    return match


# 保存对象
def save_nw(g, file_name):
    with open(file_name, 'wb') as f:  # open file with write-mode
        pickle.dump(g, f)  # serialize and save object


# 获取已经保存的网络对象
def get_nw(file_name):
    with open(file_name, 'rb') as f:
        g = pickle.load(f)  # read file and build object
    return g


# 解决中文乱码问题
def set_ch():
    from pylab import mpl
    mpl.rcParams['font.sans-serif'] = ['FangSong']  # 指定默认字体
    mpl.rcParams['axes.unicode_minus'] = False  # 解决保存图像是负号'-'显示为方块的问题


# 展示图形
def show_nw(graph):
    set_ch()
    import matplotlib.pyplot as plt
    nx.draw(graph, pos=nx.spring_layout(graph), node_size=1000, with_labels=True)
    plt.show()


# 创建文件夹，若有则不创建，否则才创建
def create_directory(directory):
    if not os.path.exists(directory):
        os.mkdir(directory)


def get_time():
    import time
    ISOTIMEFORMAT = '%Y-%m-%d %X'
    return time.strftime(ISOTIMEFORMAT, time.localtime())


# 用于生成xls文件
# {'key_word':((x),(y))}
def create_xlsx(key_dict, names, dir):
    # names = ['节点数','比例1','比例2','比例3']
    # 引入xls写的库
    import xlsxwriter
    # xls 保存的路径
    workbook = xlsxwriter.Workbook(dir)
    for k, v in key_dict.items():
        # 为每个关键词创建表格
        worksheet = workbook.add_worksheet(k)
        num_col = len(v) / 2
        print(k)
        print(num_col)
        i = 0

        # 用于寻找最大值.每个关键词清空一次
        ymax_list = []
        ymin_list = []

        # Create a new chart object. In this case an embedded chart.
        chart1 = workbook.add_chart({'type': 'scatter', 'subtype': 'straight'})
        chart1.set_title({'name': k})

        # ascii A->65
        while i < num_col:
            c1 = chr(65 + 2 * i)
            c2 = chr(66 + 2 * i)
            x = v[2 * i]
            y = v[2 * i + 1]

            # Add an Excel date format.
            date_format = workbook.add_format({'num_format': 'yyyy-mm-dd'})

            # Adjust the column width.
            worksheet.set_column(2 * i, 2 * i, 15)

            # 写入x轴和y轴
            worksheet.write_column(c1 + '1', x, date_format)
            worksheet.write_column(c2 + '1', y)

            # 获取最值
            ymax_list.append(max(y))
            ymin_list.append(min(y))

            # Configure the first series.
            chart1.add_series({
                'name': names[i],
                'categories': '=' + k + '!$' + c1 + '$1:$' + c1 + '$' + str(len(x)),
                'values': '=' + k + '!$' + c2 + '$1:$' + c2 + '$' + str(len(y)),
                'line': {'none': True},
                'marker': {'type': 'automatic'},
            })

            # 设置y轴的范围
            # chart1.set_y_axis({'max': 1, 'min': 0})
            chart1.set_y_axis({'max': max(ymax_list) + 20, 'min': min(ymin_list)-20})
            # chart1.set_y_axis({'max': max(ymax_list), 'min': min(ymin_list)})
            chart1.set_size({'x_scale': 2, 'y_scale': 2})

            i += 1
        # Insert the chart into the worksheet (with an offset).
        worksheet.insert_chart('A2', chart1, {'x_offset': 25, 'y_offset': 10})

    workbook.close()


# 输入两个字符串日期
# 如果t2比t1大返回正值，反之返回负值
def compare_date(t2, t1):
    import time
    tt1 = time.mktime(time.strptime(t1, "%Y-%m-%d"))
    tt2 = time.mktime(time.strptime(t2, "%Y-%m-%d"))
    return tt2 - tt1


# txt 转换为dict
def txt2dict(word_list):
    r_dict = dict()
    for word in word_list:
        item = word.split('\t')
        r_dict[item[0]] = int(item[1])
    return r_dict


# 合并两个dict
def union_dicts(dict1, dict2):
    from collections import Counter
    return dict(Counter(dict1) + Counter(dict2))


# 求出两个dict的交集,输出列表
def inter_dicts(dict1, dict2):
    return [x for x in dict1 if x in dict2]


# d 是dict
# 返回按照value降序排序后的 key 列表
def sort_by_value(d):
    items = d.items()
    backitems = [[v[1], v[0]] for v in items]
    backitems.sort(reverse=True)
    return [backitems[i][1] for i in range(0, len(backitems))]


# sort_key_list: 排序后的key
# word_dict: 待保存的字典
def create_dict_list(sort_key_list, word_dict):
    word_list = []
    for key in sort_key_list:
        if len(key) > 1:
            vv = word_dict[key]
            word_list.append(key + "\t" + str(vv))
    return word_list


# 把dict降序排列后生成list后保存
def save_dict_list(r_dict, path):
    kk = sort_by_value(r_dict)
    w_list = create_dict_list(kk, r_dict)
    save_file(path, w_list, False)


# 获取对象列表
def get_obj_list(file_dir, type=".pkl"):
    file_name_list = sorted(get_file_list(file_dir, type))
    file_list = []
    if type == ".pkl":
        for file in file_name_list:
            file_list.append(util.get_nw(file_dir + "//" + file))
    elif type == ".txt":
        for file in file_name_list:
            word_list = get_list_from_file(file_dir + "//" + file)
            file_list.append(txt2dict(word_list))

    return file_list


# 获取对象字典列表
def get_objdict_list(file_dir, type=".pkl"):
    r_dict = dict()
    file_name_list = get_file_list(file_dir, type)
    file_list = []
    if type == ".pkl":
        for file in file_name_list:
            r_dict[file] = (util.get_nw(file_dir + "//" + file))
    elif type == ".txt":
        for file in file_name_list:
            word_list = get_list_from_file(file_dir + "//" + file)
            r_dict[file] = (txt2dict(word_list))
    return r_dict, file_name_list


def BinarySearch_Dict(sorted_key_array, r_dict, num):
    low = 0
    height = len(sorted_key_array)-1
    while low < height:
        mid = (low+height)//2
        if r_dict[sorted_key_array[mid]] > num:
            low = mid + 1

        elif r_dict[sorted_key_array[mid]]< num:
            height = mid - 1

        else:
            return mid
    return -1


