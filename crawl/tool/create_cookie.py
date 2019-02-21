

s = r"login_sid_t={0}; _s_tentry={1}; Apache={2}; SINAGLOBAL={3}; ULV={4}; SWB={5}; SCF={6}; SUB={7}; SUBP={8}; SUHB={9}; ALF={10}; SSOLoginState={11}; un={12}; wvr={13}; WBStorage={14}"
s_list = s.split("; ")
cookie = ""
for item in s_list:
    word = item.split("=")[0]
    print(r"if '{0}' in cookie_dict:".format(word))
    print("\tcookie = cookie + '{0}' + '='+cookie_dict['{0}']+'; ' ".format(word,))
    print()