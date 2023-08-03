from data import map

import http.client, urllib, json

class query:
    def __init__(self,api_key='a9658b7dc366efef131a934a018e9f12') -> None:
        self.key = api_key
    
    def constellation(self,astro = map.constellation_map['金牛座']):
        conn = http.client.HTTPSConnection('apis.tianapi.com')  #接口域名
        params = urllib.parse.urlencode({'key':self.key,'astro':astro})
        headers = {'Content-type':'application/x-www-form-urlencoded'}
        conn.request('POST','/star/index',params,headers)
        tianapi = conn.getresponse()
        result = tianapi.read()
        data = result.decode('utf-8')
        if data['code'] == 200:
            dict_data = json.loads(data)
            res = ''
            for item in dict_data['result']['list']:
                res += item['type']+':'+item['content']+'\n'
            return res
        
            
        