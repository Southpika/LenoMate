import azure.cognitiveservices.speech as speechsdk
import time

SPEECH_KEY, SPEECH_REGION = 'f4cdaef2d60c4d95ba92ace56879e98c', 'eastasia'
speech_config = speechsdk.SpeechConfig(subscription=SPEECH_KEY, region=SPEECH_REGION)
speech_config.speech_recognition_language = "zh-CN"
audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)


def recognize_from_microphone():
    print("Speak into your microphone.")
    speech_recognition_result = speech_recognizer.recognize_once()
    print(f"Recognized: {speech_recognition_result.text}")
    return speech_recognition_result.text


if __name__ == '__main__':
    while True:
        recognize_from_microphone()
        time.sleep(3)
