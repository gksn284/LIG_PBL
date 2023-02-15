---------------------------------------------------------------------------------
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.STD_LOGIC_UNSIGNED.ALL;

entity UART is
Port ( clk : in  STD_LOGIC;
           rxd : in  STD_LOGIC;
           txd : out  STD_LOGIC;
           UART_to_MD : out  STD_LOGIC_VECTOR (23 downto 0):=(others => '0')
           );
end UART;

architecture Behavioral of UART is

   -- RX
   type rx_state_type is (RX_IDLE_ST, REC_ST, WAIT_ST, DECODE_ST);
   signal rx_state : rx_state_type:=RX_IDLE_ST;
   
   signal rx_clk_cnt : integer range 0 to 500:= 0; -- 8.68us -> 20ns * 434
   signal rx_data_cnt : integer range 0 to 10:= 0; -- 
   signal rx_frame_cnt : integer range 0 to 5:= 0;
   signal rx_data_temp : std_logic_vector(9 downto 0) := (others => '1');
   signal rx_data_lat_1 : std_logic_vector(7 downto 0) := X"00";
   signal rx_data_lat_2 : std_logic_vector(7 downto 0) := X"00";
   signal rx_data_lat_3 : std_logic_vector(7 downto 0) := X"00";
   signal rx_data_lat_4 : std_logic_vector(7 downto 0) := X"00";
   signal rx_data_lat_5 : std_logic_vector(7 downto 0) := X"00";
   
   signal tx_req_s : std_logic := '0';   -- '0' : Not,  '1' : tx_req
   -- TX
   type tx_state_type is (TX_IDLE_ST, TX_ST);
   signal tx_state : tx_state_type:=TX_IDLE_ST;
   
   signal tx_clk_cnt : integer range 0 to 500:= 0; -- 8.68us -> 20ns * 434
   signal tx_data_cnt : integer range 0 to 12:= 0; -- 
   signal tx_frame_cnt : integer range 0 to 5:= 0;
   signal tx_wait_cnt : integer range 0 to 250000000:= 0;
   
   signal tx_req_data_1 : std_logic_vector(7 downto 0) := X"A5";
   signal tx_req_data_2 : std_logic_vector(7 downto 0) := X"A5";
   signal tx_req_data_3 : std_logic_vector(7 downto 0) := X"A5";
   signal tx_data_temp : std_logic_vector(11 downto 0) := (others => '1');
   
   constant tx_start_frame : std_logic_vector(7 downto 0) := X"A5";
   constant tx_end_frame : std_logic_vector(7 downto 0) := X"5A";
   
   -- escape counter
   signal escape_cnt : integer range 0 to 5000000:= 0;
   signal escape_en  : std_logic:='0';
begin

   -- rx
   process(clk)
   begin
      if(rising_edge(clk)) then
         case rx_state is
            when RX_IDLE_ST =>
               rx_clk_cnt <= 0;
               rx_data_cnt <= 0;
               rx_frame_cnt <= 0;
               rx_data_temp <= (others => '1');
               rx_data_lat_1 <= (others => '0');
               rx_data_lat_2 <= (others => '0');
               rx_data_lat_3 <= (others => '0');
               rx_data_lat_4 <= (others => '0');
               rx_data_lat_5 <= (others => '0');
               tx_req_s <= '0';
					UART_to_MD <= (others => '0');
               if (rxd = '0') then
                  rx_state <= REC_ST;
               end if;
               
            when REC_ST =>
               if (rx_clk_cnt = 217) then
                  rx_data_temp(9) <= rxd;
                  rx_clk_cnt <= rx_clk_cnt + 1;
               elsif (rx_clk_cnt = 434) then
                  if (rx_data_cnt = 9) then
                     rx_data_cnt <= 0;
                     rx_state <= WAIT_ST;
                  else
                     rx_data_temp <= '1' & rx_data_temp(9 downto 1);
                     rx_data_cnt <= rx_data_cnt + 1;
                  end if;
                  rx_clk_cnt <= 0;
               else
                  rx_clk_cnt <= rx_clk_cnt + 1;
               end if;
               if (escape_en = '1') then
                  rx_state <= RX_IDLE_ST;
               end if;
            when WAIT_ST =>
               rx_clk_cnt <= 0;
               if (rx_frame_cnt = 0) then
                  rx_data_lat_1 <= rx_data_temp(8 downto 1);
                  if (rxd = '0') then
                     rx_frame_cnt <= rx_frame_cnt + 1;
                     rx_state <= REC_ST;
                  end if;
               elsif (rx_frame_cnt = 1) then
                  rx_data_lat_2 <= rx_data_temp(8 downto 1);
                  if (rxd = '0') then
                     rx_frame_cnt <= rx_frame_cnt + 1;
                     rx_state <= REC_ST;
                  end if;
               elsif (rx_frame_cnt = 2) then
                  rx_data_lat_3 <= rx_data_temp(8 downto 1);
                  if (rxd = '0') then
                     rx_frame_cnt <= rx_frame_cnt + 1;
                     rx_state <= REC_ST;
                  end if;
               elsif (rx_frame_cnt = 3) then
                  rx_data_lat_4 <= rx_data_temp(8 downto 1);
                  if (rxd = '0') then
                     rx_frame_cnt <= rx_frame_cnt + 1;
                     rx_state <= REC_ST;
                  end if;
               elsif (rx_frame_cnt = 4) then
                  rx_data_lat_5 <= rx_data_temp(8 downto 1);
                  rx_frame_cnt <= 0;
                  rx_state <= DECODE_ST;
               end if;
               
               if (escape_en = '1') then
                  rx_state <= RX_IDLE_ST;
               end if;
            
            when DECODE_ST =>
               if (rx_clk_cnt = 0) then
                  if (rx_data_lat_1 = X"A5") then
                     if(rx_data_lat_5 = X"5A") then
                        tx_req_s <= '1';
                        tx_req_data_1 <= X"A5";
                        tx_req_data_2 <= X"A5";
                        tx_req_data_3 <= X"A5";
                        UART_TO_MD <= rx_data_lat_2 & rx_data_lat_3 & rx_data_lat_4;
                        rx_state <= RX_IDLE_ST;
                     end if;
                  end if;
                  rx_clk_cnt <= rx_clk_cnt + 1;
               elsif (rx_clk_cnt = 5) then
                  rx_clk_cnt <= 0;
                  rx_state <= RX_IDLE_ST;
               else
                  rx_clk_cnt <= rx_clk_cnt + 1;
               end if;
               
               if (escape_en = '1') then
                  rx_state <= RX_IDLE_ST;
               end if;
            
            when others =>
               rx_state <= RX_IDLE_ST;
         end case;  
      end if;
   end process;
  
   process(clk)
   begin
      if(falling_edge(clk)) then
         if(escape_cnt = 500000 and rx_state /= RX_IDLE_ST) then
            escape_cnt <= 0;
            escape_en <= '1';
         elsif (rx_state = RX_IDLE_ST) then
            escape_cnt <= 0;
            escape_en <= '0';
         else
            escape_cnt <= escape_cnt+1;
         end if;
      end if;
   end process;
  
   process(clk)
   begin
      if (falling_edge(clk)) then
         case tx_state is
            when TX_IDLE_ST =>
               tx_clk_cnt <= 0;
               tx_data_cnt <= 0;
               tx_frame_cnt <= 0;
               txd <= '1';
               tx_data_temp <= (others => '1');
               if (tx_req_s = '1') then
                  tx_state <= TX_ST;
               end if;
               
            when TX_ST =>
               -- frame_1
               if (tx_frame_cnt = 0) then
                  if (tx_clk_cnt = 0) then
                     tx_data_temp <= "111" & tx_start_frame & '0';
                     tx_clk_cnt <= tx_clk_cnt + 1;
                  elsif (tx_clk_cnt = 1) then
                     txd <= tx_data_temp(0);
                     tx_clk_cnt <= tx_clk_cnt + 1;
                  elsif (tx_clk_cnt = 434) then
                     if (tx_data_cnt = 11) then
                        tx_clk_cnt <= 0;
                        tx_data_cnt <= 0;
                        tx_frame_cnt <= tx_frame_cnt + 1;
                     else
                        tx_data_temp <= '1' & tx_data_temp(11 downto 1);
                        tx_data_cnt <= tx_data_cnt + 1;
                        tx_clk_cnt <= 1;
                     end if;
                  else
                     tx_clk_cnt <= tx_clk_cnt + 1;
                  end if;
                  
               -- frame_2
               elsif (tx_frame_cnt = 1) then
                  if (tx_clk_cnt = 0) then
                     tx_data_temp <= "111" & tx_req_data_1 & '0';
                     tx_clk_cnt <= tx_clk_cnt + 1;
                  elsif (tx_clk_cnt = 1) then
                     txd <= tx_data_temp(0);
                     tx_clk_cnt <= tx_clk_cnt + 1;
                  elsif (tx_clk_cnt = 434) then
                     if (tx_data_cnt = 11) then
                        tx_clk_cnt <= 0;
                        tx_data_cnt <= 0;
                        tx_frame_cnt <= tx_frame_cnt + 1;
                     else
                        tx_data_temp <= '1' & tx_data_temp(11 downto 1);
                        tx_data_cnt <= tx_data_cnt + 1;
                        tx_clk_cnt <= 1;
                     end if;
                  else
                     tx_clk_cnt <= tx_clk_cnt + 1;
                  end if;
                  
               -- frame_3
               elsif (tx_frame_cnt = 2) then
                  if (tx_clk_cnt = 0) then
                     tx_data_temp <= "111" & tx_req_data_2 & '0';
                     tx_clk_cnt <= tx_clk_cnt + 1;
                  elsif (tx_clk_cnt = 1) then
                     txd <= tx_data_temp(0);
                     tx_clk_cnt <= tx_clk_cnt + 1;
                  elsif (tx_clk_cnt = 434) then
                     if (tx_data_cnt = 11) then
                        tx_clk_cnt <= 0;
                        tx_data_cnt <= 0;
                        tx_frame_cnt <= tx_frame_cnt + 1;
                     else
                        tx_data_temp <= '1' & tx_data_temp(11 downto 1);
                        tx_data_cnt <= tx_data_cnt + 1;
                        tx_clk_cnt <= 1;
                     end if;
                  else
                     tx_clk_cnt <= tx_clk_cnt + 1;
                  end if;
                  
               -- frame_4
               elsif (tx_frame_cnt = 3) then
                  if (tx_clk_cnt = 0) then
                     tx_data_temp <= "111" & tx_req_data_3 & '0';
                     tx_clk_cnt <= tx_clk_cnt + 1;
                  elsif (tx_clk_cnt = 1) then
                     txd <= tx_data_temp(0);
                     tx_clk_cnt <= tx_clk_cnt + 1;
                  elsif (tx_clk_cnt = 434) then
                     if (tx_data_cnt = 11) then
                        tx_clk_cnt <= 0;
                        tx_data_cnt <= 0;
                        tx_frame_cnt <= tx_frame_cnt + 1;
                     else
                        tx_data_temp <= '1' & tx_data_temp(11 downto 1);
                        tx_data_cnt <= tx_data_cnt + 1;
                        tx_clk_cnt <= 1;
                     end if;
                  else
                     tx_clk_cnt <= tx_clk_cnt + 1;
                  end if;
                  
               -- frame_5
               elsif (tx_frame_cnt = 4) then
                  if (tx_clk_cnt = 0) then
                     tx_data_temp <= "111" & tx_end_frame & '0';
                     tx_clk_cnt <= tx_clk_cnt + 1;
                  elsif (tx_clk_cnt = 1) then
                     txd <= tx_data_temp(0);
                     tx_clk_cnt <= tx_clk_cnt + 1;
                  elsif (tx_clk_cnt = 434) then
                     if (tx_data_cnt = 11) then
                        tx_clk_cnt <= 0;
                        tx_data_cnt <= 0;
                        tx_frame_cnt <= 0;
                        tx_state <= TX_IDLE_ST;
                     else
                        tx_data_temp <= '1' & tx_data_temp(11 downto 1);
                        tx_data_cnt <= tx_data_cnt + 1;
                        tx_clk_cnt <= 1;
                     end if;
                  else
                     tx_clk_cnt <= tx_clk_cnt + 1;
                  end if;
               end if;
            
            when others =>
               tx_state <= TX_IDLE_ST;
         end case;
         
      end if;
   
   end process;

end Behavioral;