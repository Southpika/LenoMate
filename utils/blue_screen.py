import json
import web_search
import os
import os
from datetime import datetime,date

class bs_check:
    def __init__(self) -> None:
        
        with open("bug_code.json", "r", encoding="utf-8") as f:
            self.bug_code_list = json.load(f)
    
    def analyze(self,bug_file_location):
        with open(bug_file_location, "r", encoding="utf-8") as f:
            bug_file = f.read()
        start_location = bug_file.find('BUGCHECK_STR:')+len('BUGCHECK_STR:')
        bugcode = bug_file[start_location:start_location+bug_file[start_location:].find('\n')].strip()
        
        return self.bug_code_list[bugcode]


def is_file_created_today_with(folder_path):
    today = date.today()
    latest_file = None
    latest_creation_time = 0

    for file in os.listdir(folder_path):
        if file.endswith(".txt"):
            file_path = os.path.join(folder_path, file)
            creation_time = os.path.getctime(file_path)
            creation_date = datetime.fromtimestamp(creation_time).date()

            if creation_date == today and creation_time > latest_creation_time:
                latest_creation_time = creation_time
                latest_file = file

    if latest_file:
        print(f"The latest .txt file created today is: {latest_file}")
        return file_path
    else:
        print("No .txt file created today found.")
        return


if __name__ == '__main__':
    bs_check = bs_check()
    print(bs_check.analyze("/Users/tanzhehao/Library/Containers/com.tencent.xinWeChat/Data/Library/Application Support/com.tencent.xinWeChat/2.0b4.0.9/f9c1b78085446ad69eef3d9e6fb0e1fb/Message/MessageTemp/46af0f2fda75f7eda47be5c4a1887151/File/output.txt"))