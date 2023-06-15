import wave
import pyaudio
import threading


# 播放
def play2():
    is_playing = threading.Event()
    is_playing.set()
    wf = wave.open(r"../data/result.wav", 'rb')
    p = pyaudio.PyAudio()
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)

    data = wf.readframes(2048)
    while len(data) > 0:
        stream.write(data)
        data = wf.readframes(2048)
    while stream.is_active():
        is_playing.wait()
    stream.stop_stream()
    stream.close()
    p.terminate()
    print('播放已结束')

# 定义全局变量


# 回调函数


def play():
    is_playing = threading.Event()
    wf = wave.open('./data/result.wav', 'rb')

    # 初始化 PyAudio
    p = pyaudio.PyAudio()

    def callback(in_data, frame_count, time_info, status):
        data = wf.readframes(frame_count)

        return (data, pyaudio.paContinue)
    # 打开音频流
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True,
                    stream_callback=callback)

    # 设置事件
    is_playing.set()

    # 开始播放音频
    stream.start_stream()

    # 等待声音播放完毕
    while stream.is_active():
        is_playing.wait()

    # 停止音频流
    stream.stop_stream()
    stream.close()

    # 终止 PyAudio
    p.terminate()

    # 关闭音频文件
    wf.close()

    print("声音播放完毕，程序结束")
    return True

if __name__ == '__main__':
    play()
