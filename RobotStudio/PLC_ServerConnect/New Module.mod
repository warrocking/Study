! =====================================================================
    ! PLC ?? ?? -> "di20_conveyor_beforePress" ?? ??
    ! -> ??? ???? ???? ?? -> ??? ???? ?? ??
    ! -> ???? ????? -> ??? ???? ???? ?? ????
    ! -> ?? ??? abb? ??? ??????
    ! -> di21_PressClear(??????) ????
    ! -> ?? ??? ???? ?? ?? ??
    ! -> ?? ? ?? ????? ????? ?? ??
    ! -> ??? ??
    ! -> PLC?? ?? ????(di22_conveyor_afterPress)(?? ? ?? ??)
    ! -> ??? ??? ??? ??? ????? ???? 
    ! -> ?? ???? ????
    ! -> ??? ?? ?????? ??? ?????? (?? ??? ?? ?? ??)
    ! =====================================================================



MODULE MainModule
    TASK PERS tooldata tool1:=[TRUE,[[3.25653,-2.2499,106.27],[1,0,0,0]],[0.2,[0,0,50],[1,0,0,0],0,0,0]];

    
    VAR robtarget p_home := [[341.23,-3.36,271.12],[3.79713E-06,0.457163,-0.889383,-8.18065E-06],[0,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    
    !p_cbP = p_conveyor_beforePress
    !p_cbP_up : p_conveyor_beforePress_LittleUp
    !p_cbP_down : p_conveyor_beforePress_LittleDown
    VAR robtarget p_cbP :=[[249.73,-599.58,182.31],[2.17221E-05,0.458123,-0.888889,0.000564805],[-1,0,-2,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    VAR robtarget p_cbP_up :=[[0,0,0],[1,0,0,0],[0,0,0,0],[9E9,9E9,9E9,9E9,9E9,9E9]];
    VAR robtarget p_cbP_down:=[[249.71,-599.54,153.48],[1.66702E-05,0.458122,-0.888889,0.000485405],[-1,0,-2,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    
    ! p_ctP : p_conveyor_to_Press
    VAR robtarget p_ctP :=[[360.29,-510.19,202.27],[1.42393E-05,0.458181,-0.888859,4.45747E-05],[-1,-1,-2,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    
    ! 
    VAR robtarget p_press :=[[423.09,-477.32,99.04],[1.5994E-05,0.458198,-0.88885,1.11716E-05],[-1,-1,-2,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    VAR robtarget p_press_LittleDown :=[[423.05,-477.28,64.14],[3.58104E-05,0.458201,-0.888849,-7.04984E-05],[-1,-1,-2,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    ! p_caP : p_conveyor_afterPress
    ! p_caP_down : p_conveyor_afterPress_LittleDown
    VAR robtarget p_caP :=[[606.50,-442.24,433.63],[0.000103673,0.458229,-0.888834,-0.000187241],[-1,-1,-2,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    VAR robtarget p_caP_down :=[[606.50,-442.24,327.45],[9.43419E-05,0.458213,-0.888842,-0.000173811],[-1,-1,-2,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    ! p_caP_SC : p_conveyor_afterPress_SensorClear
    ! p_caP_SC_down : p_conveyor_afterPress_SensorClear_LittleDonw
    VAR robtarget p_caP_SC :=[[609.42,4.54,177.17],[0.000288402,0.458226,-0.888835,-0.000295341],[0,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    VAR robtarget p_caP_SC_down :=[[609.39,4.54,137.08],[0.000340193,0.458234,-0.888832,-0.000317474],[0,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];


    VAR speeddata v_moveSpeed_fast := v200;
    VAR speeddata v_moveSpeed_slow := v50;
    var num count := 0;
    CONST robtarget p_ptc:=[[403.88,-479.76,241.96],[0.000116689,0.458213,-0.888842,-0.000234633],[-1,-1,-2,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    VAR robtarget p_caP10:=[[423.08,-477.31,373.30],[2.10763E-05,0.458207,-0.888846,-2.09688E-07],[-1,-1,-2,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    VAR robtarget p_caP20:=[[423.08,-477.31,373.30],[2.10763E-05,0.458207,-0.888846,-2.09688E-07],[-1,-1,-2,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    PROC Main()
        
        
        ! ?? ??? ??? ??
        movel p_home, v_moveSpeed_fast, fine, tool1;

        movel p_cbP, v_moveSpeed_fast, fine, tool1;
        movel p_cbP_up, v_moveSpeed_fast, fine, tool1;
        movel p_cbP_down, v_moveSpeed_fast, fine, tool1;

        movel p_ctP, v_moveSpeed_fast, fine, tool1;
        
        movel p_press, v_moveSpeed_fast, fine, tool1;
        movel p_press_LittleDown, v_moveSpeed_fast, fine, tool1;
        
        movel p_caP, v_moveSpeed_fast, fine, tool1;
        movel p_caP_down, v_moveSpeed_fast, fine, tool1;

        movel p_caP_SC, v_moveSpeed_fast, fine, tool1;
        movel p_caP_SC_down, v_moveSpeed_fast, fine, tool1;
        ! ?? ??? ??? ??
        
        
        
        !!! real main function
        AccSet 1,1;
        Check_Connection;    ! PC ?? ??? - ? ?? ??? ? ??? ??? ????
        MOVEL p_home, v_moveSpeed_fast, fine, tool1;
        while true Do
            IF di20_conveyor_beforePress = 1 THEN
                ! move ( home -> conveyor_beforePress)
                MoveL p_cbP, v_moveSpeed_fast, fine, tool1;
                MoveL p_cbP_down, v_moveSpeed_slow, fine, tool1;!MoveL Offs(p_cbP, 0, 0, 0), v_moveSpeed_slow, fine, tool1;
                Grip_on;
                MoveL p_cbP, v_moveSpeed_slow, fine, tool1;
                !move ( conveyor_beforePress -> Press)
                Movel p_ctP, v_moveSpeed_slow, fine, tool1;
                Movel p_press, v_moveSpeed_fast, fine, tool1;
                Movel p_press_LittleDown, v_moveSpeed_slow, fine, tool1;
                Grip_off;
                movel p_press, v_moveSpeed_slow, fine, tool1;
                ! move (press -> home)
                moveL p_home, v_moveSpeed_fast, fine, tool1;
            ENDIF
            
            IF di21_PressClear = 1 THEN
                ! move (home -> press)
                MoveL p_press, v_moveSpeed_fast, fine, tool1;
                MoveL p_press_LittleDown, v_moveSpeed_slow, fine, tool1;
                Grip_on;
                movel p_press, v_moveSpeed_slow, fine, tool1;

                ! move (press -> afterpress)
                movel p_caP, v_moveSpeed_fast,fine, tool1;
                moveL p_caP_down, v_moveSpeed_slow, fine, tool1;
                Grip_off;
                movel p_caP, v_moveSpeed_fast, fine, tool1;
                ! move (afterpress -> home)
                movel p_home, v_moveSpeed_fast, fine, tool1;

            ENDIF


            IF di22_conveyor_afterPress = 1 THEN
                MoveL p_caP_SC, v_moveSpeed_fast, fine, tool1;
                movel p_caP_SC_down, v_moveSpeed_slow, fine, tool1;
                Grip_on;
                MoveL p_caP_SC, v_moveSpeed_slow, fine, tool1;
                MoveL p_home, v_moveSpeed_fast, fine, tool1;
            ENDIF



        ENDWHILE
        








    ENDPROC

    ! PC?? ?? ??? ?? (ex_p224.mod? ?? ?? ?? ??)
    ! ??? ?? ? ?? ???? ???, Main()?? ? ??? ??? ? ?? ???
    ! ? ??? ??? ??? (?? ?? ?? ??)
    PROC Check_Connection()
        VAR socketdev check_server_socket;
        VAR socketdev check_client_socket;
        VAR string check_received_string;

        SocketCreate check_server_socket;                        ! ?? ?? ??
        SocketBind check_server_socket, "192.168.3.3", 5000;      ! ?? ???? IP/??? ?? ???
        SocketListen check_server_socket;                         ! ????? ?? ?? ??

        TPWrite "Check_Connection: waiting for PC...";
        SocketAccept check_server_socket, check_client_socket;    ! PC ?? ?? (??? ??? ??? ??)

        SocketReceive check_client_socket \Str:=check_received_string; ! PC? ?? ??? ??
        TPWrite "Check_Connection: received - " + check_received_string;
        SocketSend check_client_socket \Str:="Connection OK";     ! ?? ?? ??

        SocketClose check_client_socket;                          ! ??? ?? ??
        SocketClose check_server_socket;

        ERROR
            TPWrite "Check_Connection: socket error, ERRNO="\Num:=ERRNO; ! ?? ?? ?????? ??? ?? ??
    ENDPROC















    PROC Grip_on()
        PulseDO\PLength:=0.2, do00_grip_on;
        WaitDI di00_grip_on_sen,1;
        WaitTime 0.2;
    ENDPROC
    
    PROC Grip_off()
        PulseDO\PLength:=0.2, do01_grip_off;
        WaitDI di01_grip_off_sen,1;
        WaitTime 0.2;
    ENDPROC

ENDMODULE