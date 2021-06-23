import time, datetime, os
import cv2
from cv2 import *
import numpy as np
import threading
from db import upload_file
# from audio import tts
from serial import myserial
from pygame import mixer


icon_path = './res/icon.png'
icon = cv2.imread(icon_path, cv2.IMREAD_UNCHANGED)
W = 1000
H = 1400
icon = cv2.resize(icon, (W,H))

image = icon[:,:,0:3]
alpha = icon[:,:,3]
mask_image = alpha / 255.0
mask_border = 1.0 - mask_image

x1 = 800
y1 = 400
x2 = x1 + W
y2 = y1 + H

class Cam:
    def __init__(self, show=True, framerate=25, width=3280, height=2464):
        global icon

        self.size = (width, height)
        self.show = show
        self.framerate = framerate

        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 2592) #192440
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1944) #1080
        self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
        
        cv2.namedWindow('video',cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty('video', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

        if self.cap.isOpened():
            print(f"width: {self.cap.get(3)}, height: {self.cap.get(4)}")
        else:
            print("No Camera")
    
        self.fname = ''
        self.now = None

        self.face_classfier = cv2.CascadeClassifier("./res/haarcascade_frontalface_default.xml")

        self.tempPeriod = True
        self.cropped_face = None
        self.faces = None
        self.frame = None
        
        mixer.init()

    def face_recognize(self):
        image = cv2.imread(self.fname)
        image_gs = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        cropped_face = None
        faces = self.face_classfier.detectMultiScale(image_gs, scaleFactor=1.1, minNeighbors=1, minSize=(600,600), maxSize=(850,850))
        # 얼굴이 있으면 <class 'numpy.ndarray'>
        # 얼굴이 없으면 <class 'tuple'>
        if type(faces) != tuple:
            for (x,y,w,h) in faces:
                # cv2.imwrite('cropped_'+self.fname, image[y:y+h, x:x+w])
                cv2.imwrite(self.fname, image[y:y+h, x:x+w])
                print(f'w:{w}, h:{h}')
            
            print('-face detected')
            return 1
        else:
            print('-no face detected')
            return 0

    def tempOff(self):
        self.tempPeriod = False    
        print('-preview timeout')    

    def stream_pic(self):
        global W,H, x1, x2, y1, y2
        global image, alpha, mask_image, mask_border
        t = threading.Timer(10, self.tempOff)
        t.start()
        count = 0
        while self.tempPeriod:
            print(f'------------{count}')
            ret, frame = self.cap.read()
            if ret:
                self.frame = frame
                frame_icon = frame.copy()
                for c in range(0,3):
                    frame_icon[y1:y2, x1:x2, c] = (image[:, :, c]*mask_image + frame_icon[y1:y2, x1:x2, c]*mask_border)

                # 이미지 크기 줄여서 출력
                frame_icon = cv2.resize(frame_icon, (800,480))
                cv2.imshow('video', frame_icon)
                if cv2.waitKey(1)==27:
                    cv2.imwrite('test.jpg', frame)
                    self.cap.release()
                    cv2.destroyAllWindows()
                    break    # ESC키
                
            else:
                print("error")
            count += 1
        
        
    def count_pic(self, num):
        time.sleep(2)
        for i in reversed(range(1,num+1)):
            print('play song ------------------------------------', i)
            mixer.music.load(f'./res/{i}.mp3')
            mixer.music.play(0)
            
            time.sleep(1)
        cv2.imwrite(self.fname, self.frame, params=[cv2.IMWRITE_JPEG_QUALITY,100])
        print('============촬영완료')

    def send_data(self):
        # upload_file(self.fname, myserial)
        upload_file('20210531_102835777.jpg', myserial)
        os.remove(self.fname)
        pass

    def run(self):
        self.tempPeriod= True
        self.now = datetime.datetime.now() # 녹화 시작 시간
        self.fname = self.now.strftime("%Y%m%d_%H:%M:%S") +'.jpg'
        
        streamThread = threading.Thread(target=self.stream_pic)
        streamThread.start()

        print('-start preview')
        mixer.music.load("./res/촬영_시작합니다.mp3")
        mixer.music.play(0)

        time.sleep(2)
        self.count_pic(3)
        
        streamThread.join() # streamThread가 끝날때까지 대기
        
        if self.face_recognize():
            mixer.music.load("./res/얼굴_인식_완료.mp3")
            mixer.music.play(0)
            print('얼굴 인식 완료')
            self.send_data()
            time.sleep(3)
            # self.cap.release()
            # cv2.destroyAllWindows()
        else:
            mixer.music.load("./res/얼굴_인식_실패.mp3")
            mixer.music.play(0)
            print('얼굴 인식 실패')
            time.sleep(3)

            os.remove(self.fname)
            self.run()


# stream_pic-> count_pic(사진촬영) -> face_recognize(얼굴인식) -> 있으면 
                                                            # -> 없으면 다시 촬영
    
if __name__ == '__main__':
    cam = Cam()
    cam.run()