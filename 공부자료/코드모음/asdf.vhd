library ieee;
use ieee.std_logic_1164.all;
use ieee.std_logic_unsigned.all;

entity rs232_rx_test is
port(
	CLK : in std_logic;	-- 20 ns
	RXD : in std_logic;
	TXD : out std_logic;
	
	SEG_CA : out std_logic;
	SEG_CB : out std_logic;
	SEG_CC : out std_logic;
	SEG_CD : out std_logic;
	SEG_CE : out std_logic;
	SEG_CF : out std_logic;
	SEG_CG : out std_logic;
	SEG_DP : out std_logic;
	
	SEG_AN0 : out std_logic;
	
	BTN_0 : in std_logic;
	BTN_1 : in std_logic;
	BTN_2 : in std_logic;
	BTN_3 : in std_logic
);
end rs232_rx_test;

architecture behavior of rs232_rx_test is

	type state_type is (IDLE_ST, RX_ST, DECODE_ST);
	signal state : state_type := IDLE_ST;
	
	-- rs223 buad rate : 9600 bps
	-- 1 period = 104.2 us
	signal time_cnt : integer range 0 to 5210 := 0; -- 5210 = 104200/20
	signal rx_cnt : integer range 0 to 9 := 0;
	
	signal latch_data : std_logic_vector(9 downto 0);
	signal seg_data : std_logic_vector(7 downto 0) := X"00";
	
	
	-- Segment(CG,CF,...,CB,CA,DP)
	-- '1' : Segment OFF
	-- '0' : Segment ON
	--			  --(CA)--
	--			 |			 |
	--		(CF)|		    |(CB)
	--			 |			 |
	--			  --(CG)--
	--			 |			 |
	--		(CE)|		    |(CC)
	--			 |			 |
	--			  --(CD)--		.(DP)
	
	constant const_seg_1 : std_logic_vector(7 downto 0) := "00001100";
	constant const_seg_2 : std_logic_vector(7 downto 0) := "10110110";
	constant const_seg_3 : std_logic_vector(7 downto 0) := "10011110";
	constant const_seg_4 : std_logic_vector(7 downto 0) := "11011100";
	constant const_seg_5 : std_logic_vector(7 downto 0) := "11011010";
	constant const_seg_6 : std_logic_vector(7 downto 0) := "11111010";
	constant const_seg_7 : std_logic_vector(7 downto 0) := "00011110";
	constant const_seg_8 : std_logic_vector(7 downto 0) := "11111110";
	constant const_seg_9 : std_logic_vector(7 downto 0) := "11011110";
	constant const_seg_0 : std_logic_vector(7 downto 0) := "01111110";
	constant const_seg_dot : std_logic_vector(7 downto 0) := "00000001";

	
	signal tx_time_cnt : integer range 0 to 5210 := 0; -- 5210 = 104200/20
	signal tx_cnt : integer range 0 to 9 := 0;
	signal data_temp : std_logic_Vector(7 downto 0);
	
	
	constant const_tx_A : std_logic_vector(7 downto 0) := X"41";
	constant const_tx_B : std_logic_vector(7 downto 0) := X"42";
	constant const_tx_C : std_logic_vector(7 downto 0) := X"43";
	constant const_tx_D : std_logic_vector(7 downto 0) := X"44";

begin

	process(CLK)
	begin
		if (rising_edge(CLK)) then
		
			case state is
			
				when IDLE_ST =>
					if (RXD = '0') then
						state <= RX_ST;
					end if;
					time_cnt <= 0;
					rx_cnt <= 0;
					latch_data <= (others => '1');
				 
				 
				when RX_ST =>
					if (time_cnt = 2605) then
						latch_data(9) <= RXD;
						time_cnt <= time_cnt + 1;
					elsif (time_cnt = 5210) then
						if (rx_cnt < 9) then
							latch_data <= '1' & latch_data(9 downto 1);
							time_cnt <= 0;
							rx_cnt <= rx_cnt + 1;
						else
							time_cnt <= 0;
							rx_cnt <= 0;
							state <= DECODE_ST;
						end if;
					else
						time_cnt <= time_cnt + 1;
					end if;	
						
				
				when DECODE_ST =>
					if (latch_data(8 downto 1) = X"31") then
						seg_data <= const_seg_1;
					elsif (latch_data(8 downto 1) = X"32") then
						seg_data <= const_seg_2;
					elsif (latch_data(8 downto 1) = X"33") then
						seg_data <= const_seg_3;
					elsif (latch_data(8 downto 1) = X"34") then
						seg_data <= const_seg_4;
					elsif (latch_data(8 downto 1) = X"35") then
						seg_data <= const_seg_5;
					elsif (latch_data(8 downto 1) = X"36") then
						seg_data <= const_seg_6;
					elsif (latch_data(8 downto 1) = X"37") then
						seg_data <= const_seg_7;
					elsif (latch_data(8 downto 1) = X"38") then
						seg_data <= const_seg_8;
					elsif (latch_data(8 downto 1) = X"39") then
						seg_data <= const_seg_9;
					elsif (latch_data(8 downto 1) = X"30") then
						seg_data <= const_seg_0;
					else
						seg_data <= const_seg_dot;
					end if;
					state <= IDLE_ST;
				
				when others =>
				
			end case;
		
		end if;
	end process;
	
	SEG_CG <= not seg_data(7);
	SEG_CF <= not seg_data(6);
	SEG_CE <= not seg_data(5);
	SEG_CD <= not seg_data(4);
	SEG_CC <= not seg_data(3);
	SEG_CB <= not seg_data(2);
	SEG_CA <= not seg_data(1);
	SEG_DP <= not seg_data(0);
	
	SEG_AN0 <= '0';
	
	
	
	process(CLK)
	begin
		if (rising_Edge(CLK)) then
			if (tx_time_cnt = 0) then
				if (BTN_0 = '1') then
					data_Temp <= const_tx_A;
					tx_time_cnt <= tx_time_cnt + 1;
				elsif (BTN_1 = '1') then
					data_Temp <= const_tx_B;
					tx_time_cnt <= tx_time_cnt + 1;
				elsif (BTN_2 = '1') then
					data_Temp <= const_tx_C;
					tx_time_cnt <= tx_time_cnt + 1;
				elsif (BTN_3 = '1') then
					data_Temp <= const_tx_D;
					tx_time_cnt <= tx_time_cnt + 1;
				end if;
				TXD <= '1';
				
			elsif (tx_time_cnt = 1) then
				-- start_bit
				if (tx_cnt = 0) then
					TXD <= '0';
				-- data_bit	
				elsif (tx_cnt < 9) then
					TXD <= data_Temp(0);
				-- stop_bit
				else
					TXD <= '1';
				end if;
				tx_time_cnt <= tx_time_cnt + 1;
				
			elsif(tx_time_cnt = 5210) then
				if (tx_cnt = 0) then
					tx_cnt <= tx_cnt + 1;
					tx_time_cnt <= 1;
				elsif (tx_cnt < 9) then
					data_Temp <= '1' & data_Temp(7 downto 1);
					tx_cnt <= tx_cnt + 1;
					tx_time_cnt <= 1;
				else
					data_temp <= (others => '0');
					tx_cnt <= 0;
					tx_time_cnt <= 0;
				end if;
				
			else
				tx_time_cnt <= tx_time_cnt + 1;
			end if;
		
		end if;
	
	end  process;

end behavior;