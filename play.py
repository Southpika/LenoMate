import wave
import pyaudio


# 播放
def play():
    wf = wave.open(r"result.wav", 'rb')
    p = pyaudio.PyAudio()
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)

    data = wf.readframes(2048)
    while len(data) > 0:
        stream.write(data)
        data = wf.readframes(2048)

    stream.stop_stream()

    stream.close()

    p.terminate()


if __name__ == '__main__':
    play()
