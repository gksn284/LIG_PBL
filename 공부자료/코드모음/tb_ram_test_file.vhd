--------------------------------------------------------------------------------
-- Company: 
-- Engineer:
--
-- Create Date:   20:26:15 01/17/2023
-- Design Name:   
-- Module Name:   C:/work1/work_led/tb_ram_test_file.vhd
-- Project Name:  work_led
-- Target Device:  
-- Tool versions:  
-- Description:   
-- 
-- VHDL Test Bench Created by ISE for module: ram_test_file
-- 
-- Dependencies:
-- 
-- Revision:
-- Revision 0.01 - File Created
-- Additional Comments:
--
-- Notes: 
-- This testbench has been automatically generated using types std_logic and
-- std_logic_vector for the ports of the unit under test.  Xilinx recommends
-- that these types always be used for the top-level I/O of a design in order
-- to guarantee that the testbench will bind correctly to the post-implementation 
-- simulation model.
--------------------------------------------------------------------------------
LIBRARY ieee;
USE ieee.std_logic_1164.ALL;
 
-- Uncomment the following library declaration if using
-- arithmetic functions with Signed or Unsigned values
--USE ieee.numeric_std.ALL;
 
ENTITY tb_ram_test_file IS
END tb_ram_test_file;
 
ARCHITECTURE behavior OF tb_ram_test_file IS 
 
    -- Component Declaration for the Unit Under Test (UUT)
 
    COMPONENT ram_test_file
    PORT(
         clka : IN  std_logic;
         wea : IN  std_logic_vector(0 downto 0);
         addra : IN  std_logic_vector(3 downto 0);
         dina : IN  std_logic_vector(7 downto 0);
         douta : OUT  std_logic_vector(7 downto 0)
        );
    END COMPONENT;
    

   --Inputs
   signal clka : std_logic := '0';
   signal wea : std_logic_vector(0 downto 0) := (others => '0');
   signal addra : std_logic_vector(3 downto 0) := (others => '0');
   signal dina : std_logic_vector(7 downto 0) := (others => '0');

 	--Outputs
   signal douta : std_logic_vector(7 downto 0);

   -- Clock period definitions
   constant clka_period : time := 20 ns;
 
BEGIN
 
	-- Instantiate the Unit Under Test (UUT)
   uut: ram_test_file PORT MAP (
          clka => clka,
          wea => wea,
          addra => addra,
          dina => dina,
          douta => douta
        );

   -- Clock process definitions
   clka_process :process
   begin
		clka <= '0';
		wait for clka_period/2;
		clka <= '1';
		wait for clka_period/2;
   end process;
 

   -- Stimulus process
   stim_proc: process
   begin		
      -- hold reset state for 100 ns.
      wait for 100 ns;	

      wait for clka_period*10;

      -- insert stimulus here 
		
		addra <= "0000";
		dina <= X"00";
		wea <= "0";
		
		wait for clka_period*10;
		
		-- addr : 0x1
		-- data : 0xaa
		
		addra <= X"1";
		dina <= X"AA";
		wea <= "1";
		wait for clka_period*5;
		
		addra <= "0000";
		dina <= X"00";
		wea <= "0";
		
		
		
		wait for clka_period*20;



		-- addr : 0x2
		-- data : 0xbb
		
		addra <= X"2";
		dina <= X"BB";
		wea <= "1";
		wait for clka_period*5;
		
		addra <= "0000";
		dina <= X"00";
		wea <= "0";
		
		wait for clka_period*20;
		
		
		-- read
		addra <= X"1";
		wait for clka_period*20;
		
		
		addra <= X"2";
		wait for clka_period*20;
		

      wait;
   end process;

END;
