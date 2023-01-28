from tkinter import *
from tkinter import ttk
from serial import Serial
from PIL import Image, ImageTk
from keras.models import load_model
import tkinter.messagebox as msgbox
import tkinter.font as ft
import serial.tools.list_ports
import sys, natsort, datetime, threading, time, binascii
import cv2 as cv
import numpy as np
import winsound as sd

CAM_ID = 1 # camid 설정
connect_state = 0
debug_state = 0
page_state = 0 # 0: 수동모드, 1: 자동모드

model = load_model('img/lig_model.h5')

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
        
        sd.Beep(1000, 1000) # 알림음 설정
        msgbox.showinfo("알림", "연결되었습니다.")

    except:
        msgbox.showwarning("경고", "연결에 실패하였습니다.\n설정을 확인하십시오.")

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
        
            if(receive_data == b'\xA5\x31\x32\x33\x5A'):
                print("초음파 O")
            else:
                print("초음파 X")

def write_uart(byte_hex):
    global py_serial
    
    py_serial.write(byte_hex)
    return

def ack_check():
    threading.Thread(target=ack_func).start()

def ack_func():
    global receive_data

    start_time = time.time()
    timeout = 1
    
    while(True):
        if(time.time() > start_time + timeout):
            sd.Beep(3000, 1000) # ACk 못 받았을 경우 경고음
            return


def frame_1to2_show(): # Uart -> 자체점검모드
    # Uart Connect연결 후 자체점검모드 Page 진입
    frame_main1.pack_forget()
    frame_main2.pack(side="top", fill="both", expand=True)
    window_label.config(text="Arm Control Pad (PBL)")

def sudong_btn_show():
    global page_state

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
    btn_pause.config(state="disabled")

    debug_btn.config(state="normal")

    page_state = 0 # 수동 모드 진입 변수 설정

def auto_btn_show():
    global page_state
    
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

    debug_btn.config(state="disabled")

    page_state = 1 # 자동 모드 진입 변수 설정

def debug_page():
    global debug_state, window2_log_box

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

    window2_bottom = Frame(window2)
    window2_bottom.pack(side="bottom", fill="both", expand=True)
    
    debug_val = Entry(window2_bottom)
    debug_val.insert(0, "00112233FF")
    debug_val.pack(side="left", fill="both", expand = True, padx=5, pady=5, ipady=4)

    debug_val_btn = Button(window2_bottom, text="전송", width = 4, command=debug_func, fg="black")
    debug_val_btn.pack(side="right", padx=1, pady=3)

    window2.mainloop()
    return

def log_update(msg):
    now = str(datetime.datetime.now())[0:-7]
    log_box.insert(END, f"[{now}] {msg}")
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

    cv.imwrite("img/capture.png", img)
    resize_img = cv.resize(img, (24,24))    #24 x 24로 사이즈 줄이기 
    resize_img_gray = cv.cvtColor(resize_img, cv.COLOR_BGR2GRAY)    # 흑백으로 변환
    resize_img_gray[resize_img_gray>100] = 255

    cam.release()   # 카메라 동적할당 해제

    # classes = ['circle', 'square', 'triangle']        # 라벨
    input_arr = np.array([resize_img])  # Convert single image to a batch.
    pred = model.predict(input_arr)                                             # 예측하기
    where = np.where(pred == pred.max())[1][0]      # 넘파이는 인덱스찾는 함수가 numpy.where이다.

    if where == 0: # circle
        pattern_label.config(text="○")
    elif where == 1: # square
        pattern_label.config(text="☆")
    else: # triangle
        pattern_label.config(text="△")

    capture_img = ImageTk.PhotoImage(Image.open("img/capture.png"))
    img_label.config(image=capture_img)
    img_label.image=capture_img
    
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
            state1_img = PhotoImage(file="img/auto_img/red_circle.png")
        elif(p1 == 2): # pattern 선택이 ☆일 때
            state1_img = PhotoImage(file="img/auto_img/red_star.png")
        elif(p1 == 3): # pattern 선택이 △일 때
            state1_img = PhotoImage(file="img/auto_img/red_triangle.png")

    elif(c1 == 2): # color 선택이 Green 일때
        if(p1 == 1): # pattern 선택이 ○일 때
            state1_img = PhotoImage(file="img/auto_img/green_circle.png")
        elif(p1 == 2): # pattern 선택이 ☆일 때
            state1_img = PhotoImage(file="img/auto_img/green_star.png")
        elif(p1 == 3): # pattern 선택이 △일 때
            state1_img = PhotoImage(file="img/auto_img/green_triangle.png")

    elif(c1 == 3): # color 선택이 Blue 일때
        if(p1 == 1): # pattern 선택이 ○일 때
            state1_img = PhotoImage(file="img/auto_img/blue_circle.png")
        elif(p1 == 2): # pattern 선택이 ☆일 때
            state1_img = PhotoImage(file="img/auto_img/blue_star.png")
        elif(p1 == 3): # pattern 선택이 △일 때
            state1_img = PhotoImage(file="img/auto_img/blue_triangle.png")

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
            state2_img = PhotoImage(file="img/auto_img/red_circle.png")
        elif(p2 == 2): # pattern 선택이 ☆일 때
            state2_img = PhotoImage(file="img/auto_img/red_star.png")
        elif(p2 == 3): # pattern 선택이 △일 때
            state2_img = PhotoImage(file="img/auto_img/red_triangle.png")

    elif(c2 == 2): # color 선택이 Green 일때
        if(p2 == 1): # pattern 선택이 ○일 때
            state2_img = PhotoImage(file="img/auto_img/green_circle.png")
        elif(p2 == 2): # pattern 선택이 ☆일 때
            state2_img = PhotoImage(file="img/auto_img/green_star.png")
        elif(p2 == 3): # pattern 선택이 △일 때
            state2_img = PhotoImage(file="img/auto_img/green_triangle.png")

    elif(c2 == 3): # color 선택이 Blue 일때
        if(p2 == 1): # pattern 선택이 ○일 때
            state2_img = PhotoImage(file="img/auto_img/blue_circle.png")
        elif(p2 == 2): # pattern 선택이 ☆일 때
            state2_img = PhotoImage(file="img/auto_img/blue_star.png")
        elif(p2 == 3): # pattern 선택이 △일 때
            state2_img = PhotoImage(file="img/auto_img/blue_triangle.png")

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
            state3_img = PhotoImage(file="img/auto_img/red_circle.png")
        elif(p3 == 2): # pattern 선택이 ☆일 때
            state3_img = PhotoImage(file="img/auto_img/red_star.png")
        elif(p3 == 3): # pattern 선택이 △일 때
            state3_img = PhotoImage(file="img/auto_img/red_triangle.png")

    elif(c3 == 2): # color 선택이 Green 일때
        if(p3 == 1): # pattern 선택이 ○일 때
            state3_img = PhotoImage(file="img/auto_img/green_circle.png")
        elif(p3== 2): # pattern 선택이 ☆일 때
            state3_img = PhotoImage(file="img/auto_img/green_star.png")
        elif(p3 == 3): # pattern 선택이 △일 때
            state3_img = PhotoImage(file="img/auto_img/green_triangle.png")

    elif(c3 == 3): # color 선택이 Blue 일때
        if(p3== 1): # pattern 선택이 ○일 때
            state3_img = PhotoImage(file="img/auto_img/blue_circle.png")
        elif(p3 == 2): # pattern 선택이 ☆일 때
            state3_img = PhotoImage(file="img/auto_img/blue_star.png")
        elif(p3 == 3): # pattern 선택이 △일 때
            state3_img = PhotoImage(file="img/auto_img/blue_triangle.png")

    opt_state3.config(image=state3_img)
    opt_state3.image = state3_img

def stop():
    global py_serial

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
sudong_btn = Button(notebook_sudong_1_0, text="시작", width = 5, command=sudong_btn_show, fg="blue")
sudong_btn.pack(side="top", padx=1, pady=3, fill="both", expand=True)

notebook_sudong_1_1 = LabelFrame(notebook_sudong_1, text="Motor#1", font=font2) # PWM 조작 바1
notebook_sudong_1_1.pack(side="top")
motor_var1 = IntVar()
scale1 = Scale(notebook_sudong_1_1, variable=motor_var1, orient=HORIZONTAL, from_=0, to=180, width=20, length=300, fg='green', cursor="dot").pack(side="left", fill="both")
motor_btn1 = Button(notebook_sudong_1_1, text="동작", width = 5, command=None, fg="green", state='disabled')
motor_btn1.pack(side="right", padx=1, pady=3, fill="both", expand=True)

notebook_sudong_1_2 = LabelFrame(notebook_sudong_1, text="Motor#2", font=font2) # PWM 조작 바2
notebook_sudong_1_2.pack(side="top")
motor_var2 = IntVar()
scale2 = Scale(notebook_sudong_1_2, variable=motor_var2, orient=HORIZONTAL, from_=0, to=180, width=20, length=300, fg='green', cursor="dot").pack(side="left", fill="both")
motor_btn2 = Button(notebook_sudong_1_2, text="동작", width = 5, command=None, fg="green", state='disabled')
motor_btn2.pack(side="right", padx=1, pady=3, fill="both", expand=True)

notebook_sudong_1_3 = LabelFrame(notebook_sudong_1, text="Motor#3", font=font2) # PWM 조작 바3
notebook_sudong_1_3.pack(side="top")
motor_var3 = IntVar()
scale3 = Scale(notebook_sudong_1_3, variable=motor_var3, orient=HORIZONTAL, from_=0, to=180, width=20, length=300, fg='green', cursor="dot").pack(side="left", fill="both")
motor_btn3 = Button(notebook_sudong_1_3, text="동작", width = 5, command=None, fg="green", state='disabled')
motor_btn3.pack(side="right", padx=1, pady=3, fill="both", expand=True)

notebook_sudong_1_4 = LabelFrame(notebook_sudong_1, text="Motor#4", font=font2) # PWM 조작 바4
notebook_sudong_1_4.pack(side="top")
motor_var4 = IntVar()
scale4 = Scale(notebook_sudong_1_4, variable=motor_var4, orient=HORIZONTAL, from_=0, to=180, width=20, length=300, fg='green', cursor="dot").pack(side="left", fill="both")
motor_btn4 = Button(notebook_sudong_1_4, text="동작", width = 5, command=None, fg="green", state='disabled')
motor_btn4.pack(side="right", padx=1, pady=3, fill="both", expand=True)

notebook_sudong_1_5 = LabelFrame(notebook_sudong_1, text="Motor#5", font=font2) # PWM 조작 바5
notebook_sudong_1_5.pack(side="top")
motor_var5 = IntVar()
scale5 = Scale(notebook_sudong_1_5, variable=motor_var5, orient=HORIZONTAL, from_=0, to=180, width=20, length=300, fg='green', cursor="dot").pack(side="left", fill="both")
motor_btn5 = Button(notebook_sudong_1_5, text="동작", width = 5, command=None, fg="green", state='disabled')
motor_btn5.pack(side="right", padx=1, pady=3, fill="both", expand=True)

notebook_sudong_1_6 = LabelFrame(notebook_sudong_1, text="벨트", font=font2) # 벨트 On/Off
notebook_sudong_1_6.pack(side="left")
belt_btn = Button(notebook_sudong_1_6, text="On", width = 13, height=6, command=ack_check, fg="brown", state='disabled')
belt_btn.pack(side="top", padx=1, pady=3, fill="both", expand=True)

notebook_sudong_1_7 = LabelFrame(notebook_sudong_1, text="초음파 센서", font=font2) # 초음파 센서 Checking
notebook_sudong_1_7.pack(side="right", fill="both", expand=True)
wave_btn = Button(notebook_sudong_1_7, text="Check", width = 13, height=6, command=lambda: write_uart(b'\xA5\x32\x33\x34\x5A'), fg="brown", state='disabled')
wave_btn.pack(side="left", padx=1, pady=3)
notebook_sudong_1_7_2 = Frame(notebook_sudong_1_7)
notebook_sudong_1_7_2.pack(side="right", fill="both", expand=True)
Label(notebook_sudong_1_7_2, text="無", font=font3, fg='blue').pack(side="bottom")

notebook_sudong_2 = Frame(notebook_sudong)
notebook_sudong_2.pack(side="right", fill="both", expand=True)

notebook_sudong_2_1 = Frame(notebook_sudong_2)
notebook_sudong_2_1.pack(side="top", fill="both", expand=True)

notebook_sudong_2_1_1 = LabelFrame(notebook_sudong_2_1, text="RGB 센서", font=font2)
notebook_sudong_2_1_1.pack(side="left", fill="both", expand=True)

rgb_btn = Button(notebook_sudong_2_1_1, text="Check", width = 13, height=6, command=None, fg="darkorange", state='disabled')
rgb_btn.pack(side="left", padx=1, pady=3)
rgb_frame = LabelFrame(notebook_sudong_2_1_1, text=f"[R: {255} G: {255} B: {255}]", fg='white', bg='red') # 색 판별에 따라  bg바뀜
rgb_frame.pack(side="right", fill="both", expand=True)

notebook_sudong_2_1_2 = LabelFrame(notebook_sudong_2_1, text="패턴 인식", font=font2)
notebook_sudong_2_1_2.pack(side="right", fill="both", expand=True)

pattern_btn = Button(notebook_sudong_2_1_2, text="Check", width = 13, height=6, command=capture_predict, fg="darkorange", state='disabled')
pattern_btn.pack(side="left", padx=1, pady=3)
pattern_label = Label(notebook_sudong_2_1_2, text="無", font=font3, fg='purple')
pattern_label.pack()

notebook_sudong_2_2 = Frame(notebook_sudong_2)
notebook_sudong_2_2.pack(side="top", fill="both", expand=True)

init_img = ImageTk.PhotoImage(Image.open("img/init.png"))
img_label = Label(notebook_sudong_2_2, image=init_img)
img_label.pack(side="top")

############################################################자동모드
notebook_auto=ttk.Frame(notebook)
notebook.add(notebook_auto, text="자동모드")

notebook_auto_1 = Frame(notebook_auto) # 로그를 나타내는 부분
notebook_auto_1.pack(side="left", fill="both")

notebook_auto_1_1 = LabelFrame(notebook_auto_1, text="Auto Mode Control", font=font2) # 수동 모드 조작
notebook_auto_1_1.pack(side="top", fill="both")
auto_btn = Button(notebook_auto_1_1, text="시작", width=45, command=auto_btn_show, fg="blue")
auto_btn.pack(side="top", padx=1, pady=3, fill="both")

notebook_auto_1_2 = Frame(notebook_auto_1) # 로그를 나타내는 부분
notebook_auto_1_2.pack(side="top", fill='both', expand=True)

scrollbar = Scrollbar(notebook_auto_1_2)
scrollbar.pack(side="right" ,fill ="y")
log_box = Listbox(notebook_auto_1_2, yscrollcommand=scrollbar.set, width=45, height=10, selectbackground="green", takefocus=False, activestyle="none")
log_box.pack(side="left", fill="y")

notebook_auto_2 = Frame(notebook_auto) # 옵션을 나타내는 부분
notebook_auto_2.pack(side="right", fill="both", expand=True)

notebook_auto_2_1 = LabelFrame(notebook_auto_2, text="1번 상자 옵션", font=font2) # 1번 상자 옵션
notebook_auto_2_1.pack(side="top", fill="both")

notebook_auto_2_1_1 = LabelFrame(notebook_auto_2_1, text="Color", font=font4) # 1번 상자 색상
notebook_auto_2_1_1.pack(side="left", fill="both")

color_radio_var1 = IntVar()
color_radio1 = Radiobutton(notebook_auto_2_1_1, text="Red", fg='red', value=1, variable=color_radio_var1)
color_radio1.pack(side='left')
color_radio2 = Radiobutton(notebook_auto_2_1_1, text="Green", fg='green', value=2, variable=color_radio_var1)
color_radio2.pack(side='left')
color_radio3 = Radiobutton(notebook_auto_2_1_1, text="Blue", fg='blue', value=3, variable=color_radio_var1)
color_radio3.pack(side='left')
color_radio1.select()

notebook_auto_2_1_2 = LabelFrame(notebook_auto_2_1, text="Pattern", font=font4) # 1번 상자 패턴
notebook_auto_2_1_2.pack(side="left", fill="both")

pattern_radio_var1 = IntVar()
pattern_radio1 = Radiobutton(notebook_auto_2_1_2, text="○", value=1, variable=pattern_radio_var1)
pattern_radio1.pack(side='left')
pattern_radio2 = Radiobutton(notebook_auto_2_1_2, text="☆", value=2, variable=pattern_radio_var1)
pattern_radio2.pack(side='left')
pattern_radio3 = Radiobutton(notebook_auto_2_1_2, text="△", value=3, variable=pattern_radio_var1)
pattern_radio3.pack(side='left')
pattern_radio1.select()

notebook_auto_2_1_3 = LabelFrame(notebook_auto_2_1, text="Count", font=font4) # 1번 상자 count
notebook_auto_2_1_3.pack(side="left", fill="both")

count_label1 = Label(notebook_auto_2_1_3, text="0", font = ("맑은 고딕",20))
count_label1.pack(side='top', fill="both", expand=True)

state1_img = PhotoImage(file="img/auto_img/red_circle.png")
opt_state1 = Label(notebook_auto_2_1, image=state1_img)
opt_state1.pack(side="left", fill="both")

opt1_btn = Button(notebook_auto_2_1, text="Update", width = 13, height=6, command=option_update1, bg="lightcyan", state="disabled")
opt1_btn.pack(side="left", padx=1, pady=3, fill="both", expand=True)

notebook_auto_2_2 = LabelFrame(notebook_auto_2, text="2번 상자 옵션", font=font2) # 2번 상자 옵션
notebook_auto_2_2.pack(side="top", fill="both")

notebook_auto_2_2_1 = LabelFrame(notebook_auto_2_2, text="Color", font=font4) # 2번 상자 색상
notebook_auto_2_2_1.pack(side="left", fill="both")

color_radio_var2= IntVar()
color_radio5 = Radiobutton(notebook_auto_2_2_1, text="Red", fg='red', value=1, variable=color_radio_var2)
color_radio5.pack(side='left')
color_radio6 = Radiobutton(notebook_auto_2_2_1, text="Green", fg='green', value=2, variable=color_radio_var2)
color_radio6.pack(side='left')
color_radio7 = Radiobutton(notebook_auto_2_2_1, text="Blue", fg='blue', value=3, variable=color_radio_var2)
color_radio7.pack(side='left')
color_radio6.select()

notebook_auto_2_2_2 = LabelFrame(notebook_auto_2_2, text="Pattern", font=font4) # 2번 상자 패턴
notebook_auto_2_2_2.pack(side="left", fill="both")

pattern_radio_var2 = IntVar()
pattern_radio5 = Radiobutton(notebook_auto_2_2_2, text="○", value=1, variable=pattern_radio_var2)
pattern_radio5.pack(side='left')
pattern_radio6 = Radiobutton(notebook_auto_2_2_2, text="☆", value=2, variable=pattern_radio_var2)
pattern_radio6.pack(side='left')
pattern_radio7 = Radiobutton(notebook_auto_2_2_2, text="△", value=3, variable=pattern_radio_var2)
pattern_radio7.pack(side='left')
pattern_radio6.select()

notebook_auto_2_2_3 = LabelFrame(notebook_auto_2_2, text="Count", font=font4) # 2번 count
notebook_auto_2_2_3.pack(side="left", fill="both")

count_label2 = Label(notebook_auto_2_2_3, text="0", font = ("맑은 고딕",20))
count_label2.pack(side='top', fill="both", expand=True)

state2_img = PhotoImage(file="img/auto_img/green_star.png")
opt_state2 = Label(notebook_auto_2_2, image=state2_img)
opt_state2.pack(side="left", fill="both")

opt2_btn = Button(notebook_auto_2_2, text="Update", width = 13, height=6, command=option_update2, bg="lightcyan", state="disabled")
opt2_btn.pack(side="left", padx=1, pady=3, fill="both", expand=True)

notebook_auto_2_3 = LabelFrame(notebook_auto_2, text="3번 상자 옵션", font=font2) # 3번 상자 옵션
notebook_auto_2_3.pack(side="top", fill="both")

notebook_auto_2_3_1 = LabelFrame(notebook_auto_2_3, text="Color", font=font4) # 3번 상자 색상
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
notebook_auto_2_3_2 = LabelFrame(notebook_auto_2_3, text="Pattern", font=font4) # 3번 상자 패턴
notebook_auto_2_3_2.pack(side="left", fill="both")

pattern_radio_var3 = IntVar()
pattern_radio9 = Radiobutton(notebook_auto_2_3_2, text="○", value=1, variable=pattern_radio_var3)
pattern_radio9.pack(side='left')
pattern_radio10 = Radiobutton(notebook_auto_2_3_2, text="☆", value=2, variable=pattern_radio_var3)
pattern_radio10.pack(side='left')
pattern_radio11 = Radiobutton(notebook_auto_2_3_2, text="△", value=3, variable=pattern_radio_var3)
pattern_radio11.pack(side='left')
pattern_radio11.select()

notebook_auto_2_3_3 = LabelFrame(notebook_auto_2_3, text="Count", font=font4) # 2번 count
notebook_auto_2_3_3.pack(side="left", fill="both")

count_label3 = Label(notebook_auto_2_3_3, text="0", font = ("맑은 고딕",20))
count_label3.pack(side='top', fill="both", expand=True)

state3_img = PhotoImage(file="img/auto_img/blue_triangle.png")
opt_state3 = Label(notebook_auto_2_3, image=state3_img)
opt_state3.pack(side="left", fill="both")

opt3_btn = Button(notebook_auto_2_3, text="Update", width = 13, height=6, command=option_update3, bg="lightcyan", state="disabled")
opt3_btn.pack(side="left", padx=1, pady=3, fill="both", expand=True)

notebook_auto_2_4 = Frame(notebook_auto_2)
notebook_auto_2_4.pack(side="top", fill="both", expand=True)

notebook_auto_2_4_1 = Frame(notebook_auto_2_4)
notebook_auto_2_4_1.pack(side="left", fill="both", expand=True)
start_img = PhotoImage(file="img/start.png")
# start_img = ImageTk.PhotoImage(Image.open("img/start.png"))
btn_start = Label(notebook_auto_2_4_1, image=start_img, state="disabled")
btn_start.bind("<Button-1>", None)
btn_start.pack()

notebook_auto_2_4_2 = Frame(notebook_auto_2_4)
notebook_auto_2_4_2.pack(side="left", fill="both", expand=True)
pause_img = PhotoImage(file="img/pause.png")
# pause_img = ImageTk.PhotoImage(Image.open("img/pause.png"))
btn_pause = Label(notebook_auto_2_4_2, image=pause_img, state='disabled')
btn_pause.bind("<Button-1>", None)
btn_pause.pack()

notebook_auto_2_4_3 = Frame(notebook_auto_2_4)
notebook_auto_2_4_3.pack(side="left", fill="both", expand=True)
reset_img = PhotoImage(file="img/reset.png")
# reset_img = ImageTk.PhotoImage(Image.open("img/reset.png"))
btn_reset = Label(notebook_auto_2_4_3, image=reset_img, state='disabled')
btn_reset.bind("<Button-1>", None)
btn_reset.pack()

###############################################################################################################################
frame_main5 = Frame(window)
frame_main5.pack(side="bottom", fill="both", expand=True)

ttk.Separator(frame_main5, orient='horizontal').pack(fill="x", padx=1, pady=1)
Button(frame_main5, text="Close", width = 10, command=stop, fg='red').pack(side="top", padx=1, pady=3, fill="both", expand=True)

port_check()
# port_combobox.current(0)
log_update("프로그램 시작")
for i in range(100):
    log_update(f"Test{i}")

window.mainloop()