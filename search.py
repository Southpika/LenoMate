import os
import getpass
from urllib.parse import quote

path = f"C:\\Users\\{getpass.getuser()}"
url = "start search-ms:displayname=Results&crumb=&crumb=System.Generic.String:%s&crumb=location:%s" % (
    quote(input("请输入查找项：")), quote(path))
os.system(url.replace('&', '^&'))