# import threading
# import queue
# import numpy as np

# # 模拟加载和运行模型的函数
# def load_and_run_model(input_queue):
#     # 模型加载过程，可以根据实际情况进行编写
#     print("模型加载中...")
#     # 模型加载完成
#     print("模型加载完成")

#     while True:
#         try:
#             # 从输入队列中获取输入数据
#             input_data = input_queue.get()
#             # 在这里进行模型处理
#             # 模型处理逻辑...
#             # 将输入数据转换为numpy数组
#             input_array = eval(input_data)
#             # 运行模型，这里我们简单地将输入数据乘以2
#             output_array = input_array * 2
#             # 将结果转换为字符串
#             output_data = str(output_array)

#             # 处理完成后，可以将结果返回给主线程，或者进行其他操作
#             print("模型输出：", output_data)
#         except KeyboardInterrupt:
#             break

# # 创建一个输入队列
# input_queue = queue.Queue()

# # 创建一个线程，用于加载和运行模型
# model_thread = threading.Thread(target=load_and_run_model, args=(input_queue,))
# # 设置线程为后台线程，使程序可以退出
# model_thread.daemon = True
# # 启动线程
# model_thread.start()


# try:
#     while True:
#         # 接收用户输入
#         input_data = input("请输入数据（按下Ctrl+C退出）：")
#         # 将输入数据放入输入队列
#         if input_data == "exit":
#             break
#         input_queue.put(input_data)
# except KeyboardInterrupt:
#     pass



# # while True:
# #     # 接收用户输入
# #     input_data = input("请输入数据（输入'exit'退出）：")
# #     if input_data == "exit":
# #         break
# #     # 将输入数据放入输入队列
# #     input_queue.put(input_data)

# input_queue.put(None)  # 发送终止信号给模型线程
# # 退出程序时，清空输入队列并等待模型线程结束
# input_queue.join()

import threading
import queue
import numpy as np
import signal
import sys

# 全局标志变量，控制程序运行状态
running = True

# 模拟加载和运行模型的函数
def load_and_run_model(input_queue):
    # 模型加载过程，可以根据实际情况进行编写
    print("模型加载中...")
    # 模型加载完成
    print("模型加载完成")
    global running
    while running:
        try:
            # 从输入队列中获取输入数据
            input_data = input_queue.get()
            if input_data is None:
                break  # 收到终止信号时退出循环

            # 在这里进行模型处理
            # 模型处理逻辑...
            # 将输入数据转换为numpy数组
            input_array = np.array(input_data)
            # 运行模型，这里我们简单地将输入数据乘以2
            output_array = input_array * 2
            # 将结果转换为字符串
            output_data = str(output_array)

            # 处理完成后，可以将结果返回给主线程，或者进行其他操作
            print("模型输出：", output_data)
        except KeyboardInterrupt:
            break

# 创建一个输入队列
input_queue = queue.Queue()

# 创建一个线程，用于加载和运行模型
model_thread = threading.Thread(target=load_and_run_model, args=(input_queue,))
# 设置线程为后台线程，使程序可以退出
model_thread.daemon = True
# 启动线程
model_thread.start()

def signal_handler(signal, frame):
    global running
    running = False
    input_queue.put(None)  # 发送终止信号给模型线程
    input_queue.join()
    sys.exit(0)

# 设置信号处理函数，捕获 Ctrl+C 信号
signal.signal(signal.SIGINT, signal_handler)

try:
    while True:
        # 接收用户输入
        input_data = input("请输入数据（按下Ctrl+C退出）：")
        # 将输入数据放入输入队列
        input_queue.put(input_data)
except KeyboardInterrupt:
    pass

# 退出程序时，清空输入队列并等待模型线程结束
running = False  # 设置运行标志为False，终止模型线程的循环
input_queue.put(None)  # 发送终止信号给模型线程
input_queue.join()


