import azure.cognitiveservices.speech as speechsdk
from time import sleep
import threading

SPEECH_KEY, SPEECH_REGION = '729a7e9b72294950b07727391e561d79', 'eastasia'
speech_config = speechsdk.SpeechConfig(subscription=SPEECH_KEY, region=SPEECH_REGION)
audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)
speech_config.speech_synthesis_voice_name = 'zh-CN-XiaochenNeural'
speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)


def speech_synthesis(text):
    speech_synthesizer.stop_speaking()
    speech_synthesis_result = speech_synthesizer.speak_text(text)
    return speech_synthesis_result


if __name__ == '__main__':
    for i in range(3):
        threading.Thread(target=speech_synthesis, args=(
            "这段代码首先找到两个句子的最小长度，然后逐字符比较它们，找到第一个不同的字符位置，并返回从那个位置开始的字符作为不同之处。如果一个句子比另一个句子长，那么返回较长句子的剩余部分。如果两个句子相同，返回空字符串表示没有不同之处。",)).start()
        sleep(5)
