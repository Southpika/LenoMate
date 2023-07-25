import json, requests, re, time
from urllib.parse import quote
from bs4 import BeautifulSoup
from selenium import webdriver


def search_web(keyword):
	options = webdriver.ChromeOptions()
	options.add_argument('headless')
	options.add_experimental_option('excludeSwitches', ['enable-logging'])
	driver = webdriver.Chrome(options=options)
	driver.get(quote("https://cn.bing.com/search?q="+str(keyword),safe='/:?=.'))
	for i in range(0, 20000, 350):
		time.sleep(0.02)
		driver.execute_script('window.scrollTo(0, %s)' % i)
	html = driver.execute_script("return document.documentElement.outerHTML")
	driver.close()
	soup = BeautifulSoup(html, 'html.parser')
	item_list = soup.find_all(class_='b_algo')
	relist = []
	for items in item_list:
		item_prelist = items.find('h2')
		item_title = re.sub(r'(<[^>]+>|\s)','',str(item_prelist))
		href_s = item_prelist.find("a", href=True)
		href = href_s["href"]
		relist.append([item_title, href])
	item_list = soup.find_all(class_ ='ans_nws ans_nws_fdbk')
	for items in item_list:
		for i in range(1,10):
			item_prelist = items.find(class_ = f"nws_cwrp nws_itm_cjk item{i}", url=True, titletext=True)
			if item_prelist is not None:
				url = item_prelist["url"].replace('\ue000','').replace('\ue001','')
				title = item_prelist["titletext"]
				relist.append([title, url])
	return relist

def search_wx(url):
	headers = {
		"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36 Edg/111.0.1661.44",
	}
	r = requests.get(url, headers=headers)
	html = r.text
	soup = BeautifulSoup(html, 'html.parser')
	item_list = soup.find(class_='rich_media_wrp')
	item_title = re.sub(r'(<[^>]+>|\s)','',str(item_list))
	return item_title

def search_zhihu_que(url):
    headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36 Edg/111.0.1661.44",
    }
    r = requests.get(url, headers=headers)
    html = r.text
    soup = BeautifulSoup(html, 'html.parser')
    item_list = soup.find_all(class_='List-item')
    relist = []
    for items in item_list:
        item_prelist = items.find(class_ = "RichText ztext CopyrightRichText-richText css-1g0fqss")
        item_title = re.sub(r'(<[^>]+>|\s)','',str(item_prelist))
        relist.append(item_title)
    return relist

def search_baidu_zhidao(url):
    headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36 Edg/111.0.1661.44",
    }
    r = requests.get(url, headers=headers)
    r.encoding = 'utf-8'
    html = str(r.text)
    soup = BeautifulSoup(html, 'html.parser')
    item_list = soup.find(class_='rich-content-container rich-text-')
    item_title = re.sub(r'(<[^>]+>|\s)','',str(item_list))
    return item_title

def search_baike_sougou(url):
    headers = {
		"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36 Edg/111.0.1661.44",
	}
    r = requests.get(url, headers=headers)
    html_s = r.text
    soup_s = BeautifulSoup(html_s, 'html.parser')
    content = soup_s.find(class_='abstract')
    content = re.sub(r'(<[^>]+>|\s)','',str(content))
    return content

def search_zhihu_zhuanlan(url):
    headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36 Edg/111.0.1661.44",
    }
    r = requests.get(url, headers=headers)
    html = r.text
    soup = BeautifulSoup(html, 'html.parser')
    item_list = soup.find(class_='RichText ztext Post-RichText css-1g0fqss')
    item_title = re.sub(r'(<[^>]+>|\s)','',str(item_list))
    return item_title


def ext_zhihu(url):
    if "/answer" in url:
        rep = url.replace('https://www.zhihu.com/question/','')
        rep_l = rep[rep.rfind("/answer"):][7:]
        rep = 'https://www.zhihu.com/question/' + rep.replace("/answer"+rep_l,"")
        return rep
    else:
        return url

def search_tencent_news(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36 Edg/111.0.1661.44",
    }
    # url = 'https:///rain/a/20230720A05EIW00'
    r = requests.get(url, headers=headers)
    html_s = r.text
    soup_s = BeautifulSoup(html_s, 'html.parser')
    content = soup_s.find(class_='content-article')
    
    return re.sub(r'(<[^>]+>|\s)','',str(content))
class web_searcher:
    def __init__(self,web_num) -> None:
        self.web_num = web_num
    
    def search_main(self,query ,feature: list = []):
        web_list = search_web(query)
        # web = search_web(query)
        # print(self.web_list,web)
        self.web_list = []
        for item in web_list:
            if item not in self.web_list:
                self.web_list.append(item)
        return_content = []
        reference_list = []
        for items in self.web_list:
            if "zhihu.com/question/" in items[1] or '知乎回复' in feature:
                return_content.append(str(search_zhihu_que(ext_zhihu(items[1])))[0:500]) #int(get_config().get("web").get('web_max_length'))
                reference_list.append(items[1])
            if "baike.sogou.com" in items[1] or '百科' in feature:
                return_content.append(str(search_baike_sougou(items[1]))[0:1000])
                reference_list.append(items[1])
            if "zhidao.baidu.com" in items[1] or '百度知道' in feature:
                return_content.append(str(search_baidu_zhidao(items[1]))[0:200])
                reference_list.append(items[1])
            if "zhuanlan.zhihu.com" in items[1] or '知乎专栏' in feature:
                return_content.append(str(search_zhihu_zhuanlan(items[1]))[0:1000])
                reference_list.append(items[1])
            if 'new.qq.com' in items[1]:
                return_content.append(str(search_tencent_news(items[1]))[0:1000])
                reference_list.append(items[1])
            if "mp.weixin.qq.com" in items[1] and '微信公众号' in feature:
                return_content.append(str(search_wx(items[1]))[0:1000])
                reference_list.append(items[1])
        return [reference_list[:self.web_num],return_content[:self.web_num]]

if __name__ == '__main__':
    web_tool = web_searcher(5)
    print(web_tool.search_main(input('你想要查什么:\n')))