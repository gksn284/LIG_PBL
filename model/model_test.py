
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
    cam = cv.VideoCapture(camid)                      #현재 컴퓨터에 연결된 메인 카메라 불러오기 
    if cam.isOpened() == False:                       # 캠 연결 불가시 출력문구
        print ('can''t open the cam (%d)' % camid)    
        return None

    ret, img = cam.read()                   # ret: 읽음 여부, img: 이미지 파일
    if ret == 0:                            # 읽음 실패시 출력문구
        print ('frame is not exist')
        return None
    

    


    # 사진 전처리
    # cv.imwrite('640image.png',img, params=[cv.IMWRITE_PNG_COMPRESSION,0])   # 640 x 480 이미지 저장
    img_gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)    # 흑백으로 변환
    
    '''이미지 자르기'''
    img_gray = img_gray[100:330, 130:450]  # y값의 범위, x값의 범위
    cv.imwrite('640image.png',img_gray, params=[cv.IMWRITE_PNG_COMPRESSION,0])   # 640 x 480 이미지 저장

    '''그림자 제거'''
    gray_planes = cv.split(img_gray)

    result_planes = []

    for plane in gray_planes:
        dilated_img = cv.dilate(plane, np.ones((50,50), np.uint8))
        bg_img = cv.medianBlur(dilated_img, 21) # 관심화소 주변 커널 크기(21 x 21) 내의 픽셀을 기준으로 정렬한 후 중간값 뽑아서 픽셀값으로 사용함.
        diff_img = 255 - cv.absdiff(plane, bg_img)  # 현재 이미지와 차이 구함
        result_planes.append(diff_img)
        
    result = cv.merge(result_planes)
    cv.imwrite('shadows_out.png', result)
        
        
    resize_img_gray = cv.resize(result, (28,28))    #28 x 28로 사이즈 줄이기                    
    

    ret, resize_img_gray= cv.threshold(resize_img_gray, 100, 255, cv.THRESH_BINARY+cv.THRESH_OTSU)  #100넘으면 밝게 만듬

    # 테스트 사진 저장
    cv.imwrite('28image_gray_final.png',resize_img_gray, params=[cv.IMWRITE_PNG_COMPRESSION,0])
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
        classes = ['circle', 'squre', 'triangle']        # 라벨들

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
    
