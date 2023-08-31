import azure.cognitiveservices.speech as speechsdk

SPEECH_KEY, SPEECH_REGION = 'f4cdaef2d60c4d95ba92ace56879e98c', 'eastasia'


def speech_synthesis(text):
    speech_config = speechsdk.SpeechConfig(subscription=SPEECH_KEY, region=SPEECH_REGION)
    audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)
    speech_config.speech_synthesis_voice_name = 'zh-CN-XiaochenNeural'
    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
    speech_synthesis_result = speech_synthesizer.speak_text_async(text).get()
    return speech_synthesis_result


if __name__ == '__main__':
    speech_synthesis(input("Enter some text that you want to speak >"))
