import pyaudio
import sys
import wave
from tqdm import tqdm

TIME = 5  # 录音时间

# 如果没有参数，就将输出文件设置为'01.wav'
if len(sys.argv) == 1:
    file_name = "01.wav"
else:
    file_name = sys.argv[1]


def main():
    # 实例化一个PyAudio对象
    pa = pyaudio.PyAudio()
    # 打开声卡，设置 采样深度为16位、声道数为2、采样率为16K、输入、采样点缓存数量为2048
    stream = pa.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=2048)
    # 新建一个列表，用来存储采样到的数据
    record_buf = []

    # 开始采样
    for i in tqdm(range(8 * 5)):  # 录音5秒
        audio_data = stream.read(2048)  # 读出声卡缓冲区的音频数据
        record_buf.append(audio_data)  # 将读出的音频数据追加到record_buf列表

    wf = wave.open(file_name, 'wb')  # 创建一个音频文件，名字为“01.wav"
    wf.setnchannels(1)  # 设置声道数为2
    wf.setsampwidth(2)  # 设置采样深度为2个字节，即16位
    wf.setframerate(16000)  # 设置采样率为16000
    # 将数据写入创建的音频文件
    wf.writeframes("".encode().join(record_buf))
    # 写完后将文件关闭
    wf.close()
    # 停止声卡
    stream.stop_stream()
    # 关闭声卡
    stream.close()
    # 终止pyaudio
    pa.terminate()


if __name__ == '__main__':
    main()
