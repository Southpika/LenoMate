import os
import time
default_path = os.path.join(os.path.expanduser("~"), "Desktop") ## desktop_path

def time_suffix():
    return time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))

class operation():
    def __init__(self,inputs,path=default_path,summary='notebook'):
        self.path = path
        self.inputs = inputs
        self.summary = summary
    def fit(self):
        file_name = 'LenoMate_'+self.summary+'_'+time_suffix()+'.txt'
        file_name = os.path.join(default_path,file_name)
        with open(file_name,'w',encoding='utf-8') as f:
            f.write(self.inputs)
        f.close()

if __name__ == '__main__':
    
    inputs = input('你想要记录什么： ')
    inp = {'inputs':inputs}
    opt = operation(**inp)
    opt.fit()
    print('完成记录')