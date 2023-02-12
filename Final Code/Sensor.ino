#include <Wire.h>
#include "Adafruit_TCS34725.h"

#define TRIG 12
#define ECHO 8

uint8_t rx_data[5] = {};  //MCU로 부터 수신받는 데이터
uint8_t tx_data[5] = {0xA5, 0x00, 0x00, 0x00, 0x5A};  //MCU로 보내는 데이터
uint16_t clear, red, green, blue;

Adafruit_TCS34725 tcs = Adafruit_TCS34725(TCS34725_INTEGRATIONTIME_50MS, TCS34725_GAIN_4X);   // Adafruit_TCS34725라이브러리 사용을 위한 객체 생성

int mode_state = 0;  // 0: 수동 1: 자동
int auto_state = 0; // 0: stop 1: start
float cycletime;
float distance;

void setup(){
  Serial.begin(115200);

  pinMode(TRIG, OUTPUT);
  pinMode(ECHO, INPUT);

  tcs.begin();
}

void loop() {
  if (mode_state == 0) {  // 수동
    if (Serial.available()) {
      rx_data[0] = Serial.read(); delay(10);
      rx_data[1] = Serial.read(); delay(10);
      rx_data[2] = Serial.read(); delay(10);
      rx_data[3] = Serial.read(); delay(10);
      rx_data[4] = Serial.read(); delay(10);

      if ((rx_data[0] == 0xA5) && (rx_data[4] == 0x5A)) {                            // SOF, EOF가 제대로 왔을 경우
        if ((rx_data[1] == 0x35) && (rx_data[2] == 0x11) && (rx_data[3] == 0x11)) {  // 수동모드 설정
          mode_state = 0;
        } 
        else if ((rx_data[1] == 0x35) && (rx_data[2] == 0xFF) && (rx_data[3] == 0xFF)) {  // 자동모드 설정
          mode_state = 1;
        }
        else if ((rx_data[1] == 0x3E) && (rx_data[2] == 0xBB) && (rx_data[3] == 0xBB)) {  // 초음파 제어
          digitalWrite(TRIG, HIGH);
          delay(10);
          digitalWrite(TRIG, LOW);

          cycletime = pulseIn(ECHO, HIGH);
          distance = ((340 * cycletime) / 10000) / 2;

          if (distance < 5) {  // 물체O
            tx_data[1] = 0x32;
            tx_data[2] = 0x10;
            tx_data[3] = 0x00;
          } else {  //물체 x
            tx_data[1] = 0x32;
            tx_data[2] = 0x00;
            tx_data[3] = 0x01;
          }
          for (int i = 0; i < 5; i++) Serial.write(tx_data[i]); // MCU로 데이터 전송
        } 
        else if ((rx_data[1] == 0x3D) && (rx_data[2] == 0xAA) && (rx_data[3] == 0xAA)) {  // RGB 제어
          tcs.getRawData(&red, &green, &blue, &clear);                                           // 색상 감지 센서에서 데이터 값 받아오기

          int r = map(red, 0, 21504, 0, 1025);    // 색상 감지 센서에서 받아온 빨간색 데이터값을 3색led에서 사용할수 있도록 수치 변경
          int g = map(green, 0, 21504, 0, 1025);  // 녹색
          int b = map(blue, 0, 21504, 0, 1025);   // 파란색

          if (r > g && r > b) {
            tx_data[1] = 0x31; tx_data[2] = 0x11; tx_data[3] = 0x00;
          }

          if (g > b && g > r) {
            tx_data[1] = 0x31; tx_data[2] = 0x01; tx_data[3] = 0x00;
          }

          if (b > r && b > g) {
            tx_data[1] = 0x31; tx_data[2] = 0x10; tx_data[3] = 0x00;
          }
          for (int i = 0; i < 5; i++) Serial.write(tx_data[i]); // MCU로 데이터 전송
        }
      }
    }
  } 
  else {  // 자동모드
    if (Serial.available()){
      rx_data[0] = Serial.read(); delay(10);
      rx_data[1] = Serial.read(); delay(10);
      rx_data[2] = Serial.read(); delay(10);
      rx_data[3] = Serial.read(); delay(10);
      rx_data[4] = Serial.read(); delay(10);

      if ((rx_data[0] == 0xA5) && (rx_data[4] == 0x5A)) {                            // SOF, EOF가 제대로 왔을 경우
        if ((rx_data[1] == 0x35) && (rx_data[2] == 0x11) && (rx_data[3] == 0x11)) {  // 수동모드 설정
          mode_state = 0;
        } 
        else if ((rx_data[1] == 0x35) && (rx_data[2] == 0xFF) && (rx_data[3] == 0xFF)) {  // 자동모드 설정
          mode_state = 1;
        }
        else if ((rx_data[1] == 0x36) && (rx_data[2] == 0x00) && (rx_data[3] == 0xFF)) {  // start
          auto_state = 1;
        }
        else if ((rx_data[1] == 0x36) && (rx_data[2] == 0xFF) && (rx_data[3] == 0x00)) {  // stop
          auto_state = 0;
        }
      }
    }
    else { // 자동모드 작성
      if(auto_state == 1){
        digitalWrite(TRIG, HIGH);
        delay(10);
        digitalWrite(TRIG, LOW);

        cycletime = pulseIn(ECHO, HIGH);
        distance = ((340 * cycletime) / 10000) / 2;

        if (distance < 5) {  // 물체O
          tx_data[1] = 0x32; tx_data[2] = 0x10; tx_data[3] = 0x00;
          for (int i = 0; i < 5; i++) Serial.write(tx_data[i]); // MCU로 물체 정보데이터 전송
          delay(6000);

          tcs.getRawData(&red, &green, &blue, &clear);                                           // 색상 감지 센서에서 데이터 값 받아오기

          int r = map(red, 0, 21504, 0, 1025);    // 색상 감지 센서에서 받아온 빨간색 데이터값을 3색led에서 사용할수 있도록 수치 변경
          int g = map(green, 0, 21504, 0, 1025);  // 녹색
          int b = map(blue, 0, 21504, 0, 1025);   // 파란색

          if (r > g && r > b) {
            tx_data[1] = 0x31; tx_data[2] = 0x11; tx_data[3] = 0x00;
          }

          if (g > b && g > r) {
            tx_data[1] = 0x31; tx_data[2] = 0x01; tx_data[3] = 0x00;
          }

          if (b > r && b > g) {
            tx_data[1] = 0x31; tx_data[2] = 0x10; tx_data[3] = 0x00;
          }

          for (int i = 0; i < 5; i++) Serial.write(tx_data[i]); // MCU로 데이터 전송
          auto_state = 0;
        }
      }
      delay(10);
    }
  }
}
