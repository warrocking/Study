MODULE MainModule

    ! ?? ?? - ??
! di00_Axle_Cylinder_FDone          : ? ?? ??
! di01_Axle_Gripper_Off             : ? ?? off
! di02_Axle_Gripper_On              : ? ?? of
! di03_Tier_Supply_Done             : ??? ?? ??
! di04_Battery_Supply_Done          : ??? ?? ??
! di05_Assembly_Cylinder_Forward    : ?? ? ?? ??
! di06_Assembly_Cylinder_Back       : ?? ? ?? ??
! di07_Motor_Supply_Done            : ?? ????

! ?? ?? - ??
! do00_First_AD_On                  : ??? ??
! do01_Second_AD_ON                 : ??? ??
! do02_Process_Start                : ???? ??
! do03_Axle_Supply_Forward          : ? ?? ?? ??
! do04_Axle_Supply_Back             : ? ?? ?? ??
! do05_Assembly_Cylinder_Forward    : ?? ??? ??
! do06_Assembly_Cylinder_Back       : ?? ??? ??
! do07_Tier_Supply                  : ??? ?? ??
! do08_Axle_Gripper_On              : ? ?? ?? ??
! do09_Axle_Gripper_Off             : ? ?? ?? ??
! do10_Battery_Supply               : ??? ?? ??
! do11_Motor_Supply                 : ?? ?? ??
! 
    CONST num OFS_APPROACH := 25;

    CONST num OFS_TIRE_LINK := 20;

    PERS robtarget p_home := [[375.37,20.48,540.81],[2.15925E-05,-0.419202,0.907893,6.67298E-05],[0,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    PERS robtarget p_Center_Horizontal := [[495.40,-125.50,390.72],[9.46944E-06,-0.402863,-0.91526,3.30582E-06],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_Center_Vertical := [[495.41,-125.49,390.74],[7.02526E-06,-0.391828,0.920039,-4.79484E-06],[-1,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    PERS robtarget p_axle_pick := [[226.04,-197.79,168.89],[0.000161403,-0.37853,-0.925589,9.06342E-05],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    PERS robtarget p_axle_assembly := [[493.51,-124.35,264.43],[7.63616E-06,-0.390391,-0.920649,0.000124174],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    PERS robtarget p_tier := [[233.42,-577.36,176.15],[3.31494E-06,-0.424953,-0.905216,0.000109129],[-1,-1,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    PERS robtarget p_tier_link_1_swing := [[483.42,-128.61,396.52],[3.32078E-05,-0.391804,0.920049,-2.49801E-05],[-1,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_tier_link_3_swing := [[483.42,-128.61,396.52],[3.32078E-05,-0.391804,0.920049,-2.49801E-05],[-1,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_tier_link_4_swing := [[522.26,-55.29,296.20],[0.164304,0.341149,0.832786,-0.403844],[0,-1,1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    PERS robtarget p_tier_link_2_swing30 := [[483.42,-128.61,396.52],[3.32078E-05,-0.391804,0.920049,-2.49801E-05],[-1,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_tier_link_2_swing60 := [[483.42,-128.61,396.52],[3.32078E-05,-0.391804,0.920049,-2.49801E-05],[-1,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    PERS robtarget p_Lower_body_pick := [[398.44,-506.76,144.94],[0.000356066,-0.378527,-0.92559,-1.21045E-05],[-1,-1,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    PERS robtarget p_Lower_body_link := [[495.44,-117.46,273.87],[0.000615037,0.393088,-0.919501,-0.000433774],[-1,-1,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    PERS robtarget p_battery_pick := [[260.06,-434.02,162.34],[1.68825E-05,0.408876,-0.91259,-0.000223169],[-1,0,-2,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    PERS robtarget p_battery_link := [[467.19,-124.38,280.99],[0.000259606,0.403281,-0.915076,-9.67854E-05],[-1,-1,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    PERS robtarget p_motor_pick := [[273.96,-325.06,162.39],[4.74872E-05,0.392428,-0.919783,-7.87849E-05],[-1,-1,-2,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    PERS robtarget p_motor_link := [[520.29,-123.25,283.51],[0.000460739,0.389431,-0.921056,-0.000303543],[-1,-1,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    PERS robtarget p_assembly_pick := [[495.39,-125.48,279.87],[3.84032E-05,0.391841,-0.920033,-2.80412E-05],[-1,-1,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    PERS robtarget p_conveyor_Exit := [[337.16,288.69,197.75],[0.000382539,0.39267,-0.919679,-0.000106524],[0,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    VAR speeddata v_fast := v200;

    VAR speeddata v_slow := v50;

    CONST string ROBOT_IP := "192.168.3.3";
    CONST num ROBOT_PORT := 5000;

    PERS robtarget p_tier_1_Set:= [[429.70,-210.20,280.23],[2.23864E-05,0.367494,0.930026,7.99124E-06],[-1,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_tier_1_15 := [[429.70,-210.20,280.23],[0.147489,-0.368498,-0.887163,-0.235367],[-1,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_tier_1_30 := [[429.70,-210.20,280.23],[0.229467,-0.350747,-0.851801,-0.314257],[-1,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_tier_1_45 := [[429.70,-210.20,280.23],[0.229625,-0.353793,-0.812087,-0.403258],[-1,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_tier_1_60 := [[429.70,-210.20,280.23],[0.270611,-0.334972,-0.787527,-0.440867],[-1,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_tier_1_75 := [[429.70,-210.20,280.23],[0.297597,-0.321358,-0.726748,-0.529152],[-1,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_tier_1_90 := [[431.18,-201.84,262.72],[0.312663,-0.312588,-0.63418,-0.634308],[-1,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_tier_1_link := [[431.17,-168.30,262.73],[0.312677,-0.312583,-0.634171,-0.634313],[-1,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    PERS robtarget p_tier_2_Set:= [[531.32,-200.29,280.97],[4.43347E-06,-0.412095,-0.911141,2.68129E-06],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_tier_2_15 := [[529.63,-192.53,291.42],[0.0656852,-0.414923,-0.902171,-0.0980439],[-1,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_tier_2_30 := [[529.62,-192.53,291.41],[0.125579,-0.411086,-0.878018,-0.210529],[-1,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_tier_2_45 := [[529.64,-200.05,293.26],[0.181652,-0.398016,-0.840699,-0.319077],[-1,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_tier_2_60 := [[529.63,-208.62,284.61],[0.210605,-0.33483,-0.819965,-0.413754],[-1,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_tier_2_75 := [[529.63,-208.62,284.61],[0.265602,-0.31464,-0.759136,-0.504153],[-1,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_tier_2_90 := [[530.85,-206.38,262.88],[0.312865,-0.312802,-0.634122,-0.634161],[-1,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_tier_2_link := [[530.84,-166.19,262.89],[0.312889,-0.312798,-0.634113,-0.634159],[-1,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    
    PERS robtarget p_tier_3_Set := [[430.43,-56.70,299.17],[1.08864E-05,-0.402847,-0.915267,2.79987E-06],[-1,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_tier_3_15 := [[430.42,-56.70,299.16],[0.0277264,0.406798,0.902166,-0.140869],[0,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_tier_3_30 := [[430.43,-56.70,299.17],[0.107705,0.392712,0.874585,-0.263206],[0,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_tier_3_45 := [[430.42,-47.28,290.46],[0.170308,0.362939,0.812887,-0.422475],[0,-1,1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_tier_3_60 := [[430.42,-47.28,290.46],[0.209173,0.33445,0.739561,-0.54538],[0,-1,1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_tier_3_75 := [[430.41,-41.77,267.96],[0.223542,0.321517,0.708076,-0.587609],[0,-1,1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_tier_3_90 := [[428.95,-45.41,264.81],[0.274165,0.274195,0.651786,-0.651786],[0,-1,1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_tier_3_link := [[428.95,-82.22,264.83],[0.274133,0.274167,0.651764,-0.651834],[0,-1,1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    
    PERS robtarget p_tier_4_Set := [[532.75,-43.49,282.44],[5.99017E-05,-0.401017,-0.91607,2.16294E-05],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_tier_4_15 := [[531.16,-54.80,272.25],[0.0130184,0.398725,0.913686,-0.0776301],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_tier_4_30 := [[531.17,-54.80,272.25],[0.0836523,0.381098,0.8883,-0.242259],[0,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_tier_4_45 := [[531.16,-54.80,272.25],[0.131041,0.365204,0.863283,-0.322796],[0,-1,1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_tier_4_60 := [[531.16,-54.80,272.25],[0.179859,0.345186,0.838967,-0.380304],[0,-1,1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_tier_4_75 := [[531.17,-54.80,272.25],[0.188413,0.344304,0.778335,-0.49005],[0,-1,1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_tier_4_90 := [[529.13,-50.32,264.21],[0.267067,0.267054,0.654723,-0.654748],[0,-1,1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_tier_4_link := [[529.13,-83.48,264.25],[0.267052,0.267059,0.654701,-0.654774],[0,-1,1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    VAR socketdev srv_server_socket;
    VAR socketdev srv_client_socket;
    VAR string srv_received_string;
    VAR bool srv_keep_listening := TRUE;
    TASK PERS tooldata tool3:=[TRUE,[[0,0,160],[1,0,0,0]],[0.1,[0,0,80],[1,0,0,0],0,0,0]];
    

    PROC Main()
        
        Init;
        MoveL p_Center_Horizontal, v1000, z50, tool3;

        Run_Socket_Server;
    ENDPROC

    PROC Init()

        AccSet 1, 1;
        MoveL p_home, v_fast, fine, tool3;

        Absorption_Off 3; !SetDo do00, do01 0
        
        !PulseDO\PLength := 0.2,  do03_Axle_Supply_Forward;
        PulseDO\PLength := 0.2,  do04_Axle_Supply_Back;
        !PulseDO\PLength := 0.2,  do05_Assembly_Cylinder_Forward;
        PulseDO\PLength := 0.2,  do06_Assembly_Cylinder_Back;
        !PulseDO\PLength := 0.2,  do07_Tier_Supply;
        !PulseDO\PLength := 0.2,  do08_Axle_Gripper_On;
        PulseDO\PLength := 0.2,  do09_Axle_Gripper_Off;
        !PulseDO\PLength := 0.2,  do10_Battery_Supply;
        !PulseDO\PLength := 0.2,  do11_Motor_Supply;
        
    ENDPROC

    PROC Run_Socket_Server()

        Start_Server ROBOT_IP, ROBOT_PORT;

        WHILE srv_keep_listening DO
            TPWrite "Waiting for connector...";
            SocketAccept srv_server_socket, srv_client_socket;
            TPWrite "Connector connected. Waiting for commands.";

            WHILE TRUE DO
                SocketReceive srv_client_socket \Str:=srv_received_string;
                TPWrite "Command received: " + srv_received_string;
                Handle_Command srv_received_string;
            ENDWHILE
        ENDWHILE

        ERROR
            IF ERRNO = ERR_SOCK_TIMEOUT THEN
                RETRY;
            ELSEIF ERRNO = ERR_SOCK_CLOSED THEN
                Start_Server ROBOT_IP, ROBOT_PORT;
                SocketAccept srv_server_socket, srv_client_socket;
                RETRY;
            ELSE
                TPWrite "Socket error, ERRNO="\Num:=ERRNO;
                Stop;
            ENDIF
    ENDPROC

    PROC Start_Server(string ip, num port)

        Close_All_Sockets;
        SocketCreate srv_server_socket;
        SocketBind srv_server_socket, ip, port;
        SocketListen srv_server_socket;
    ENDPROC

    PROC Close_All_Sockets()

        SocketClose srv_server_socket;
        SocketClose srv_client_socket;
        ERROR
            TRYNEXT;
    ENDPROC

    PROC Handle_Command(string cmd)
        !IF (StrLen(cmd) >= 5) AND (StrPart(cmd, 1, 5) = "Start") THEN
        !        !MoveL p_Center, v_moveSpeed, fine, tool3;
        !        TPWrite "Move done";
        !        Run_Assembly_Cycle;
        !ELSEIF (StrLen(cmd) >= 3) AND (StrPart(cmd, 1, 3) = "End") THEN
            ! ??
        !ELSEIF (StrLen(cmd) >= 9) AND (StrPart(cmd, 1, 9) = "Emergency") THEN
            ! ??
        !ENDIF


        IF cmd = "Start" OR cmd = "start" THEN
            TPWrite "Move Start";
            Run_Assembly_Cycle;
        ELSEIF cmd = "End" OR cmd = "END" THEN
            !??
        ELSEIF cmd = "Emergency" THEN
            !??
        ENDIF
    ENDPROC

    PROC Run_Assembly_Cycle()

        Axle;
        MoveJ p_Center_Horizontal, v_fast, z30, tool3;

        Lower_Body;
        MoveJ p_Center_Vertical, v_fast, z30, tool3;

        !Vaulting;
        !MoveJ p_Center_Vertical, v_fast, z30, tool3;

        Battery;
        MoveJ p_Center_Vertical, v_fast, z30, tool3;

        Motor;
        MoveJ p_Center_Horizontal, v_fast, z30, tool3;

        Tier_Linked;
        MoveJ p_Center_Vertical, v_fast, z30, tool3;

        Sender;
        MoveJ p_Center_Horizontal, v_fast, z30, tool3;
    ENDPROC

    PROC Axle()

        PulseDO\PLength := 0.2,  do03_Axle_Supply_Forward;
        MoveJ Offs(p_axle_pick, 0, 0, OFS_APPROACH), v_fast, z30, tool3;
        WaitDI di00_Axle_Cylinder_FDone, 1;

        MoveL p_axle_pick, v_slow, fine, tool3;
        Absorption_On 3;
        PulseDO\PLength := 0.2,  do04_Axle_Supply_Back;
        
        MoveL Offs(p_axle_pick,0,0,60), v_slow, fine, tool3;
        
        PulseDO\PLength := 0.2, do09_Axle_Gripper_Off;
        
        MoveL p_Center_Horizontal, v_fast, z30, tool3;
        MoveL Offs(p_axle_assembly, 0, 0, OFS_APPROACH), v_fast, z30, tool3;
        WaitDI di01_Axle_Gripper_Off, 1;
        PulseDO\PLength := 0.2, do13_Axle_Gripper_Off_End;

        MoveL p_axle_assembly, v_slow, fine, tool3;
        PulseDO\PLength := 0.2, do08_Axle_Gripper_On;
        WaitDI di02_Axle_Gripper_On, 1;
        PulseDO\PLength := 0.2, do12_Axle_Gripper_On_End;
!
        Absorption_Off 3;
        MoveL Offs(p_axle_assembly, 0, 0, OFS_APPROACH+20), v_slow, fine, tool3;
    ENDPROC

    PROC Lower_Body()

        MoveJ Offs(p_Lower_body_pick,0,0,40), v_fast, z30, tool3;
        MoveL p_Lower_body_pick, v_slow, fine, tool3;
        Absorption_On 3;
        MoveL Offs(p_Lower_body_pick, 0, 0, OFS_APPROACH), v_slow, fine, tool3;

        MoveL p_Center_Vertical, v_fast, z30, tool3;
        MoveL Offs(p_Lower_body_link, 0, 0, OFS_APPROACH), v_fast, z30, tool3;
        MoveL p_Lower_body_link, v_slow, fine, tool3;
        Absorption_Off 3;
        MoveL Offs(p_Lower_body_link, 0, 0, OFS_APPROACH+20), v_slow, fine, tool3;
    ENDPROC

    PROC Vaulting()
    ENDPROC

    PROC Battery()

        PulseDO \PLength := 0.2, do10_Battery_Supply;
        MoveL Offs(p_battery_pick, 0, 0, OFS_APPROACH), v_fast, z30, tool3;
        WaitDI di04_Battery_Supply_Done, 1;

        MoveL p_battery_pick, v_slow, fine, tool3;
        Absorption_On 3;
        MoveL Offs(p_battery_pick, 0, 0, OFS_APPROACH), v_slow, fine, tool3;

        MoveL p_Center_Vertical, v_fast, z30, tool3;
        MoveL Offs(p_battery_link,0,0,40), v_fast, z30, tool3;
        MoveL p_battery_link, v_slow, fine, tool3;
        Absorption_Off 3;
        MoveL Offs(p_battery_link, 0, 0, OFS_APPROACH), v_slow, fine, tool3;
    ENDPROC

    PROC Motor()

        PulseDO \PLength := 0.2, do11_Motor_Supply;
        MoveL Offs(p_motor_pick, 0, 0, OFS_APPROACH), v_fast, z30, tool3;
        WaitDI di07_Motor_Supply_Done, 1;

        MoveL p_motor_pick, v_slow, fine, tool3;
        Absorption_On 3;
        MoveL Offs(p_motor_pick, 0, 0, OFS_APPROACH), v_slow, fine, tool3;

        MoveL p_Center_Vertical, v_fast, z30, tool3;
        MoveL Offs(p_motor_link,0,0,40), v_fast, z30, tool3;

        MoveL p_motor_link, v_slow, fine, tool3;
        Absorption_Off 3;
        MoveL Offs(p_motor_link,0,0,40), v_slow, fine, tool3;
    ENDPROC

    PROC Tier_Linked()
        VAR num n_tireIndex := 0;
        PulseDO \PLength := 0.2, do07_Tier_Supply;

        FOR n_tireIndex FROM 1 TO 4 DO
            MoveJ Offs(p_tier, 0, 0, OFS_APPROACH), v_fast, z30, tool3;
            WaitDI di03_Tier_Supply_Done, 1;
            MoveL p_tier, v_slow, fine, tool3;

            Absorption_On 1;
            MoveL Offs(p_tier, 0, 0, OFS_APPROACH), v_slow, fine, tool3;
            MoveJ p_Center_Horizontal, v_fast, z30, tool3;

            TEST n_tireIndex
            CASE 1:
                MoveL p_tier_1_Set, v_slow, fine, tool3;
                MoveL p_tier_1_15, v_slow, fine, tool3;
                MoveL p_tier_1_30, v_slow, fine, tool3;
                MoveL p_tier_1_45, v_slow, fine, tool3;
                MoveL p_tier_1_60, v_slow, fine, tool3;
                MoveL p_tier_1_75, v_slow, fine, tool3;
                MoveL p_tier_1_90, v_slow, fine, tool3;
                MoveL p_tier_1_link, v_slow, fine, tool3;
                Absorption_Off 1;
                MoveL p_tier_1_90, v_slow, fine, tool3;
                MoveL p_tier_1_75, v_slow, fine, tool3;
                MoveL p_tier_1_60, v_slow, fine, tool3;
                MoveL p_tier_1_45, v_slow, fine, tool3;
                MoveL p_tier_1_30, v_slow, fine, tool3;
                MoveL p_tier_1_15, v_slow, fine, tool3;
                MoveL p_tier_1_Set, v_slow, fine, tool3;
            CASE 2:
                MoveL p_tier_2_Set, v_slow, fine, tool3;
                MoveL p_tier_2_15, v_slow, fine, tool3;
                MoveL p_tier_2_30, v_slow, fine, tool3;
                MoveL p_tier_2_45, v_slow, fine, tool3;
                MoveL p_tier_2_60, v_slow, fine, tool3;
                MoveL p_tier_2_75, v_slow, fine, tool3;
                MoveL p_tier_2_90, v_slow, fine, tool3;
                MoveL p_tier_2_link, v_slow, fine, tool3;
                Absorption_Off 1;
                MoveL p_tier_2_90, v_slow, fine, tool3;
                MoveL p_tier_2_75, v_slow, fine, tool3;
                MoveL p_tier_2_60, v_slow, fine, tool3;
                MoveL p_tier_2_45, v_slow, fine, tool3;
                MoveL p_tier_2_30, v_slow, fine, tool3;
                MoveL p_tier_2_15, v_slow, fine, tool3;
                MoveL p_tier_2_Set, v_slow, fine, tool3;
            CASE 3:
                MoveL p_tier_3_Set, v_slow, fine, tool3;
                MoveL p_tier_3_15, v_slow, fine, tool3;
                MoveL p_tier_3_30, v_slow, fine, tool3;
                MoveL p_tier_3_45, v_slow, fine, tool3;
                MoveL p_tier_3_60, v_slow, fine, tool3;
                MoveL p_tier_3_75, v_slow, fine, tool3;
                MoveL p_tier_3_90, v_slow, fine, tool3;
                MoveL p_tier_3_link, v_slow, fine, tool3;
                Absorption_Off 1;
                MoveL p_tier_3_90, v_slow, fine, tool3;
                MoveL p_tier_3_75, v_slow, fine, tool3;
                MoveL p_tier_3_60, v_slow, fine, tool3;
                MoveL p_tier_3_45, v_slow, fine, tool3;
                MoveL p_tier_3_30, v_slow, fine, tool3;
                MoveL p_tier_3_15, v_slow, fine, tool3;
                MoveL p_tier_3_Set, v_slow, fine, tool3;
            CASE 4:
                MoveL p_tier_4_Set, v_slow, fine, tool3;
                MoveL p_tier_4_15, v_slow, fine, tool3;
                MoveL p_tier_4_30, v_slow, fine, tool3;
                MoveL p_tier_4_45, v_slow, fine, tool3;
                MoveL p_tier_4_60, v_slow, fine, tool3;
                MoveL p_tier_4_75, v_slow, fine, tool3;
                MoveL p_tier_4_90, v_slow, fine, tool3;
                MoveL p_tier_4_link, v_slow, fine, tool3;
                Absorption_Off 1;
                MoveL p_tier_4_90, v_slow, fine, tool3;
                MoveL p_tier_4_75, v_slow, fine, tool3;
                MoveL p_tier_4_60, v_slow, fine, tool3;
                MoveL p_tier_4_45, v_slow, fine, tool3;
                MoveL p_tier_4_30, v_slow, fine, tool3;
                MoveL p_tier_4_15, v_slow, fine, tool3;
                MoveL p_tier_4_Set, v_slow, fine, tool3;
                
                !???
                
            ENDTEST
            MoveJ p_Center_Horizontal, v_fast, z30, tool3;

        ENDFOR
    ENDPROC

    PROC Sender()

        MoveL Offs(p_assembly_pick, 0, 0, OFS_APPROACH), v_fast, z30, tool3;
        MoveL p_assembly_pick, v_slow, fine, tool3;
        Absorption_On 3;

        PulseDO\PLength := 0.2, do09_Axle_Gripper_Off;
        WaitDI di01_Axle_Gripper_Off, 1;
        PulseDO\PLength := 0.2, do13_Axle_Gripper_Off_End;

        MoveL Offs(p_assembly_pick, 0, 0, OFS_APPROACH + 50), v_slow, fine, tool3;

        MoveJ Offs(p_conveyor_Exit, 0, 0, OFS_APPROACH), v_fast, z30, tool3;
        MoveL p_conveyor_Exit, v_slow, fine, tool3;
        Absorption_Off 3;
        MoveL Offs(p_conveyor_Exit, 0, 0, OFS_APPROACH), v_slow, fine, tool3;

    ENDPROC

    PROC Absorption_On(num SetNum)
        IF SetNum = 1 THEN
            SetDo do00_First_AD_On, 1;
            WaitTime 0.3;
        ELSEIF SetNum = 2 THEN
            SetDo do01_Second_AD_ON, 1;
            WaitTime 0.3;
        ELSEIF SetNum = 3 THEN
            SetDo do00_First_AD_On, 1;
            SetDo do01_Second_AD_ON, 1;
            WaitTime 0.3;
        ENDIF
    ENDPROC

    PROC Absorption_Off(num SetNum)
        IF SetNum = 1 THEN
            SetDo do00_First_AD_On, 0;
            WaitTime 0.3;
        ELSEIF SetNum = 2 THEN
            SetDo do01_Second_AD_ON, 0;
            WaitTime 0.3;
        ELSEIF SetNum = 3 THEN
            SetDo do00_First_AD_On, 0;
            SetDo do01_Second_AD_ON, 0;
            WaitTime 0.3;
        ENDIF
    ENDPROC

ENDMODULE
