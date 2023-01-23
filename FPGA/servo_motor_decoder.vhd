----------------------------------------------------------------------------------
-- Company: 
-- Engineer: 
-- 
-- Create Date:    13:36:33 01/23/2023 
-- Design Name: 
-- Module Name:    servo_motor_decoder - Behavioral 
-- Project Name: 
-- Target Devices: 
-- Tool versions: 
-- Description: 
--
-- Dependencies: 
--
-- Revision: 
-- Revision 0.01 - File Created
-- Additional Comments: 
--
----------------------------------------------------------------------------------
-- memo
-- clk : 50MHz -> 20ns/bit
-- servo motor period : 20ms -> need 1000000 clk_count
-- servo motor duty ratio : 0.05 to 0.1 -> 1~2ms need 50000~100000 clk_count
-- input : Let angle_in be [7:0]
-- angle_in : 0 to 180 (-90~90), let 50000 as 0, 100000 as 180
--				  								 
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.STD_LOGIC_UNSIGNED.ALL;
USE ieee.numeric_std.ALL;

entity servo_motor_decoder is
    Port ( clk : in  STD_LOGIC;
           angle_in : in  STD_LOGIC_vector (7 downto 0);
           angle_out : out  STD_LOGIC);
end servo_motor_decoder;

architecture Behavioral of servo_motor_decoder is
		signal clk_count 	: integer range 0 to 1000000; -- count clk
		signal duty_std 	: integer range 0 to 100000; -- stand for duty ratio
		signal duty_var 	: integer range 0 to 100000; -- to increase/decrease duty var
begin
	process(clk)
	begin
		if rising_edge(clk) then
			duty_std <= 50000 + to_integer(signed(angle_in)) * 278; -- 50000 + angle_in * 278
			if (clk_count< duty_var) then -- output '0' ('"not gate)
				angle_out <= '0';
			elsif (clk_count < 1000000) then
				angle_out <= '1';
			elsif (clk_count=1000000) then
				clk_count <= 0;
				angle_out <= '0';
				if (duty_var < duty_std) then
					duty_var <= duty_var + 100;
				elsif ( duty_var > duty_std) then
					duty_var <= duty_var - 100;
				end if;
			end if;
			clk_count <= clk_count+1;
		end if;
	end process;
end Behavioral;

