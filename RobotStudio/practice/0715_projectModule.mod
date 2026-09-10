MODULE MainModule
    TASK PERS tooldata tool1:=[TRUE,[[3.25653,-2.2499,106.27],[1,0,0,0]],[0.2,[0,0,50],[1,0,0,0],0,0,0]];
    VAR socketdev server_socket;        ! ??(??) ? ?? ??
    VAR socketdev client_socket;        ! ??? ????? ?? ??
    VAR string received_string;         ! ???????? ?? ??? ??
    VAR bool keep_listening := TRUE;    ! ?? ?? ?? (?? WHILE ?? ??)
    VAR bool ck_bit := TRUE;            ! ?? ??????? ?? ?? ?? (?? WHILE ?? ??)
    
    VAR robtarget p_home := [[342.30,-38.16,327.52],[1.20614E-05,0.456804,-0.889567,-5.42704E-06],[-1,-1,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    
    VAR robtarget p_conveyor1 :=[[245.59,-581.05,207.18],[1.14514E-05,0.45812,-0.88889,0.000379034],[-1,0,-2,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    VAR robtarget p_conveyor1_down:=[[244.10,-580.92,166.51],[1.70431E-06,-0.458097,0.888902,-0.000177303],[-1,0,-2,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    
    VAR robtarget p_press :=[[411.86,-47.57,98.45],[0.000129012,0.456798,-0.88957,-8.33663E-05],[-1,-1,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    VAR robtarget p_press_down :=[[411.80,-48.68,58.58],[0.00020165,0.456723,-0.889609,-0.000132007],[-1,-1,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];


    VAR robtarget p_conveyor2_Start :=[[607.20,-442.00,409.61],[0.000144954,0.458218,-0.88884,-0.000278745],[-1,-1,-2,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    VAR robtarget p_conveyor2_Start_down :=[[607.21,-442.00,344.33],[0.000128478,0.458225,-0.888836,-0.000242942],[-1,-1,-2,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    VAR robtarget p_conveyor2_End :=[[609.42,4.54,177.17],[0.000288402,0.458226,-0.888835,-0.000295341],[0,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    VAR robtarget p_conveyor2_End_down :=[[609.39,4.54,137.08],[0.000340193,0.458234,-0.888832,-0.000317474],[0,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];


    VAR speeddata v_moveSpeed_fast := v200;
    VAR speeddata v_moveSpeed_slow := v50;
    
    VAR robtarget p_air := [[498.32,128.85,314.22],[0.00991695,-0.473527,0.880721,-0.00191809],[0,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    VAR robtarget p_air_down := [[498.28,128.83,279.88],[0.00985577,-0.473526,0.880723,-0.00189769],[0,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    VAR robtarget p_whiteTrash := [[647.37,332.27,97.24],[0.000492514,0.458242,-0.888828,-0.000361908],[0,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    
    VAR robtarget p_conveyor3_Start := [[487.22,351.95,130.29],[0.000537726,0.458263,-0.888816,-0.000356932],[0,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    VAR robtarget p_conveyor3_Start_down := [[487.18,351.93,103.27],[0.00059735,0.458263,-0.888817,-0.000346637],[0,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    

    VAR robtarget p_toolBox := [[-238.57,585.75,302.27],[0.0100652,-0.473592,0.880685,-0.00167316],[1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    VAR robtarget p_toolBox_Midpoint:= [[-233.11,341.85,255.01],[0.0100186,-0.473717,0.880618,-0.00189851],[1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    
    
    VAR robtarget p_tool1 := [[-218.90,591.26,289.15],[0.00989142,-0.473443,0.880767,-0.00197897],[1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    VAR robtarget p_tool1_down := [[-218.90,591.28,260.27],[0.0098852,-0.473457,0.88076,-0.00196406],[1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    
    VAR robtarget p_tool2 := [[-269.41,591.01,277.28],[0.0100133,-0.473679,0.880639,-0.0018834],[1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    VAR robtarget p_tool2_down := [[-269.40,590.99,259.45],[0.0100129,-0.473701,0.880627,-0.00193727],[1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    
    VAR robtarget p_tool1_operation := [[272.41,364.92,252.95],[0.000366383,0.979904,-0.199466,-0.000668161],[0,0,-2,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    VAR robtarget p_tool1_operation_down := [[272.41,364.92,149.89],[0.000381649,0.979907,-0.199453,-0.000669273],[0,0,-2,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    
    VAR robtarget p_tool2_operation := [[17.14,354.58,212.38],[0.000494989,0.979904,-0.19947,-0.000650089],[0,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    VAR robtarget p_tool2_operation_down := [[21.75,349.04,165.53],[0.000527621,0.979902,-0.199476,-0.000641933],[0,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    
    VAR robtarget p_conveyor3_End := [[-270.25,341.93,125.38],[0.0100726,-0.473587,0.880688,-0.00165141],[1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    VAR robtarget p_conveyor3_End_down := [[-270.25,341.93,125.38],[0.0100726,-0.473587,0.880688,-0.00165141],[1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
        
    VAR robtarget p_repository := [[-460.85,330.92,126.28],[0.000224263,-0.960018,0.279938,-0.000668673],[1,-1,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    VAR robtarget p_repository_down := [[-456.44,326.33,93.77],[0.010096,-0.473503,0.880733,-0.00173656],[1,-1,1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    VAR robtarget p_repository_up := [[-460.83,330.91,315.63],[0.000216562,-0.960012,0.279958,-0.000679889],[1,-1,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
        
    VAR bool canStart := false;
    VAR num tiltAngle := 30;
    VAR robtarget p_tool11:=[[269.30,359.41,243.95],[0.0100748,-0.473702,0.880625,-0.00193869],[0,-1,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];    ! ? ? ???? - ? ?? ??? ??? ??
    PROC Main()
        
        AccSet 1,1;                                     ! ??? 100%? ??
        SocketCreate server_socket;                      ! ?? ?? ??
        SocketBind server_socket, "192.168.3.3", 5000;    ! ?? ???? IP/??? ?? ???
        SocketListen server_socket;                       ! ????? ?? ?? ??
        AccSet 1,1;
        !Check_Connection;    ! PC ?? ??? - ? ?? ??? ? ??? ??? ????
        MOVEL p_home, v_moveSpeed_fast, fine, tool1;


        WHILE keep_listening DO                            ! ?? ??: ?????? ??? ?? ? ??? ??
            SocketAccept server_socket, client_socket;      ! ????? ?? ?? (??? ??? ??)
            ck_bit := TRUE;                                 ! ? ?????? ?? ?? ?? ?? ???

            WHILE ck_bit DO                                  ! ?? ?????? ?? ??
                SocketReceive client_socket \Str:=received_string; ! ???????? ??? ?? (??? ??? ??)
                TPWrite "Client wrote - " + received_string;         ! ?????? ?? ?? ?? (????)
                SocketSend client_socket \Str:="Message acknowledged"; ! ?? ?? ??? ?????? ??

                IF received_string = "start" THEN                  ! ??? "11"??
                    PulseDO\PLength:=0.2, do06_Material_Conveyor;
                    WaitTime 0.2;
                    while true Do
                        IF di20_conveyor_beforePress = 1 THEN
                            ! move ( home -> conveyor_beforePress)
                            MoveL p_conveyor1, v_moveSpeed_fast, fine, tool1;
                            MoveL p_conveyor1_down, v_moveSpeed_slow, fine, tool1;!MoveL Offs(p_conveyor1, 0, 0, 0), v_moveSpeed_slow, fine, tool1;
                            Grip_on;
                            MoveL p_conveyor1, v_moveSpeed_slow, fine, tool1;
                            !move ( conveyor_beforePress -> Press)
                            Movel p_home, v_moveSpeed_fast, fine, tool1;
                            Movel p_press, v_moveSpeed_fast, fine, tool1;
                            Movel p_press_down, v_moveSpeed_slow, fine, tool1;
                            Grip_off;
                            movel p_press, v_moveSpeed_slow, fine, tool1;

                            !!Signal Shoot
                            PulseDO\PLength:=0.2, do05_pressStart;
                            !WaitTime 0.2;
                            !moveL p_home, v_moveSpeed_fast, fine, tool1;
                
                           
                
                        ENDIF
            
                       IF di21_PressClear = 1 THEN
                            ! move (home -> press)
                            !moveL p_home, v_moveSpeed_fast, fine, tool1; ! Movement for exception handling
                            MoveL p_press, v_moveSpeed_fast, fine, tool1;
                            MoveL p_press_down, v_moveSpeed_slow, fine, tool1;
                            Grip_on;
                            movel p_press, v_moveSpeed_slow, fine, tool1;
                            
                            MoveL p_home, v_moveSpeed_fast, fine, tool1;

                            moveL p_air, v_moveSpeed_fast, fine, tool1;
                            moveL p_air_down, v_moveSpeed_slow, fine, tool1;
                            !!Signal Shoot
                            PulseDO\PLength:=0.2, do07_AirStart;
                            !WaitTime 0.2;




                            !!!!!!! time selcet
                            ! Reorient operation
                            MoveJ p_air_down, v_moveSpeed_slow, fine, tool1;   ! ?? ??? ?? ??
                            MoveL RelTool(p_air_down, 0, 0, 0 \Rx:=tiltAngle),  v_moveSpeed_slow, fine, tool1; ! ?? 1 (X? ?? +tiltAngle)
                            MoveL RelTool(p_air_down, 0, 0, 0 \Ry:=tiltAngle),  v_moveSpeed_slow, fine, tool1; ! ?? 2 (Y? ?? +tiltAngle)
                            MoveL RelTool(p_air_down, 0, 0, 0 \Rx:=-tiltAngle), v_moveSpeed_slow, fine, tool1; ! ?? 3 (X? ?? -tiltAngle)
                            MoveL RelTool(p_air_down, 0, 0, 0 \Ry:=-tiltAngle), v_moveSpeed_slow, fine, tool1; ! ?? 4 (Y? ?? -tiltAngle)
                            MoveJ p_air_down, v_moveSpeed_slow, fine, tool1;   ! ?? ???? ??
                            ! Reorient operation end
                            
                            
                            moveL p_air, v_moveSpeed_slow, fine, tool1;

                        ENDIF
                
                        IF di23_AirEnd = 1 THEN
                            moveL p_air, v_moveSpeed_slow, fine, tool1;
                            moveL p_home, v_moveSpeed_fast, fine, tool1;
                
                            movel p_conveyor2_Start, v_moveSpeed_fast,fine, tool1;
                            moveL p_conveyor2_Start_down, v_moveSpeed_slow, fine, tool1;
                            Grip_off;
                            movel p_conveyor2_Start, v_moveSpeed_slow, fine, tool1;
                            
                            ! Signal shoot
                            PulseDO\PLength:=0.2, do02_plcstart;
                            movel p_home, v_moveSpeed_fast, fine, tool1;
                            WaitTime 0.2;
                            
                        
                    
                        ENDIF
                
            
            

                        IF di22_conveyor_afterPress = 1 THEN
                            MoveL p_conveyor2_End, v_moveSpeed_fast, fine, tool1;
                            movel p_conveyor2_End_down, v_moveSpeed_slow, fine, tool1;
                            Grip_on;
                            MoveL p_conveyor2_End, v_moveSpeed_slow, fine, tool1;
                            MoveL p_home, v_moveSpeed_fast, fine, tool1;
                
                            ! here to trash move code
                            IF  di04_plastic_black = 1 THEN
                                MoveL p_conveyor3_Start, v_moveSpeed_fast, fine, tool1;
                                MoveL p_conveyor3_Start_down, v_moveSpeed_slow, fine, tool1;
                                Grip_off;
                
                                MoveL p_conveyor3_Start, v_moveSpeed_slow, fine, tool1;
                                MoveL p_home, v_moveSpeed_fast, fine, tool1;
                
                                PulseDO\PLength:=0.2, do08_ProcStart;
                                WaitTime 0.2;
                
                
                            ELSEIF di05_plastic_white = 1 THEN
                                MoveL p_whiteTrash, v_moveSpeed_fast, fine, tool1;
                                Grip_off;
                                MoveL p_home, v_moveSpeed_fast, fine, tool1;
                                PulseDO\PLength:=0.2, do06_Material_Conveyor;
                                WaitTime 0.2;
                            ENDIF
                
                
                
                        ENDIF
            
                        ! tool1 operation start
                        IF di25_Bead_Coating_start = 1 THEN
                            MoveJ p_toolBox_Midpoint, v_moveSpeed_fast, fine, tool1;
                            MoveJ p_toolBox, v_moveSpeed_fast, fine, tool1;
                            MoveL p_tool1, v_moveSpeed_fast, fine, tool1;
                            MoveL p_tool1_down, v_moveSpeed_slow, fine, tool1;
                            Grip_on;
                            MoveL p_tool1, v_moveSpeed_slow, fine, tool1;
                            MoveJ p_toolBox_Midpoint, v_moveSpeed_fast, fine, tool1;
                            MoveJ p_tool1_operation, v_moveSpeed_fast, fine, tool1;
                            
                            ! operation start
                            MoveJ p_tool1_operation_down, v_moveSpeed_slow, fine, tool1;
                            WaitTime 2;
                            MoveJ p_tool1_operation, v_moveSpeed_slow, fine, tool1;
                            
                            ! operation end

                            

                            ! Signal shoot
                            PulseDO\PLength:=0.2, do09_Bead_coating_End;
    
                            MoveJ p_toolBox_Midpoint, v_moveSpeed_fast, fine, tool1;
                            MoveJ p_toolBox, v_moveSpeed_fast, fine, tool1;
                            MoveL p_tool1, v_moveSpeed_fast, fine, tool1;
                            MoveL p_tool1_down, v_moveSpeed_slow, fine, tool1;
                            Grip_off;
                            MoveL p_tool1, v_moveSpeed_slow, fine, tool1;
                            MoveL p_toolBox, v_moveSpeed_fast, fine, tool1;
                
                        ENDIF
                        

                        ! tool 2 operation start
                        IF di29_Coating_Start = 1 THEN
                            MoveJ p_toolBox, v_moveSpeed_fast, fine, tool1;
                            MoveL p_tool2, v_moveSpeed_fast, fine, tool1;
                            MoveL p_tool2_down, v_moveSpeed_slow, fine, tool1;
                            Grip_on;
                            MoveL p_tool2, v_moveSpeed_slow, fine, tool1;
                            MoveJ p_toolBox_Midpoint, v_moveSpeed_fast, fine, tool1;
                            MoveL p_tool2_operation, v_moveSpeed_fast, fine, tool1;
                            
                            
                            
                            
                            ! tool2 operation motion start
                            MoveL p_tool2_operation_down, v_moveSpeed_slow, fine, tool1;
                            WaitTime 2;
                            MoveL p_tool2_operation, v_moveSpeed_slow, fine, tool1;
                            ! tool2 operation motion end

                            
                            
                            
                            ! Signal shoot
                            PulseDO\PLength:=0.2, do10_Proc_conveyor_restart;

                            
                            MoveL p_toolBox_Midpoint, v_moveSpeed_fast, fine, tool1;
                            MoveL p_toolBox, v_moveSpeed_fast, fine, tool1;
                            MoveL p_tool2, v_moveSpeed_fast, fine, tool1;
                            MoveL p_tool2_down, v_moveSpeed_slow, fine, tool1;
                            Grip_off;
                            MoveL p_tool2, v_moveSpeed_slow, fine, tool1;
                            MoveJ p_toolBox, v_moveSpeed_fast, fine, tool1;
                        ENDIF

                        IF di27_Storage_Move = 1 THEN
                            
                            !Temporary code
                            MoveJ p_toolBox_Midpoint, v_moveSpeed_fast, fine, tool1;
                            !Temporary code
                            
                            
                            
                            
                            MoveJ p_conveyor3_End, v_moveSpeed_fast, fine, tool1;
                            MoveL p_conveyor3_End_down, v_moveSpeed_slow, fine, tool1;
                            Grip_on;
                            MoveL p_conveyor3_End, v_moveSpeed_slow, fine, tool1;
                            MoveL p_repository, v_moveSpeed_fast, fine, tool1;
                            MoveL p_repository_down, v_moveSpeed_slow, fine, tool1;
                            Grip_off;
                            MoveL p_repository, v_moveSpeed_slow, fine, tool1;
                            MoveJ p_repository_up, v_moveSpeed_fast, fine, tool1;
                            MoveJ p_home, v_moveSpeed_fast, fine, tool1;
                            RETURN;
                        ENDIF

                    ENDWHILE


                ENDIF

                IF received_string = "22" THEN                  ! ??? "22"??
                    
                ENDIF

                IF received_string = "33" THEN                  ! ??? "33"??
                    
                ENDIF

                IF received_string = "end" THEN                  ! ??? "qq"(??)??
                    ck_bit := FALSE;                               ! ?? ?? ?? ?? -> ? ????? ??? ??? ?
                ENDIF

                received_string := "";                            ! ?? ??? ?? ??? ?? ???
            ENDWHILE

            SocketClose client_socket;                          ! ?? ????? ?? ?? (?? ??? ?? ??)
            RETURN;
        ENDWHILE

        SocketClose server_socket;                            ! ?? ?? ?? (?? ?? ?)

        ERROR                                                  ! ---- ?? ??? ----
        IF ERRNO=ERR_SOCK_TIMEOUT THEN                         ! ?? ???? ???
            RETRY;                                                ! ?? ?? ?? ???? ???
        ELSEIF ERRNO=ERR_SOCK_CLOSED THEN                      ! ??? ??? ?? ?? ???
            SocketClose server_socket;                            ! ?? ?? ?? ??
            SocketClose client_socket;                            ! ?? ????? ?? ??
            SocketCreate server_socket;                           ! ?? ?? ???
            SocketBind server_socket, "192.168.3.3", 5000;        ! ?? IP/??? ????
            SocketListen server_socket;                           ! ??? ?? ??
            SocketAccept server_socket, client_socket;            ! ? ????? ?? ??
            RETRY;                                                ! ?? ?? ?? ???? ???
        ELSE                                                    ! ? ? ? ? ?? ???
            TPWrite "ERRNO = "\Num:=ERRNO;                        ! ?? ??? ?????? ??
            Stop;                                                  ! ???? ??
        ENDIF

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