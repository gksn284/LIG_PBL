library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.STD_LOGIC_UNSIGNED.ALL;
USE ieee.numeric_std.ALL;

entity motor_driver is
    Port ( clk : in  STD_LOGIC;
           motor_1 : out STD_LOGIC;
           motor_2 : out STD_LOGIC;
           motor_3 : out STD_LOGIC;
           motor_4 : out STD_LOGIC;
           motor_5 : out STD_LOGIC;
           step_motor : out STD_LOGIC;
           stepin : out std_logic;
           dirpin : out std_logic;
           UART_to_MD : in STD_LOGIC_VECTOR(23 downto 0));
           
end motor_driver;

architecture Behavioral of motor_driver is
   -- md_motor -> INIT_ST -> IDLE_ST -> DEC_ST -> COMMAND_ST -> IDLE_ST ...
   type md_state_type is (INIT_ST, RST_ST, IDLE_ST, DEC_ST,X50_ST,X51_ST, X52_ST, X53_ST, X54_ST, X55_ST, X56_ST, X57_ST, X600001_ST, X600002_ST, X600003_ST,X61_ST);
   signal md_state : md_state_type:= INIT_ST;
   
   -- state별 하는거
   -- INIT : 처음 초기화 하는 곳, rst을 안거칠수도 있어서 혹시 몰라서 넣어둠
   -- IDLE : 명령어가 UART로부터 들어오기 전까지 기다리는 상태, SAVE된 각도만 계속 출력
   -- DEC : 명령어 구분하는 STATE여기서 명령어 뜯어서 구분
   -- 나머지는 전부 명령어 STATE 너희가 다 채워 넣어야댐 출력은 전부 8BIT ANGLE로
   
   --서보모터 1 2 3 4 5 제어 할 때 쓰는 변수
   signal cnt_m : integer range 0 to 1000000 := 0;
   signal cnt_4s : integer range 0 to 1000 := 0;
   
   --스탭모터 제어 할 때 쓰는 변수
   signal cnt : integer range 0 to 40000;
   
   -- 명령어 잠시 저장할 곳 : 
   signal command_save :  std_logic_vector(23 downto 0):= x"000000";
   
   -- 최근 명령으로 들어온 각도 저장할 거
   signal motor_1_save : integer range 25000 to 125000:= 58330;
   signal motor_2_save : integer range 25000 to 125000:= 25000;
   signal motor_3_save : integer range 25000 to 125000:= 40000;
   signal motor_4_save : integer range 25000 to 125000:= 47000;
   signal motor_5_save : integer range 25000 to 125000:= 105553; 
   
   --초기화
   constant motor_1_init : integer:= 58330;
   constant motor_2_init : integer:= 25000;
   constant motor_3_init : integer:= 40000;
   constant motor_4_init : integer:= 47000;
   constant motor_5_init : integer:= 105553; 
   
   
   -- 명령어 0X61FFFF
begin
   process(clk)
   begin
      if(falling_edge(clk)) then
         --motor s1
         if (cnt_m <= motor_1_save) then
            motor_1 <= '1';
         else
            motor_1 <= '0';
         end if;
         -- motor 2
         if (cnt_m <= motor_2_save) then
            motor_2 <= '1';
         else
            motor_2 <= '0';
         end if;
         
         -- motor 3
         if (cnt_m <= motor_3_save) then
            motor_3 <= '1';
         else
            motor_3 <= '0';
         end if;

         -- motor 4
         if (cnt_m <= motor_4_save) then
            motor_4 <= '1';
         else
            motor_4 <= '0';
         end if;

         -- motor 5
         if (cnt_m <= motor_5_save) then
            motor_5 <= '1';
         else
            motor_5 <= '0';
         end if;
         -- step_motor : '0'  enable, '1' : disable
            -- dir : '0' 고정
            -- stepin : pwm
         if (cnt < 20000) then
            stepin <= '1';
            cnt <= cnt + 1;
         elsif (cnt = 40000) then
            cnt <= 0;
         else
            stepin <= '0';
            cnt <= cnt + 1;
         end if;
            dirpin <= '0';
            
         --counting
         if(cnt_m = 1000000) then
            cnt_m <= 0;
            cnt_4s <= cnt_4s +1;
         else
            cnt_m <= cnt_m+1;
         end if;
               
         case md_state is
            when INIT_ST =>
               motor_1_save <= motor_1_init;
               motor_2_save <= motor_2_init;
               motor_3_save <= motor_3_init;
               motor_4_save <= motor_4_init;
               motor_5_save <= motor_5_init;
               step_motor <= '1';
               md_state <= IDLE_ST;
               
            when RST_ST =>
               motor_1_save <= motor_1_init;
               motor_2_save <= motor_2_init;
               motor_3_save <= motor_3_init;
               motor_4_save <= motor_4_init;
               motor_5_save <= motor_5_init;
               step_motor <= '1';
               md_state <= IDLE_ST;
               
            
            
            when IDLE_ST =>
               if(UART_to_MD/=X"000000") then
                  command_save <= UART_to_MD;
                  md_state <= DEC_ST;
               else
                  command_save <= (others=>'0');
               end if;
               cnt_4s <= 0;
            
            when DEC_ST =>
               if(command_save(23 downto 16)=X"50") then
                  md_state <= X50_ST;
               elsif(command_save(23 downto 16)=X"51") then
                  md_state <= X51_ST;
               elsif(command_save(23 downto 16)=X"52") then
                  md_state <= X52_ST;
               elsif(command_save(23 downto 16)=X"53") then
                  md_state <= X53_ST;
               elsif(command_save(23 downto 16)=X"54") then
                  md_state <= X54_ST;
               elsif(command_save(23 downto 16)=X"55") then
                  md_state <= X55_ST;
               elsif(command_save(23 downto 16)=X"56") then
                  md_state <= X56_ST;
               elsif(command_save(23 downto 16)=X"57") then
                  md_state <= X57_ST;
               elsif(command_save=X"600001") then
                  md_state <= X600001_ST;
               elsif(command_save=X"600002") then
                  md_state <= X600002_ST;
               elsif(command_save=X"600003") then
                  md_state <= X600003_ST;
               elsif(command_save(23 downto 16)=X"61") then
                  md_state <= X61_ST;
               else
                  md_state <= IDLE_ST;
               end if;

            when X50_ST =>
               motor_1_save <= 58330;
               motor_2_save <= 30000;
               motor_3_save <= 40000;
               motor_4_save <= 47000;
               motor_5_save <= 105553;
               md_State <= IDLE_ST;
            when X51_ST =>
               --놓기
               motor_1_save <= 25000 + to_integer(signed(command_save(7 downto 0))) * 555;
               step_motor <= '1';
               md_State <= IDLE_ST;               
            when X52_ST =>   
               motor_2_save <= 25000 + to_integer(signed(command_save(7 downto 0))) * 555;
               step_motor <= '1';
               md_State <= IDLE_ST;
               
            when X53_ST =>
               motor_3_save <= 25000 + to_integer(signed(command_save(7 downto 0))) * 555;
               step_motor <= '1';
               md_State <= IDLE_ST;
               
            when X54_ST =>
               motor_4_save <= 25000 + to_integer(signed(command_save(7 downto 0))) * 555;
               step_motor <= '1';
               md_State <= IDLE_ST;
               
            when X55_ST =>
               motor_5_save <= 25000 + to_integer(signed(command_save(7 downto 0))) * 555;
               step_motor <= '1';
               md_State <= IDLE_ST;
               
            when X56_ST =>
               --벨트 동작
               if(command_save(15 downto 0)=(X"0FF0")) then
                  step_motor <= '0'; --벨트 enable 변수 : 0이면 동작 1이면 정지
               --벨트 정지
               elsif(command_save(15 downto 0)=(X"0110")) then
                  step_motor <= '1';
                  --여기서 서보모터 카운트 초기화
               end if;
               md_state <= IDLE_ST;
               
            when X57_ST =>
               md_State <= RST_ST;
               
            when X600001_ST =>
               --default
               if (cnt_4s < 50) then
                  motor_1_save <= 58330;
                  motor_2_save <= 25000;
                  motor_3_save <= 40000;
                  motor_4_save <= 47000;
                  motor_5_save <= 105553;
               --before grip 1
               elsif (cnt_4s < 100) then
                  if(cnt_m = 1000000) then
                     if(motor_3_save <= 57000) then
                        motor_3_save <= motor_3_save + 1000;
                     end if;
                  end if;
               --motor_1 grip o
               elsif (cnt_4s < 150) then
                  motor_1_save <= 125000;
               --motor_3 up
               elsif (cnt_4s < 200) then
                  if(cnt_m = 1000000) then
                     if(41000 <= motor_3_save) then
                        motor_3_save <= motor_3_save - 1000;
                     end if;
                  end if;                              
               --box1
               elsif (cnt_4s < 250) then
                  if(cnt_m = 1000000) then
                     if(63108 <= motor_5_save) then
                        motor_5_save <= motor_5_save - 2000;
                     else
                        motor_5_save <= 61108;
                     end if;
                  end if;
                  
               elsif (cnt_4s < 300) then
                  motor_2_save <= 30000;
                  if(cnt_m = 1000000) then
                     if(motor_4_save <= 75000) then
                        motor_4_save <= motor_4_save + 2000;
                     end if;
                     
                     if(motor_3_save <= 85000) then
                        motor_3_save <= motor_3_save + 2000;
                     else
                        motor_3_save <= 87000;
                     end if;
                  end if;
                  
               --motor_1 grip x
               elsif (cnt_4s < 350) then
                  motor_1_save <= 58330;
                  
               elsif (cnt_4s < 400) then
                  motor_1_save <= 58330;
                  motor_2_save <= 25000;
                  motor_3_save <= 40000;
                  motor_4_save <= 47000;
               --default
               elsif (cnt_4s < 450) then
                  motor_5_save <= 105553;
                  md_state <= IDLE_ST;
               end if;
               
            when X600002_ST =>
               --default
               if (cnt_4s < 50) then
                  motor_1_save <= 58330;
                  motor_2_save <= 25000;
                  motor_3_save <= 40000;
                  motor_4_save <= 47000;
                  motor_5_save <= 105553;
               --before grip 1
               elsif (cnt_4s < 100) then
                  if(cnt_m = 1000000) then
                     if(motor_3_save <= 57000) then
                        motor_3_save <= motor_3_save + 1000;
                     end if;
                  end if;
               --motor_1 grip o
               elsif (cnt_4s < 150) then
                  motor_1_save <= 125000;
               --motor_3 up
               elsif (cnt_4s < 200) then
                  if(cnt_m = 1000000) then
                     if(41000 <= motor_3_save) then
                        motor_3_save <= motor_3_save - 1000;
                     end if;
                  end if;                              
               --box2
               elsif (cnt_4s < 250) then
                  if(cnt_m = 1000000) then
                     if(63108 <= motor_5_save) then
                        motor_5_save <= motor_5_save - 2000;
                     else
                        motor_5_save <= 61108;
                     end if;
                  end if; 

               elsif (cnt_4s < 300) then
                  motor_2_save <= 30000;
                  if(cnt_m = 1000000) then
                     if(motor_4_save <= 57330) then
                        motor_4_save <= motor_4_save + 1000;
                     else
                        motor_4_save <= 58330;
                     end if;
                  
                     if(motor_3_save <= 71222) then
                        motor_3_save <= motor_3_save + 1000;
                     else
                        motor_3_save <= 72222;
                     end if;
                  end if;
               --motor_1 grip x
               elsif (cnt_4s < 350) then
                  motor_1_save <= 58330;  
                  
               elsif (cnt_4s < 400) then
                  motor_1_save <= 58330;
                  motor_2_save <= 25000;
                  motor_3_save <= 40000;
                  motor_4_save <= 47000;   
               --default
               elsif (cnt_4s < 450) then
                  motor_5_save <= 105553;
                  md_state <= IDLE_ST;                  
               end if;
               
            when X600003_ST =>
               --default
               if (cnt_4s < 50) then
                  motor_1_save <= 58330;
                  motor_2_save <= 25000;
                  motor_3_save <= 40000;
                  motor_4_save <= 47000;
                  motor_5_save <= 105553;
               --before grip 1
               elsif (cnt_4s < 100) then
                  if(cnt_m = 1000000) then
                     if(motor_3_save <= 57000) then
                        motor_3_save <= motor_3_save + 1000;
                     end if;
                  end if;
               --motor_1 grip o
               elsif (cnt_4s < 150) then
                  motor_1_save <= 125000;
               --motor_3 up
               elsif (cnt_4s < 200) then
                  if(cnt_m = 1000000) then
                     if(41000 <= motor_3_save) then
                        motor_3_save <= motor_3_save - 1000;
                     end if;
                  end if;                              
               --box3_1
               elsif (cnt_4s < 250) then
                  motor_2_save <= 30000;
                  if(cnt_m = 1000000) then
                     if(63108 <= motor_5_save) then
                        motor_5_save <= motor_5_save - 2000;
                     else
                        motor_5_save <= 61108;
                     end if;
                  end if;
               --box3_2
               elsif (cnt_4s < 300) then
                  if(cnt_m = 1000000) then
                     if(motor_3_save <= 54000) then
                        motor_3_save <= motor_3_save + 1000;
                     else
                        motor_3_save <= 55000;
                     end if;
                  end if;
                                             
               --motor_1 grip x
               elsif (cnt_4s < 350) then
                  motor_1_save <= 58330;                           
               --default
               elsif (cnt_4s < 400) then
                  motor_1_save <= 58330;
                  motor_2_save <= 25000;
                  motor_3_save <= 40000;
                  motor_4_save <= 47000;
                  motor_5_save <= 105553;
                  md_state <= IDLE_ST;
               end if;
         
            when X61_ST =>
               --시작, 리셋 같음(1 2 3번 상자에 넣으라는 명령 전까지는 전부 디폴트 유지해야함.)
               if (command_save(15 downto 0) = X"00FF" or command_save(15 downto 0) = X"FFFF") then
                  step_motor <= '0';
               end if;
               md_State <= IDLE_ST;

            when others =>
               md_state <= IDLE_ST;
         end case;
      end if;
   end process;

end Behavioral;