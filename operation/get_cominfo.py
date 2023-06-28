import uuid
import socket
import wmi

# class computer_info:
#     def get_mac_address(self):
#         #获取物理MAC
#         mac = uuid.UUID(int = uuid.getnode()).hex[-12:]
#         self.mac =  ":".join([mac[e:e+2] for e in range(0,11,2)])
#         return self.mac

#     def get_computer_name_ip(self):
#         #获取本机电脑名
#         self.name = socket.getfqdn(socket.gethostname())
#         #获取本机ip
#         self.addr = socket.gethostbyname(socket.gethostname())
#         return self.name,self.addr
    

#     def pysic(self):
#         c = wmi.WMI()
#         self.physical_disk = c.Win32_DiskDrive()[0].SerialNumber
#         self.cpu = c.Win32_Processor()[0].ProcessorId.strip()
#         self.board_id = c.Win32_BaseBoard()[0].SerialNumber
#         self.bios_id = c.Win32_BIOS()[0].SerialNumber.strip()
    
#     def fit(self):
#         self.get_mac_address()
#         self.get_computer_name_ip()
#         self.pysic()
#         return f"""本机物理MAC地址是：{self.mac},
# 本机电脑名是：{self.name}
# 本机IP是：{self.addr}
# 本机硬盘序列号是：{self.physical_disk}
# 本机CPU序列号是：{self.cpu}
# 本机主板序列号是：{self.board_id}
# 本机bios序列号是：{self.bios_id}"""


class information:
    w = wmi.WMI() # 获取配置信息
    list = []

class computer_info(information):
    def __init__(self):
        self.info()

    # 获取配置信息
    def info(self):
    
        for BIOSs in information.w.Win32_ComputerSystem():
            information.list.append("本机电脑名称: %s" % BIOSs.Caption)
            information.list.append("本机使用者: %s" % BIOSs.UserName)
            
        
        address = hex(uuid.getnode())[2:]
        address =  ":".join([address[e:e+2] for e in range(0,11,2)])
        information.list.append("本机MAC地址: %s" % address)
        
        for BIOS in information.w.Win32_BIOS():
            # information.list.append("使用日期: %s" % BIOS.Description)
            information.list.append("本机主板型号: %s" % BIOS.SerialNumber)
            
        for processor in information.w.Win32_Processor():
            information.list.append("本机CPU型号: %s" % processor.Name.strip())
            
        for memModule in information.w.Win32_PhysicalMemory():
            
            totalMemSize = int(memModule.Capacity)
            information.list.append("本机内存厂商: %s" % memModule.Manufacturer)
            information.list.append("本机内存型号: %s" % memModule.PartNumber.strip())
            information.list.append("本机内存大小: %.2fGB" % (totalMemSize / 1024**3))
            
        for disk in information.w.Win32_DiskDrive(InterfaceType="IDE"):
            
            diskSize = int(disk.size)
            information.list.append("本机磁盘名称: %s" % disk.Caption)
            information.list.append("本机磁盘大小: %.2fGB" % (diskSize / 1024**3))
            
        for xk in information.w.Win32_VideoController():
            information.list.append("本机GPU(显卡)名称: %s" % xk.name)

        def get_host_ip():
            """
            查询本机ip地址
            :return: ip
            """
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(('8.8.8.8', 80))
                ip = s.getsockname()[0]
            finally:
                s.close()
            return ip
        addr = get_host_ip()
        information.list.append("本机IP地址: %s" % addr)
        
    def fit(self):
        return '\n'.join(information.list)

if __name__ == '__main__':
    computer = computer_info()
    print(computer.fit())
    print('*'*50)
    # infor = information()
    # INFOs = INFO()
    # print(INFOs.fit())