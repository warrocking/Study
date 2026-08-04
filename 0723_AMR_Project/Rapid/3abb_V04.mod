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

    VAR speeddata v_fast := v200;
    VAR speeddata v_slow := v50;



    CONST string ROBOT_IP := "192.168."; 
    CONST num ROBOT_PORT := 5000;
    VAR socketdev srv_server_socket;
    VAR socketdev srv_client_socket;
    VAR string srv_received_string;
    VAR bool srv_keep_listening := TRUE;
    VAR num ProcessNum := 0;
    PROC Main()
        MoveL p_home, v1000, z50, tool1;
        Init;
        Run_Socket_Server;
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



    PROC Init()
        Dripper_Off;
        MoveJ p_home, v500, z50, tool1;
        ProcessNum := 0;

    ENDPROC

    PROC Run_Upper_Body_Assembly()
        
        
        Press_Process;
        
        Upper_Body_Process;

        Welding_Process;

        Door_Docking_Process;

        Car_Delivery;


        !?? ?
        ProcessNum := ProcessNum+1;
    ENDPROC

    Proc Press_Process()
        PulseDO\PLength := 0.2, do02_Press_Start;
        WaitDI di02_PLC_Press_Done,1;
    ENDPROC

    Proc Upper_Body_Process()
        
        IF ProcessNum = 0 THEN !?? ?? ?? ??
            ! PickUp Left_Left
            MoveJ p_Body, v_fast, z30, tool1;
            MoveJ p_Body_L, v_fast, z30, tool1;
            MoveL p_Body_L_L, v_fast, z30, tool1;
            MoveL p_Body_L_L_D, v_slow, fine, tool1;
            Dripper_On;
            MoveL p_Body_L_L, v_slow, fine, tool1;
            MoveL p_Body_L, v_fast, z30, tool1;
            MoveL p_Body, v_fast, z30, tool1;

            ! Assembly Left_Left
            MoveL p_Body_Docking, v_fast, z30, tool1;
            MoveL p_Body_Docking_R, v_fast, z30, tool1;
            MoveL p_Body_Docking_R_D, v_slow, fine, tool1;
            Dripper_Off;
            MoveL p_Body_Docking_R, v_slow, fine, tool1;
            MoveL p_Body_Docking, v_fast, z30, tool1;
            
            ! PickUp Left_Right
            MoveJ p_Body, v_fast, z30, tool1;
            MoveJ p_Body_L, v_fast, z30, tool1;
            MoveL p_Body_L_R, v_fast, z30, tool1;
            MoveL p_Body_L_R_D, v_slow, fine, tool1;
            Dripper_On;
            MoveL p_Body_L_R, v_slow, fine, tool1;
            MoveL p_Body_L, v_fast, z30, tool1;
            MoveL p_Body, v_fast, z30, tool1;

            ! Assembly Left_Right
            MoveL p_Body_Docking, v_fast, z30, tool1;
            MoveL p_Body_Docking_L, v_fast, z30, tool1;
            MoveL p_Body_Docking_L_D, v_slow, fine, tool1;
            Dripper_Off;
            MoveL p_Body_Docking_L, v_slow, fine, tool1;
            MoveL p_Body_Docking, v_fast, z30, tool1;

        ELSEIF ProcessNum = 1 THEN
            ! PickUp Right_Left
            MoveJ p_Body, v_fast, z30, tool1;
            MoveJ p_Body_R, v_fast, z30, tool1;
            MoveL p_Body_R_L, v_fast, z30, tool1;
            MoveL p_Body_R_L_D, v_slow, fine, tool1;
            Dripper_On;
            MoveL p_Body_R_L, v_slow, fine, tool1;
            MoveL p_Body_R, v_fast, z30, tool1;
            MoveL p_Body, v_fast, z30, tool1;

            ! Assembly Right_Left
            MoveL p_Body_Docking, v_fast, z30, tool1;
            MoveL p_Body_Docking_R, v_fast, z30, tool1;
            MoveL p_Body_Docking_R_D, v_slow, fine, tool1;
            Dripper_Off;
            MoveL p_Body_Docking_R, v_slow, fine, tool1;
            MoveL p_Body_Docking, v_fast, z30, tool1;

            ! PickUp Right_Right
            MoveJ p_Body_R, v_fast, z30, tool1;
            MoveL p_Body_R_R, v_fast, z30, tool1;
            MoveL p_Body_R_R_Down , v_slow,fine ,tool1 ;
            Dripper_On ;
            MoveL p_Body_R_R ,v_slow,fine ,tool1 ;
            MoveL p_Body_R ,v_fast,z30 ,tool1 ;
            MoveL p_Body ,v_fast,z30 ,tool1 ;

            ! Assembly Right_Right
            MoveL p_Body_Docking ,v_fast,z30 ,tool1 ;
            MoveL p_Body_Docking_L ,v_fast,z30 ,tool1 ;
            MoveL p_Body_Docking_L_D ,v_slow,fine ,tool1 ;
            Dripper_Off ;
            MoveL p_Body_Docking_L ,v_slow,fine ,tool1 ;
            MoveL p_Body_Docking ,v_fast,z30 ,tool1 ;
            
        ENDIF
        
        MoveJ p_Body_Assembly, v_fast, z30, tool1;
        PulseDO\PLength:=0.2, do03_Body_Start;
        WaitDI di03_PLC_Body_Docking_On, 1;
       
        MoveL p_Body_Assembly_Down, v_slow, fine, tool1;
        Dripper_On;
        PulseDO\PLength := 0.2, do04_Body_Pick;
        WaitDI di04_PLC_Body_Docking_Off, 1;
        
        MoveL p_Body_Assembly, v_slow, z30, tool1;
        MoveL p_Body_Docking, v_fast, z30, tool1;
        
        MoveL p_Body_Center, v_fast, z30, tool1;
        MoveL p_Body_Center_Down, v_slow, fine, tool1;
        Dripper_Off;
        MoveL p_Body_Center, v_slow, fine, tool1;

    ENDPROC

    Proc Welding_Process()
        MoveJ p_Tool_PickUp, v_fast, z30, tool1;
        MoveL p_Tool_PickDown, v_slow, fine, tool1;
        Dripper_On;
        MoveL p_Tool_PickUp, v_slow, fine, tool1;
        MoveL p_Welding_Start, v_fast, z30, tool1;
        
        MoveL p_Point1 , v_fast, z10, tool1;
        !?? ?? ??
        MoveL p_point2 , v_slow, z30, tool1;
        MoveL p_point3 , v_slow, z30, tool1;
        MoveL p_point4 , v_slow, z30, tool1;
        MoveL p_point5 , v_slow, z30, tool1;
        MoveL p_point6 , v_slow, z30, tool1;
        MoveL p_point7 , v_slow, z30, tool1;
        MoveL p_point8 , v_slow, z30, tool1;
        MoveL p_point9 , v_slow, z30, tool1;
        !?? ?? ?
        MoveL p_point10, v_slow, z30, tool1;

        MoveL p_Welding_End, v_fast, z30, tool1;
        MoveL p_Tool_PickUp, v_fast, z30, tool1;
        MoveL p_Tool_PickDown, v_slow, fine, tool1;
        Dripper_Off;
        MoveL p_Tool_PickUp, v_fast, fine, tool1;
        MoveL p_Home, v_fast, z30, tool1;
    ENDPROC

    PROC Door_Docking_Process()
        IF ProcessNum = 0 THEN 
            !Door PickUP_Left_Left
            MoveJ p_Door, v_fast, z30, tool1;
            MoveJ p_Door_L, v_fast, z30, tool1;
            MoveL p_Door_L_L, v_fast, z30, tool1;
            MoveL p_Door_L_L_Down, v_slow, fine, tool1;
            Dripper_On;
            MoveL p_Door_L_L, v_slow, fine, tool1;
            MoveL p_Door_L, v_fast, z30, tool1;
            MoveL p_Door, v_fast, z30, tool1;

            !Door Docking_Left_Left
            MoveL p_Door_R, v_fast, z30, tool1;
            MoveL p_Door_R_Docking, v_fast, z30, tool1;
            MoveL p_Door_R_Docking_In, v_slow, fine, tool1;
            Dripper_Off;
            MoveL p_Door_R_Docking, v_slow, fine, tool1;
            MoveL p_Door_R, v_fast, z30, tool1;
            MoveJ p_Door, v_fast, z30, tool1;

            !Door PickUP_Left_Right
            MoveJ p_Door_L, v_fast, z30, tool1;
            MoveL p_Door_L_R, v_fast, z30, tool1;
            MoveL p_Door_L_R_Down, v_slow, fine, tool1;
            Dripper_On;
            MoveL p_Door_L_R, v_slow, fine, tool1;
            MoveL p_Door_L, v_fast, z30, tool1;

            !Door Docking_Left_Right
            MoveL p_Door_L_Docking, v_fast, z30, tool1;
            MoveL p_Door_L_Docking_In, v_slow, fine, tool1;
            Dripper_Off;
            MoveL p_Door_L_Docking, v_slow, fine, tool1;
            MoveL p_Door_L, v_fast, z30, tool1;
            MoveJ p_Door, v_fast, z30, tool1;


        ELSEIF ProcessNum = 1 THEN
            !Door PickUP_Right_Left
            MoveJ p_Door, v_fast, z30, tool1;
            MoveJ p_Door_R, v_fast, z30, tool1;
            MoveL p_Door_R_L, v_fast, z30, tool1;
            MoveL p_Door_R_L_Down, v_slow, fine, tool1;
            Dripper_On;
            MoveL p_Door_R_L, v_slow, fine, tool1;
            MoveL p_Door_R, v_fast, z30, tool1;

            !Door Docking_Right_Left
            MoveL p_Door_R_Docking, v_fast, z30, tool1;
            MoveL p_Door_R_Docking_In, v_slow, fine, tool1;
            Dripper_Off;
            MoveL p_Door_R_Docking, v_slow, fine, tool1;
            MoveL p_Door_R, v_fast, z30, tool1;
            

            !Door PickUP_Right_Right
            !MoveJ p_Door_R, v_fast, z30, tool1;
            MoveL p_Door_R_R, v_fast, z30, tool1;
            MoveL p_Door_R_R_Down, v_slow, fine, tool1;
            Dripper_On;
            MoveL p_Door_R_R, v_slow, fine, tool1;
            MoveL p_Door_R, v_fast, z30, tool1;
            MoveL p_Door, v_fast, z30, tool1;

            !Door Docking_Right_Right
            MoveL p_Door_L, v_fast, z30, tool1;
            MoveL p_Door_L_Docking, v_fast, z30, tool1;
            MoveL p_Door_L_Docking_In, v_slow, fine, tool1;
            Dripper_Off;
            MoveL p_Door_L_Docking, v_slow, fine, tool1;
            MoveL p_Door_L, v_fast, z30, tool1;
            MoveJ p_Door, v_fast, z30, tool1;
        ENDIF
        
        MoveL Offs(p_Door_Assembly, 0, 0, 30), v_fast, z30, tool1;
        MoveJ p_Home, v_fast, fine, tool1;

    ENDPROC

    PROC Car_Delivery()
        MoveL p_Car_Up, v_fast, z30, tool1;
        MoveL p_Car_Down, v_slow, fine, tool1;
        Dripper_On;
        MoveL p_Car_Up, v_slow, fine, tool1;
        MoveL p_Car_Delivery_Up, v_slow, z30, tool1;!??? ???
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


