import json
import web_search
import os
import os
from datetime import datetime,date

import subprocess
import sys
import os



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


class bs_check_client:
    def __init__(self):
        self.local_symbol_path = r"f:\symbols"
        self.cdb_exe_path = r"C:\Program Files (x86)\Windows Kits\10\Debuggers\x64\cdb.exe"
        self.windows_symbol_path = r"srv*%s*https://msdl.microsoft.com/download/symbols" % self.local_symbol_path
        
    def is_file_created_today_with(self,folder_path):
        today = date.today()
        latest_file = None
        latest_creation_time = 0

        for file in os.listdir(folder_path):
            if file.endswith(".dmp"):
                file_path = os.path.join(folder_path, file)
                creation_time = os.path.getctime(file_path)
                creation_date = datetime.fromtimestamp(creation_time).date()

                if creation_date == today and creation_time > latest_creation_time:
                    latest_creation_time = creation_time
                    latest_file = file

        if latest_file:
            print(f"The latest .dmp file created today is: {latest_file}")
            self.run_command(self.windows_symbol_path,file_path)
            return 
        else:
            print("No .dmp file created today found.")
            return


    def run_command(self,sym_path, dmp_file):
        cdb_command = ".reload; !analyze -v;"
        cdb_command += ".printf\"\\n==================== 当前异常现场 ====================\\n\"; .excr;"
        cdb_command += ".printf\"\\n==================== 异常线程堆栈 ====================\\n\"; kv;"
        cdb_command += ".printf\"\\n==================== 所有线程堆栈 ====================\\n\"; ~* kv;"
        cdb_command += "q"
        cdb_command += "qd"  # 退出Windbg

        # 使用Popen方法来运行Windbg并执行命令
        cmd = [self.cdb_exe_path, '-z', dmp_file, '-y', sym_path, '-c', cdb_command]
        process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        output, error = process.communicate()

        with open('blue_sceen.txt', 'w+', encoding='utf-8') as f:
            f.write(output)


if __name__ == '__main__':
    bs_check = bs_check()
    print(bs_check.analyze("/Users/tanzhehao/Library/Containers/com.tencent.xinWeChat/Data/Library/Application Support/com.tencent.xinWeChat/2.0b4.0.9/f9c1b78085446ad69eef3d9e6fb0e1fb/Message/MessageTemp/46af0f2fda75f7eda47be5c4a1887151/File/output.txt"))