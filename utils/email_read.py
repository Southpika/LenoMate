import poplib,re
from email.parser import Parser
from email.header import decode_header,Header
from email.utils import parseaddr

def print_email(msg):
    res = ''
    for header in ['From', 'To', 'Subject']:
        value = msg.get(header, '')
        if value:
            if header == 'Subject':
                value = decode_str(value)
            else:
                hdr, addr = parseaddr(value)
                name = decode_str(hdr)
                value = u'%s <%s>' % (name, addr)
        # print('%s: %s' % (header, value))
        res += '%s: %s' % (header, value) + '\n'
    # 获取邮件主体信息
    # attachment_files = []
    
    for part in msg.walk():
        # 获取附件名称类型
        # file_name = part.get_filename()
        # 获取数据类型
        contentType = part.get_content_type()
        # 获取编码格式
        mycode = part.get_content_charset()
        # if file_name:
        #     h = Header(file_name)
        #     # 对附件名称进行解码
        #     dh = decode_header(h)
        #     filename = dh[0][0]
            # if dh[0][1]:
            #     # 将附件名称可读化
            #     filename = decode_str(str(filename, dh[0][1]))
            # attachment_files.append(filename)
            # 下载附件
            # data = part.get_payload(decode=True)
            # 在当前目录下创建文件
            # with open(filename, 'wb') as f:
            #     # 保存附件
            #     f.write(data)
        if not mycode: mycode = 'utf-8'
        if contentType == 'text/plain':
            data = part.get_payload(decode=True)
            content = data.decode(mycode)
            # print('正文：',re.sub(r'(\r\n){2,}',r'\n\n',content))
            res += re.sub(r'(\r\n){2,}',r'\n\n',content)
        elif contentType == 'text/html':
            data = part.get_payload(decode=True)
            content = data.decode(mycode)
            # print('正文：', content)
            res += re.sub(r'(<[^>]+>|\s)','',str(content))
    # print('附件名列表：', attachment_files)
    return res

def decode_str(s):
    value, charset = decode_header(s)[0]
    if charset:
        value = value.decode(charset)
    return value

class email_reciever:
    def __init__(self,receiverMail,authCode,email_type) -> None:
        self.receiverMail = receiverMail
        pop3_server = email_type #'pop.qq.com'
        self.server = poplib.POP3_SSL(pop3_server, 995)
        self.server.user(receiverMail)
        self.server.pass_(authCode)
        print('邮件数量:%s  占用空间:%s' % self.server.stat())
        
    
    def load_email(self,idx = None):
        resp, mails, octets = self.server.list()
        if not idx:  idx = len(mails)
        resp, lines, octets = self.server.retr(idx)
        msg_content = b'\r\n'.join(lines).decode('utf-8')
        msg = Parser().parsestr(msg_content)
        content = print_email(msg)
        return content
        
# # 接收者邮箱地址
# receiverMail = 'xxxxxx@qq.com'
# # 接收者 QQ 邮箱授权码
# authCode = 'xxxxxxxxx'
# pop3_server = 'pop.qq.com'
# # 连接到 POP3 服务器
# server = poplib.POP3_SSL(pop3_server, 995)
# # 身份认证
# server.user(receiverMail)
# server.pass_(authCode)
# # stat() 返回邮件数量和占用空间
# print('邮件数量:%s  占用空间:%s' % server.stat())
# # list() 返回所有邮件的编号，lines 存储了邮件的原始文本的每一行
# resp, mails, octets = server.list()
# index = len(mails)
# # 获取最新一封邮件
# resp, lines, octets = server.retr(index)
# msg_content = b'\r\n'.join(lines).decode('utf-8')
# # 解析邮件
# msg = Parser().parsestr(msg_content)
# print_email(msg)
# # 根据邮件索引号直接从服务器删除邮件
# # server.dele(1)
# # 关闭连接
# server.quit()