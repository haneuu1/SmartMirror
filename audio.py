import requests
import json
import io
import threading
import time

from pydub import AudioSegment
from pydub.playback import play
import wave
import pyaudio

API_KEY = "kakao_api_key"

SST_URL = "https://kakaoi-newtone-openapi.kakao.com/v1/recognize"
SST_HEADERS = {
    "Transter-Encoding": "chunked",
    "Content-Type": "application/octet-stream",
    "X-DSS-Service": "DICTATION",
    "Authorization": "KakaoAK " + API_KEY
}

def stt(audio):
    res = requests.post(SST_URL, headers=SST_HEADERS, data=audio)
    if res.status_code == 200:
        success = True
        sx = res.text.find('{"type":"finalResult"')
        ex = res.text.rindex('}') + 1
        if sx == -1: # 인식에 실패한 경우
            success = False
            sx = res.text.find('{"type":"errorCalled"')
        
        result_json_string = res.text[sx:ex]
        result = json.loads(result_json_string)
        return result['value']
