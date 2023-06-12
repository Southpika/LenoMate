import uuid
import socket
import wmi

class computer_info:
    def get_mac_address(self):
        #获取物理MAC
        mac = uuid.UUID(int = uuid.getnode()).hex[-12:]
        self.mac =  ":".join([mac[e:e+2] for e in range(0,11,2)])
        return self.mac

    def get_computer_name_ip(self):
        #获取本机电脑名
        self.name = socket.getfqdn(socket.gethostname())
        #获取本机ip
        self.addr = socket.gethostbyname(socket.gethostname())
        return self.name,self.addr
    

    def pysic(self):
        c = wmi.WMI()
        self.physical_disk = c.Win32_DiskDrive()[0].SerialNumber
        self.cpu = c.Win32_Processor()[0].ProcessorId.strip()
        self.board_id = c.Win32_BaseBoard()[0].SerialNumber
        self.bios_id = c.Win32_BIOS()[0].SerialNumber.strip()
    
    def fit(self):
        self.get_mac_address()
        self.get_computer_name_ip()
        self.pysic()
        return f"""本机物理MAC地址是：{self.mac},
本机电脑名是：{self.name}
本机IP是：{self.addr}
本机硬盘序列号是：{self.physical_disk}
本机CPU序列号是：{self.cpu}
本机主板序列号是：{self.board_id}
本机bios序列号是：{self.bios_id}"""

if __name__ == '__main__':
    computer = computer_info()
    print(computer.fit())