from tkinter import *
from tkinter import ttk
from serial import Serial
from PIL import Image, ImageTk
from keras.models import load_model
import tkinter.messagebox as msgbox
import tkinter.font as ft
import serial.tools.list_ports
import sys, natsort, datetime, threading, time, binascii, sys, os
import cv2 as cv
import numpy as np
import winsound as sd

CAM_ID = 1 # camid 설정
connect_state = 0
debug_state = 0
mode_state = 0 # 0: 수동모드, 1: 자동모드
belt_state = 0
auto_state = 0 # 0: 정지, 1: 시작
receive_data = b'\x00\x00\x00\x00\x00'

def port_check(): # 연결 가능한 port check
    ports = serial.tools.list_ports.comports()
    available_ports = []

    for p in ports:
        available_ports.append(p.device)

    available_ports = natsort.natsorted(available_ports)
    port_combobox.config(values=available_ports)

def uart_connect(): # Uart port 연결 버튼
    global py_serial, connect_state

    try:
        py_serial = Serial(port=f'{port_combobox.get()}', baudrate=int(baud_rate_combobox.get()))
        threading.Thread(target=start_U).start()
        connect_state = 1

        frame_1to2_show()
        debug_btn.pack(side="right", padx=1, pady=3)

        write_uart(b'\xA5\x01\x00\x01\x5A')
        ack_check(b'\xA5\x01\x10\x00\x5A')
        
        msgbox.showinfo("알림", "연결되었습니다.")

    except:
        msgbox.showwarning("경고", "연결에 실패하였습니다.\n설정을 확인하십시오.")

def frame_1to2_show(): # Uart → 수동모드
    # Uart Connect연결 후 수동모드 Page 진입
    frame_main1.pack_forget()
    frame_main2.pack(side="top", fill="both", expand=True)
    window_label.config(text="Arm Control Pad (PBL)")

def start_U(): # Uart 메세지 받는 함수
    global py_serial, receive_data, debug_state, window2_log_box

    while True: # 수신 Text 처리
        bytestoread = py_serial.in_waiting
        if(bytestoread > 0):
            receive_data = py_serial.read(5)

            if(debug_state == 1):
                window2_log_box.insert(END, f"[수신] {binascii.hexlify(receive_data)}")
                window2_log_box.update()
                window2_log_box.see(END)

            elif(mode_state == 1 and auto_state == 1): # 자동모드
                if(receive_data == b'\xA5\x3C\xCC\xCC\x5A'): # 캡쳐 제어
                    log_update("초음파 장치에서 물체감지")
                    time.sleep(5)

                    pattern = capture_predict()

                    if(pattern == 0): # ○: 0 패턴정보
                        write_uart(b'\xA5\x30\x00\x11\x5A')
                        log_update("인식된 Pattern: ○")
                    elif(pattern == 1): # □: 1 패턴정보
                        write_uart(b'\xA5\x30\x00\x10\x5A')
                        log_update("인식된 Pattern: ㅁ")
                    elif(pattern == 2): # △: 2 패턴정보
                        write_uart(b'\xA5\x30\x00\x01\x5A')
                        log_update("인식된 Pattern: △")

                elif(receive_data == b'\xA5\x31\x11\x00\x5A'): # Red log
                    log_update("인식된 색상: Red")
                elif(receive_data == b'\xA5\x31\x01\x00\x5A'): # Green log
                    log_update("인식된 색상: Green")
                elif(receive_data == b'\xA5\x31\x10\x00\x5A'): # Blue log
                    log_update("인식된 색상: Blue")

                elif(receive_data == b'\xA5\x41\xAA\xAA\x5A'):
                    log_update("Belt 동작 시작")
                elif(receive_data == b'\xA5\x41\x11\x11\x5A'):
                    log_update("Belt 동작 정지")
                
                elif(receive_data == b'\xA5\x60\x00\x01\x5A'): # A 상자에 대한 명령 수행 log
                    log_update("A 상자로 타겟을 운반 진행")
                    log_enter()
                    count_label1.config(text=str(int(count_label1.cget("text")) + 1))
                elif(receive_data == b'\xA5\x60\x00\x02\x5A'): # B 상자에 대한 명령 수행 log
                    log_update("B 상자로 타겟을 운반 진행")
                    log_enter()
                    count_label2.config(text=str(int(count_label2.cget("text")) + 1))
                elif(receive_data == b'\xA5\x60\x00\x03\x5A'): # C 상자에 대한 명령 수행 log
                    log_update("C 상자로 타겟을 운반 진행")
                    log_enter()
                    count_label3.config(text=str(int(count_label3.cget("text")) + 1))
                elif(receive_data == b'\xA5\x60\xFF\xFF\x5A'): # C 상자에 대한 명령 수행 log
                    log_update("조건에 맞는 상자가 없음 PASS")
                    log_enter()
                                   
def write_uart(byte_hex): # Uart로 Byte 쏘는 함수
    global py_serial
    
    py_serial.write(byte_hex)

def ack_func(byte_hex):
    global receive_data, mode_state

    start_time = time.time()
    timeout = 1
        
    while(True):
        if(receive_data == byte_hex):
            print("Uart Ack 정상 수신") # 나중에 삭제할 줄
            receive_data = b'\x00\x00\x00\x00\x00'
            return
        else:
            if(time.time() > start_time + timeout):
                sd.Beep(3000, 500) # ACk 못 받았을 경우 0.5초 경고음
                print("Uart Ack 수신 불량") # 나중에 삭제할 줄
                receive_data = b'\x00\x00\x00\x00\x00'
                if(mode_state == 1):
                    log_update("Ack Error→ 확인 필요")
                    log_enter()
                msgbox.showwarning("경고", "제어에 실패하였습니다.\n연결을 확인해주십시오.")
                return

def ack_check(byte_hex): # Ack 기다리는 함수
    threading.Thread(target=lambda: ack_func(byte_hex)).start()

def sudong_motor(num): # Motor #1 ~ #5 제어 함수
    if(num == 1): # Motor #1
        motor1 = (motor_var1.get()).to_bytes(1, 'little') # hex단위인 str형으로 받음
        byte = b'\xA5\x11\x00' + motor1 + b'\x5A'
        write_uart(byte)
        ack_check(b'\xA5\x11\xFF\xFF\x5A') # 임시 Ack

    elif(num == 2): # Motor #2
        motor2 = (motor_var2.get()).to_bytes(1, 'little') # hex단위인 str형으로 받음
        byte = b'\xA5\x12\x00' + motor2 + b'\x5A'
        write_uart(byte)
        ack_check(b'\xA5\x12\xFF\xFF\x5A') # 임시 Ack

    elif(num == 3): # Motor #3
        motor3 = (motor_var3.get()).to_bytes(1, 'little') # hex단위인 str형으로 받음
        byte = b'\xA5\x13\x00' + motor3 + b'\x5A'
        write_uart(byte)
        ack_check(b'\xA5\x13\xFF\xFF\x5A') # 임시 Ack

    elif(num == 4): # Motor #4
        motor4 = (motor_var4.get()).to_bytes(1, 'little') # hex단위인 str형으로 받음
        byte = b'\xA5\x14\x00' + motor4 + b'\x5A'
        write_uart(byte)
        ack_check(b'\xA5\x14\xFF\xFF\x5A') # 임시 Ack

    elif(num == 5): # Motor #5
        motor5 = (motor_var5.get()).to_bytes(1, 'little') # hex단위인 str형으로 받음
        byte = b'\xA5\x15\x00' + motor5 + b'\x5A'
        write_uart(byte)
        ack_check(b'\xA5\x15\xFF\xFF\x5A') # 임시 Ack

def sudong_wave():
    def receive_func():
        global receive_data

        start_time = time.time()
        timeout = 1
        
        while(True):
            if(time.time() > start_time + timeout):
                sd.Beep(3000, 500) # receive 못 받았을 경우 0.5초 경고음
                print("Uart receive 수신 불량") # 나중에 삭제할 코드
                receive_data = b'\x00\x00\x00\x00\x00'
                return
            else:
                if(receive_data == b'\xA5\x32\x00\x01\x5A'): # 물체 없음 정보 수신
                    print("Uart 물체 없음 정보 수신") # 나중에 삭제할 코드
                    wave_label.config(text='X')
                    receive_data = b'\x00\x00\x00\x00\x00'
                    return
                elif(receive_data == b'\xA5\x32\x10\x00\x5A'): # 물체 존재 정보 수신
                    print("Uart 물체 존재 정보 수신") # 나중에 삭제할 코드
                    wave_label.config(text='O')
                    receive_data = b'\x00\x00\x00\x00\x00'
                    return

    write_uart(b'\xA5\x3B\xBB\xBB\x5A') # 초음파 센서 정보 요청
    threading.Thread(target=receive_func).start()
    
def sudong_rgb():
    def receive_func():
        global receive_data

        start_time = time.time()
        timeout = 1
        
        while(True):
            if(time.time() > start_time + timeout):
                sd.Beep(3000, 500) # receive 못 받았을 경우 0.5초 경고음
                print("Uart receive 수신 불량") # 나중에 삭제할 코드
                receive_data = b'\x00\x00\x00\x00\x00'
                return
            else:
                if(receive_data == b'\xA5\x31\x11\x00\x5A'): # Red 정보 수신
                    print("Uart Red 정보 수신") # 나중에 삭제할 코드
                    rgb_frame.config(text="Red", bg="red")
                    receive_data = b'\x00\x00\x00\x00\x00'
                    return
                elif(receive_data == b'\xA5\x31\x01\x00\x5A'): # Green 정보 수신
                    print("Uart Green 정보 수신") # 나중에 삭제할 코드
                    rgb_frame.config(text="Green", bg="green")
                    receive_data = b'\x00\x00\x00\x00\x00'
                    return
                elif(receive_data == b'\xA5\x31\x10\x00\x5A'): # Blue 정보 수신
                    print("Uart Blue 정보 수신") # 나중에 삭제할 코드
                    rgb_frame.config(text="Blue", bg="Blue")
                    receive_data = b'\x00\x00\x00\x00\x00'
                    return

    write_uart(b'\xA5\x3A\xAA\xAA\x5A') # rgb 센서 정보 요청
    threading.Thread(target=receive_func).start()

def sudong_belt():
    global belt_state

    if(belt_state == 0): # 벨트 동작
        write_uart(b'\xA5\x16\x0F\xF0\x5A')
        ack_check(b'\xA5\x41\xAA\xAA\x5A') # Ack
        belt_btn.config(text='Off')
        belt_state = 1
    else: # 벨트 정지
        write_uart(b'\xA5\x16\x01\x10\x5A')
        ack_check(b'\xA5\x41\x11\x11\x5A') # Ack
        belt_btn.config(text='On')
        belt_state = 0   

def sudong_select_btn():
    global mode_state

    mode_state = 0 # 수동 모드 진입 변수 설정

    write_uart(b'\xA5\x10\x11\x11\x5A')
    ack_check(b'\xA5\xF0\x1F\x1F\x5A')

    motor_btn1.config(state="normal")
    motor_btn2.config(state="normal")
    motor_btn3.config(state="normal")
    motor_btn4.config(state="normal")
    motor_btn5.config(state="normal")
    belt_btn.config(state="normal")
    wave_btn.config(state="normal")
    rgb_btn.config(state="normal")
    pattern_btn.config(state="normal")

    opt1_btn.config(state="disabled")
    opt2_btn.config(state="disabled")
    opt3_btn.config(state="disabled")
    btn_start.config(state="disabled")
    btn_reset.config(state="disabled")

def auto_select_btn():
    global mode_state, auto_state

    log_update("Auto Mode 시작")
    log_enter()

    mode_state = 1 # 자동 모드 진입 변수 설정

    write_uart(b'\xA5\x10\xFF\xFF\x5A')
    ack_check(b'\xA5\xF0\xF1\xF1\x5A')

    if(auto_state == 1):
        write_uart(b'\xA5\x2A\x00\xFF\x5A')
        ack_check(b'\xA5\x4B\x00\xFF\x5A') # Ack
        auto_state = 0
    
    motor_btn1.config(state="disabled")
    motor_btn2.config(state="disabled")
    motor_btn3.config(state="disabled")
    motor_btn4.config(state="disabled")
    motor_btn5.config(state="disabled")
    belt_btn.config(state="disabled")
    wave_btn.config(state="disabled")
    rgb_btn.config(state="disabled")
    pattern_btn.config(state="disabled")

    opt1_btn.config(state="normal")
    opt2_btn.config(state="normal")
    opt3_btn.config(state="normal")
    btn_start.config(state="normal")
    btn_reset.config(state="disabled")

def debug_page():
    global debug_state, window2, window2_log_box

    debug_state = 1

    def debug_func():
        msg = debug_val.get()
        
        if(len(msg) != 10):
            msgbox.showwarning("경고", "5 Byte단위로만 전송해야합니다.\n다시 확인해주세요.")
            return

        write_uart(binascii.unhexlify(msg))

        window2_log_box.insert(END, f"[송신] b\'{msg}\'")
        window2_log_box.update()
        window2_log_box.see(END)

    def debug_close():
        global debug_state, window2

        window2.destroy()
        debug_state = 0

    window2 = Tk()
    window2.wm_attributes("-topmost",1)
    window2.title("Debug")
    window2.geometry("-1005+0")
    window2.resizable(False, False)

    window2_top = Frame(window2)
    window2_top.pack(side="top", fill="both", expand=True)

    window2_scrollbar = Scrollbar(window2_top)
    window2_scrollbar.pack(side="right" ,fill ="y")
    window2_log_box = Listbox(window2_top, yscrollcommand=window2_scrollbar.set, width=30, height=10, selectbackground="green", takefocus=False, activestyle="none")
    window2_log_box.pack(side="left", fill="y")

    window2_middle = Frame(window2)
    window2_middle.pack(side="top", fill="both", expand=True)
    
    debug_val = Entry(window2_middle)
    debug_val.insert(0, "00112233FF")
    debug_val.pack(side="left", fill="both", expand = True, padx=5, pady=5, ipady=4)

    debug_val_btn = Button(window2_middle, text="전송", width = 4, command=debug_func, fg="black")
    debug_val_btn.pack(side="right", padx=1, pady=3)

    window2_bottom = Frame(window2)
    window2_bottom.pack(side="top", fill="both", expand=True)
    
    ttk.Separator(window2_bottom, orient='horizontal').pack(side="top", fill="x", padx=1, pady=1)
    close_btn = Button(window2_bottom, text="닫기", command=debug_close, fg="red")
    close_btn.pack(side="top", fill="both", expand = True, padx=1, pady=3)

    window2.mainloop()

def log_update(msg):
    now = str(datetime.datetime.now())[2:-7]
    log_box.insert(END, f"[{now}] {msg}")
    log_box.update()
    log_box.see(END)

def log_enter():
    log_box.insert(END, "")
    log_box.update()
    log_box.see(END)

def capture_predict(camid = CAM_ID): # 사진 찍고 예측값 반환
    cam = cv.VideoCapture(camid)
    if cam.isOpened() == False:
        print ('can''t open the cam (%d)' % camid)    # 캠 연결 불가때
        return None

    ret, img = cam.read()                   # ret: 읽음 여부, img: 이미지 파일
    if ret == 0:                            # 읽음 실패시 프린트하기.
        print ('frame is not exist')
        return None
    
    cv.imwrite("test1.png", img)
    img_gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)    # 흑백으로 변환
    img_gray = img_gray[60:430, 100:450]  # y값의 범위, x값의 범위 640 x 480
    cv.imwrite( "test2.png", img_gray)
    gray_planes = cv.split(img_gray)
    result_planes = []

    for plane in gray_planes:
        dilated_img = cv.dilate(plane, np.ones((50,50), np.uint8))
        bg_img = cv.medianBlur(dilated_img, 21) # 관심화소 주변 커널 크기(21 x 21) 내의 픽셀을 기준으로 정렬한 후 중간값 뽑아서 픽셀값으로 사용함.
        diff_img = 255 - cv.absdiff(plane, bg_img)  # 현재 이미지와 차이 구함
        result_planes.append(diff_img)
        
    result = cv.merge(result_planes)

    resize_img = cv.resize(result, (28,28))                                    #28 x 28로 사이즈 줄이기
    ret, resize_img = cv.threshold(resize_img, 100, 255, cv.THRESH_BINARY+cv.THRESH_OTSU)

    cam.release()   # 카메라 동적할당 해제

    resize_img.resize(1,28,28)
    pred = model.predict(resize_img)                                             # 예측하기
    where = np.where(pred == pred.max())[1][0]      # 넘파이는 인덱스찾는 함수가 numpy.where이다.

    if where == 0: # circle
        pattern_label.config(text="○")
    elif where == 1: # square
        pattern_label.config(text="□")
    else: # triangle
        pattern_label.config(text="△")

    image = cv.cvtColor(img, cv.COLOR_BGR2RGB)
    image = Image.fromarray(image)
    image = ImageTk.PhotoImage(image)
    img_label.config(image=image)
    img_label.image=image

    return where

def option_update1():
    c1 = color_radio_var1.get()
    c2 = color_radio_var2.get()
    c3 = color_radio_var3.get()
    p1 = pattern_radio_var1.get()
    p2 = pattern_radio_var2.get()
    p3 = pattern_radio_var3.get()

    if(((c1 == c2) and (p1 == p2)) or ((c3 == c1) and (p3 == p1))):
        msgbox.showwarning("경고", "중복되는 설정입니다.\n다시 설정하십시오.")
        return

    if(c1 == 1): # color 선택이 Red 일때
        if(p1 == 1): # pattern 선택이 ○일 때
            write_uart(b'\xA5\x20\x11\x11\x5A')
            ack_check(b'\xA5\x4A\x11\x11\x5A')
            state1_img = PhotoImage(file=resource_path("./img/auto_img/red_circle.png"))
            log_update("A 상자 → Red, Circle 분류 Set")
            log_enter()
        elif(p1 == 2): # pattern 선택이 □일 때
            write_uart(b'\xA5\x20\x11\x10\x5A')
            ack_check(b'\xA5\x4A\x11\x10\x5A')
            state1_img = PhotoImage(file=resource_path("./img/auto_img/red_square.png"))
            log_update("A 상자 → Red, Square 분류 Set")
            log_enter()
        elif(p1 == 3): # pattern 선택이 △일 때
            write_uart(b'\xA5\x20\x11\x01\x5A')
            ack_check(b'\xA5\x4A\x11\x01\x5A')
            state1_img = PhotoImage(file=resource_path("./img/auto_img/red_triangle.png"))
            log_update("A 상자 → Red, Triangle 분류 Set")
            log_enter()

    elif(c1 == 2): # color 선택이 Green 일때
        if(p1 == 1): # pattern 선택이 ○일 때
            write_uart(b'\xA5\x20\x01\x11\x5A')
            ack_check(b'\xA5\x4A\x01\x11\x5A')
            state1_img = PhotoImage(file=resource_path("./img/auto_img/green_circle.png"))
            log_update("A 상자 → Green, Circle 분류 Set")
            log_enter()
        elif(p1 == 2): # pattern 선택이 □일 때
            write_uart(b'\xA5\x20\x01\x10\x5A')
            ack_check(b'\xA5\x4A\x01\x10\x5A')
            state1_img = PhotoImage(file=resource_path("./img/auto_img/green_square.png"))
            log_update("A 상자 → Green, Square 분류 Set")
            log_enter()
        elif(p1 == 3): # pattern 선택이 △일 때
            write_uart(b'\xA5\x20\x01\x01\x5A')
            ack_check(b'\xA5\x4A\x01\x01\x5A')
            state1_img = PhotoImage(file=resource_path("./img/auto_img/green_triangle.png"))
            log_update("A 상자 → Green, Triangle 분류 Set")
            log_enter()

    elif(c1 == 3): # color 선택이 Blue 일때
        if(p1 == 1): # pattern 선택이 ○일 때
            write_uart(b'\xA5\x20\x10\x11\x5A')
            ack_check(b'\xA5\x4A\x10\x11\x5A')
            state1_img = PhotoImage(file=resource_path("./img/auto_img/blue_circle.png"))
            log_update("A 상자 → Blue, Circle 분류 Set")
            log_enter()
        elif(p1 == 2): # pattern 선택이 □일 때
            write_uart(b'\xA5\x20\x10\x10\x5A')
            ack_check(b'\xA5\x4A\x10\x10\x5A')
            state1_img = PhotoImage(file=resource_path("./img/auto_img/blue_square.png"))
            log_update("A 상자 → Blue, Square 분류 Set")
            log_enter()
        elif(p1 == 3): # pattern 선택이 △일 때
            write_uart(b'\xA5\x20\x10\x01\x5A')
            ack_check(b'\xA5\x4A\x10\x01\x5A')
            state1_img = PhotoImage(file=resource_path("./img/auto_img/blue_triangle.png"))
            log_update("A 상자 → Blue, Triangle 분류 Set")
            log_enter()

    opt_state1.config(image=state1_img)
    opt_state1.image = state1_img

def option_update2():
    c1 = color_radio_var1.get()
    c2 = color_radio_var2.get()
    c3 = color_radio_var3.get()
    p1 = pattern_radio_var1.get()
    p2 = pattern_radio_var2.get()
    p3 = pattern_radio_var3.get()

    if(((c1 == c2) and (p1 == p2)) or ((c3 == c2) and (p3 == p2))):
        msgbox.showwarning("경고", "중복되는 설정입니다.\n다시 설정하십시오.")
        return
    
    if(c2 == 1): # color 선택이 Red 일때
        if(p2 == 1): # pattern 선택이 ○일 때
            write_uart(b'\xA5\x21\x11\x11\x5A')
            ack_check(b'\xA5\x4A\x11\x11\x5A')
            state2_img = PhotoImage(file=resource_path("./img/auto_img/red_circle.png"))
            log_update("B 상자 → Red, Circle 분류 Set")
        elif(p2 == 2): # pattern 선택이 □일 때
            write_uart(b'\xA5\x21\x11\x10\x5A')
            ack_check(b'\xA5\x4A\x11\x10\x5A')
            state2_img = PhotoImage(file=resource_path("./img/auto_img/red_square.png"))
            log_update("B 상자 → Red, Square 분류 Set")
        elif(p2 == 3): # pattern 선택이 △일 때
            write_uart(b'\xA5\x21\x11\x01\x5A')
            ack_check(b'\xA5\x4A\x11\x01\x5A')
            state2_img = PhotoImage(file=resource_path("./img/auto_img/red_triangle.png"))
            log_update("B 상자 → Red, Triangle 분류 Set")

    elif(c2 == 2): # color 선택이 Green 일때
        if(p2 == 1): # pattern 선택이 ○일 때
            write_uart(b'\xA5\x21\x01\x11\x5A')
            ack_check(b'\xA5\x4A\x01\x11\x5A')
            state2_img = PhotoImage(file=resource_path("./img/auto_img/green_circle.png"))
            log_update("B 상자 → Green, Circle 분류 Set")
        elif(p2 == 2): # pattern 선택이 □일 때
            write_uart(b'\xA5\x21\x01\x10\x5A')
            ack_check(b'\xA5\x4A\x01\x10\x5A')
            state2_img = PhotoImage(file=resource_path("./img/auto_img/green_square.png"))
            log_update("B 상자 → Green, Square 분류 Set")
        elif(p2 == 3): # pattern 선택이 △일 때
            write_uart(b'\xA5\x21\x01\x01\x5A')
            ack_check(b'\xA5\x4A\x01\x01\x5A')
            state2_img = PhotoImage(file=resource_path("./img/auto_img/green_triangle.png"))
            log_update("B 상자 → Green, Triangle 분류 Set")

    elif(c2 == 3): # color 선택이 Blue 일때
        if(p2 == 1): # pattern 선택이 ○일 때
            write_uart(b'\xA5\x21\x10\x11\x5A')
            ack_check(b'\xA5\x4A\x10\x11\x5A')
            state2_img = PhotoImage(file=resource_path("./img/auto_img/blue_circle.png"))
            log_update("B 상자 → Blue, Circle 분류 Set")
        elif(p2 == 2): # pattern 선택이 □일 때
            write_uart(b'\xA5\x21\x10\x10\x5A')
            ack_check(b'\xA5\x4A\x10\x10\x5A')
            state2_img = PhotoImage(file=resource_path("./img/auto_img/blue_square.png"))
            log_update("B 상자 → Blue, Square 분류 Set")
        elif(p2 == 3): # pattern 선택이 △일 때
            write_uart(b'\xA5\x21\x10\x01\x5A')
            ack_check(b'\xA5\x4A\x10\x01\x5A')
            state2_img = PhotoImage(file=resource_path("./img/auto_img/blue_triangle.png"))
            log_update("B 상자 → Blue, Triangle 분류 Set")

    opt_state2.config(image=state2_img)
    opt_state2.image = state2_img

def option_update3():
    c1 = color_radio_var1.get()
    c2 = color_radio_var2.get()
    c3 = color_radio_var3.get()
    p1 = pattern_radio_var1.get()
    p2 = pattern_radio_var2.get()
    p3 = pattern_radio_var3.get()

    if(((c3 == c2) and (p3 == p2)) or ((c3 == c1) and (p3 == p1))):
        msgbox.showwarning("경고", "중복되는 설정입니다.\n다시 설정하십시오.")
        return

    if(c3 == 1): # color 선택이 Red 일때
        if(p3 == 1): # pattern 선택이 ○일 때
            write_uart(b'\xA5\x22\x11\x11\x5A')
            ack_check(b'\xA5\x4A\x11\x11\x5A')
            state3_img = PhotoImage(file=resource_path("./img/auto_img/red_circle.png"))
            log_update("C 상자 → Red, Circle 분류 Set")
        elif(p3 == 2): # pattern 선택이 □일 때
            write_uart(b'\xA5\x22\x11\x10\x5A')
            ack_check(b'\xA5\x4A\x11\x10\x5A')
            state3_img = PhotoImage(file=resource_path("./img/auto_img/red_square.png"))
            log_update("C 상자 → Red, Square 분류 Set")
        elif(p3 == 3): # pattern 선택이 △일 때
            write_uart(b'\xA5\x22\x11\x01\x5A')
            ack_check(b'\xA5\x4A\x11\x01\x5A')
            state3_img = PhotoImage(file=resource_path("./img/auto_img/red_triangle.png"))
            log_update("C 상자 → Red, Triangle 분류 Set")

    elif(c3 == 2): # color 선택이 Green 일때
        if(p3 == 1): # pattern 선택이 ○일 때
            write_uart(b'\xA5\x22\x01\x11\x5A')
            ack_check(b'\xA5\x4A\x01\x11\x5A')
            state3_img = PhotoImage(file=resource_path("./img/auto_img/green_circle.png"))
            log_update("C 상자 → Green, Circle 분류 Set")
        elif(p3== 2): # pattern 선택이 □일 때
            write_uart(b'\xA5\x22\x01\x10\x5A')
            ack_check(b'\xA5\x4A\x01\x10\x5A')
            state3_img = PhotoImage(file=resource_path("./img/auto_img/green_square.png"))
            log_update("C 상자 → Green, Square 분류 Set")
        elif(p3 == 3): # pattern 선택이 △일 때
            write_uart(b'\xA5\x22\x01\x01\x5A')
            ack_check(b'\xA5\x4A\x01\x01\x5A')
            state3_img = PhotoImage(file=resource_path("./img/auto_img/green_triangle.png"))
            log_update("C 상자 → Green, Triangle 분류 Set")

    elif(c3 == 3): # color 선택이 Blue 일때
        if(p3== 1): # pattern 선택이 ○일 때
            write_uart(b'\xA5\x22\x10\x11\x5A')
            ack_check(b'\xA5\x4A\x10\x11\x5A')
            state3_img = PhotoImage(file=resource_path("./img/auto_img/blue_circle.png"))
            log_update("C 상자 → Blue, Circle 분류 Set")
        elif(p3 == 2): # pattern 선택이 □일 때
            write_uart(b'\xA5\x22\x10\x10\x5A')
            ack_check(b'\xA5\x4A\x10\x10\x5A')
            state3_img = PhotoImage(file=resource_path("./img/auto_img/blue_square.png"))
            log_update("C 상자 → Blue, Square 분류 Set")
        elif(p3 == 3): # pattern 선택이 △일 때
            write_uart(b'\xA5\x22\x10\x01\x5A')
            ack_check(b'\xA5\x4A\x10\x01\x5A')
            state3_img = PhotoImage(file=resource_path("./img/auto_img/blue_triangle.png"))
            log_update("C 상자 → Blue, Triangle 분류 Set")

    opt_state3.config(image=state3_img)
    opt_state3.image = state3_img

def auto_mode_start(event):
    global mode_state, auto_state

    if(mode_state == 1 and auto_state == 0):
        log_update("※자동 분류 시작※")
        log_enter()

        write_uart(b'\xA5\x2A\x00\xFF\x5A')
        ack_check(b'\xA5\x4B\x00\xFF\x5A') # Ack

        btn_start.config(state="disabled")
        btn_reset.config(state="normal")

        auto_state = 1
    else:
        msgbox.showwarning("경고", "동작 상태를 확인해주십시오.")

def auto_mode_reset(event):
    global mode_state, auto_state

    if(mode_state == 1 and auto_state == 1):
        write_uart(b'\xA5\x2A\xFF\x00\x5A')
        ack_check(b'\xA5\x4B\xFF\x00\x5A') # 임시 Ack

        btn_start.config(state="normal")
        btn_reset.config(state="disabled")

        log_update("※자동 분류 정지※")
        log_enter()

        auto_state = 0
    else:
        msgbox.showwarning("경고", "동작 상태를 확인해주십시오.")

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def stop():
    global py_serial, connect_state

    if connect_state == 1:
        py_serial.close()
        
    window.quit()
    sys.exit()
    
# =============================================================================================================================================#
window = Tk()
window.wm_attributes("-topmost",1)
window.title("Arm Control")
window.geometry("-0+0")
window.resizable(False, False)

font1 = ft.Font(family="맑은 고딕", size=15, slant="italic", weight="bold")
font2 = ft.Font(family="맑은 고딕", size=15, weight="bold")
font3 = ft.Font(family="맑은 고딕", size=60, weight="bold")
font4 = ft.Font(family="맑은 고딕", size=15)

window_top = Frame(window)
window_top.pack(side="top", fill="both", expand=True)

window_label = Label(window_top, text=f"Control Connection", font = ("맑은 고딕",18))
window_label.pack(side='left', fill="both", expand=True)

debug_btn = Button(window_top, text="Debug", width = 5, command=debug_page, fg="green", bg='yellow')

################################################################################################################################################
frame_main1 = Frame(window)
frame_main1.pack(side="top", fill="both", expand=True)

frame_port = LabelFrame(frame_main1, text="Port Num", fg='blue')
frame_port.pack(side="top")
# port_value = ["COM" + str(i) for i in range(1, 16)]
port_combobox = ttk.Combobox(frame_port, width = 20, height=10, values=None, state="readonly", font=("맑은 고딕",14))
port_combobox.pack(side="top", padx=1, pady=3)

frame_baud_rate = LabelFrame(frame_main1, text="Baud Rate", fg='blue')
frame_baud_rate.pack(side="top")
baud_rate_value = ["1200", "2400", "4800", "9600", "14400", "19200", "28800", "38400", "57600", "115200"]
baud_rate_combobox = ttk.Combobox(frame_baud_rate, width = 20, height=10, values=baud_rate_value, state="readonly", font=("맑은 고딕",14))
baud_rate_combobox.current(9)
baud_rate_combobox.pack(side="top", padx=1, pady=3)

frame_main1_2 = Frame(frame_main1)
frame_main1_2.pack(side="top", fill="both", expand=True)

btn_connect = Button(frame_main1_2, text="Uart Connect", width = 10, command=uart_connect, font = font1)
btn_connect.pack(side="left", padx=1, pady=3, fill="both", expand=True)

btn_re = Button(frame_main1_2, text="↺", width = 3, command=port_check, font = font2)
btn_re.pack(side="right", padx=1, pady=3, fill="both", expand=True)

############################################################수동모드
frame_main2 = Frame(window)

notebook = ttk.Notebook(frame_main2, width=1000, height=600)
notebook.pack()

notebook_sudong=ttk.Frame(notebook)
# notebook_sudong=ttk.Frame(notebook, cursor="wait")
notebook.add(notebook_sudong, text="수동모드")

notebook_sudong_1 = Frame(notebook_sudong)
notebook_sudong_1.pack(side="left", fill="both", expand=True)

notebook_sudong_1_0 = LabelFrame(notebook_sudong_1, text="Manual Mode Control", font=font2) # 수동 모드 조작
notebook_sudong_1_0.pack(side="top", fill="both")
sudong_btn = Button(notebook_sudong_1_0, text="시작", width = 5, command=sudong_select_btn, fg="blue")
sudong_btn.pack(side="top", padx=1, pady=3, fill="both", expand=True)

notebook_sudong_1_1 = LabelFrame(notebook_sudong_1, text="Motor#1", font=font2) # PWM 조작 바1
notebook_sudong_1_1.pack(side="top")
motor_var1 = IntVar()
scale1 = Scale(notebook_sudong_1_1, variable=motor_var1, orient=HORIZONTAL, from_=60, to=180, width=20, length=300, fg='green', cursor="dot").pack(side="left", fill="both")
motor_btn1 = Button(notebook_sudong_1_1, text="동작", width = 5, command=lambda: sudong_motor(1), fg="green", state="disabled")
motor_btn1.pack(side="right", padx=1, pady=3, fill="both", expand=True)

notebook_sudong_1_2 = LabelFrame(notebook_sudong_1, text="Motor#2", font=font2) # PWM 조작 바2
notebook_sudong_1_2.pack(side="top")
motor_var2 = IntVar()
scale2 = Scale(notebook_sudong_1_2, variable=motor_var2, orient=HORIZONTAL, from_=0, to=180, width=20, length=300, fg='green', cursor="dot").pack(side="left", fill="both")
motor_btn2 = Button(notebook_sudong_1_2, text="동작", width = 5, command=lambda: sudong_motor(2), fg="green", state="disabled")
motor_btn2.pack(side="right", padx=1, pady=3, fill="both", expand=True)

notebook_sudong_1_3 = LabelFrame(notebook_sudong_1, text="Motor#3", font=font2) # PWM 조작 바3
notebook_sudong_1_3.pack(side="top")
motor_var3 = IntVar()
scale3 = Scale(notebook_sudong_1_3, variable=motor_var3, orient=HORIZONTAL, from_=30, to=70, width=20, length=300, fg='green', cursor="dot").pack(side="left", fill="both")
motor_btn3 = Button(notebook_sudong_1_3, text="동작", width = 5, command=lambda: sudong_motor(3), fg="green", state="disabled")
motor_btn3.pack(side="right", padx=1, pady=3, fill="both", expand=True)

notebook_sudong_1_4 = LabelFrame(notebook_sudong_1, text="Motor#4", font=font2) # PWM 조작 바4
notebook_sudong_1_4.pack(side="top")
motor_var4 = IntVar()
scale4 = Scale(notebook_sudong_1_4, variable=motor_var4, orient=HORIZONTAL, from_=10, to=60, width=20, length=300, fg='green', cursor="dot").pack(side="left", fill="both")
motor_btn4 = Button(notebook_sudong_1_4, text="동작", width = 5, command=lambda: sudong_motor(4), fg="green", state="disabled")
motor_btn4.pack(side="right", padx=1, pady=3, fill="both", expand=True)

notebook_sudong_1_5 = LabelFrame(notebook_sudong_1, text="Motor#5", font=font2) # PWM 조작 바5
notebook_sudong_1_5.pack(side="top")
motor_var5 = IntVar()
scale5 = Scale(notebook_sudong_1_5, variable=motor_var5, orient=HORIZONTAL, from_=65, to=145, width=20, length=300, fg='green', cursor="dot").pack(side="left", fill="both")
motor_btn5 = Button(notebook_sudong_1_5, text="동작", width = 5, command=lambda: sudong_motor(5), fg="green", state="disabled")
motor_btn5.pack(side="right", padx=1, pady=3, fill="both", expand=True)

notebook_sudong_1_6 = LabelFrame(notebook_sudong_1, text="벨트", font=font2) # 벨트 On/Off
notebook_sudong_1_6.pack(side="left")
belt_btn = Button(notebook_sudong_1_6, text="On", width = 13, height=6, command=sudong_belt, fg="brown", state="disabled")
belt_btn.pack(side="top", padx=1, pady=3, fill="both", expand=True)

notebook_sudong_1_7 = LabelFrame(notebook_sudong_1, text="초음파 센서", font=font2) # 초음파 센서 Checking
notebook_sudong_1_7.pack(side="right", fill="both", expand=True)
wave_btn = Button(notebook_sudong_1_7, text="Check", width = 13, height=6, command=sudong_wave, fg="brown", state="disabled")
wave_btn.pack(side="left", padx=1, pady=3)
notebook_sudong_1_7_2 = Frame(notebook_sudong_1_7)
notebook_sudong_1_7_2.pack(side="right", fill="both", expand=True)
wave_label = Label(notebook_sudong_1_7_2, text="無", font=font3, fg='blue')
wave_label.pack(side="bottom")

notebook_sudong_2 = Frame(notebook_sudong)
notebook_sudong_2.pack(side="right", fill="both", expand=True)

notebook_sudong_2_1 = Frame(notebook_sudong_2)
notebook_sudong_2_1.pack(side="top", fill="both", expand=True)

notebook_sudong_2_1_1 = LabelFrame(notebook_sudong_2_1, text="RGB 센서", font=font2)
notebook_sudong_2_1_1.pack(side="left", fill="both", expand=True)

rgb_btn = Button(notebook_sudong_2_1_1, text="Check", width = 13, height=6, command=sudong_rgb, fg="darkorange", state="disabled")
rgb_btn.pack(side="left", padx=1, pady=3)
rgb_frame = LabelFrame(notebook_sudong_2_1_1, fg='white', bg='white') # 색 판별에 따라  bg바뀜
rgb_frame.pack(side="right", fill="both", expand=True)

notebook_sudong_2_1_2 = LabelFrame(notebook_sudong_2_1, text="패턴 인식", font=font2)
notebook_sudong_2_1_2.pack(side="right", fill="both", expand=True)

pattern_btn = Button(notebook_sudong_2_1_2, text="Check", width = 13, height=6, command=capture_predict, fg="darkorange", state="disabled")
pattern_btn.pack(side="left", padx=1, pady=3)
pattern_label = Label(notebook_sudong_2_1_2, text="無", font=font3, fg='purple')
pattern_label.pack()

notebook_sudong_2_2 = Frame(notebook_sudong_2)
notebook_sudong_2_2.pack(side="top", fill="both", expand=True)

init_img = ImageTk.PhotoImage(Image.open(resource_path("./img/init.png")))
img_label = Label(notebook_sudong_2_2, image=init_img)
img_label.pack(side="top")

############################################################자동모드
notebook_auto=ttk.Frame(notebook)
notebook.add(notebook_auto, text="자동모드")

notebook_auto_1 = Frame(notebook_auto) # 로그를 나타내는 부분
notebook_auto_1.pack(side="left", fill="both")

notebook_auto_1_1 = LabelFrame(notebook_auto_1, text="Auto Mode Control", font=font2) # 수동 모드 조작
notebook_auto_1_1.pack(side="top", fill="both")
auto_btn = Button(notebook_auto_1_1, text="시작", width=45, command=auto_select_btn, fg="blue")
auto_btn.pack(side="top", padx=1, pady=3, fill="both")

notebook_auto_1_2 = Frame(notebook_auto_1) # 로그를 나타내는 부분
notebook_auto_1_2.pack(side="top", fill='both', expand=True)

scrollbar = Scrollbar(notebook_auto_1_2)
scrollbar.pack(side="right" ,fill ="y")
log_box = Listbox(notebook_auto_1_2, yscrollcommand=scrollbar.set, width=45, height=10, selectbackground="green", takefocus=False, activestyle="none")
log_box.pack(side="left", fill="y")

notebook_auto_2 = Frame(notebook_auto) # 옵션을 나타내는 부분
notebook_auto_2.pack(side="right", fill="both", expand=True)

notebook_auto_2_1 = LabelFrame(notebook_auto_2, text="A 상자 옵션", font=font2) # A 상자 옵션
notebook_auto_2_1.pack(side="top", fill="both")

notebook_auto_2_1_1 = LabelFrame(notebook_auto_2_1, text="Color", font=font4) # A 상자 색상
notebook_auto_2_1_1.pack(side="left", fill="both")

color_radio_var1 = IntVar()
color_radio1 = Radiobutton(notebook_auto_2_1_1, text="Red", fg='red', value=1, variable=color_radio_var1)
color_radio1.pack(side='left')
color_radio2 = Radiobutton(notebook_auto_2_1_1, text="Green", fg='green', value=2, variable=color_radio_var1)
color_radio2.pack(side='left')
color_radio3 = Radiobutton(notebook_auto_2_1_1, text="Blue", fg='blue', value=3, variable=color_radio_var1)
color_radio3.pack(side='left')
color_radio1.select()

notebook_auto_2_1_2 = LabelFrame(notebook_auto_2_1, text="Pattern", font=font4) # A 상자 패턴
notebook_auto_2_1_2.pack(side="left", fill="both")

pattern_radio_var1 = IntVar()
pattern_radio1 = Radiobutton(notebook_auto_2_1_2, text="○", value=1, variable=pattern_radio_var1)
pattern_radio1.pack(side='left')
pattern_radio2 = Radiobutton(notebook_auto_2_1_2, text="□", value=2, variable=pattern_radio_var1)
pattern_radio2.pack(side='left')
pattern_radio3 = Radiobutton(notebook_auto_2_1_2, text="△", value=3, variable=pattern_radio_var1)
pattern_radio3.pack(side='left')
pattern_radio1.select()

notebook_auto_2_1_3 = LabelFrame(notebook_auto_2_1, text="Count", font=font4) # A 상자 count
notebook_auto_2_1_3.pack(side="left", fill="both")

count_label1 = Label(notebook_auto_2_1_3, text="0", font = ("맑은 고딕",20))
count_label1.pack(side='top', fill="both", expand=True)

state1_img = PhotoImage(file=resource_path("./img/auto_img/red_circle.png"))
opt_state1 = Label(notebook_auto_2_1, image=state1_img)
opt_state1.pack(side="left", fill="both")

opt1_btn = Button(notebook_auto_2_1, text="Update", width = 13, height=6, command=option_update1, bg="lightcyan", state="disabled")
opt1_btn.pack(side="left", padx=1, pady=3, fill="both", expand=True)

notebook_auto_2_2 = LabelFrame(notebook_auto_2, text="B 상자 옵션", font=font2) # B 상자 옵션
notebook_auto_2_2.pack(side="top", fill="both")

notebook_auto_2_2_1 = LabelFrame(notebook_auto_2_2, text="Color", font=font4) # B 상자 색상
notebook_auto_2_2_1.pack(side="left", fill="both")

color_radio_var2= IntVar()
color_radio5 = Radiobutton(notebook_auto_2_2_1, text="Red", fg='red', value=1, variable=color_radio_var2)
color_radio5.pack(side='left')
color_radio6 = Radiobutton(notebook_auto_2_2_1, text="Green", fg='green', value=2, variable=color_radio_var2)
color_radio6.pack(side='left')
color_radio7 = Radiobutton(notebook_auto_2_2_1, text="Blue", fg='blue', value=3, variable=color_radio_var2)
color_radio7.pack(side='left')
color_radio6.select()

notebook_auto_2_2_2 = LabelFrame(notebook_auto_2_2, text="Pattern", font=font4) # B 상자 패턴
notebook_auto_2_2_2.pack(side="left", fill="both")

pattern_radio_var2 = IntVar()
pattern_radio5 = Radiobutton(notebook_auto_2_2_2, text="○", value=1, variable=pattern_radio_var2)
pattern_radio5.pack(side='left')
pattern_radio6 = Radiobutton(notebook_auto_2_2_2, text="□", value=2, variable=pattern_radio_var2)
pattern_radio6.pack(side='left')
pattern_radio7 = Radiobutton(notebook_auto_2_2_2, text="△", value=3, variable=pattern_radio_var2)
pattern_radio7.pack(side='left')
pattern_radio6.select()

notebook_auto_2_2_3 = LabelFrame(notebook_auto_2_2, text="Count", font=font4) # B count
notebook_auto_2_2_3.pack(side="left", fill="both")

count_label2 = Label(notebook_auto_2_2_3, text="0", font = ("맑은 고딕",20))
count_label2.pack(side='top', fill="both", expand=True)

state2_img = PhotoImage(file=resource_path("./img/auto_img/green_square.png"))
opt_state2 = Label(notebook_auto_2_2, image=state2_img)
opt_state2.pack(side="left", fill="both")

opt2_btn = Button(notebook_auto_2_2, text="Update", width = 13, height=6, command=option_update2, bg="lightcyan", state="disabled")
opt2_btn.pack(side="left", padx=1, pady=3, fill="both", expand=True)

notebook_auto_2_3 = LabelFrame(notebook_auto_2, text="C 상자 옵션", font=font2) # C 상자 옵션
notebook_auto_2_3.pack(side="top", fill="both")

notebook_auto_2_3_1 = LabelFrame(notebook_auto_2_3, text="Color", font=font4) # C 상자 색상
notebook_auto_2_3_1.pack(side="left", fill="both")

color_radio_var3= IntVar()
color_radio9 = Radiobutton(notebook_auto_2_3_1, text="Red", fg='red', value=1, variable=color_radio_var3)
color_radio9.pack(side='left')
color_radio10 = Radiobutton(notebook_auto_2_3_1, text="Green", fg='green', value=2, variable=color_radio_var3)
color_radio10.pack(side='left')
color_radio11 = Radiobutton(notebook_auto_2_3_1, text="Blue", fg='blue', value=3, variable=color_radio_var3)
color_radio11.pack(side='left')
color_radio11.select()

ttk.Separator(notebook_auto_2_3_1, orient='vertical').pack(fill="x", padx=1, pady=1)
notebook_auto_2_3_2 = LabelFrame(notebook_auto_2_3, text="Pattern", font=font4) # C 상자 패턴
notebook_auto_2_3_2.pack(side="left", fill="both")

pattern_radio_var3 = IntVar()
pattern_radio9 = Radiobutton(notebook_auto_2_3_2, text="○", value=1, variable=pattern_radio_var3)
pattern_radio9.pack(side='left')
pattern_radio10 = Radiobutton(notebook_auto_2_3_2, text="□", value=2, variable=pattern_radio_var3)
pattern_radio10.pack(side='left')
pattern_radio11 = Radiobutton(notebook_auto_2_3_2, text="△", value=3, variable=pattern_radio_var3)
pattern_radio11.pack(side='left')
pattern_radio11.select()

notebook_auto_2_3_3 = LabelFrame(notebook_auto_2_3, text="Count", font=font4) # B count
notebook_auto_2_3_3.pack(side="left", fill="both")

count_label3 = Label(notebook_auto_2_3_3, text="0", font = ("맑은 고딕",20))
count_label3.pack(side='top', fill="both", expand=True)

state3_img = PhotoImage(file=resource_path("./img/auto_img/blue_triangle.png"))
opt_state3 = Label(notebook_auto_2_3, image=state3_img)
opt_state3.pack(side="left", fill="both")

opt3_btn = Button(notebook_auto_2_3, text="Update", width = 13, height=6, command=option_update3, bg="lightcyan", state="disabled")
opt3_btn.pack(side="left", padx=1, pady=3, fill="both", expand=True)

notebook_auto_2_4 = Frame(notebook_auto_2)
notebook_auto_2_4.pack(side="top", fill="both", expand=True)

notebook_auto_2_4_1 = Frame(notebook_auto_2_4)
notebook_auto_2_4_1.pack(side="left", fill="both", expand=True)
start_img = PhotoImage(file=resource_path("./img/start.png"))
# start_img = ImageTk.PhotoImage(Image.open("img/start.png"))
btn_start = Label(notebook_auto_2_4_1, image=start_img, state="disabled")
btn_start.bind("<ButtonRelease-1>", auto_mode_start)
btn_start.pack()

notebook_auto_2_4_2 = Frame(notebook_auto_2_4) # 로고
notebook_auto_2_4_2.pack(side="left", fill="both", expand=True)
mark_img = PhotoImage(file=resource_path("./img/mark.png"))
# reset_img = ImageTk.PhotoImage(Image.open("img/reset.png"))
btn_mark = Label(notebook_auto_2_4_2, image=mark_img)
btn_mark.pack()

notebook_auto_2_4_3 = Frame(notebook_auto_2_4)
notebook_auto_2_4_3.pack(side="left", fill="both", expand=True)
reset_img = PhotoImage(file=resource_path("./img/reset.png"))
# reset_img = ImageTk.PhotoImage(Image.open("img/reset.png"))
btn_reset = Label(notebook_auto_2_4_3, image=reset_img, state='disabled')
btn_reset.bind("<ButtonRelease-1>", auto_mode_reset)
btn_reset.pack()

###############################################################################################################################
frame_main5 = Frame(window)
frame_main5.pack(side="bottom", fill="both", expand=True)

ttk.Separator(frame_main5, orient='horizontal').pack(fill="x", padx=1, pady=1)
Button(frame_main5, text="Close", width = 10, command=stop, fg='red').pack(side="top", padx=1, pady=3, fill="both", expand=True)

model = load_model(resource_path('./img/lig_model.h5'))
port_check()
log_update("프로그램 시작")
log_enter()

window.mainloop()