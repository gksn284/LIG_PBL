# -*- coding: utf-8 -*-
import cv2 as cv
import numpy as np
import time
from matplotlib import pyplot as plt
from keras.models import load_model



CAM_ID = 0      # camid 설정


'''opencv로 화면 출력 저장, resize하기 캡쳐 함수'''

    
    


               

  
''' main '''

model = load_model('lig_model.h5')  # 모델 불러오기

# while문 돌리기
print("################# model start #######################")
k = 160

while(True):
    #i = 1
    
    print("press anykey to start, press q to quit \n")
    key_input = input()
    
    if key_input == 'q':        # q 입력시 종료
        break
    
    else: 
        start = time.time()
        #cam = cv.VideoCapture(camid, cv.CoAP_DSHOW)            #현재 컴퓨터에 연결된 메인 카메라 불러오기      
        cam = cv.VideoCapture(CAM_ID)
        if cam.isOpened() == False:
            print ('can''t open the cam (%d)' % CAM_ID)    # 캠 연결 불가때

        ret, img = cam.read()                   # ret: 읽음 여부, img: 이미지 파일
        if ret == 0:                            # 읽음 실패시 프린트하기.
            print ('frame is not exist')
    
        resize_img = cv.resize(img, (28,28))    #24 x 24로 사이즈 줄이기
        resize_img_gray = cv.cvtColor(resize_img, cv.COLOR_BGR2GRAY)
        
        cv.imwrite('test.png',img, params=[cv.IMWRITE_PNG_COMPRESSION,0])
        
        
        # 사진 배경 흰색으로 만들기 위한 2중 for문 -> 배경 강제로 하얗게 만들기
        ret2, resize_img_gray= cv.threshold(resize_img_gray, 40, 255, cv.THRESH_BINARY+cv.THRESH_OTSU)    
        # resize_img_gray[resize_img_gray>100] = 255      # ndarray배열에서 바로 줄이는 방법
         
        
        print(k)
        name = 'sample/test' + str(k) +'.png' 
         
                         # 출력 테스트
        cv.imwrite(name, resize_img_gray, params=[cv.IMWRITE_PNG_COMPRESSION,0])   # 사진 저장
        # print(resize_img_gray)
        #cv.imshow("resize_img", img)
        end = time.time()
        #plt.imshow(resize_img_gray, cmap='gray')   # matplotlib으로 화면 송출, 0일수록 검정, 255일수록 하양
        #plt.show()
        cam.release()   # 카메라 동적할당 해제

        print("opencv time: %f sec" %(end - start))
            #input_arr = tf.keras.utils.img_to_array(current_img)                                       # 이미지 넘파이 배열로 바꾸기? 근데 필요없음.   
        np.set_printoptions(formatter={'float': lambda x: "{0:0.3f}".format(x)})    # x당 0.3f씩만 -> 있어도 되고 없어도 되는 줄
        plt.imshow(resize_img_gray, cmap='gray')                    # matplotlib으로 화면 송출, 0일수록 검정, 255일수록 하양
        plt.show()
        

    k = k + 1
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
        
