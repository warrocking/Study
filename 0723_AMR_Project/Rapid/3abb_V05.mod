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

    ! Home / safe position
    PERS robtarget p_home := [[489.74,-27.58,601.64],[5.16503E-05,0.687919,-0.725787,0.000127384],[-1,-1,-2,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    ! ===== Upper body panel station =====
    PERS robtarget p_Body := [[-134.25,563.62,370.53],[3.12666E-05,0.688066,-0.725648,5.77533E-05],[1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_Body_L := [[-10.94,583.54,255.05],[6.39722E-05,0.688077,-0.725637,9.09593E-05],[1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_Body_L_L := [[44.78,592.37,195.70],[6.38944E-05,0.688065,-0.725649,8.85658E-05],[0,-1,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_Body_L_L_D := [[44.78,592.37,179.65],[7.64528E-05,0.688064,-0.72565,9.88073E-05],[0,-1,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_Body_L_R := [[-64.53,592.38,195.70],[4.59639E-05,0.688079,-0.725636,6.44889E-05],[1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_Body_L_R_D := [[-64.53,592.37,178.56],[5.96375E-05,0.688079,-0.725636,8.23022E-05],[1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_Body_R := [[-250.55,592.36,250.37],[6.42408E-05,0.688073,-0.725642,8.47056E-05],[1,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_Body_R_L := [[-197.91,589.41,200.68],[5.36277E-05,0.688072,-0.725643,5.01318E-05],[1,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_Body_R_L_D := [[-197.90,589.40,182.47],[6.67946E-05,0.688071,-0.725643,8.08772E-05],[1,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_Body_R_R := [[-304.26,589.42,200.68],[4.98926E-05,0.688074,-0.72564,4.41599E-05],[1,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_Body_R_R_Down := [[-304.26,589.41,182.40],[5.5944E-05,0.688073,-0.725642,6.45307E-05],[1,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_Body_Docking := [[369.59,345.42,335.46],[0.000161568,0.688013,-0.725698,6.76197E-05],[0,-1,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_Body_Docking_L := [[334.47,192.22,222.00],[0.000204477,0.999985,0.00540559,-0.000181063],[0,-1,-2,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_Body_Docking_L_D := [[334.46,192.21,201.93],[0.000217642,0.999985,0.00540497,-0.000200572],[0,-1,-2,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_Body_Docking_R := [[337.95,510.70,206.83],[0.000243374,0.999969,-0.00780964,-0.000124017],[0,-1,-2,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_Body_Docking_R_D := [[337.95,510.69,189.81],[0.0002617,0.999969,-0.00780634,-0.000134949],[0,-1,-2,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_Body_Assembly := [[369.52,345.32,284.14],[0.000556613,0.688017,-0.725694,5.94809E-05],[0,-1,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_Body_Assembly_Down := [[369.59,345.42,227.15],[0.000214458,0.688031,-0.725682,5.98623E-05],[0,-1,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_Body_Center := [[523.72,-29.21,386.61],[0.000170218,0.688028,-0.725685,5.89275E-05],[-1,-1,-2,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_Body_Center_Down := [[523.72,-29.21,348.69],[0.000179907,0.688028,-0.725684,5.21166E-05],[-1,-1,-2,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    ! ===== Welding station (tool pickup + 10 weld points) =====
    PERS robtarget p_Tool_PickUp := [[650.74,-350.38,312.67],[5.22831E-05,0.687932,-0.725776,0.000137781],[-1,-1,-2,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_Tool_PickDown := [[650.73,-350.38,285.92],[5.65773E-05,0.687933,-0.725774,0.000120322],[-1,-1,-2,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_Welding_Start := [[650.72,-26.92,342.63],[0.184216,0.662782,-0.699344,-0.194171],[-1,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_Point1 := [[650.71,-26.92,312.81],[0.184229,0.662781,-0.699337,-0.194185],[-1,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_point2 := [[633.09,-26.92,314.86],[0.184282,0.662775,-0.699318,-0.194227],[-1,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_point3 := [[633.10,-26.92,357.35],[0.184272,0.662777,-0.699322,-0.194214],[-1,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_point4 := [[566.83,-26.92,370.99],[0.0943491,-0.681404,0.718913,-0.0997478],[-1,-1,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_point5 := [[557.66,-26.91,395.81],[0.0943496,-0.681399,0.718918,-0.0997531],[-1,-1,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_point6 := [[446.18,-23.32,381.97],[0.264203,-0.629477,0.669377,-0.29307],[-1,0,-2,1],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_point7 := [[423.52,-23.33,343.30],[0.35834,-0.581065,0.616027,-0.393024],[-1,0,-2,1],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_point8 := [[391.17,-23.31,318.66],[0.477932,-0.487486,0.513897,-0.519469],[-1,0,-2,1],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_point9 := [[391.17,-23.31,277.02],[0.477902,-0.487512,0.513923,-0.519446],[-1,0,-2,1],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_point10 := [[374.29,-23.31,277.01],[0.477891,-0.487518,0.513933,-0.519441],[-1,0,-2,1],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_Welding_End := [[377.13,-14.13,346.89],[6.43336E-05,-0.506074,0.86249,-4.09571E-05],[-1,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    PERS robtarget p_Change_angle_3to4 := [[0,0,0],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_Change_angle_4to5 := [[0,0,0],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_Change_angle_5to6 := [[0,0,0],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_Change_angle_6to7 := [[0,0,0],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_Change_angle_7to8 := [[0,0,0],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_Change_angle_8to9 := [[0,0,0],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    ! ===== Door station =====
    PERS robtarget p_Door := [[0,0,0],[1,0,0,0],[0,0,0,0],[9E9,9E9,9E9,9E9,9E9,9E9]];
    PERS robtarget p_Door_L := [[0,0,0],[1,0,0,0],[0,0,0,0],[9E9,9E9,9E9,9E9,9E9,9E9]];
    PERS robtarget p_Door_L_L := [[0,0,0],[1,0,0,0],[0,0,0,0],[9E9,9E9,9E9,9E9,9E9,9E9]];
    PERS robtarget p_Door_L_L_Down := [[0,0,0],[1,0,0,0],[0,0,0,0],[9E9,9E9,9E9,9E9,9E9,9E9]];
    PERS robtarget p_Door_L_R := [[0,0,0],[1,0,0,0],[0,0,0,0],[9E9,9E9,9E9,9E9,9E9,9E9]];
    PERS robtarget p_Door_L_R_Down := [[0,0,0],[1,0,0,0],[0,0,0,0],[9E9,9E9,9E9,9E9,9E9,9E9]];
    PERS robtarget p_Door_R := [[0,0,0],[1,0,0,0],[0,0,0,0],[9E9,9E9,9E9,9E9,9E9,9E9]];
    PERS robtarget p_Door_R_L := [[0,0,0],[1,0,0,0],[0,0,0,0],[9E9,9E9,9E9,9E9,9E9,9E9]];
    PERS robtarget p_Door_R_L_Down := [[0,0,0],[1,0,0,0],[0,0,0,0],[9E9,9E9,9E9,9E9,9E9,9E9]];
    PERS robtarget p_Door_R_R := [[0,0,0],[1,0,0,0],[0,0,0,0],[9E9,9E9,9E9,9E9,9E9,9E9]];
    PERS robtarget p_Door_R_R_Down := [[0,0,0],[1,0,0,0],[0,0,0,0],[9E9,9E9,9E9,9E9,9E9,9E9]];
    PERS robtarget p_Door_L_Docking := [[0,0,0],[1,0,0,0],[0,0,0,0],[9E9,9E9,9E9,9E9,9E9,9E9]];
    PERS robtarget p_Door_L_Docking_In := [[0,0,0],[1,0,0,0],[0,0,0,0],[9E9,9E9,9E9,9E9,9E9,9E9]];
    PERS robtarget p_Door_R_Docking := [[0,0,0],[1,0,0,0],[0,0,0,0],[9E9,9E9,9E9,9E9,9E9,9E9]];
    PERS robtarget p_Door_R_Docking_In := [[0,0,0],[1,0,0,0],[0,0,0,0],[9E9,9E9,9E9,9E9,9E9,9E9]];

    ! ===== Delivery station =====
    PERS robtarget p_Car_Up := [[0,0,0],[1,0,0,0],[0,0,0,0],[9E9,9E9,9E9,9E9,9E9,9E9]];
    PERS robtarget p_Car_Down := [[0,0,0],[1,0,0,0],[0,0,0,0],[9E9,9E9,9E9,9E9,9E9,9E9]];
    PERS robtarget p_Car_Delivery_Up := [[0,0,0],[1,0,0,0],[0,0,0,0],[9E9,9E9,9E9,9E9,9E9,9E9]];
    PERS robtarget p_Car_Delivery_Down := [[0,0,0],[1,0,0,0],[0,0,0,0],[9E9,9E9,9E9,9E9,9E9,9E9]];

    VAR speeddata v_fast := v200;
    VAR speeddata v_slow := v50;



    CONST string ROBOT_IP := "192.168."; 
    CONST num ROBOT_PORT := 5000;
    VAR socketdev srv_server_socket;
    VAR socketdev srv_client_socket;
    VAR string srv_received_string;
    VAR bool srv_keep_listening := TRUE;
    VAR num ProcessNum := 0;
    PERS robtarget p_Body_Docking10:=[[-250.55,592.35,250.36],[6.80212E-05,0.688079,-0.725635,0.000101044],[1,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
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
            MoveJ p_Body, v_fast, z30, tool1;
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
        MoveL Offs(p_Body_Center,0,0,-15), v_fast, z30, tool1;
        MoveL p_Body_Center_Down, v_slow, fine, tool1;
        Dripper_Off;
        MoveJ Offs(p_Body_Center,0,0,30), v_fast, z30, tool1;

    ENDPROC

    Proc Welding_Process()
        MoveJ p_Tool_PickUp, v_fast, z30, tool1;
        MoveL p_Tool_PickDown, v_slow, fine, tool1;
        Dripper_On;
        MoveL Offs(p_Tool_PickUp, 0, 0, 30), v_fast, fine, tool1;
        MoveL p_Welding_Start, v_fast, z30, tool1;
        
        MoveL p_Point1 , v_slow, z10, tool1;
        !?? ?? ??
        MoveL p_point2, v10, z10, tool1;
        MoveL p_point3 , v10, z10, tool1;
        MoveL p_Change_angle_3to4, v10, z10, tool1;
        MoveL p_point4 , v10, z10, tool1;
        MoveL p_Change_angle_4to5, v10, z10, tool1;
        MoveL p_point5 , v10, z10, tool1;
        MoveL p_Change_angle_5to6, v10, z10, tool1;
        MoveL p_point6 , v10, z10, tool1;
        MoveL p_Change_angle_6to7, v10, z10, tool1;
        MoveL p_point7 , v10, z10, tool1;
        MoveL p_Change_angle_7to8, v10, z10, tool1;
        MoveL p_point8 , v10, z10, tool1;
        MoveL p_Change_angle_8to9, v10, z10, tool1;
        MoveL p_point9 , v10, z10, tool1;
        !?? ?? ?
        MoveL p_point10, v10, z30, tool1;

        MoveL p_Welding_End, v_slow, z30, tool1;
        MoveL Offs(p_Tool_PickUp, 0, 0, 30), v_fast, z30, tool1;
        MoveL p_Tool_PickUp, v_fast, z30, tool1;
        MoveL p_Tool_PickDown, v_slow, fine, tool1;
        Dripper_Off;
        MoveL p_Tool_PickUp, v_slow, fine, tool1;
        MoveL Offs(p_Tool_PickUp, 0, 0, 30), v_fast, z30, tool1;
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


