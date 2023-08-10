import os
import json
import argparse


class search_tool:
    def __init__(self, map_loc='./operation/exe_location.json'):
        self.map_loacation = map_loc
        if os.path.isfile(self.map_loacation):
            with open(self.map_loacation, 'r') as load_f:
                self.hash_map = json.load(load_f)
                print(self.hash_map)
        else:
            self.hash_map = {}

    def open_app(self, b, a='C:/'):
        find_file = self.search_file(a=a, b=b)
        if find_file:
            app_dir = os.path.join(find_file, b)
            print(app_dir)
            os.startfile(app_dir)
            return '找到了'
        else:
            return '没找到,请确认应用程序名字是否在C盘'

    def search_file(self, a, b):
        if b in self.hash_map.keys():
            return self.hash_map[b]
        if b not in self.hash_map.keys():

            for root, dirs, files in os.walk((a), topdown=True):
                if b in files:
                    print('找到了')
                    self.hash_map[b] = root
                    with open(self.map_loacation, 'w') as write_f:
                        json.dump(self.hash_map, write_f, indent=4, ensure_ascii=True)
                    return root
                else:
                    pass
            print('没找到')
            return None


if __name__ == "__main__":
    # a=input('请输入想要查找的磁盘：')+':/'
    # b=input('请输入想要查找的文件名和后缀：')
    parser = argparse.ArgumentParser('Search App')
    parser.add_argument('--a', default='C', type=str)
    parser.add_argument('--b', type=str)
    args = parser.parse_args()
    a = args.a + ':/Users'
    test = search_tool()
    # print(a,args.b)
    test.open_app(a=a, b=args.b)

#   app_dir = r'D:\360download\花生壳\HskDDNS.exe'
#   open_app(app_dir)
