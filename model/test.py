# -*- coding: utf-8 -*-
import cv2 as cv
import time
import numpy as np
from matplotlib import pyplot as plt

CAM_ID = 0  
camid = CAM_ID


start = time.time()
'''비디오 캡쳐'''
#cam = cv.VideoCapture(camid, cv.CoAP_DSHOW)            #현재 컴퓨터에 연결된 메인 카메라 불러오기      
cam = cv.VideoCapture(camid)
if cam.isOpened() == False:
    print ('can''t open the cam (%d)' % camid)    # 캠 연결 불가때
 
ret, img = cam.read()                   # ret: 읽음 여부, img: 이미지 파일
if ret == 0:                            # 읽음 실패시 프린트하기.
    print ('frame is not exist')

cv.imwrite('640image.png',img, params=[cv.IMWRITE_PNG_COMPRESSION,0])   # 640 x 480 이미지 저장
img_gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)    # 흑백으로 변환


'''그림자 제거'''
gray_planes = cv.split(img_gray)

result_planes = []
result_norm_planes = []

for plane in gray_planes:
    dilated_img = cv.dilate(plane, np.ones((50,50), np.uint8))
    bg_img = cv.medianBlur(dilated_img, 21) # 관심화소 주변 커널 크기(21 x 21) 내의 픽셀을 기준으로 정렬한 후 중간값 뽑아서 픽셀값으로 사용함.
    diff_img = 255 - cv.absdiff(plane, bg_img)  # 현재 이미지와 차이 구함
    result_planes.append(diff_img)
    
result = cv.merge(result_planes)
cv.imwrite('shadows_out.png', result)


'''이미지 resize''' 
resize_img = cv.resize(result, (28,28))    #24 x 24로 사이즈 줄이기                    
cv.imwrite('capture_28img.png',resize_img, params=[cv.IMWRITE_PNG_COMPRESSION,0])
print("-----")


'''이미지 흑백변환'''  
cv.imwrite('capture_28img_gray.png',resize_img, params=[cv.IMWRITE_PNG_COMPRESSION,0])
ret2, resize_img_gray= cv.threshold(resize_img, 100, 255, cv.THRESH_BINARY+cv.THRESH_OTSU)    
cv.imwrite('capture_28imag_gray_final.png',resize_img_gray, params=[cv.IMWRITE_PNG_COMPRESSION,0])



end = time.time()
plt.imshow(resize_img_gray, cmap='gray')   # matplotlib으로 화면 송출, 0일수록 검정, 255일수록 하양
plt.show()

cam.release()   # 카메라 동적할당 해제
print("opencv time: %f sec" %(end - start))
