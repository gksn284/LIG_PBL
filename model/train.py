# 0. 사용할 패키지 불러오기
import numpy as np
import cv2 as cv
from tensorflow import keras
from keras.utils import plot_model
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import Flatten
from keras.layers import Dropout
from keras.layers.convolutional import Conv2D
from keras.layers.convolutional import MaxPooling2D
from keras.preprocessing.image import ImageDataGenerator


# 랜덤시드 고정시키기
np.random.seed(3)


# 1. 데이터 생성하기
train_datagen = ImageDataGenerator(rescale=1./255)  # 클래스로 객체 생성
# 훈련 제너레이터 생성
train_generator = train_datagen.flow_from_directory(    
        'warehouse/handwriting_shape/train',            # 인풋 이미지 경로 지정
        target_size=(28, 28),                           # 패치 이미지 크기 지정
        batch_size=3,                                   # 배치 크기 지정
        color_mode= "grayscale",                        # 흑백, 채널은 1개
        class_mode='categorical')                       # 분류 방식 지정 -> categorical: 2D one-hot 부호화된 라벨 반환 

# 흑백이미지의 경우 채널 차원이 없는 2차원 배열이지만 conv2D 층을 사용하기 위해 마지막에 채널 차원 (1)을 추가해야 한다. 

test_datagen = ImageDataGenerator(rescale=1./255)
# 테스트 제너레이터 생성
test_generator = test_datagen.flow_from_directory(       
        'warehouse/handwriting_shape/test',             
        target_size=(28, 28),                           
        batch_size=3,                              # 한번에 가져오는 배치 사이즈
        shuffle = False,                           # 섞지 않는다     
        color_mode= "grayscale",                   # 흑백, 채널은 1개
        class_mode='categorical')


# 2. 케라스 모델 구성하기
#2-1 모델 생성하기(층 생성)
model = Sequential()            # 제일 처음으로 받아오는 층: Sequential
model.add(Conv2D(32, kernel_size=(3, 3),    # 필터크기는 3, 활성화함수는 relu
                 activation='relu',
                 input_shape=(28, 28, 1)))      
model.add(MaxPooling2D(pool_size=(4, 4)))
model.add(Conv2D(64, (3, 3), activation='relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))   # 풀링 크기는 2x2
model.add(Flatten())                        # Flaten층            
#model.add(Dropout(0.2))
model.add(Dense(90, activation='relu'))
model.add(Dense(3, activation='softmax'))       


#2-2 케라스 모델 학습과정 설정하기 
model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
# loss: 사용 손실함수, 다중 클래스 문제이므로 저렇게 설정함. optimizer: 가중치 검색 최적화, 효과적인 경사하강법 알고리즘 중 adam 사용
# metrics: 평가척도 나타냄

# 2-2-1 모델 구조 요약
print(model.summary())                                          # tensorflow의 keras 라이브러리에 있다. 모델 구조 출력
#print(keras.utils.plot_model(model, show_shape = True))         # 자세하게 모델 구조 출력

# 2-3 모델 훈련
model.fit_generator(
        train_generator,    #훈련 데이터셋 제공할 제너레이터 지정. 앞에 있던 train_generator 지정
        steps_per_epoch=15, # 한 에포크에 사용할 스텝 수 지정. 45개 훈련샘플, 배치사이즈 3이므로 15스텝 지정
        epochs=50,          # 학습 반복 횟수
        validation_data=test_generator, # 검증데이터셋 제공할 제너레이터 지정
        validation_steps=5)             # 한 에포크 종료마다 검증할때 사용되는 검증 스텝 수 지정. 15개 검증샘플, 배치사이즈 3 -> 5스텝


# 2-4 모델 평가
print("######## Evaluate ########")
scores = model.evaluate_generator(test_generator, steps=5)
print("%s: %.2f%%" %(model.metrics_names[1], scores[1]*100))

# 2-5 모델 저장
model.save('lig_model.h5')


#2-6 모델 사용하기
# print("######### Predict ###########")
# #current_image = tf.keras.utils.load_img('warehouse/handwriting_shape/test/test.png')       # 케라스로 이미지 로드하기
# current_img  = cv.imread('warehouse/handwriting_shape/test/test1.png')                       # opencv로 이미지 로드하기
# #input_arr = tf.keras.utils.img_to_array(current_img)                                       # 이미지 넘파이 배열로 바꾸기? 근데 필요없음.
# input_arr = np.array([current_img])  # Convert single image to a batch.
# pred = model.predict(input_arr)                                             # 예측하기
# #np.set_printoptions(formatter={'float': lambda x: "{0:0.3f}".format(x)})    # x당 0.3f씩만 -> 있어도 되고 없어도 되는 줄

# classes = ['circle', 'triangle', 'star']       # 라벨들
# print(pred)
# # 출력
# #print() # 인덱스만 출력하고 싶을때
# #print(np.where(pred == pred.max()))                   # 넘파이는 인덱스찾는 함수가 numpy.where이다.


# 2-7 모델 테스트
# 제너레이터에서 출력되는걸로 생성하기
# 여러 이미지 데이터 불러올땐 제너레이터로 만든다. 
output = model.predict_generator(test_generator, steps=5)
np.set_printoptions(formatter={'float': lambda x: "{0:0.3f}".format(x)})    # x당 0.3f씩만    
print(test_generator.class_indices)
print(output)

#print('\n'.join(test_generator.filename))   #파일 이름을 엔터키 순서대로 출력해주는 코드


