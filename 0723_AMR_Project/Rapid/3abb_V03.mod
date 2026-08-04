MODULE MainModule
    !Digital Input
    !di00_PLC_Grip_ON
    !di01_PLC_Grip_OFF
    !di02_PLC_Press_Done
    !di03_PLC_Body_Docking_On
    !di04_PLC_Body_Docking_Off
    
    !Digital Output
    !do00_Gripper_On
    !do01_Gripper_Off
    !do02_Press_Start
    !do03_Body_Start
    !do04_Body_Pick
    !do05_Body_Docking_Done



    TASK PERS tooldata tool1 := [
    TRUE,
    [[0, 0, 110], [1, 0, 0, 0]],
    [0.2, [0, 0, 50], [1, 0, 0, 0], 0, 0, 0]
    ];
    ! Travel speed for empty or long moves
    ! 빈 상태 이동이나 장거리 이동에 쓰는 속도
    VAR speeddata v_fast := v200;
    ! Careful (slow) speed for pick/place moves
    ! 픽업/배치 동작에 쓰는 신중한(느린) 속도
    VAR speeddata v_slow := v50;

    ! ===== NOT YET TAUGHT - every target below is a placeholder (pos 0,0,0, no rotation).
    !       Re-teach all of them before running; this only makes the file compile/load. =====
    ! ===== 아직 티칭 안 됨 - 아래 좌표 전부 placeholder(위치 0,0,0, 회전 없음)입니다.
    !       실행 전 전부 다시 티칭하세요; 이건 파일이 컴파일/로드되게만 해줍니다. =====

    ! ----- Shared home / return waypoints -----
    ! ----- 공용 홈/복귀 경유점 -----
    PERS robtarget p_home := [[0,0,0],[1,0,0,0],[0,0,0,0],[9E9,9E9,9E9,9E9,9E9,9E9]];
    PERS robtarget p_Assembly_Up := [[0,0,0],[1,0,0,0],[0,0,0,0],[9E9,9E9,9E9,9E9,9E9,9E9]];
    PERS robtarget p_Assembly_Down := [[0,0,0],[1,0,0,0],[0,0,0,0],[9E9,9E9,9E9,9E9,9E9,9E9]];

    ! ----- Upper body panel station (Upper_Body_Process) -----
    ! ----- 차체 상부 패널 스테이션 (Upper_Body_Process) -----
    PERS robtarget p_L_Body_R_PickUp := [[0,0,0],[1,0,0,0],[0,0,0,0],[9E9,9E9,9E9,9E9,9E9,9E9]];
    PERS robtarget p_L_Body_R_PickDown := [[0,0,0],[1,0,0,0],[0,0,0,0],[9E9,9E9,9E9,9E9,9E9,9E9]];
    PERS robtarget p_L_Body_L_PickUp := [[0,0,0],[1,0,0,0],[0,0,0,0],[9E9,9E9,9E9,9E9,9E9,9E9]];
    PERS robtarget p_L_Body_L_PickDown := [[0,0,0],[1,0,0,0],[0,0,0,0],[9E9,9E9,9E9,9E9,9E9,9E9]];
    PERS robtarget p_R_Body_R_PickUp := [[0,0,0],[1,0,0,0],[0,0,0,0],[9E9,9E9,9E9,9E9,9E9,9E9]];
    PERS robtarget p_R_Body_R_PickDown := [[0,0,0],[1,0,0,0],[0,0,0,0],[9E9,9E9,9E9,9E9,9E9,9E9]];
    PERS robtarget p_R_Body_L_PickUp := [[0,0,0],[1,0,0,0],[0,0,0,0],[9E9,9E9,9E9,9E9,9E9,9E9]];
    PERS robtarget p_R_Body_L_PickDown := [[0,0,0],[1,0,0,0],[0,0,0,0],[9E9,9E9,9E9,9E9,9E9,9E9]];
    PERS robtarget p_Body_Assembly := [[0,0,0],[1,0,0,0],[0,0,0,0],[9E9,9E9,9E9,9E9,9E9,9E9]];
    PERS robtarget p_Body_Assembly_R := [[0,0,0],[1,0,0,0],[0,0,0,0],[9E9,9E9,9E9,9E9,9E9,9E9]];
    PERS robtarget p_Body_Assembly_R_D := [[0,0,0],[1,0,0,0],[0,0,0,0],[9E9,9E9,9E9,9E9,9E9,9E9]];
    PERS robtarget p_Body_Assembly_L := [[0,0,0],[1,0,0,0],[0,0,0,0],[9E9,9E9,9E9,9E9,9E9,9E9]];
    PERS robtarget p_Body_Assembly_L_D := [[0,0,0],[1,0,0,0],[0,0,0,0],[9E9,9E9,9E9,9E9,9E9,9E9]];

    ! ----- Main chassis body pick (separate from the L/R panel picks above) -----
    ! ----- 차체 하부 본체 픽업 (위의 좌/우 패널 픽업과는 별개) -----
    PERS robtarget p_body_PickUp := [[0,0,0],[1,0,0,0],[0,0,0,0],[9E9,9E9,9E9,9E9,9E9,9E9]];
    PERS robtarget p_body_PickDown := [[0,0,0],[1,0,0,0],[0,0,0,0],[9E9,9E9,9E9,9E9,9E9,9E9]];

    ! ----- Welding tool rack + 10 weld points (Welding_Process) -----
    ! ----- 용접 툴 거치대 + 용접 지점 10개 (Welding_Process) -----
    PERS robtarget p_Tool_PickUp := [[0,0,0],[1,0,0,0],[0,0,0,0],[9E9,9E9,9E9,9E9,9E9,9E9]];
    PERS robtarget p_Tool_PickDown := [[0,0,0],[1,0,0,0],[0,0,0,0],[9E9,9E9,9E9,9E9,9E9,9E9]];
    PERS robtarget p_Point1 := [[0,0,0],[1,0,0,0],[0,0,0,0],[9E9,9E9,9E9,9E9,9E9,9E9]];
    PERS robtarget p_point2 := [[0,0,0],[1,0,0,0],[0,0,0,0],[9E9,9E9,9E9,9E9,9E9,9E9]];
    PERS robtarget p_point3 := [[0,0,0],[1,0,0,0],[0,0,0,0],[9E9,9E9,9E9,9E9,9E9,9E9]];
    PERS robtarget p_point4 := [[0,0,0],[1,0,0,0],[0,0,0,0],[9E9,9E9,9E9,9E9,9E9,9E9]];
    PERS robtarget p_point5 := [[0,0,0],[1,0,0,0],[0,0,0,0],[9E9,9E9,9E9,9E9,9E9,9E9]];
    PERS robtarget p_point6 := [[0,0,0],[1,0,0,0],[0,0,0,0],[9E9,9E9,9E9,9E9,9E9,9E9]];
    PERS robtarget p_point7 := [[0,0,0],[1,0,0,0],[0,0,0,0],[9E9,9E9,9E9,9E9,9E9,9E9]];
    PERS robtarget p_point8 := [[0,0,0],[1,0,0,0],[0,0,0,0],[9E9,9E9,9E9,9E9,9E9,9E9]];
    PERS robtarget p_point9 := [[0,0,0],[1,0,0,0],[0,0,0,0],[9E9,9E9,9E9,9E9,9E9,9E9]];
    PERS robtarget p_point10 := [[0,0,0],[1,0,0,0],[0,0,0,0],[9E9,9E9,9E9,9E9,9E9,9E9]];

    ! ----- Door station (Door_Docking_Process) -----
    ! ----- 도어 스테이션 (Door_Docking_Process) -----
    PERS robtarget p_L_Door_R_PickUp := [[0,0,0],[1,0,0,0],[0,0,0,0],[9E9,9E9,9E9,9E9,9E9,9E9]];
    PERS robtarget p_L_Door_R_PickDown := [[0,0,0],[1,0,0,0],[0,0,0,0],[9E9,9E9,9E9,9E9,9E9,9E9]];
    PERS robtarget p_L_Door_L_PickUp := [[0,0,0],[1,0,0,0],[0,0,0,0],[9E9,9E9,9E9,9E9,9E9,9E9]];
    PERS robtarget p_L_Door_L_PickDown := [[0,0,0],[1,0,0,0],[0,0,0,0],[9E9,9E9,9E9,9E9,9E9,9E9]];
    PERS robtarget p_R_Door_R_PickUp := [[0,0,0],[1,0,0,0],[0,0,0,0],[9E9,9E9,9E9,9E9,9E9,9E9]];
    PERS robtarget p_R_Door_R_PickDown := [[0,0,0],[1,0,0,0],[0,0,0,0],[9E9,9E9,9E9,9E9,9E9,9E9]];
    PERS robtarget p_R_Door_L_PickUp := [[0,0,0],[1,0,0,0],[0,0,0,0],[9E9,9E9,9E9,9E9,9E9,9E9]];
    PERS robtarget p_R_Door_L_PickDown := [[0,0,0],[1,0,0,0],[0,0,0,0],[9E9,9E9,9E9,9E9,9E9,9E9]];
    PERS robtarget p_Door_Assembly := [[0,0,0],[1,0,0,0],[0,0,0,0],[9E9,9E9,9E9,9E9,9E9,9E9]];
    PERS robtarget p_Door_Assembly_R := [[0,0,0],[1,0,0,0],[0,0,0,0],[9E9,9E9,9E9,9E9,9E9,9E9]];
    PERS robtarget p_Door_Assembly_R_D := [[0,0,0],[1,0,0,0],[0,0,0,0],[9E9,9E9,9E9,9E9,9E9,9E9]];
    PERS robtarget p_Door_Assembly_L := [[0,0,0],[1,0,0,0],[0,0,0,0],[9E9,9E9,9E9,9E9,9E9,9E9]];
    PERS robtarget p_Door_Assembly_L_D := [[0,0,0],[1,0,0,0],[0,0,0,0],[9E9,9E9,9E9,9E9,9E9,9E9]];

    ! ----- Exit delivery station (Car_Delivery) -----
    ! ----- 출하 인계 스테이션 (Car_Delivery) -----
    PERS robtarget p_Car_Delivery_Up := [[0,0,0],[1,0,0,0],[0,0,0,0],[9E9,9E9,9E9,9E9,9E9,9E9]];
    PERS robtarget p_Car_Delivery_Down := [[0,0,0],[1,0,0,0],[0,0,0,0],[9E9,9E9,9E9,9E9,9E9,9E9]];

    CONST string ROBOT_IP := "192.168."; ! 수정 필요
    CONST num ROBOT_PORT := 5000;
    VAR socketdev srv_server_socket;
    VAR socketdev srv_client_socket;
    VAR string srv_received_string;
    VAR bool srv_keep_listening := TRUE;
    VAR num ProcessNum := 0;
    PROC Main()
        MoveL p_home, v1000, z50, tool3;
        Init;
        Run_Socket_Server;
    ENDPROC

    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    ! 서버 코드 끝
    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    PROC Run_Socket_Server()
        ! Role: Waits for a connector to connect, then repeatedly waits for a command and
        !       dispatches it to Handle_Command. Rebuilds the connection if it drops.
        ! ??: ??? ??? ?????, ??? ?? ??? Handle_Command? ???.
        !       ??? ??? ?? ???.
        ! Process: Start_Server once -> WHILE(accept a connector -> WHILE(receive a
        !          command -> Handle_Command)) -> ERROR: retry on timeout, rebuild+retry
        !          on socket-closed, else log and stop.
        ! ??: Start_Server ? ? ?? -> WHILE(??? ?? ?? -> WHILE(?? ?? ->
        !       Handle_Command)) -> ERROR: ????? ???, ?? ??? ??? ?
        !       ???, ? ?? ?? ??? ??.
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
        ! Role: (Re)builds the server socket from scratch on the given ip/port.
        ! ??: ??? ip/port? ?? ??? ???? ?? ???.
        Close_All_Sockets;
        SocketCreate srv_server_socket;
        SocketBind srv_server_socket, ip, port;
        SocketListen srv_server_socket;
    ENDPROC
    PROC Close_All_Sockets()
        ! Role: Best-effort close - a socket that was never created raises an error here;
        !       TRYNEXT just skips to the next line instead of stopping the program.
        ! ??: ??? ?? ??? ?? - ?? ? ?? ??? ? ?? ??? ??? ??
        !       ??? ??? ???, TRYNEXT? ????? ??? ?? ?? ?? ????.
        SocketClose srv_server_socket;
        SocketClose srv_client_socket;
        ERROR
            TRYNEXT;
    ENDPROC
    PROC Handle_Command(string cmd)
        IF cmd = "Start" OR cmd = "start" THEN
            TPWrite "Move Start";
            Run_Upper_Body_Assembly;
        ELSEIF cmd = "End" OR cmd = "END" THEN
            !??
        ELSEIF cmd = "Emergency" THEN
            !??
        ENDIF
    ENDPROC
    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    ! 서버 코드 끝
    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!


    PROC Init()
        ! Role: Resets every output this module drives, before starting automatic operation.
        ! 역할: 자동운전을 시작하기 전에, 이 모듈이 다루는 모든 출력을 초기화한다.
        SetDo do00_Dripper, 0;
        ProcessNum := 0;

    ENDPROC

    PROC Run_Upper_Body_Assembly()
        
        
        Press_Process;
        
        Upper_Body_Process;

        Welding_Process;

        Door_Docking_Process;

        Car_Delivery;


        !공정 끝
        ProcessNum := ProcessNum+1;
    ENDPROC

    Proc Press_Process()
        PulseDO\PLength := 0.2, do02_Press_Start;
        WaitDI di02_PLC_Press_Done,1;
    ENDPROC

    Proc Upper_Body_Process()
        
        IF ProcessNum = 0 THEN !차제 재료 왼쪽 사용
            ! 오른쪽 차채 
            MoveJ p_L_Body_R_PickUp, v_fast, z30, tool1;
            MoveL p_L_Body_R_PickDown, v_slow, fine, tool1;
            Dripper_On;
            MoveL p_L_Body_R_PickDown, v_slow, fine, tool1;
            MoveL p_Body_Assembly, v_fast, z30, tool1;
            MoveL p_Body_Assembly_R, v_fast, z30, tool1;
            MoveL p_Body_Assembly_R_D, v_slow, fine, tool1;
            Dripper_Off;
            MoveL p_Body_Assembly_R, v_slow, fine, tool1;
           
            
            !왼쪽 차채
            MoveJ p_L_Body_L_PickUp, v_fast, z30, tool1;
            MoveL p_L_Body_L_PickDown, v_slow, fine, tool1;
            Dripper_On;
            MoveL p_L_Body_L_PickDown, v_slow, fine, tool1;
            MoveL p_Body_Assembly, v_fast, z30, tool1;
            MoveL p_Body_Assembly_L, v_fast, z30, tool1;
            MoveL p_Body_Assembly_L_D, v_slow, fine, tool1;
            Dripper_Off;
            MoveL p_Body_Assembly_L, v_slow, fine, tool1;
            


        ELSEIF ProcessNum = 1 THEN! 차제 재료 오른쪽 사용
            ! 오른쪽 차채 
            MoveJ p_R_Body_R_PickUp, v_fast, z30, tool1;
            MoveL p_R_Body_R_PickDown, v_slow, fine, tool1;
            Dripper_On;
            MoveL p_R_Body_R_PickDown, v_slow, fine, tool1;
            MoveL p_Body_Assembly, v_fast, z30, tool1;
            MoveL p_Body_Assembly_R, v_fast, z30, tool1;
            MoveL p_Body_Assembly_R_D, v_slow, fine, tool1;
            Dripper_Off;
            MoveL p_Body_Assembly_R, v_slow, fine, tool1;
            
            
            !왼쪽 차채
            MoveJ p_R_Body_L_PickUp, v_fast, z30, tool1;
            MoveL p_R_Body_L_PickDown, v_slow, fine, tool1;
            Dripper_On;
            MoveL p_R_Body_L_PickDown, v_slow, fine, tool1;
            MoveL p_Body_Assembly, v_fast, z30, tool1;
            MoveL p_Body_Assembly_L, v_fast, z30, tool1;
            MoveL p_Body_Assembly_L_D, v_slow, fine, tool1;
            Dripper_Off;
            MoveL p_Body_Assembly_L, v_slow, fine, tool1;
            
        ENDIF
        
        MoveL Offs(p_Body_Assembly, 0, 0, 30), v_fast, z30, tool1;
        PulseDO\PLength:=0.2, do03_Body_Start;
        WaitDI di03_PLC_Body_Docking_On, 1;
        MoveL p_body_PickDown, v_slow, fine, tool1;
        Dripper_On;
        PulseDO\PLength := 0.2, do04_Body_Pick;
        WaitDI di04_PLC_Body_Docking_Off, 1;
        MoveL p_body_PickUp, v_slow, fine, tool1;
        MoveL p_Assembly_Up, v_fast, z30, tool1;
        MoveL p_Assembly_Down, v_slow, fine, tool1;
        Dripper_Off;
        MoveL p_Assembly_Up, v_slow, fine, tool1;
        MoveJ p_home, v_fast, z30, tool1;

    ENDPROC

    Proc Welding_Process()
        MoveJ p_Tool_PickUp, v_fast, z30, tool1;
        MoveL p_Tool_PickDown, v_slow, fine, tool1;
        Dripper_On;
        MoveL p_Tool_PickUp, v_fast, fine, tool1;
        MoveL p_Assembly_Up, v_fast, z30, tool1;
        
        MoveL p_Point1 , v_slow, z10, tool1;
        !실제 용접 시작
        MoveL p_point2 , v_slow, z30, tool1;
        MoveL p_point3 , v_slow, z30, tool1;
        MoveL p_point4 , v_slow, z30, tool1;
        MoveL p_point5 , v_slow, z30, tool1;
        MoveL p_point6 , v_slow, z30, tool1;
        MoveL p_point7 , v_slow, z30, tool1;
        MoveL p_point8 , v_slow, z30, tool1;
        MoveL p_point9 , v_slow, z30, tool1;
        !실제 용접 끝
        MoveL p_point10, v_slow, z30, tool1;

        MoveL Offs(p_Tool_PickUp, -20, 0, 30), v_fast, z30, tool1;
        MoveL p_Tool_PickUp, v_fast, z30, tool1;
        MoveL p_Tool_PickDown, v_slow, fine, tool1;
        Dripper_Off;
        MoveL p_Tool_PickUp, v_fast, fine, tool1;
        MoveL p_Home, v500, z30, tool1;
    ENDPROC

    PROC Door_Docking_Process()
        IF ProcessNum = 0 THEN !차제 재료 왼쪽 사용
            ! 오른쪽 차채 
            MoveJ p_L_Door_R_PickUp, v_fast, z30, tool1;
            MoveL p_L_Door_R_PickDown, v_slow, fine, tool1;
            Dripper_On;
            MoveL p_L_Door_R_PickDown, v_slow, fine, tool1;
            MoveL p_Door_Assembly, v_fast, z30, tool1;
            MoveL p_Door_Assembly_R, v_fast, z30, tool1;
            MoveL p_Door_Assembly_R_D, v_slow, fine, tool1;
            Dripper_Off;
            MoveL p_Door_Assembly_R, v_slow, fine, tool1;
           
            
            !왼쪽 차채
            MoveJ p_L_Door_L_PickUp, v_fast, z30, tool1;
            MoveL p_L_Door_L_PickDown, v_slow, fine, tool1;
            Dripper_On;
            MoveL p_L_Door_L_PickDown, v_slow, fine, tool1;
            MoveL p_Door_Assembly, v_fast, z30, tool1;
            MoveL p_Door_Assembly_L, v_fast, z30, tool1;
            MoveL p_Door_Assembly_L_D, v_slow, fine, tool1;
            Dripper_Off;
            MoveL p_Door_Assembly_L, v_slow, fine, tool1;
            


        ELSEIF ProcessNum = 1 THEN! 차제 재료 오른쪽 사용
            ! 오른쪽 차채 
            MoveJ p_R_Door_R_PickUp, v_fast, z30, tool1;
            MoveL p_R_Door_R_PickDown, v_slow, fine, tool1;
            Dripper_On;
            MoveL p_R_Door_R_PickDown, v_slow, fine, tool1;
            MoveL p_Door_Assembly, v_fast, z30, tool1;
            MoveL p_Door_Assembly_R, v_fast, z30, tool1;
            MoveL p_Door_Assembly_R_D, v_slow, fine, tool1;
            Dripper_Off;
            MoveL p_Door_Assembly_R, v_slow, fine, tool1;
            
            
            !왼쪽 차채
            MoveJ p_R_Door_L_PickUp, v_fast, z30, tool1;
            MoveL p_R_Door_L_PickDown, v_slow, fine, tool1;
            Dripper_On;
            MoveL p_R_Door_L_PickDown, v_slow, fine, tool1;
            MoveL p_Door_Assembly, v_fast, z30, tool1;
            MoveL p_Door_Assembly_L, v_fast, z30, tool1;
            MoveL p_Door_Assembly_L_D, v_slow, fine, tool1;
            Dripper_Off;
            MoveL p_Door_Assembly_L, v_slow, fine, tool1;
            
        ENDIF
        
        MoveL Offs(p_Door_Assembly, 0, 0, 30), v_fast, z30, tool1;
        MoveJ p_Home, v500, fine, tool1;

    ENDPROC

    PROC Car_Delivery()
        MoveL p_Assembly_Up, v_fast, z30, tool1;
        MoveL p_Assembly_Down, v_slow, fine, tool1;
        Dripper_On;
        MoveL p_Assembly_Up, v_slow, fine, tool1;
        MoveL p_Car_Delivery_Up, v_slow, z30, tool1;!일부로 느리게
        MoveL p_Car_Delivery_Down, v_slow, fine, tool1;
        Dripper_Off;
        MoveL p_Car_Delivery_Up, v_fast, fine, tool1;
        PulseDO\PLength :=0.2, do05_Body_Docking_Done;
        MoveJ p_Home, v_fast, z30, tool1;
    ENDPROC








    PROC Dripper_On()
        PulseDO\PLength :=0.2, do00_Gripper_On;
    ENDPROC

    PROC Dripper_Off()
        PulseDO\PLength :=0.2, do01_Gripper_Off;
    ENDPROC



ENDMODULE


