/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * @file           : main.c
  * @brief          : Main program body
  ******************************************************************************
  * @attention
  *
  * Copyright (c) 2023 STMicroelectronics.
  * All rights reserved.
  *
  * This software is licensed under terms that can be found in the LICENSE file
  * in the root directory of this software component.
  * If no LICENSE file comes with this software, it is provided AS-IS.
  *
  ******************************************************************************
  */
/* USER CODE END Header */
/* Includes ------------------------------------------------------------------*/
#include "main.h"

/* Private includes ----------------------------------------------------------*/
/* USER CODE BEGIN Includes */

/* USER CODE END Includes */

/* Private typedef -----------------------------------------------------------*/
/* USER CODE BEGIN PTD */

/* USER CODE END PTD */

/* Private define ------------------------------------------------------------*/
/* USER CODE BEGIN PD */
#define MAX_QUEUE_SIZE		(255)
/* USER CODE END PD */

/* Private macro -------------------------------------------------------------*/
/* USER CODE BEGIN PM */

/* USER CODE END PM */

/* Private variables ---------------------------------------------------------*/
UART_HandleTypeDef huart5;
UART_HandleTypeDef huart1;
UART_HandleTypeDef huart6;

/* USER CODE BEGIN PV */

/* USER CODE END PV */

/* Private function prototypes -----------------------------------------------*/
void SystemClock_Config(void);
static void MX_GPIO_Init(void);
static void MX_UART5_Init(void);
static void MX_USART1_UART_Init(void);
static void MX_USART6_UART_Init(void);
static void MX_NVIC_Init(void);
/* USER CODE BEGIN PFP */
void push(uint8_t new_data);
uint8_t pop(void);
uint8_t notempty(void);
/* USER CODE END PFP */

/* Private user code ---------------------------------------------------------*/
/* USER CODE BEGIN 0 */
uint8_t queue_buffer[MAX_QUEUE_SIZE] = {0,};
uint8_t head;
uint8_t tail;

uint8_t rx_data1[5]; // 5byte씩 받을 데이터 변수
uint8_t rx_data5[5]; // 5byte씩 받을 데이터 변수
uint8_t rx_data6[5]; // 5byte씩 받을 데이터 변수
uint8_t receive_data[5]; // 받은 데이터 (5byte 크기)
uint8_t send_data[5] = {0xA5, 0x00, 0x00, 0x00, 0x5A}; // 보낼 데이터 (5byte 크기)

int mode_state = 0; // 0은 수동, 1은 자동
uint8_t box1_opt[2] = {0x11, 0x11}; // 박스 옵션 (기본은 Red, Circle)
uint8_t box2_opt[2] = {0x01, 0x10}; // 박스 옵션 (기본은 Green, Square)
uint8_t box3_opt[2] = {0x10, 0x01}; // 박스 옵션 (기본은 Blue, Triangle)
uint8_t auto_box_info[2] = {0x00, 0x00}; // {색상(R:11, G:01, B:10), 패턴(Circle:11, Triangle:01, Square:10)}
/* USER CODE END 0 */

/**
  * @brief  The application entry point.
  * @retval int
  */
int main(void)
{
  /* USER CODE BEGIN 1 */

  /* USER CODE END 1 */

  /* MCU Configuration--------------------------------------------------------*/

  /* Reset of all peripherals, Initializes the Flash interface and the Systick. */
  HAL_Init();

  /* USER CODE BEGIN Init */

  /* USER CODE END Init */

  /* Configure the system clock */
  SystemClock_Config();

  /* USER CODE BEGIN SysInit */

  /* USER CODE END SysInit */

  /* Initialize all configured peripherals */
  MX_GPIO_Init();
  MX_UART5_Init();
  MX_USART1_UART_Init();
  MX_USART6_UART_Init();

  /* Initialize interrupts */
  MX_NVIC_Init();
  /* USER CODE BEGIN 2 */
  HAL_UART_Receive_IT(&huart1, rx_data1, 5);
  HAL_UART_Receive_IT(&huart5, rx_data5, 5);
  HAL_UART_Receive_IT(&huart6, rx_data6, 5);
  /* USER CODE END 2 */

  /* Infinite loop */
  /* USER CODE BEGIN WHILE */
  while (1)
  {
    /* USER CODE END WHILE */
	if(mode_state == 0){ // 수동모드
		if (notempty()) { // PC에서 받은 명령이 Queue에 찰 경우
			receive_data[0] = pop(); receive_data[1] = pop(); receive_data[2] = pop(); receive_data[3] = pop(); receive_data[4] = pop();

			if(receive_data[0] == 0xA5 && receive_data[4] == 0x5A){ // SOF랑 EOF 체크
				if(receive_data[1] == 0x01 && receive_data[2] == 0x00 && receive_data[3] == 0x01){ // 통신 점검 요청
					send_data[1] = 0x01; send_data[2] = 0x10; send_data[3] = 0x00; // 통신 점검 Ack
				}
				else if(receive_data[1] == 0x10 && receive_data[2] == 0x11 && receive_data[3] == 0x11){ // 수동 모드 시작
					mode_state = 0;

					send_data[1] = 0x57; send_data[2] = 0xF0; send_data[3] = 0xF0; // FPGA로 모터 Reset 동작
					HAL_UART_Transmit(&huart5, send_data, sizeof(send_data), 100); // MCU로 FPGA 제어 명령
					HAL_Delay(10);

					send_data[1] = 0x35; send_data[2] = 0x11; send_data[3] = 0x11; // Arduino로 수동모드 정보
					HAL_UART_Transmit(&huart6, send_data, sizeof(send_data), 100); // MCU로 정보 전송
					HAL_Delay(10);

					send_data[1] = 0xF0; send_data[2] = 0x1F; send_data[3] = 0x1F; // 수동 모드 Ack
				}
				else if(receive_data[1] == 0x10 && receive_data[2] == 0xFF && receive_data[3] == 0xFF){ // 자동 모드 시작
					mode_state = 1;

					send_data[1] = 0x57; send_data[2] = 0xF0; send_data[3] = 0xF0; // FPGA로 모터 Reset 동작
					HAL_UART_Transmit(&huart5, send_data, sizeof(send_data), 100); // MCU로 FPGA 제어 명령
					HAL_Delay(10);

					send_data[1] = 0x35; send_data[2] = 0xFF; send_data[3] = 0xFF; // Arduino로 자동모드 정보
					HAL_UART_Transmit(&huart6, send_data, sizeof(send_data), 100); // MCU로 정보 전송
					HAL_Delay(10);

					send_data[1] = 0xF0; send_data[2] = 0xF1; send_data[3] = 0xF1; // 자동 모드 Ack
				}
				else if(receive_data[1] == 0x11 && receive_data[2] == 0x00 && (receive_data[3] >= 0x00) && (receive_data[3] <= 0xB4)){ // Motor1 수동 제어
					send_data[1] = 0x51; send_data[2] = receive_data[2]; send_data[3] = receive_data[3]; // FPGA로 보낼 명령
					HAL_UART_Transmit(&huart5, send_data, sizeof(send_data), 100); // MCU로 FPGA 전송
					HAL_Delay(10);

					send_data[1] = 0x11; send_data[2] = 0xFF; send_data[3] = 0xFF; // Motor1 수동 제어 Ack
				}
				else if(receive_data[1] == 0x12 && receive_data[2] == 0x00 && (receive_data[3] >= 0x00) && (receive_data[3] <= 0xB4)){ // Motor2 수동 제어
					send_data[1] = 0x52; send_data[2] = receive_data[2]; send_data[3] = receive_data[3]; // FPGA로 보낼 명령
					HAL_UART_Transmit(&huart5, send_data, sizeof(send_data), 100); // MCU로 FPGA 전송
					HAL_Delay(10);

					send_data[1] = 0x12; send_data[2] = 0xFF; send_data[3] = 0xFF; // Motor2 수동 제어 Ack
				}
				else if(receive_data[1] == 0x13 && receive_data[2] == 0x00 && (receive_data[3] >= 0x00) && (receive_data[3] <= 0xB4)){ // Motor3 수동 제어
					send_data[1] = 0x53; send_data[2] = receive_data[2]; send_data[3] = receive_data[3]; // FPGA로 보낼 명령
					HAL_UART_Transmit(&huart5, send_data, sizeof(send_data), 100); // MCU로 FPGA 전송
					HAL_Delay(10);

					send_data[1] = 0x13; send_data[2] = 0xFF; send_data[3] = 0xFF; // Motor3 수동 제어 Ack
				}
				else if(receive_data[1] == 0x14 && receive_data[2] == 0x00 && (receive_data[3] >= 0x00) && (receive_data[3] <= 0xB4)){ // Motor4 수동 제어
					send_data[1] = 0x54; send_data[2] = receive_data[2]; send_data[3] = receive_data[3]; // FPGA로 보낼 명령
					HAL_UART_Transmit(&huart5, send_data, sizeof(send_data), 100); // MCU로 FPGA 전송
					HAL_Delay(10);

					send_data[1] = 0x14; send_data[2] = 0xFF; send_data[3] = 0xFF; // Motor4 수동 제어 Ack
				}
				else if(receive_data[1] == 0x15 && receive_data[2] == 0x00 && (receive_data[3] >= 0x00) && (receive_data[3] <= 0xB4)){ // Motor5 수동 제어
					send_data[1] = 0x55; send_data[2] = receive_data[2]; send_data[3] = receive_data[3]; // FPGA로 보낼 명령
					HAL_UART_Transmit(&huart5, send_data, sizeof(send_data), 100); // MCU로 FPGA 전송
					HAL_Delay(10);

					send_data[1] = 0x15; send_data[2] = 0xFF; send_data[3] = 0xFF; // Motor5 수동 제어 Ack
				}
				else if(receive_data[1] == 0x3A && receive_data[2] == 0xAA && receive_data[3] == 0xAA){ // RGB 제어
					send_data[1] = 0x3D; send_data[2] = 0xAA; send_data[3] = 0xAA;
					HAL_UART_Transmit(&huart6, send_data, sizeof(send_data), 100); // MCU로 Arduino 제어 명령
					continue;
				}
				else if(receive_data[1] == 0x3B && receive_data[2] == 0xBB && receive_data[3] == 0xBB){ // 초음파 제어
					send_data[1] = 0x3E; send_data[2] = 0xBB; send_data[3] = 0xBB;
					HAL_UART_Transmit(&huart6, send_data, sizeof(send_data), 100); // MCU로 Arduino 제어 명령
					continue;
				}
				else if(receive_data[1] == 0x16 && receive_data[2] == 0x0F && receive_data[3] == 0xF0){ // 벨트 동작 제어
					send_data[1] = 0x56; send_data[2] = 0x0F; send_data[3] = 0xF0; // FPGA로 보낼 명령
					HAL_UART_Transmit(&huart5, send_data, sizeof(send_data), 100); // MCU로 FPGA 전송
					HAL_Delay(10);

					send_data[1] = 0x41; send_data[2] = 0xAA; send_data[3] = 0xAA; // Ack
				}
				else if(receive_data[1] == 0x16 && receive_data[2] == 0x01 && receive_data[3] == 0x10){ // 벨트 정지 제어
					send_data[1] = 0x56; send_data[2] = 0x01; send_data[3] = 0x10; // FPGA로 보낼 명령
					HAL_UART_Transmit(&huart5, send_data, sizeof(send_data), 100); // MCU로 FPGA 전송
					HAL_Delay(10);

					send_data[1] = 0x41; send_data[2] = 0x11; send_data[3] = 0x11; // Ack
				}
				else if(receive_data[1] == 0x31){ // Arduino에서 RGB정보를 받았을 경우
					HAL_GPIO_TogglePin(GPIOF, GPIO_PIN_7); // 테스트용, 삭제할 코드
					send_data[1] = receive_data[1]; send_data[2] = receive_data[2]; send_data[3] = receive_data[3]; // Ack
				}
				else if(receive_data[1] == 0x32){ // Arduino에서 초음파 정보를 받았을 경우
					HAL_GPIO_TogglePin(GPIOF, GPIO_PIN_10); // 테스트용, 삭제할 코드
					send_data[1] = receive_data[1]; send_data[2] = receive_data[2]; send_data[3] = receive_data[3]; // Ack
				}
				else{ // SOF, EOF는 정상이나 안의 Data가 이상할 경우
					// 그냥 0xA50000005A 전송
				}
			}
			else{ // Uart 통신 SOF, EOF Error에 대한 코드 적기
				// 그냥 0xA50000005A 전송
			}

			HAL_UART_Transmit(&huart1, send_data, sizeof(send_data), 100); // MCU에서 PC로 전송
			send_data[1] = 0x00; send_data[2] = 0x00; send_data[3] = 0x00; // 보내고 data 초기화
		}
	}
	else if(mode_state == 1){ // 자동모드
		if (notempty()){
			receive_data[0] = pop(); receive_data[1] = pop(); receive_data[2] = pop(); receive_data[3] = pop(); receive_data[4] = pop();

			if(receive_data[1] == 0x10 && receive_data[2] == 0x11 && receive_data[3] == 0x11){ // 수동 모드 시작
				mode_state = 0;

				send_data[1] = 0x57; send_data[2] = 0xF0; send_data[3] = 0xF0; // FPGA로 모터 Reset 동작
				HAL_UART_Transmit(&huart5, send_data, sizeof(send_data), 100); // MCU로 FPGA 제어 명령
				HAL_Delay(10);

				send_data[1] = 0x36; send_data[2] = 0xFF; send_data[3] = 0x00; // Arduino로 stop 정보
				HAL_UART_Transmit(&huart6, send_data, sizeof(send_data), 100); // MCU로 Arduino 제어 명령
				HAL_Delay(10);

				send_data[1] = 0x35; send_data[2] = 0x11; send_data[3] = 0x11; // Arduino로 수동모드 정보
				HAL_UART_Transmit(&huart6, send_data, sizeof(send_data), 100); // MCU로 정보 전송
				HAL_Delay(10);

				send_data[1] = 0xF0; send_data[2] = 0x1F; send_data[3] = 0x1F; // 수동 모드 Ack
			}
			else if(receive_data[1] == 0x10 && receive_data[2] == 0xFF && receive_data[3] == 0xFF){ // 자동 모드 시작
				mode_state = 1;

				send_data[1] = 0x57; send_data[2] = 0xF0; send_data[3] = 0xF0; // FPGA로 모터 Reset 동작
				HAL_UART_Transmit(&huart5, send_data, sizeof(send_data), 100); // MCU로 FPGA 제어 명령
				HAL_Delay(10);

				send_data[1] = 0x36; send_data[2] = 0xFF; send_data[3] = 0x00; // Arduino로 stop 정보
				HAL_UART_Transmit(&huart6, send_data, sizeof(send_data), 100); // MCU로 Arduino 제어 명령
				HAL_Delay(10);

				send_data[1] = 0x35; send_data[2] = 0xFF; send_data[3] = 0xFF; // Arduino로 자동모드 정보
				HAL_UART_Transmit(&huart6, send_data, sizeof(send_data), 100); // MCU로 정보 전송
				HAL_Delay(10);

				send_data[1] = 0xF0; send_data[2] = 0xF1; send_data[3] = 0xF1; // 자동 모드 Ack
			}
			else if(receive_data[1] == 0x20){ // Box1 옵션 선택
				box1_opt[0] = receive_data[2]; box1_opt[1] = receive_data[3];
				send_data[1] = 0x4A; send_data[2] = box1_opt[0]; send_data[3] = box1_opt[1]; // Ack
			}
			else if(receive_data[1] == 0x21){ // Box2 옵션 선택
				box2_opt[0] = receive_data[2]; box2_opt[1] = receive_data[3];
				send_data[1] = 0x4A; send_data[2] = box2_opt[0]; send_data[3] = box2_opt[1]; // Ack
			}
			else if(receive_data[1] == 0x22){ // Box3 옵션 선택
				box3_opt[0] = receive_data[2]; box3_opt[1] = receive_data[3];
				send_data[1] = 0x4A; send_data[2] = box3_opt[0]; send_data[3] = box3_opt[1]; // Ack
			}
			else if(receive_data[1] == 0x2A && receive_data[2] == 0x00 && receive_data[3] == 0xFF){ // Start
				send_data[1] = 0x56; send_data[2] = 0x0F; send_data[3] = 0xF0; // FPGA로 벨트 동작
				HAL_UART_Transmit(&huart5, send_data, sizeof(send_data), 100); // MCU로 FPGA 제어 명령
				HAL_Delay(10);

				send_data[1] = 0x36; send_data[2] = 0x00; send_data[3] = 0xFF; // Arduino로 start 정보
				HAL_UART_Transmit(&huart6, send_data, sizeof(send_data), 100); // MCU로 Arduino 제어 명령
				HAL_Delay(10);

				send_data[1] = 0x41; send_data[2] = 0xAA; send_data[3] = 0xAA; // PC로 벨트 동작 log
				HAL_UART_Transmit(&huart1, send_data, sizeof(send_data), 100); // MCU로 PC 로그 명령
				HAL_Delay(10);

				send_data[1] = 0x4B; send_data[2] = 0x00; send_data[3] = 0xFF; // Ack
			}
			else if(receive_data[1] == 0x2A && receive_data[2] == 0xFF && receive_data[3] == 0x00){ // Stop
				send_data[1] = 0x56; send_data[2] = 0x01; send_data[3] = 0x10; // FPGA로 벨트 정지
				HAL_UART_Transmit(&huart5, send_data, sizeof(send_data), 100); // MCU로 FPGA 제어 명령
				HAL_Delay(10);

				send_data[1] = 0x57; send_data[2] = 0xF0; send_data[3] = 0xF0; // FPGA로 모터 Reset 동작
				HAL_UART_Transmit(&huart5, send_data, sizeof(send_data), 100); // MCU로 FPGA 제어 명령
				HAL_Delay(10);

				send_data[1] = 0x36; send_data[2] = 0xFF; send_data[3] = 0x00; // Arduino로 stop 정보
				HAL_UART_Transmit(&huart6, send_data, sizeof(send_data), 100); // MCU로 Arduino 제어 명령
				HAL_Delay(10);

				send_data[1] = 0x41; send_data[2] = 0x11; send_data[3] = 0x11; // PC로 벨트 정지 log
				HAL_UART_Transmit(&huart1, send_data, sizeof(send_data), 100); // MCU로 PC 로그 명령
				HAL_Delay(10);

				send_data[1] = 0x4B; send_data[2] = 0xFF; send_data[3] = 0x00; // Ack
			}
			else if(receive_data[1] == 0x32 && receive_data[2] == 0x10 && receive_data[3] == 0x00){ // Arduino에서 초음파 정보를 받았을 경우
				send_data[1] = 0x3C; send_data[2] =0xCC; send_data[3] = 0xCC; // PC로 패턴인식 요청 (+PC에서 벨트 정지 log)
				HAL_UART_Transmit(&huart1, send_data, sizeof(send_data), 100);
				send_data[1] = 0x00; send_data[2] = 0x00; send_data[3] = 0x00; // 보내고 data 초기화

				HAL_Delay(4800);
				send_data[1] = 0x56; send_data[2] = 0x01; send_data[3] = 0x10; // FPGA로 벨트 정지
				HAL_UART_Transmit(&huart5, send_data, sizeof(send_data), 100); // MCU로 FPGA 제어 명령
				HAL_Delay(10);

				send_data[1] = 0x36; send_data[2] = 0xFF; send_data[3] = 0x00; // Arduino로 Stop 보냄
				HAL_UART_Transmit(&huart6, send_data, sizeof(send_data), 100); // MCU로 Arduino 제어 명령
				HAL_Delay(10);
				continue;
			}
			else if(receive_data[1] == 0x31){ // RGB 정보 수신
				auto_box_info[0] = receive_data[2]; // RGB, 변수에 저장

				send_data[1] = 0x31; send_data[2] = receive_data[2]; send_data[3] = receive_data[3]; // PC에서 RGB log
			}
			else if(receive_data[1] == 0x30){ // 패턴 정보 수신
				auto_box_info[1] = receive_data[3]; // 패턴, 변수에 저장
				continue;
			}

			HAL_UART_Transmit(&huart1, send_data, sizeof(send_data), 100);
			send_data[1] = 0x00; send_data[2] = 0x00; send_data[3] = 0x00; // 보내고 data 초기화
			HAL_Delay(10);
		}
		else{ // 자동모드 반복부분
			if(auto_box_info[0] != 0x00 && auto_box_info[1] != 0x00){
				if(auto_box_info[0] == box1_opt[0] && auto_box_info[1] == box1_opt[1]){ // Box 1에 맞는 조건이면 Box 1로 운반 명령
					send_data[1] = 0x60; send_data[2] = 0x00; send_data[3] = 0x01; // FPGA로 보낼 명령, PC Log
					HAL_UART_Transmit(&huart5, send_data, sizeof(send_data), 100); // FPGA로 전송
					HAL_Delay(10);
					send_data[1] = 0x60; send_data[2] = 0x00; send_data[3] = 0x01; // PC로 보낼 명령, PC Log
					HAL_UART_Transmit(&huart1, send_data, sizeof(send_data), 100); // PC로 Log 전송
					HAL_Delay(10000);
				}
				else if(auto_box_info[0] == box2_opt[0] && auto_box_info[1] == box2_opt[1]){ // Box 2에 맞는 조건이면 Box 2로 운반 명령
					send_data[1] = 0x60; send_data[2] = 0x00; send_data[3] = 0x02; // FPGA로 보낼 명령, PC Log
					HAL_UART_Transmit(&huart5, send_data, sizeof(send_data), 100); // FPGA로 전송
					HAL_Delay(10);
					send_data[1] = 0x60; send_data[2] = 0x00; send_data[3] = 0x02; // PC로 보낼 명령, PC Log
					HAL_UART_Transmit(&huart1, send_data, sizeof(send_data), 100); // PC로 Log 전송
					HAL_Delay(10000);
				}
				else if(auto_box_info[0] == box3_opt[0] && auto_box_info[1] == box3_opt[1]){ // Box 3에 맞는 조건이면 Box 3로 운반 명령
					send_data[1] = 0x60; send_data[2] = 0x00; send_data[3] = 0x03; // FPGA로 보낼 명령, PC Log
					HAL_UART_Transmit(&huart5, send_data, sizeof(send_data), 100); // FPGA로 전송
					HAL_Delay(10);
					send_data[1] = 0x60; send_data[2] = 0x00; send_data[3] = 0x03; // PC로 보낼 명령, PC Log
					HAL_UART_Transmit(&huart1, send_data, sizeof(send_data), 100); // PC로 Log 전송
					HAL_Delay(10000);
				}
				else{ // 맞는 조건 없어서 그냥 상자 보내는 경우
					send_data[1] = 0x60; send_data[2] = 0xFF; send_data[3] = 0xFF; // PC에 보낼 정보
					HAL_UART_Transmit(&huart1, send_data, sizeof(send_data), 100); // PC로 Log 전송
					HAL_Delay(100);
				}
				send_data[1] = 0x56; send_data[2] = 0x0F; send_data[3] = 0xF0; // FPGA로 벨트 동작
				HAL_UART_Transmit(&huart5, send_data, sizeof(send_data), 100); // MCU로 FPGA 제어 명령

				HAL_Delay(10);
				send_data[1] = 0x41; send_data[2] = 0xAA; send_data[3] = 0xAA; // PC로 보낼 벨트 동작 Log
				HAL_UART_Transmit(&huart1, send_data, sizeof(send_data), 100); // PC로 Log 전송

				send_data[1] = 0x36; send_data[2] = 0x00; send_data[3] = 0xFF; // Arduino로 start 정보
				HAL_UART_Transmit(&huart6, send_data, sizeof(send_data), 100); // MCU로 Arduino에게 전송
				auto_box_info[0] = 0x00; auto_box_info[1] = 0x00;
			}
		}
	}
    /* USER CODE BEGIN 3 */
	HAL_Delay(10);
  } // while end
  /* USER CODE END 3 */
}


/**
  * @brief System Clock Configuration
  * @retval None
  */
void SystemClock_Config(void)
{
  RCC_OscInitTypeDef RCC_OscInitStruct = {0};
  RCC_ClkInitTypeDef RCC_ClkInitStruct = {0};

  /** Configure the main internal regulator output voltage
  */
  __HAL_RCC_PWR_CLK_ENABLE();
  __HAL_PWR_VOLTAGESCALING_CONFIG(PWR_REGULATOR_VOLTAGE_SCALE1);

  /** Initializes the RCC Oscillators according to the specified parameters
  * in the RCC_OscInitTypeDef structure.
  */
  RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSI;
  RCC_OscInitStruct.HSIState = RCC_HSI_ON;
  RCC_OscInitStruct.HSICalibrationValue = RCC_HSICALIBRATION_DEFAULT;
  RCC_OscInitStruct.PLL.PLLState = RCC_PLL_ON;
  RCC_OscInitStruct.PLL.PLLSource = RCC_PLLSOURCE_HSI;
  RCC_OscInitStruct.PLL.PLLM = 8;
  RCC_OscInitStruct.PLL.PLLN = 168;
  RCC_OscInitStruct.PLL.PLLP = RCC_PLLP_DIV2;
  RCC_OscInitStruct.PLL.PLLQ = 4;
  if (HAL_RCC_OscConfig(&RCC_OscInitStruct) != HAL_OK)
  {
    Error_Handler();
  }

  /** Initializes the CPU, AHB and APB buses clocks
  */
  RCC_ClkInitStruct.ClockType = RCC_CLOCKTYPE_HCLK|RCC_CLOCKTYPE_SYSCLK
                              |RCC_CLOCKTYPE_PCLK1|RCC_CLOCKTYPE_PCLK2;
  RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_PLLCLK;
  RCC_ClkInitStruct.AHBCLKDivider = RCC_SYSCLK_DIV1;
  RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV4;
  RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV2;

  if (HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_5) != HAL_OK)
  {
    Error_Handler();
  }
}

/**
  * @brief NVIC Configuration.
  * @retval None
  */
static void MX_NVIC_Init(void)
{
  /* USART1_IRQn interrupt configuration */
  HAL_NVIC_SetPriority(USART1_IRQn, 0, 0);
  HAL_NVIC_EnableIRQ(USART1_IRQn);
  /* UART5_IRQn interrupt configuration */
  HAL_NVIC_SetPriority(UART5_IRQn, 0, 0);
  HAL_NVIC_EnableIRQ(UART5_IRQn);
  /* USART6_IRQn interrupt configuration */
  HAL_NVIC_SetPriority(USART6_IRQn, 0, 0);
  HAL_NVIC_EnableIRQ(USART6_IRQn);
}

/**
  * @brief UART5 Initialization Function
  * @param None
  * @retval None
  */
static void MX_UART5_Init(void)
{

  /* USER CODE BEGIN UART5_Init 0 */

  /* USER CODE END UART5_Init 0 */

  /* USER CODE BEGIN UART5_Init 1 */

  /* USER CODE END UART5_Init 1 */
  huart5.Instance = UART5;
  huart5.Init.BaudRate = 115200;
  huart5.Init.WordLength = UART_WORDLENGTH_8B;
  huart5.Init.StopBits = UART_STOPBITS_1;
  huart5.Init.Parity = UART_PARITY_NONE;
  huart5.Init.Mode = UART_MODE_TX_RX;
  huart5.Init.HwFlowCtl = UART_HWCONTROL_NONE;
  huart5.Init.OverSampling = UART_OVERSAMPLING_16;
  if (HAL_UART_Init(&huart5) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN UART5_Init 2 */

  /* USER CODE END UART5_Init 2 */

}

/**
  * @brief USART1 Initialization Function
  * @param None
  * @retval None
  */
static void MX_USART1_UART_Init(void)
{

  /* USER CODE BEGIN USART1_Init 0 */

  /* USER CODE END USART1_Init 0 */

  /* USER CODE BEGIN USART1_Init 1 */

  /* USER CODE END USART1_Init 1 */
  huart1.Instance = USART1;
  huart1.Init.BaudRate = 115200;
  huart1.Init.WordLength = UART_WORDLENGTH_8B;
  huart1.Init.StopBits = UART_STOPBITS_1;
  huart1.Init.Parity = UART_PARITY_NONE;
  huart1.Init.Mode = UART_MODE_TX_RX;
  huart1.Init.HwFlowCtl = UART_HWCONTROL_NONE;
  huart1.Init.OverSampling = UART_OVERSAMPLING_16;
  if (HAL_UART_Init(&huart1) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN USART1_Init 2 */

  /* USER CODE END USART1_Init 2 */

}

/**
  * @brief USART6 Initialization Function
  * @param None
  * @retval None
  */
static void MX_USART6_UART_Init(void)
{

  /* USER CODE BEGIN USART6_Init 0 */

  /* USER CODE END USART6_Init 0 */

  /* USER CODE BEGIN USART6_Init 1 */

  /* USER CODE END USART6_Init 1 */
  huart6.Instance = USART6;
  huart6.Init.BaudRate = 115200;
  huart6.Init.WordLength = UART_WORDLENGTH_8B;
  huart6.Init.StopBits = UART_STOPBITS_1;
  huart6.Init.Parity = UART_PARITY_NONE;
  huart6.Init.Mode = UART_MODE_TX_RX;
  huart6.Init.HwFlowCtl = UART_HWCONTROL_NONE;
  huart6.Init.OverSampling = UART_OVERSAMPLING_16;
  if (HAL_UART_Init(&huart6) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN USART6_Init 2 */

  /* USER CODE END USART6_Init 2 */

}

/**
  * @brief GPIO Initialization Function
  * @param None
  * @retval None
  */
static void MX_GPIO_Init(void)
{
  GPIO_InitTypeDef GPIO_InitStruct = {0};

  /* GPIO Ports Clock Enable */
  __HAL_RCC_GPIOF_CLK_ENABLE();
  __HAL_RCC_GPIOC_CLK_ENABLE();
  __HAL_RCC_GPIOA_CLK_ENABLE();
  __HAL_RCC_GPIOD_CLK_ENABLE();

  /*Configure GPIO pin Output Level */
  HAL_GPIO_WritePin(GPIOF, GPIO_PIN_7|GPIO_PIN_8|GPIO_PIN_9|GPIO_PIN_10, GPIO_PIN_RESET);

  /*Configure GPIO pins : PF7 PF8 PF9 PF10 */
  GPIO_InitStruct.Pin = GPIO_PIN_7|GPIO_PIN_8|GPIO_PIN_9|GPIO_PIN_10;
  GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
  HAL_GPIO_Init(GPIOF, &GPIO_InitStruct);

}

/* USER CODE BEGIN 4 */
void HAL_UART_RxCpltCallback(UART_HandleTypeDef *huart)
{
  if (huart->Instance == USART1) {
    push(rx_data1[0]); push(rx_data1[1]); push(rx_data1[2]); push(rx_data1[3]); push(rx_data1[4]);
    HAL_UART_Receive_IT(&huart1, rx_data1, 5);
  }
  if (huart->Instance == UART5) {
    push(rx_data5[0]); push(rx_data5[1]); push(rx_data5[2]); push(rx_data5[3]); push(rx_data5[4]);
    HAL_UART_Receive_IT(&huart5, rx_data5, 5);
  }
  if (huart->Instance == USART6) {
    push(rx_data6[0]); push(rx_data6[1]); push(rx_data6[2]); push(rx_data6[3]); push(rx_data6[4]);
    HAL_UART_Receive_IT(&huart6, rx_data6, 5);
  }
}

void push(uint8_t new_data)
{
  // 새로운 데이터를 queue에 넣는다.
  queue_buffer[head] = new_data;

  head++;

  // head가 queue 마지막 위치에 도달했다면, 0으로 초기화
  if (head >= MAX_QUEUE_SIZE) {
    head = 0;
  }
}

// pop: 가장 오래된 데이터를 가져온다.
uint8_t pop(void)
{
  // tail의 위치에 데이터를 가져온다
  uint8_t pop_data = queue_buffer[tail];

  tail++;

  // tail이 queue 마지막 위치에 도달했다면, 0으로 초기화
  if (tail >= MAX_QUEUE_SIZE) {
    tail = 0;
  }

  return pop_data;
}

uint8_t notempty(void)
{
  // head와 tail의 위치가 같으면 queue가 비어있음
  return (head != tail) && (head % 5 == 0); // 5bytes가 Queue에 차면 True 반환
}
/* USER CODE END 4 */

/**
  * @brief  This function is executed in case of error occurrence.
  * @retval None
  */
void Error_Handler(void)
{
  /* USER CODE BEGIN Error_Handler_Debug */
  /* User can add his own implementation to report the HAL error return state */
  __disable_irq();
  while (1)
  {
  }
  /* USER CODE END Error_Handler_Debug */
}

#ifdef  USE_FULL_ASSERT
/**
  * @brief  Reports the name of the source file and the source line number
  *         where the assert_param error has occurred.
  * @param  file: pointer to the source file name
  * @param  line: assert_param error line source number
  * @retval None
  */
void assert_failed(uint8_t *file, uint32_t line)
{
  /* USER CODE BEGIN 6 */
  /* User can add his own implementation to report the file name and line number,
     ex: printf("Wrong parameters value: file %s on line %d\r\n", file, line) */
  /* USER CODE END 6 */
}
#endif /* USE_FULL_ASSERT */
