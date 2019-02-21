
def convert_header():
    with open("text","rb") as f:
        r_list = f.readlines()

    r_dict = dict()
    for row in r_list:
        rr = str(row).replace(r"\r\n'", "").replace(r"b'", "")
        item = rr.split(": ")
        r_dict[item[0]] = item[1]

    print(r_dict)


def convert_cookie():
    cookie_dict = dict()
    with open("text", "r") as f:
        cookie_lines = f.readlines()[0][:-1]

    items = cookie_lines.split("; ")
    for item in items:
        key, value = item.split("=")
        cookie_dict[key]= value
    print(cookie_dict)


convert_header()