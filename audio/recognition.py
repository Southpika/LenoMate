import json
from urllib import request, parse, error


def get_token():
    API_Key = "Nbcq0co6PYGXamFXHWAQUNW2"  # 官网获取的API_Key
    Secret_Key = "8cRbgT1z1xj5zMsIZgHNUCiPflPn3bXE"  # 为官网获取的Secret_Key
    # 拼接得到Url
    Url = "https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=" + API_Key + "&client_secret=" + Secret_Key
    try:
        resp = request.urlopen(Url)
        result = json.loads(resp.read().decode('utf-8'))
        # 打印access_token
        # print("access_token:", result['access_token'])
        return result['access_token']
    except error.URLError as err:
        print('token http response http code : ')
        if err.args == ():
            print(err)
        else:
            print(err.args[0].error)


def main(path="./data/voice.wav"):
    # 1、获取 access_token
    token = get_token()
    # 2、打开需要识别的语音文件
    speech_data = []
    with open(path, 'rb') as speech_file:
        speech_data = speech_file.read()
    length = len(speech_data)
    if length == 0:
        print('file 01.wav length read 0 bytes')

    # 3、设置Url里的参数
    params = {'cuid': "12345678python",  # 用户唯一标识，用来区分用户，长度为60字符以内。
              'token': token,  # 我们获取到的 Access Token
              'dev_pid': 1537}  # 1537 表示识别普通话
    # 将参数编码
    params_query = parse.urlencode(params)
    # 拼接成一个我们需要的完整的完整的url
    Url = 'http://vop.baidu.com/server_api' + "?" + params_query

    # 4、设置请求头
    headers = {
        'Content-Type': 'audio/wav; rate=16000',  # 采样率和文件格式
        'Content-Length': length
    }

    # 5、发送请求，音频数据直接放在body中
    # 构建Request对象
    req = request.Request(Url, speech_data, headers)
    # 发送请求
    res_f = request.urlopen(req)
    result = json.loads(res_f.read().decode('utf-8'))
    # print(result)
    if 'result' in result:
        print("识别结果：", result['result'][0])
    else:
        print("识别结果：无")
    return result['result'][0] if 'result' in result else ''

def main2(content):
    # 1、获取 access_token
    token = get_token()
    # 2、打开需要识别的语音文件
    length = len(content)
    if length == 0:
        print('file 01.wav length read 0 bytes')

    # 3、设置Url里的参数
    params = {'cuid': "12345678python",  # 用户唯一标识，用来区分用户，长度为60字符以内。
              'token': token,  # 我们获取到的 Access Token
              'dev_pid': 1537}  # 1537 表示识别普通话
    # 将参数编码
    params_query = parse.urlencode(params)
    # 拼接成一个我们需要的完整的完整的url
    Url = 'http://vop.baidu.com/server_api' + "?" + params_query

    # 4、设置请求头
    headers = {
        'Content-Type': 'audio/wav; rate=8000',  # 采样率和文件格式
        'Content-Length': length
    }

    # 5、发送请求，音频数据直接放在body中
    # 构建Request对象
    req = request.Request(Url, content, headers)
    # 发送请求
    res_f = request.urlopen(req)
    result = json.loads(res_f.read().decode('utf-8'))
    # # print(result)
    # print("识别结果：", result['result'][0])
    return result['result'][0] if 'result' in result else ''


if __name__ == '__main__':
    main("./01.wav")
