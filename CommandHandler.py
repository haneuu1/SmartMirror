from audio import *
from Cam2 import Cam
from WebControl import WebControl
from serial import myserial
import threading
from queue import Queue
from db import *
import threading
from pygame import mixer
import pyautogui

class CommandHandler(threading.Thread):

    commands = {
        '오늘 어때': "얼굴 체크",
        '수고했어': "홈화면으로",
        # 'news': NewsWidget(),
        '종료': "프로그램 종료",
    }

    def __init__(self):
        super().__init__()
        self.queue = Queue()
        self.cam = Cam()
        self.web = WebControl()

        mixer.init()
        
        
    def __search_for_key(self, text):  # Search for a dictionary key in the phrase
        for key in self.commands:
            if key in text:
                return key
        return None

    def add_command(self, text):
        self.queue.put(text)

    # text: 음성 인식한 결과 문장
    def run(self):
        cnt = 0
        while True:
            text = self.queue.get()
            key = self.__search_for_key(text)  # Get the relative key from phrase
            if key:
                if (key == "종료"):
                    print('-received 종료')
                    self.web.exit()

                if (key == "수고했어"):
                    print('-received 수고했어')
                    self.web.home()
                    
                if (key == "오늘 어때"):
                    print(f'-received 오늘 어때x{cnt}')
                    if cnt > 0:
                        pyautogui.hotkey('alt', 'tab') # 화면 전환
                    self.cam.run()
                    pyautogui.hotkey('alt', 'tab')
                    self.web.run('http://0.0.0.0:5000/result/{}/{}'.format(myserial, time.strftime('%Y%m%d', time.localtime(time.time()))))
                    cnt += 1

            else:
                mixer.music.load("./res/잘모르겠어요.mp3")
                mixer.music.play(0)



# if __name__ == "__main__":
#     sample_phrase = "close the tab"
#     command_handler = CommandHandler()
#     print(command_handler.run(sample_phrase))



