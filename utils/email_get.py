import imaplib, re, datetime, email
from email.header import decode_header, Header
from datetime import datetime, timedelta

IMAP_SERVER = 'outlook.office365.com'
difference = 14400
EMAIL_ADDRESS = 'XXX@outlook.com'
EMAIL_PASSWORD = '***'


def decode_str(s):
    value, charset = decode_header(s)[0]
    if charset:
        value = value.decode(charset)
    return value, charset


class email_reciever:
    def __init__(self, EMAIL_ADDRESS=EMAIL_ADDRESS, EMAIL_PASSWORD=EMAIL_PASSWORD, email_type=IMAP_SERVER,
                 difference=difference) -> None:
        self.EMAIL_ADDRESS = EMAIL_ADDRESS
        self.EMAIL_PASSWORD = EMAIL_PASSWORD
        self.IMAP_SERVER = email_type  # 'pop.qq.com'
        self.jiance = difference

    def get_email(self):
        mail = imaplib.IMAP4_SSL(self.IMAP_SERVER, 993)
        mail.login(self.EMAIL_ADDRESS, self.EMAIL_PASSWORD)
        mail.select("inbox")
        result, data = mail.uid('search', None, 'UNSEEN')
        uids = data[0].split()
        if uids:
            uid = uids[-1]
            result, data = mail.uid('fetch', uid, '(RFC822)')
            email_message = email.message_from_bytes(data[0][1])
            subject, email_encode = decode_str(email_message['Subject'])
            sender = email.utils.parseaddr(email_message['From'])[1]
            date_string = email_message.get('Date')
            date_string = date_string.replace(' (GMT+08:00)', '')
            long = len(date_string.split())
            if long == 5:
                date_obj = datetime.strptime(date_string, '%d %b %Y %H:%M:%S %z')
            elif long == 6:
                date_obj = datetime.strptime(date_string, '%a, %d %b %Y %H:%M:%S %z')
            else:
                date_obj = datetime.strptime(date_string, '%a, %d %b %Y %H:%M:%S %z (%Z)')
            # 获取当前时间
            current_time = datetime.now(date_obj.tzinfo)
            time_difference = current_time - date_obj

            if time_difference < timedelta(minutes=self.jiance):
                print(f"检测到{self.jiance}分钟以内的新邮件")
                date = date_obj.date()
                time = date_obj.time()
                temp_content = ''
                if email_message.is_multipart():
                    for part in email_message.get_payload():
                        if part.get_content_type() == 'text/plain':
                            temp_content += part.get_payload(decode=True).decode(email_encode)
                            break
                        elif part.get_content_type() == 'text/html':
                            temp_content = part.get_payload(decode=True).decode(email_encode)
                            temp_content = re.sub(r'(<[^>]+>|\s)', '', str(temp_content))
                            temp_content = re.sub(r'({[^>]+}|\s)', '', str(temp_content))
                        elif 'text' in part.get_content_type():
                            temp_content += part.get_payload(decode=True).decode(email_encode)
                        else:
                            temp_content += 'UNDECODE'
                else:
                    temp_content = email_message.get_payload(decode=True).decode(email_encode)
                body = re.sub(r'(\r\n){2,}', r'\n\n', temp_content)
                # print(body)

                res = f"Subject:{subject}\nSender:{sender}\nContent:{body}"
                return res
        return None


if __name__ == '__main__':
    tzh = email_reciever()
    print(tzh.get_email())
