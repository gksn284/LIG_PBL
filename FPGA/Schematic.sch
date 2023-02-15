<?xml version="1.0" encoding="UTF-8"?>
<drawing version="7">
    <attr value="spartan3e" name="DeviceFamilyName">
        <trait delete="all:0" />
        <trait editname="all:0" />
        <trait edittrait="all:0" />
    </attr>
    <netlist>
        <signal name="clk" />
        <signal name="XLXN_2(23:0)" />
        <signal name="rxd" />
        <signal name="txd" />
        <signal name="motor_1" />
        <signal name="motor_2" />
        <signal name="motor_3" />
        <signal name="motor_4" />
        <signal name="motor_5" />
        <signal name="step_motor" />
        <signal name="stepin" />
        <signal name="dirpin" />
        <port polarity="Input" name="clk" />
        <port polarity="Input" name="rxd" />
        <port polarity="Output" name="txd" />
        <port polarity="Output" name="motor_1" />
        <port polarity="Output" name="motor_2" />
        <port polarity="Output" name="motor_3" />
        <port polarity="Output" name="motor_4" />
        <port polarity="Output" name="motor_5" />
        <port polarity="Output" name="step_motor" />
        <port polarity="Output" name="stepin" />
        <port polarity="Output" name="dirpin" />
        <blockdef name="motor_driver">
            <timestamp>2023-2-9T5:30:0</timestamp>
            <rect width="336" x="64" y="-512" height="512" />
            <line x2="0" y1="-480" y2="-480" x1="64" />
            <rect width="64" x="0" y="-44" height="24" />
            <line x2="0" y1="-32" y2="-32" x1="64" />
            <line x2="464" y1="-480" y2="-480" x1="400" />
            <line x2="464" y1="-416" y2="-416" x1="400" />
            <line x2="464" y1="-352" y2="-352" x1="400" />
            <line x2="464" y1="-288" y2="-288" x1="400" />
            <line x2="464" y1="-224" y2="-224" x1="400" />
            <line x2="464" y1="-160" y2="-160" x1="400" />
            <line x2="464" y1="-96" y2="-96" x1="400" />
            <line x2="464" y1="-32" y2="-32" x1="400" />
        </blockdef>
        <blockdef name="UART">
            <timestamp>2023-2-9T5:30:8</timestamp>
            <rect width="256" x="64" y="-128" height="128" />
            <line x2="0" y1="-96" y2="-96" x1="64" />
            <line x2="0" y1="-32" y2="-32" x1="64" />
            <line x2="384" y1="-96" y2="-96" x1="320" />
            <rect width="64" x="320" y="-44" height="24" />
            <line x2="384" y1="-32" y2="-32" x1="320" />
        </blockdef>
        <block symbolname="motor_driver" name="XLXI_1">
            <blockpin signalname="clk" name="clk" />
            <blockpin signalname="XLXN_2(23:0)" name="UART_to_MD(23:0)" />
            <blockpin signalname="motor_1" name="motor_1" />
            <blockpin signalname="motor_2" name="motor_2" />
            <blockpin signalname="motor_3" name="motor_3" />
            <blockpin signalname="motor_4" name="motor_4" />
            <blockpin signalname="motor_5" name="motor_5" />
            <blockpin signalname="step_motor" name="step_motor" />
            <blockpin signalname="stepin" name="stepin" />
            <blockpin signalname="dirpin" name="dirpin" />
        </block>
        <block symbolname="UART" name="XLXI_2">
            <blockpin signalname="clk" name="clk" />
            <blockpin signalname="rxd" name="rxd" />
            <blockpin signalname="txd" name="txd" />
            <blockpin signalname="XLXN_2(23:0)" name="UART_to_MD(23:0)" />
        </block>
    </netlist>
    <sheet sheetnum="1" width="3520" height="2720">
        <instance x="2080" y="1552" name="XLXI_1" orien="R0">
        </instance>
        <instance x="1456" y="1360" name="XLXI_2" orien="R0">
        </instance>
        <branch name="clk">
            <wire x2="1408" y1="1264" y2="1264" x1="1376" />
            <wire x2="1456" y1="1264" y2="1264" x1="1408" />
            <wire x2="1408" y1="1072" y2="1264" x1="1408" />
            <wire x2="2080" y1="1072" y2="1072" x1="1408" />
        </branch>
        <branch name="XLXN_2(23:0)">
            <wire x2="1952" y1="1328" y2="1328" x1="1840" />
            <wire x2="1952" y1="1328" y2="1520" x1="1952" />
            <wire x2="2080" y1="1520" y2="1520" x1="1952" />
        </branch>
        <iomarker fontsize="28" x="1376" y="1264" name="clk" orien="R180" />
        <branch name="rxd">
            <wire x2="1456" y1="1328" y2="1328" x1="1376" />
        </branch>
        <iomarker fontsize="28" x="1376" y="1328" name="rxd" orien="R180" />
        <branch name="txd">
            <wire x2="1872" y1="1264" y2="1264" x1="1840" />
        </branch>
        <iomarker fontsize="28" x="1872" y="1264" name="txd" orien="R0" />
        <branch name="motor_1">
            <wire x2="2576" y1="1072" y2="1072" x1="2544" />
        </branch>
        <iomarker fontsize="28" x="2576" y="1072" name="motor_1" orien="R0" />
        <branch name="motor_2">
            <wire x2="2576" y1="1136" y2="1136" x1="2544" />
        </branch>
        <iomarker fontsize="28" x="2576" y="1136" name="motor_2" orien="R0" />
        <branch name="motor_3">
            <wire x2="2576" y1="1200" y2="1200" x1="2544" />
        </branch>
        <iomarker fontsize="28" x="2576" y="1200" name="motor_3" orien="R0" />
        <branch name="motor_4">
            <wire x2="2576" y1="1264" y2="1264" x1="2544" />
        </branch>
        <iomarker fontsize="28" x="2576" y="1264" name="motor_4" orien="R0" />
        <branch name="motor_5">
            <wire x2="2576" y1="1328" y2="1328" x1="2544" />
        </branch>
        <iomarker fontsize="28" x="2576" y="1328" name="motor_5" orien="R0" />
        <branch name="step_motor">
            <wire x2="2576" y1="1392" y2="1392" x1="2544" />
        </branch>
        <iomarker fontsize="28" x="2576" y="1392" name="step_motor" orien="R0" />
        <branch name="stepin">
            <wire x2="2576" y1="1456" y2="1456" x1="2544" />
        </branch>
        <iomarker fontsize="28" x="2576" y="1456" name="stepin" orien="R0" />
        <branch name="dirpin">
            <wire x2="2576" y1="1520" y2="1520" x1="2544" />
        </branch>
        <iomarker fontsize="28" x="2576" y="1520" name="dirpin" orien="R0" />
    </sheet>
</drawing>