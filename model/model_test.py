
# -*- coding: utf-8 -*-
import cv2 as cv
import time
import numpy as np
from matplotlib import pyplot as plt
from keras.models import load_model
import tensorflow as tf

CAM_ID = 0      # camid 설정


'''opencv로 화면 출력 저장, resize하기 캡쳐 함수'''
def capture(camid = CAM_ID):
    start = time.time()
    #cam = cv.VideoCapture(camid, cv.CoAP_DSHOW)                
    cam = cv.VideoCapture(camid)                      #현재 컴퓨터에 연결된 메인 카메라 불러오기 
    if cam.isOpened() == False:                       # 캠 연결 불가시 출력문구
        print ('can''t open the cam (%d)' % camid)    
        return None

    ret, img = cam.read()                   # ret: 읽음 여부, img: 이미지 파일
    if ret == 0:                            # 읽음 실패시 출력문구
        print ('frame is not exist')
        return None
    
    # 사진 전처리
    cv.imwrite('640image.png',img, params=[cv.IMWRITE_PNG_COMPRESSION,0])   # 640 x 480 이미지 저장
    resize_img = cv.resize(img, (28,28))                                    #28 x 28로 사이즈 줄이기
    resize_img_gray = cv.cvtColor(resize_img, cv.COLOR_BGR2GRAY)            # 흑백으로 변환
    

    # 사진 배경 흰색으로 만들기 위한 코드(ndarray에서 변경) 배경 강제로 하얗게 만들기
    ret, resize_img_gray= cv.threshold(resize_img_gray, 50, 255, cv.THRESH_BINARY+cv.THRESH_OTSU)
    #resize_img_gray[resize_img_gray>50] = 255

    # 테스트 사진 저장
    cv.imwrite('24image_gray.png',resize_img_gray, params=[cv.IMWRITE_PNG_COMPRESSION,0])
    end = time.time()

    # 카메라 동적할당 해제
    cam.release()   
    print("opencv time: %f sec" %(end - start))
    return resize_img_gray
    

            
''' main '''

model = load_model('lig_model.h5')  # 모델 불러오기


print("################# model start #######################")  # while문 돌리기
while(True):                                
    #i = 1
    print("press anykey to start, press q to quit \n")
    key_input = input()
    
    if key_input == 'q':        # q 입력시 종료
        break
    
    else: 
        img = capture(CAM_ID)          # 캡쳐함수 실행
        img.resize(1,28,28)            # 2차원인 (24, 24)를 모델에 집어넣기 위해 (1,24,24)로 바꿔준다.
        pred = model.predict(img)      # 예측하기
        np.set_printoptions(formatter={'float': lambda x: "{0:0.3f}".format(x)})    # x당 0.3f씩만 -> 있어도 되고 없어도 되는 줄
        classes = ['circle', 'star', 'triangle']        # 라벨들

        ''' 출력부분   '''
        # 커맨드창 출력
        where = np.where(pred == pred.max())[1][0]      # 넘파이는 인덱스찾는 함수가 numpy.where이다.
        print("###################")
        print(pred)
        print("pattern: " + classes[where])                   
        print("###################\n\n")
        
        # plt로 출력하기
        img = img.reshape(28,28)                         # plt로 띄우기 위해 다시 2차원으로 변경
        plt.imshow(img, cmap='gray')                    # matplotlib으로 화면 송출, 0일수록 검정, 255일수록 하양
        plt.show()

    #i += 1

   
cv.destroyAllWindows()  # 종료





# cap = cv.VideoCapture(0)    #현재 컴퓨터에 연결된 메인 카메라 return
# if not cap.isOpened():
#     print("camera open failed")
#     exit()                      # 카메라가 연결되어 있지 않으면 종료

# ret, img = cap.read()
# if not ret:                     
#     print("Can't read camera")  # 이미지 읽기 실패했을 경우 
    
# cv.imshow('test', img)          # 이미지 윈도우창에 띄우기

# if cv.waitKey(1) == ord('c'):   # 키보드 값이 c면 이미지 저장
#     img_captured = cv.imwrite('img_captured.png', img)
# #elif cv.waitKey(1) == ord('q'):       # 입력에 q가 들어오면 종료 
    
