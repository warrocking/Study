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
    PERS robtarget p_Body_L_L_D := [[43.41,591.85,177.12],[0.000111025,0.688068,-0.725646,0.000132786],[0,-1,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_Body_L_R := [[-64.51,590.22,214.03],[4.80449E-05,0.688081,-0.725634,7.30321E-05],[1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_Body_L_R_D := [[-64.51,590.20,176.80],[7.40147E-05,0.688081,-0.725634,0.000106374],[1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_Body_R := [[-250.55,592.36,250.37],[6.42408E-05,0.688073,-0.725642,8.47056E-05],[1,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_Body_R_L := [[-197.91,589.41,200.68],[5.36277E-05,0.688072,-0.725643,5.01318E-05],[1,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_Body_R_L_D := [[-197.90,589.40,182.47],[6.67946E-05,0.688071,-0.725643,8.08772E-05],[1,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_Body_R_R := [[-304.26,589.42,200.68],[4.98926E-05,0.688074,-0.72564,4.41599E-05],[1,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_Body_R_R_Down := [[-304.26,589.41,182.40],[5.5944E-05,0.688073,-0.725642,6.45307E-05],[1,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_Body_Docking := [[369.59,345.42,335.46],[0.000161568,0.688013,-0.725698,6.76197E-05],[0,-1,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_Body_Docking_L := [[338.36,188.52,227.49],[0.000118379,0.999938,0.0111187,-6.30196E-05],[0,-1,-2,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_Body_Docking_L_D := [[338.36,188.52,198.63],[0.000130609,0.999938,0.0110942,-7.52609E-05],[0,-1,-2,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_Body_Docking_R := [[338.29,506.09,215.68],[0.000663043,0.999537,-0.0304128,-0.000381125],[0,-1,-2,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_Body_Docking_R_D := [[338.28,506.08,197.21],[0.000689342,0.999537,-0.0304105,-0.000397975],[0,-1,-2,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_Body_Assembly := [[369.52,345.32,284.14],[0.000556613,0.688017,-0.725694,5.94809E-05],[0,-1,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_Body_Assembly_Down := [[369.59,345.42,227.15],[0.000214458,0.688031,-0.725682,5.98623E-05],[0,-1,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_Body_Center := [[523.72,-29.21,386.61],[0.000170218,0.688028,-0.725685,5.89275E-05],[-1,-1,-2,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_Body_Center_Down := [[523.72,-29.21,348.69],[0.000179907,0.688028,-0.725684,5.21166E-05],[-1,-1,-2,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    ! ===== Welding station (tool pickup + 10 weld points) =====
    PERS robtarget p_Tool_PickUp := [[647.47,-352.00,331.18],[6.14141E-05,0.527673,-0.849448,8.26241E-05],[-1,-1,-2,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_Tool_PickDown := [[647.46,-352.00,315.43],[7.55704E-05,0.527674,-0.849447,5.70761E-05],[-1,-1,-2,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_Welding_Start := [[647.47,-32.25,376.17],[0.0800009,0.527733,-0.844062,-0.0515401],[-1,-1,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_Point1 := [[620.42,-32.26,343.26],[0.0800685,0.527733,-0.844054,-0.0515709],[-1,-1,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_point2 := [[620.44,-32.26,383.09],[0.0800314,0.527735,-0.844057,-0.0515513],[-1,-1,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_point3 := [[568.39,-32.25,388.58],[0.0708763,-0.538956,0.837373,-0.0575295],[-1,-1,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_point4 := [[557.62,-32.24,412.96],[0.0708858,-0.538953,0.837374,-0.0575378],[-1,-1,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_point5 := [[521.05,-30.80,410.74],[0.126055,-0.534999,0.828816,-0.104647],[-1,-1,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_point6 := [[408.29,-25.00,326.20],[0.161502,0.773971,0.583878,0.184315],[-1,-1,1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_point7 := [[408.30,-23.80,368.54],[0.161519,0.773969,0.58387,0.184335],[-1,-1,1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_point8 := [[490.05,-24.93,383.77],[0.0848636,-0.775966,-0.609948,0.13652],[-1,-1,1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_point9 := [[489.62,-28.90,412.05],[0.051573,-0.782537,-0.616479,0.0702067],[-1,-1,1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_point10 := [[512.35,-28.90,412.05],[0.0515681,-0.782547,-0.616469,0.0701954],[-1,-1,1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_Welding_End := [[355.42,-31.45,251.71],[1.1103E-06,-0.664459,0.747324,-1.09402E-06],[-1,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    PERS robtarget p_Point_Left:= [[545.19,-154.06,341.67],[0.00102431,0.0901107,0.995931,-0.000206079],[-1,-1,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];   
    PERS robtarget p_Point_Left_1:= [[545.95,-112.67,335.67],[0.0197576,-0.074769,-0.965856,-0.247267],[-1,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];   
    PERS robtarget p_Point_Left_2:= [[545.95,-112.67,345.05],[0.0197376,-0.0747691,-0.965858,-0.247263],[-1,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];   
    PERS robtarget p_Point_Left_3:= [[551.78,-112.48,356.81],[0.0196497,-0.0747572,-0.965867,-0.247239],[-1,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];   
    PERS robtarget p_Point_Left_4:= [[561.32,-112.49,365.12],[0.0195886,-0.0747464,-0.965874,-0.247216],[-1,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];   
    PERS robtarget p_Point_Left_5:= [[571.13,-112.52,368.58],[0.0195345,-0.0747225,-0.965884,-0.247189],[-1,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];   
    PERS robtarget p_Point_Left_6:= [[562.13,-112.51,395.33],[0.0195159,-0.0747241,-0.965883,-0.247193],[-1,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];   
    PERS robtarget p_Point_Left_7:= [[562.14,-112.51,410.54],[0.0194914,-0.0747226,-0.965885,-0.247191],[-1,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];   
   
        ! ?? -> ?? ??
    PERS robtarget p_ChangePoint:= [[523.26,-37.45,472.31],[2.63606E-06,0.541205,-0.840891,-2.12207E-06],[-1,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];   
        
        ! ??? ?? ??
    PERS robtarget p_Point_Right := [[541.76,94.54,341.51],[1.44267E-06,-0.99054,0.137224,7.96599E-06],[0,0,-2,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];   
    PERS robtarget p_Point_Right_1:= [[546.67,55.86,335.09],[0.25806,0.958696,-0.114506,0.0345746],[0,-1,-2,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];   
    PERS robtarget p_Point_Right_2:= [[548.14,55.88,347.27],[0.258037,0.958702,-0.114497,0.0346176],[0,-1,-2,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];   
    PERS robtarget p_Point_Right_3:= [[554.75,55.89,359.60],[0.258014,0.958706,-0.114496,0.0346718],[0,-1,-2,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];   
    PERS robtarget p_Point_Right_4 := [[563.62,55.49,365.59],[0.257986,0.958709,-0.114524,0.0347107],[0,-1,-2,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];   
    PERS robtarget p_Point_Right_5:= [[571.51,55.49,367.95],[0.257976,0.95871,-0.114529,0.034732],[0,-1,-2,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];   
    PERS robtarget p_Point_Right_6:= [[561.90,55.01,394.94],[0.257945,0.958713,-0.114561,0.0347635],[0,-1,-2,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];   
    PERS robtarget p_Point_Right_7:= [[559.25,55.00,406.95],[0.257948,0.958712,-0.114565,0.03478],[0,-1,-2,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];   




    PERS robtarget p_ChangePoint_Under := [[370.08,-32.20,326.20],[0.0623725,0.797502,0.59637,0.0666582],[-1,-1,1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_Change_angle_2to3 := [[587.96,-32.25,388.58],[0.0708745,-0.538957,0.837372,-0.0575334],[-1,-1,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_Change_angle_3to4 := [[590.75,-30.34,370.60],[0.0884578,-0.682211,0.719733,-0.0935279],[-1,-1,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_Change_angle_4to5 := [[545.82,-30.80,410.74],[0.126061,-0.534996,0.828816,-0.104653],[-1,-1,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_Change_angle_5to6 := [[551.00,-29.61,394.00],[0.123138,-0.676819,0.714022,-0.130099],[-1,-1,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_Change_angle_6to7 := [[445.34,-27.84,379.12],[0.19017,0.74213,0.608087,0.208107],[-1,0,1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_Change_angle_7to8 := [[470.02,-24.93,383.78],[0.084873,-0.775958,-0.609954,0.136538],[-1,-1,1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_Change_angle_8to9 := [[478.78,-24.92,386.70],[0.0515972,-0.782534,-0.616478,0.0702392],[-1,-1,1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_Change_angle_9to10 := [[445.34,-27.84,379.12],[0.19017,0.74213,0.608087,0.208107],[-1,0,1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    ! ===== Door station =====
    PERS robtarget p_Door := [[525.23,-34.18,429.15],[0.000119974,0.527651,-0.849461,5.40934E-05],[-1,-1,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_Door_L := [[522.42,-154.63,309.57],[0.000112878,0.527648,-0.849463,4.30417E-05],[-1,-1,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_Door_L_L := [[522.41,-175.85,266.70],[0.000120146,0.527648,-0.849463,4.05123E-05],[-1,-1,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_Door_L_L_Down := [[522.42,-175.85,231.13],[0.000127122,0.527646,-0.849464,2.58868E-05],[-1,-1,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_Door_L_R := [[522.41,-130.70,266.17],[0.000124568,0.527664,-0.849453,3.44154E-05],[-1,-1,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_Door_L_R_Down := [[522.41,-130.70,231.30],[0.000137523,0.527658,-0.849457,1.88982E-05],[-1,-1,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_Door_R := [[525.23,96.72,312.72],[0.000165015,0.527649,-0.849462,2.82871E-05],[0,-1,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_Door_R_L := [[520.27,73.51,269.43],[0.000225644,0.527654,-0.849459,5.9143E-06],[0,-1,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_Door_R_L_Down := [[520.28,73.51,230.40],[0.000218344,0.527651,-0.849461,8.42241E-06],[0,-1,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_Door_R_R := [[522.25,118.33,268.98],[0.000162256,0.527649,-0.849463,3.08172E-05],[0,-1,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_Door_R_R_Down := [[522.23,118.33,227.29],[0.000218602,0.527646,-0.849464,1.09739E-05],[0,-1,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_Door_L_Docking := [[526.82,-165.99,289.19],[0.386875,-0.386859,0.591862,0.591918],[-1,0,-2,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_Door_L_Docking_In := [[526.81,-82.87,289.20],[0.386859,-0.38685,0.591849,0.591947],[-1,0,-2,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_Door_R_Docking := [[526.45,111.28,288.88],[0.345138,0.351587,-0.622501,0.608078],[0,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_Door_R_Docking_In := [[526.45,22.15,288.89],[0.345158,0.351579,-0.622495,0.608077],[0,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    ! ===== Delivery station =====
    PERS robtarget p_Car_Up := [[0,0,0],[1,0,0,0],[0,0,0,0],[9E9,9E9,9E9,9E9,9E9,9E9]];
    PERS robtarget p_Car_Down := [[0,0,0],[1,0,0,0],[0,0,0,0],[9E9,9E9,9E9,9E9,9E9,9E9]];
    PERS robtarget p_Car_Delivery_Up := [[172.27,352.21,386],[0.000301434,0.681124,-0.732168,0.00010606],[0,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_Car_Delivery_Down := [[172.27,352.21,292.24],[0.000324799,0.681125,-0.732167,0.000115609],[0,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    VAR speeddata v_fast := v200;
    VAR speeddata v_slow := v50;



    CONST string ROBOT_IP := "192.168.3.3"; 
    CONST num ROBOT_PORT := 5000;
    VAR socketdev srv_server_socket;
    VAR socketdev srv_client_socket;
    VAR string srv_received_string;
    VAR bool srv_keep_listening := TRUE;
    VAR num ProcessNum := 0;
    PERS robtarget p_Body_Docking10:=[[-250.55,592.35,250.36],[6.80212E-05,0.688079,-0.725635,0.000101044],[1,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PROC Main()
        MoveL p_home, v_fast, z50, tool1;
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
        ! Role: Decides what to do for one received command.
        ! Process: matches by PREFIX (StrPart), not exact equality (=). SocketReceive can
        !          hand back trailing CR/LF or other extra bytes depending on how the
        !          connector sends the command - an exact "cmd = "Start"" match silently
        !          fails whenever that happens, even though the TPWrite log clearly shows
        !          "Start" was received. Comparing only the first N characters is immune
        !          to whatever comes after.
        ! ??: ??(=) ?? ??? ????, ??? ??? ? ??? ?? ??? ?? StrPart?
        !       ?? ??? ????. ????? ??? ??? ?? SocketReceive? ? ??
        !       CR/LF? ?? ????? ?? ? ?????, ??? cmd = "Start"? ??? ??
        !       ??? ?? "Start"? ????? ??? ?? ?? ?? ????. ? N???
        !       ?? ????? ? ??? ???? ?? ?? ??? ????.
        IF (StrLen(cmd) >= 5) THEN
            IF (StrPart(cmd, 1, 5) = "Start") OR (StrPart(cmd, 1, 5) = "start") THEN
                TPWrite "Move Start";
                Run_Upper_Body_Assembly;
                RETURN;
            ENDIF
        ENDIF

        IF (StrLen(cmd) >= 3) THEN
            IF (StrPart(cmd, 1, 3) = "End") OR (StrPart(cmd, 1, 3) = "END") THEN
                !??
                RETURN;
            ENDIF
        ENDIF

        IF (StrLen(cmd) >= 9) THEN
            IF (StrPart(cmd, 1, 9) = "Emergency") THEN
                !??
            ENDIF
        ENDIF
    ENDPROC



    PROC Init()
        Dripper_Off;
        MoveJ p_home, v_fast, z50, tool1;
        ProcessNum := 0;

    ENDPROC

    PROC Run_Upper_Body_Assembly()
        ! Start 1회 = 완전히 독립된 차 2대(Left 공간 1대 + Right 공간 1대, 5abb의
        ! 2-유닛 패턴과 동일). Press_Process만 반복문 밖에서 1번 - 프레스는
        ! 2대분 소재를 한 번에 가공하므로 매 차량마다 다시 누를 필요가 없음.
        ! 나머지(패널 조립/도어/용접/출고)는 차량마다 전부 따로 해야 하므로
        ! 반복문 안에 그대로 둠.
        VAR num n_upperBodyCount := 0;

        Press_Process;

        FOR n_upperBodyCount FROM 1 TO 2 DO
            !TPWrite "Upper Body Assembly Cycle: " + \Num:=n_upperBodyCount;
            Upper_Body_Process;
            Door_Docking_Process;
            Welding_Process;
            IF di05_PLC_PlateReady = 1 THEN
                Car_Delivery;
                
            ELSEIF di05_PLC_PlateReady = 0 THEN
                TPWrite "Car Delivery is not ready";
                SocketSend srv_client_socket \Str:="3abb? ???";
                WaitDI di05_PLC_PlateReady,1;
                Car_Delivery;
            ENDIF
            ProcessNum := ProcessNum+1;

            ! AMR이 실제로 이 스테이션 출고 컨베이어에 도착했다는 확인
            ! ("AmrArrived") 없이는 컨베이어를 돌리지 않는다. 서버는 amr이
            ! 보내는 "STATUS CONVEYOR_START direction=FWD mode=UNTIL_D2 ..."
            ! 로그(AMR.ino V16)를 보고 AMR이 도착했다는 걸 알며, 그때만
            ! AmrArrived를 보낸다.
            SocketSend srv_client_socket \Str:="ReadyForPickup\0D\0A";
            WaitForAmrArrived;
            PulseDO\PLength := 0.2, do06_Body_Delivery;
            SocketSend srv_client_socket \Str:="ConveyDone\0D\0A";
        ENDFOR
        ProcessNum := 0;

        ! Role: Signal the central admin server that this work cycle just finished -
        !       sent back over the same connection the "Start" command arrived on.
        ! ??: ? ??? ?? ????? ?? - "Start" ??? ??? ? ?? ????
        !       ??? ????.
        SocketSend srv_client_socket \Str:="Done";
    ENDPROC

    ! Blocks on the SAME connector connection (a second SocketReceive call,
    ! made from here instead of the outer Run_Socket_Server loop) until the
    ! central server sends "AmrArrived" - i.e. the server has seen AMR's own
    ! STATUS CONVEYOR_START(FWD) report for this station. \Time:= keeps this
    ! from being a truly unbounded wait; ERR_SOCK_TIMEOUT just retries (same
    ! pattern as Run_Socket_Server's own ERROR handler).
    PROC WaitForAmrArrived()
        VAR string incoming;
        VAR bool arrived := FALSE;

        WHILE NOT arrived DO
            SocketReceive srv_client_socket \Str:=incoming \Time:=300;
            IF (StrLen(incoming) >= 10) THEN
                IF StrPart(incoming, 1, 10) = "AmrArrived" THEN
                    arrived := TRUE;
                ENDIF
            ENDIF
        ENDWHILE

        ERROR
            IF ERRNO = ERR_SOCK_TIMEOUT THEN
                RETRY;
            ENDIF
    ENDPROC

    Proc Press_Process()
        ! v14: 수동으로 확인(디버깅)할 때 WaitDI가 신호 없이 몇 초 이상 걸리면
        ! RobotStudio가 "시뮬레이션 값을 실행하시겠습니까?" 창을 띄우는데,
        ! 이 창이 떠 있는 동안에는 실제 펄스 신호가 들어와도 못 받는 문제가
        ! 있었음. 그래서 20초 타임아웃을 추가 - 20초가 지나도 신호가 없으면
        ! PLC는 이미 실행했는데 신호만 못 받은 것으로 보고 자동으로 다음
        ! 공정으로 넘어감.
        ! 기존 코드(무한 대기, 타임아웃 없음):
        !   PulseDO\PLength := 0.2, do02_Press_Start;
        !   WaitDI di02_PLC_Press_Done,1;
        VAR bool bPressTimeOut := FALSE;
        PulseDO\PLength := 0.2, do02_Press_Start;
        WaitDI di02_PLC_Press_Done, 1 \MaxTime:=20 \TimeFlag:=bPressTimeOut;
        IF bPressTimeOut THEN
            TPWrite "Press 완료 신호 20초 초과 - PLC 실행 완료로 간주하고 다음 공정 진행";
        ENDIF
    ENDPROC

    Proc Upper_Body_Process()
        ! v14: Body_Docking_Off 대기에 10초 타임아웃 추가 - 아래 di04 관련
        ! 주석 참고.
        VAR bool bDockingOffTimeOut := FALSE;

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
        ! v14: 수동 확인 중 대화창 문제(위 Press_Process 주석 참고)로 10초
        ! 타임아웃 추가 - 10초가 지나도 신호가 없으면 PLC는 이미 실행했는데
        ! 신호만 못 받은 것으로 보고 자동으로 다음 공정으로 넘어감.
        ! 기존 코드(무한 대기, 타임아웃 없음): WaitDI di04_PLC_Body_Docking_Off, 1;
        WaitDI di04_PLC_Body_Docking_Off, 1 \MaxTime:=10 \TimeFlag:=bDockingOffTimeOut;
        IF bDockingOffTimeOut THEN
            TPWrite "Body Docking Off 신호 10초 초과 - PLC 실행 완료로 간주하고 다음 공정 진행";
        ENDIF

        MoveL p_Body_Assembly, v_slow, z30, tool1;
        MoveL p_Body_Docking, v_fast, z30, tool1;
        
        MoveL Offs(p_Body_Center,0,0,20), v_fast, z30, tool1;
        MoveL Offs(p_Body_Center,0,0,-15), v_fast, z30, tool1;
        MoveL p_Body_Center_Down, v_slow, fine, tool1;
        Dripper_Off;
        MoveJ Offs(p_Body_Center,0,0,30), v_fast, z30, tool1;

    ENDPROC

    Proc Welding_Process()
        MoveJ p_Tool_PickUp, v_fast, z30, tool1;
        MoveL p_Tool_PickDown, v_slow, fine, tool1;
        Dripper_On;
        MoveL Offs(p_Tool_PickUp,0,0,45), v_fast, fine, tool1;
        MoveL p_Welding_Start, v_fast, z30, tool1;
        
        MoveL p_Point1 , v_slow, z10, tool1;
        MoveL p_point2, v10, z10, tool1;
        MoveL p_Change_angle_2to3, v10, z10, tool1;
        MoveL p_point3 , v10, z10, tool1;
        MoveL p_point4 , v10, z10, tool1;
        MoveL p_Change_angle_4to5, v10, z10, tool1;
        MoveL p_point5 , v10, z10, tool1;
        
        MoveL p_ChangePoint, v_fast, z50, tool1;
        MoveL p_ChangePoint_Under, v_fast, z50, tool1;
        
        MoveL p_point6, v150, z10, tool1;
        MoveL p_Point7, v10, z10, tool1;
        MoveL p_Change_angle_7to8, v10, z10, tool1;
        MoveL p_Point8, v10, z10, tool1;
        MoveL p_Change_angle_8to9, v10, z10, tool1;
        MoveL p_Point9, v10, z10, tool1;
        MoveL p_Point10, v10, z10, tool1;
        
        MoveL p_ChangePoint, v_fast, z50, tool1;
        
        ! ?? ??
        ! ? ???? ?? ! ??, ??? ??? ?? ! ?? ???? 3~4
        
        ! ?? ?? ??
        MoveL p_Point_Left, v_fast, z50, tool1;
        MoveL p_Point_Left_1, v10, z50, tool1;
        MoveL p_Point_Left_2, v10, z10, tool1;
        MoveL p_Point_Left_3, v10, z10, tool1;
        MoveL p_Point_Left_4, v10, z10, tool1;
        
        MoveL p_Point_Left_5, v10, z10, tool1;
        MoveL p_Point_Left_6, v10, z10, tool1;
        MoveL p_Point_Left_7, v100, z50, tool1;
        

        ! ?? -> ?? ??
        MoveL p_ChangePoint, v_fast, z50, tool1; 
        
        ! ??? ?? ??
        MoveL p_Point_Right, v_fast, z50, tool1;
        MoveL p_Point_Right_1, v10, z50, tool1;
        MoveL p_Point_Right_2, v10, z10, tool1;
        MoveL p_Point_Right_3, v10, z10, tool1;
        MoveL p_Point_Right_4, v10, z10, tool1;
        
        MoveL p_Point_Right_5, v10, z10, tool1;
        MoveL p_Point_Right_6, v10, z10, tool1;
        MoveL p_Point_Right_7, v100, z50, tool1;





        
        ! ??? -> ?? ??
        MoveL p_ChangePoint, v_fast, z50, tool1; 
        
        ! ?? ?? ?

        MoveL Offs(p_Tool_PickUp,0,0,45), v_fast, z30, tool1;
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
        MoveL p_Body_Center, v_fast, z30, tool1;
        MoveL p_Body_Center_Down, v_slow, fine, tool1;
        Dripper_On;
        MoveL p_Body_Center, v_slow, fine, tool1;
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


