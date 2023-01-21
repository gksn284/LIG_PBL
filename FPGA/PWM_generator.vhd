library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
USE IEEE.STD_LOGIC_UNSIGNED.ALL;

-- clk = 50MHz -> 20ns
-- 20ms -> clk count => 1000000
-- 1ms~2ms pw => 50000~100000
-- pw increase


entity PWM_Generator is
port (
   clk: in std_logic; -- 100MHz clock input 
   PWM_OUT: out std_logic -- PWM signal out with frequency of 10MHz
  );
end PWM_Generator;

architecture Behavioral of PWM_Generator is
 signal clk_count : integer range 0 to 1000000;
 signal pwm_std : integer range 0 to 100000;
 signal dir : std_logic :='0';
begin
   process(clk)
   begin
   if(rising_edge(clk)) then
      clk_count <= clk_count + 1;
      if(clk_count<pwm_std) then
         pwm_out <= '0';
      elsif(clk_count<1000000) then
         pwm_out <= '1';
      elsif(clk_count=1000000) then
         pwm_out<='0';
         clk_count <= 0;
         if(pwm_std<100000 and dir = '0') then
            pwm_std <= pwm_std+100;
         elsif(pwm_std=100000) then
            pwm_std <= pwm_std-100;
            dir <='1';
         elsif(pwm_std>50000 and dir='1') then
            pwm_std <=pwm_Std-100;
         elsif(pwm_std >50000) then
            pwm_std <= pwm_std+100;
            dir <='0';
         else
         end if;
      end if;
   end if;
   end process;
end Behavioral;
