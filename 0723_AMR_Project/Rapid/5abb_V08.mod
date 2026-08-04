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
    ! ===== Tire 1 - evenly re-spaced via-points (Set/90/link kept exactly as taught in
    !       versionServer5.mod; only 15/30/45/60/75 recomputed by splitting the Set->90
    !       rotation into 6 equal steps: position LERP + quaternion SLERP) =====
    ! ===== 타이어 1 - 균등 재배치 경유점 (Set/90/link은 versionServer5.mod에 티칭된 값
    !       그대로; 15/30/45/60/75만 Set->90 회전을 6등분해서 다시 계산함: 위치는
    !       LERP, 방향은 쿼터니언 SLERP 사용) =====
    PERS robtarget p_tier_1_15 := [[429.95,-208.81,277.31],[-0.057749,0.374230,0.918085,0.117202],[-1,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_tier_1_30 := [[430.19,-207.41,274.39],[-0.114523,0.374507,0.890299,0.232373],[-1,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_tier_1_45 := [[430.44,-206.02,271.48],[-0.169320,0.368320,0.847145,0.343534],[-1,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_tier_1_60 := [[430.69,-204.63,268.56],[-0.221196,0.355776,0.789371,0.448765],[-1,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_tier_1_75 := [[430.93,-203.23,265.64],[-0.269253,0.337091,0.717971,0.546251],[-1,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_tier_1_90 := [[431.18,-201.84,262.72],[0.312663,-0.312588,-0.63418,-0.634308],[-1,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_tier_1_link := [[431.17,-168.30,262.73],[0.312677,-0.312583,-0.634171,-0.634313],[-1,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    PERS robtarget p_tier_2_Set:= [[531.32,-200.29,280.97],[4.43347E-06,-0.412095,-0.911141,2.68129E-06],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    ! ===== Tire 2 - evenly re-spaced via-points (same method as tire 1) =====
    ! ===== 타이어 2 - 균등 재배치 경유점 (타이어 1과 같은 방식) =====
    PERS robtarget p_tier_2_15 := [[531.24,-201.31,277.96],[0.057765,-0.412549,-0.901532,-0.117078],[-1,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_tier_2_30 := [[531.16,-202.32,274.94],[0.114537,-0.405933,-0.876473,-0.232151],[-1,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_tier_2_45 := [[531.09,-203.33,271.93],[0.169345,-0.392361,-0.836395,-0.343247],[-1,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_tier_2_60 := [[531.01,-204.35,268.91],[0.221251,-0.372065,-0.781984,-0.448461],[-1,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_tier_2_75 := [[530.93,-205.37,265.89],[0.269366,-0.345393,-0.714172,-0.545989],[-1,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_tier_2_90 := [[530.85,-206.38,262.88],[0.312865,-0.312802,-0.634122,-0.634161],[-1,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_tier_2_link := [[530.84,-166.19,262.89],[0.312889,-0.312798,-0.634113,-0.634159],[-1,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    PERS robtarget p_tier_3_Set := [[430.43,-56.70,299.17],[1.08864E-05,-0.402847,-0.915267,2.79987E-06],[-1,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    ! ===== Tire 3 - evenly re-spaced via-points (same method as tire 1) =====
    ! ===== 타이어 3 - 균등 재배치 경유점 (타이어 1과 같은 방식) =====
    PERS robtarget p_tier_3_15 := [[430.18,-54.82,293.44],[-0.050601,-0.397438,-0.908298,0.120321],[0,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_tier_3_30 := [[429.94,-52.94,287.72],[-0.100347,-0.385227,-0.885782,0.238580],[0,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_tier_3_45 := [[429.69,-51.05,281.99],[-0.148375,-0.366422,-0.848106,0.352755],[0,-1,1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_tier_3_60 := [[429.44,-49.17,276.26],[-0.193864,-0.341346,-0.795913,0.460893],[0,-1,1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_tier_3_75 := [[429.20,-47.29,270.54],[-0.236034,-0.310427,-0.730098,0.561142],[0,-1,1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_tier_3_90 := [[428.95,-45.41,264.81],[0.274165,0.274195,0.651786,-0.651786],[0,-1,1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_tier_3_link := [[428.95,-82.22,264.83],[0.274133,0.274167,0.651764,-0.651834],[0,-1,1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    PERS robtarget p_tier_4_Set := [[532.75,-43.49,282.44],[5.99017E-05,-0.401017,-0.91607,2.16294E-05],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    ! ===== Tire 4 - evenly re-spaced via-points (same method as tire 1) =====
    ! ===== 타이어 4 - 균등 재배치 경유점 (타이어 1과 같은 방식) =====
    PERS robtarget p_tier_4_15 := [[532.15,-44.63,279.40],[-0.049251,-0.394554,-0.909553,0.120891],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_tier_4_30 := [[531.54,-45.77,276.36],[-0.097719,-0.381334,-0.887459,0.239690],[0,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_tier_4_45 := [[530.94,-46.91,273.32],[-0.144513,-0.361583,-0.850168,0.354384],[0,-1,1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_tier_4_60 := [[530.34,-48.04,270.29],[-0.188833,-0.335641,-0.798317,0.463009],[0,-1,1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_tier_4_75 := [[529.73,-49.18,267.25],[-0.229919,-0.303950,-0.732795,0.563705],[0,-1,1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
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
                MoveL p_tier_1_Set, v_slow, z30, tool3;
                MoveL p_tier_1_15, v_slow, z30, tool3;
                MoveL p_tier_1_30, v_slow, z30, tool3;
                MoveL p_tier_1_45, v_slow, z30, tool3;
                MoveL p_tier_1_60, v_slow, z30, tool3;
                MoveL p_tier_1_75, v_slow, z30, tool3;
                MoveL p_tier_1_90, v_slow, z30, tool3;
                MoveL p_tier_1_link, v_slow, fine, tool3;
                Absorption_Off 1;
                MoveL p_tier_1_90, v_slow, fine, tool3;
                MoveL p_tier_1_75, v_slow, z30, tool3;
                MoveL p_tier_1_60, v_slow, z30, tool3;
                MoveL p_tier_1_45, v_slow, z30, tool3;
                MoveL p_tier_1_30, v_slow, z30, tool3;
                MoveL p_tier_1_15, v_slow, z30, tool3;
                MoveL p_tier_1_Set, v_slow, z30, tool3;
            CASE 2:
                MoveL p_tier_2_Set, v_slow, z30, tool3;
                MoveL p_tier_2_15, v_slow, z30, tool3;
                MoveL p_tier_2_30, v_slow, z30, tool3;
                MoveL p_tier_2_45, v_slow, z30, tool3;
                MoveL p_tier_2_60, v_slow, z30, tool3;
                MoveL p_tier_2_75, v_slow, z30, tool3;
                MoveL p_tier_2_90, v_slow, z30, tool3;
                MoveL p_tier_2_link, v_slow, fine, tool3;
                Absorption_Off 1;
                MoveL p_tier_2_90, v_slow, fine, tool3;
                MoveL p_tier_2_75, v_slow, z30, tool3;
                MoveL p_tier_2_60, v_slow, z30, tool3;
                MoveL p_tier_2_45, v_slow, z30, tool3;
                MoveL p_tier_2_30, v_slow, z30, tool3;
                MoveL p_tier_2_15, v_slow, z30, tool3;
                MoveL p_tier_2_Set, v_slow, z30, tool3;
            CASE 3:
                MoveL p_tier_3_Set, v_slow, z30, tool3;
                MoveL p_tier_3_15, v_slow, z30, tool3;
                MoveL p_tier_3_30, v_slow, z30, tool3;
                MoveL p_tier_3_45, v_slow, z30, tool3;
                MoveL p_tier_3_60, v_slow, z30, tool3;
                MoveL p_tier_3_75, v_slow, z30, tool3;
                MoveL p_tier_3_90, v_slow, z30, tool3;
                MoveL p_tier_3_link, v_slow, fine, tool3;
                Absorption_Off 1;
                MoveL p_tier_3_90, v_slow, fine, tool3;
                MoveL p_tier_3_75, v_slow, z30, tool3;
                MoveL p_tier_3_60, v_slow, z30, tool3;
                MoveL p_tier_3_45, v_slow, z30, tool3;
                MoveL p_tier_3_30, v_slow, z30, tool3;
                MoveL p_tier_3_15, v_slow, z30, tool3;
                MoveL p_tier_3_Set, v_slow, z30, tool3;
            CASE 4:
                MoveL p_tier_4_Set, v_slow, z30, tool3;
                MoveL p_tier_4_15, v_slow, z30, tool3;
                MoveL p_tier_4_30, v_slow, z30, tool3;
                MoveL p_tier_4_45, v_slow, z30, tool3;
                MoveL p_tier_4_60, v_slow, z30, tool3;
                MoveL p_tier_4_75, v_slow, z30, tool3;
                MoveL p_tier_4_90, v_slow, z30, tool3;
                MoveL p_tier_4_link, v_slow, fine, tool3;
                Absorption_Off 1;
                MoveL p_tier_4_90, v_slow, fine, tool3;
                MoveL p_tier_4_75, v_slow, z30, tool3;
                MoveL p_tier_4_60, v_slow, z30, tool3;
                MoveL p_tier_4_45, v_slow, z30, tool3;
                MoveL p_tier_4_30, v_slow, z30, tool3;
                MoveL p_tier_4_15, v_slow, z30, tool3;
                MoveL p_tier_4_Set, v_slow, z30, tool3;

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
