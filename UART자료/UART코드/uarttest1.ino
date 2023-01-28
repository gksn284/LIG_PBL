//#include <SoftwareSerial.h>

//#define PIN_TX 2
//#define PIN_RX 3

//SoftwareSerial Serial2(PIN_TX, PIN_RX);
int echo = 8;
int trig = 12;
uint8_t cond =0;
//uint8_t testd[5]={0x58,0x00,0x00,0x00,0x74};
uint8_t rx_dat[5]={};
uint8_t tx_dat[3]={};
unsigned char c;  // variable to store the received character
  
void setup() {
  Serial.begin(115200);  
  //Serial2.begin(115200); // setup serial
  pinMode(trig, OUTPUT);
  pinMode(echo, INPUT);
  pinMode(LED_BUILTIN, OUTPUT);
}      
               
void loop() {
  
/*
  if(Serial.available() > 0){
      c=Serial.read();
      Serial.print(c,HEX);
      delay(2000);
  
  }
*/
  
  
  float cycletime;
  float distance;

  //if(Serial.read()==0x58){
  /*  
    digitalWrite(LED_BUILTIN, HIGH);  // turn the LED on (HIGH is the voltage level)
    delay(1000);                      // wait for a second
    digitalWrite(LED_BUILTIN, LOW); 
    delay(1000);  // turn the LED off by making the voltage LOW
  */

    digitalWrite(trig, HIGH);
    delay(10);
    digitalWrite(trig, LOW);
  
    cycletime = pulseIn(echo, HIGH); 
  
    distance = ((340 * cycletime) / 10000) / 2;  

    //Serial.print("   Distance:");
    //Serial.print(distance);
    //Serial.println("cm");
    if(distance<15){
      cond = 1;
      tx_dat[0]=0xA5;
      tx_dat[1]=0x32;
      tx_dat[2]=0x33;
      tx_dat[3]=0x34;
      tx_dat[4]=0x5A;
    
    }
    
    else{
      cond = 0;
      tx_dat[0]=0xA5;
      tx_dat[1]=0x32;
      tx_dat[2]=0x33;
      tx_dat[3]=0x35;
      tx_dat[4]=0x5A;
       
    }
    
    
    
    
    for(int i=0;i<5;i++){
       Serial.write(tx_dat[i]);
    }
    
    delay(500);
  //}
}