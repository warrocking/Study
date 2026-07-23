MODULE MainModule
    TASK PERS tooldata tool1:=[TRUE,[[3.25653,-2.2499,106.27],[1,0,0,0]],[0.2,[0,0,50],[1,0,0,0],0,0,0]];

    ! ===== Server / cycle state =====
    VAR socketdev server_socket;        ! TCP server socket (listens for the PC client)
    VAR socketdev client_socket;        ! Socket of the currently connected PC client
    VAR string received_string;         ! Last text command received from the client
    VAR bool keep_listening := TRUE;    ! Keeps Main()'s server loop running forever
    VAR bool ck_bit := TRUE;            ! TRUE while this client connection is active; "end" sets it FALSE
    VAR bool processRunning := TRUE;    ! TRUE while one Run_Production_Cycle pass is still in progress
    VAR intnum estop_interrupt;         ! Interrupt handle bound to the e-stop input (di09_interrupt)

    ! ===== Conveyor 1 -> press =====
    VAR robtarget p_home := [[342.30,-38.16,327.52],[1.20614E-05,0.456804,-0.889567,-5.42704E-06],[-1,-1,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    VAR robtarget p_conveyor1 :=[[245.59,-581.05,207.18],[1.14514E-05,0.45812,-0.88889,0.000379034],[-1,0,-2,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    VAR robtarget p_conveyor1_down:=[[244.10,-580.92,166.51],[1.70431E-06,-0.458097,0.888902,-0.000177303],[-1,0,-2,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    VAR robtarget p_press :=[[410.97,-49.06,83.91],[0.000263737,0.456792,-0.889573,-0.00017235],[-1,-1,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    VAR robtarget p_press_down :=[[410.98,-49.06,59.91],[0.000240741,0.45679,-0.889574,-0.000156984],[-1,-1,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    ! ===== Conveyor 2: cooled tire moves here after the press =====
    VAR robtarget p_conveyor2_Start :=[[607.20,-442.00,409.61],[0.000144954,0.458218,-0.88884,-0.000278745],[-1,-1,-2,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    VAR robtarget p_conveyor2_Start_down :=[[607.21,-442.00,344.33],[0.000128478,0.458225,-0.888836,-0.000242942],[-1,-1,-2,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    VAR robtarget p_conveyor2_End :=[[609.42,4.54,177.17],[0.000288402,0.458226,-0.888835,-0.000295341],[0,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    VAR robtarget p_conveyor2_End_down :=[[609.39,4.54,137.08],[0.000340193,0.458234,-0.888832,-0.000317474],[0,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    VAR speeddata v_moveSpeed_fast := v200;    ! travel speed for empty / long moves
    VAR speeddata v_moveSpeed_slow := v50;     ! careful speed for pick/place moves

    ! ===== Air cooling station =====
    ! p_air and p_air_down share the same orientation (only Z differs) - straight top-down approach.
    VAR robtarget p_air := [[521.58,94.20,306.28],[5.14586E-05,0.0188754,-0.999822,2.56678E-06],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    VAR robtarget p_air_down := [[521.59,94.19,270.57],[2.53311E-05,0.0188524,-0.999822,-3.20394E-06],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    VAR robtarget p_whiteTrash := [[7.14,-410.29,164.21],[0.000501902,-0.212669,0.977124,-2.51796E-05],[-1,0,-2,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    ! ===== Conveyor 3: only good (black) tires go here, toward tool1/tool2 =====
    VAR robtarget p_conveyor3_Start := [[432.71,359.00,129.98],[0.00107571,-0.978491,-0.206032,-0.0102408],[0,-1,-2,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    VAR robtarget p_conveyor3_Start_down := [[432.72,359.01,104.51],[0.0010881,-0.978494,-0.206015,-0.0102613],[0,-1,-2,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    ! ===== Tool rack (tool1 = bead coating tool, tool2 = spray tool) =====
    VAR robtarget p_toolBox := [[-220.83,607.62,386.27],[0.000310841,-0.992461,-0.122563,0.000233515],[1,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    VAR robtarget p_toolBox_wayPoint:= [[-59.20,413.56,316.00],[0.000192288,-0.992462,-0.122551,0.000226474],[1,0,-2,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];     ! transit point between the tool rack and the rest of the cell

    VAR robtarget p_tool1 := [[-201.25,610.55,326.17],[0.00029616,-0.992458,-0.122587,0.00022763],[1,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    VAR robtarget p_tool1_down := [[-201.25,610.54,266.40],[0.000267857,-0.992458,-0.122581,0.000223518],[1,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    VAR robtarget p_tool2 := [[-250.27,609.87,301.00],[0.000235177,-0.992458,-0.122585,0.000212353],[1,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    VAR robtarget p_tool2_down := [[-250.28,609.88,266.70],[0.000258815,-0.992457,-0.122591,0.000215434],[1,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    ! tool1 operation: hold tool1 against the tire and spin axis 6 by 180 deg to coat the bead
    VAR robtarget p_tool1_operation := [[266.18,358.33,279.50],[0.000152707,-0.985788,-0.167995,0.0002393],[0,0,-2,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    VAR robtarget p_tool1_operation_down := [[266.18,358.34,162.04],[0.000146445,-0.985655,-0.168774,0.000243667],[0,0,-2,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    VAR robtarget p_tool1_operation_down_180 :=[[260.48,353.06,162.03],[0.000273152,-0.0287263,-0.999587,-8.33304E-05],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];    ! same spot as p_tool1_operation_down, axis 6 turned 180 deg

    ! tool2 operation: hold tool2 against the tire and spray in a circle (see di25 block / MoveC below)
    VAR robtarget p_tool2_operation := [[30.08,352.22,245.56],[0.000649711,0.979908,-0.199446,-0.000633723],[0,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    VAR robtarget p_tool2_operation_down := [[30.07,352.21,168.79],[0.00067461,0.979908,-0.199448,-0.000629812],[0,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    VAR robtarget p_conveyor3_End := [[-292.64,345.81,138.85],[0.010078,-0.473537,0.880715,-0.00166355],[1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    VAR robtarget p_conveyor3_End_down := [[-292.63,345.80,100.27],[0.0100835,-0.473539,0.880714,-0.00169463],[1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    ! Count = tires currently sitting in the 4 storage boxes (0-3 while filling; back to 0 once all
    ! 4 are moved to the end box). Count = 0 also means Main() needs a fresh "start" command.
    VAR num Count := 0;

    ! ===== Air cooling reorientation sweep points =====
    ! 8 points around p_air_down, tilt 25 deg, 45 deg apart. Same XYZ as p_air_down - pure rotation,
    ! the TCP position never moves. (Chosen after testing 5/10/15/20/30 deg and MoveJ vs MoveL.)
    VAR robtarget p_air_move1:= [[521.60,94.20,270.59],[0.030062,0.025947,-0.977402,0.207627],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    VAR robtarget p_air_move2:= [[521.60,94.20,270.59],[0.184174,0.025084,-0.971490,0.147167],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    VAR robtarget p_air_move3:= [[521.60,94.20,270.59],[0.250396,0.020293,-0.967920,-0.004559],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    VAR robtarget p_air_move4:= [[521.60,94.20,270.59],[0.189936,0.014381,-0.968783,-0.158671],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    VAR robtarget p_air_move5:= [[521.60,94.20,270.59],[0.038211,0.010811,-0.973574,-0.224894],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    VAR robtarget p_air_move6:= [[521.60,94.20,270.59],[-0.115902,0.011674,-0.979485,-0.164434],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    VAR robtarget p_air_move7:= [[521.60,94.20,270.59],[-0.182124,0.016465,-0.983055,-0.012708],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    VAR robtarget p_air_move8:= [[521.60,94.20,270.59],[-0.121664,0.022377,-0.982192,0.141405],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    ! ===== Tire storage: 4 boxes fill up one at a time, then all 4 move to the end box together =====
    ! p_repository / _down / _up: shared point used to grab all 4 filled boxes as one batch
    VAR robtarget p_repository := [[-428.96,314.71,144.50],[0.000471623,-0.363008,0.931785,-0.0015633],[1,0,1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    VAR robtarget p_repository_down := [[-428.95,314.70,41.99],[0.000494594,-0.363009,0.931784,-0.00160134],[1,0,1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    VAR robtarget p_repository_up := [[-428.33,316.57,385.27],[0.000355322,-0.36321,0.931706,-0.00166084],[1,0,1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    ! individual box slots 1-4, one tire dropped in each (Count picks which one, see di26 below)
    VAR robtarget p_repository1:= [[-450.55,299.35,48.12],[0.00105081,-0.978495,-0.206013,-0.0102878],[1,-1,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    VAR robtarget p_repository1_down:= [[-450.55,299.34,14.28],[0.00103909,-0.978497,-0.206002,-0.0102968],[1,-1,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    VAR robtarget p_repository2:= [[-450.11,347.64,53.19],[0.00083725,0.999731,0.0231684,9.80167E-05],[1,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    VAR robtarget p_repository2_down:= [[-450.10,347.63,10.02],[0.000852907,0.999731,0.0231692,0.000117714],[1,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    VAR robtarget p_repository3:= [[-400.13,300.38,56.31],[0.000860401,0.999731,0.0231697,0.000125038],[1,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    VAR robtarget p_repository3_down:= [[-400.12,300.37,9.53],[0.00087719,0.999731,0.0231717,0.00014718],[1,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    VAR robtarget p_repository4:= [[-403.82,342.47,48.30],[0.000466965,-0.363014,0.931782,-0.00155946],[1,0,1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    VAR robtarget p_repository4_down:= [[-403.81,342.46,15.04],[0.00048093,-0.363013,0.931783,-0.00158591],[1,0,1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    ! batch drop-off point, reached once all 4 boxes are picked up together
    VAR robtarget p_EndBox := [[-87.19,-387.47,264.81],[0.000373537,-0.363168,0.931722,-0.00167997],[-2,0,-2,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    VAR robtarget p_EndBox_down := [[-87.19,-387.47,166.75],[0.000377551,-0.363162,0.931724,-0.00166614],[-2,0,-2,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    ! transit waypoints on the way from p_repository_up to p_EndBox (collision-free path around the cell)
    VAR robtarget p_repository_Waypoint1:=[[353.83,316.58,385.26],[0.000379553,-0.363207,0.931707,-0.00165671],[0,-1,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    VAR robtarget p_repository_Waypoint2:=[[353.84,-334.17,385.25],[0.000382817,-0.363206,0.931707,-0.00167823],[-1,-1,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    VAR robtarget p_repository_Waypoint3:=[[-51.66,-381.08,385.24],[0.000379558,-0.363208,0.931707,-0.00166893],[-2,0,-2,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    VAR robtarget p_EndBox_waypoint := [[361.19,-228.04,264.81],[0.000380923,-0.363157,0.931726,-0.00169341],[-1,-1,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];    ! transit point leaving the end box area (used by TEST_MOVE)
    VAR num sprayRadius := 10;          ! radius (mm) of the tool2 spray circle around p_tool2_operation_down
    VAR num count_White := 0;           ! counts defective (white) tires seen; picks the CASE in the di23 block below
    VAR robtarget p_tool2_down10:=[[-59.20,413.56,316.00],[0.000190789,-0.992463,-0.122548,0.000226438],[1,0,-2,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];    ! not referenced anywhere currently

    PROC Main()

        IDelete estop_interrupt;                          ! clear any old interrupt binding first
        CONNECT estop_interrupt WITH Trap_EStop;          ! route the interrupt to Trap_EStop
        ISignalDI di09_interrupt, 1, estop_interrupt;     ! fire it when di09_interrupt goes to 1
        IWatch estop_interrupt;                           ! start watching for that signal

        AccSet 1,1;                                       ! full acceleration
        SocketCreate server_socket;                       ! create the TCP server socket
        SocketBind server_socket, "192.168.3.3", 5000;    ! bind to this IP/port
        SocketListen server_socket;                       ! start listening for a client
        MOVEL p_home, v_moveSpeed_fast, z30, tool1;

        WHILE keep_listening DO                            ! server loop: runs forever
            SocketAccept server_socket, client_socket;      ! block here until a PC client connects
            ck_bit := TRUE;                                 ! reset "keep talking to this client" flag

            IF Count > 0 THEN                                ! a batch was already in progress
                Run_Continuous_Production;                     ! -> resume automatically, no "start" needed
            ENDIF

            WHILE ck_bit DO                                  ! keep talking to this client
                SocketReceive client_socket \Str:=received_string; ! wait for one text command
                TPWrite "Client wrote - " + received_string;         ! show it on the teach pendant (debug)
                SocketSend client_socket \Str:="Message acknowledged"; ! acknowledge receipt

                IF received_string = "start" THEN                  ! "start" command
                    Run_Continuous_Production;
                ENDIF

                IF received_string = "end" THEN                  ! "end" command
                    ck_bit := FALSE;                              ! stop talking to this client
                ENDIF

                received_string := "";                           ! clear the buffer for the next command
            ENDWHILE

            SocketClose client_socket;                          ! client said "end" -> close this connection
        ENDWHILE

        SocketClose server_socket;                            ! (never reached in normal operation)

        ERROR                                                 ! ---- error handler for Main ----
        IF ERRNO=ERR_SOCK_TIMEOUT THEN                        ! a socket call timed out
            RETRY;                                              ! just retry the same instruction
        ELSEIF ERRNO=ERR_SOCK_CLOSED THEN                     ! connection was dropped
            SocketClose server_socket;                           ! close everything and rebuild the server
            SocketClose client_socket;
            SocketCreate server_socket;
            SocketBind server_socket, "192.168.3.3", 5000;
            SocketListen server_socket;
            SocketAccept server_socket, client_socket;           ! wait for the client to reconnect
            ck_bit := TRUE;                                       ! resume the inner command loop
            RETRY;                                                ! go back to where the error happened
        ELSE                                                   ! any other error
            TPWrite "ERRNO = "\Num:=ERRNO;                        ! log it on the teach pendant
            Stop;                                                ! and stop the program
        ENDIF

    ENDPROC
    
    
    ! =====================================================================
    ! Run_Continuous_Production - runs one cycle, then keeps running more
    ! automatically (no new "start" needed) as long as Count > 0 and the
    ! client hasn't sent "end".
    ! =====================================================================
    PROC Run_Continuous_Production()
        Run_Production_Cycle;

        WHILE Count > 0 AND ck_bit DO
            Check_For_End_Command;
            IF ck_bit THEN
                Run_Production_Cycle;
            ENDIF
        ENDWHILE
    ENDPROC


    ! =====================================================================
    ! Run_Production_Cycle - one full pass through the tire process.
    ! Each IF block below fires on one PLC digital input and does one
    ! stage. The WHILE loop keeps checking di21-di26 until either di26
    ! (storage complete) or a defective tire ends the cycle.
    !
    ! Stage order: di21 conveyor1->press, di22 press->cooling->conveyor2,
    ! di23 conveyor2->color sort->conveyor3/trash, di24 tool1 bead coating,
    ! di25 tool2 spray, di26 conveyor3->storage box->(every 4th) end box.
    ! =====================================================================
    PROC Run_Production_Cycle()
        processRunning := TRUE;
        PulseDO\PLength:=0.2, do05_1st_con_Start;         ! tell the PLC to start conveyor 1
        WaitTime 0.2;
        WHILE processRunning DO
            IF di21_1st_Con_End= 1 THEN
                ! di21: tire reached the end of conveyor 1 -> pick it up and load the press
                ! move ( home -> conveyor_1)
                MoveL p_conveyor1, v_moveSpeed_fast, z30, tool1;
                MoveL p_conveyor1_down, v_moveSpeed_slow, fine, tool1;
                Grip_on;                                        ! grab the tire
                MoveL p_conveyor1, v_moveSpeed_slow, fine, tool1;
                !move ( conveyor_1 -> Press)
                Movel p_home, v_moveSpeed_fast, z30, tool1;
                Movel p_press, v_moveSpeed_fast, z30, tool1;
                Movel p_press_down, v_moveSpeed_slow, fine, tool1;
                Grip_off;                                       ! drop the tire into the press
                movel p_press, v_moveSpeed_slow, fine, tool1;
                !!Signal Shoot
                PulseDO\PLength:=0.2, do06_pressStart;           ! tell the PLC to start pressing
            ENDIF

            IF di22_PressEnd = 1 THEN
                ! di22: press finished -> pick the pressed tire up, cool it, hand it to conveyor 2
                ! move (home -> press)
                MoveL p_press, v_moveSpeed_fast, z30, tool1;
                MoveL p_press_down, v_moveSpeed_slow, fine, tool1;
                Grip_on;                                         ! grab the tire from the press
                movel p_press, v_moveSpeed_slow, fine, tool1;
                MoveL p_home, v_moveSpeed_fast, z30, tool1;
                moveL p_air, v_moveSpeed_fast, z30, tool1;        ! approach the cooling station
                moveL p_air_down, v_moveSpeed_slow, fine, tool1;

                Reorient_CoolingSweep;                            ! rotate the tire through the air jets
                WaitTime 0.2;

                !moveL p_air, v_moveSpeed_slow, z30, tool1;
                moveL p_air, v_moveSpeed_slow, fine, tool1;
                !moveL p_home, v_moveSpeed_fast, z30, tool1;
                movel p_conveyor2_Start, v_moveSpeed_fast,z30, tool1;
                moveL p_conveyor2_Start_down, v_moveSpeed_slow, fine, tool1;
                Grip_off;                                        ! place the tire on conveyor 2
                movel p_conveyor2_Start, v_moveSpeed_slow, fine, tool1;

                ! Signal shoot
                PulseDO\PLength:=0.2, do08_2nd_Con_Start;         ! tell the PLC to start conveyor 2
                movel p_home, v_moveSpeed_fast, z30, tool1;
                WaitTime 0.2;
            ENDIF

            IF di23_2nd_Con_End = 1 THEN
                ! di23: tire reached the end of conveyor 2 -> pick it up, check the color sensor
                MoveL p_conveyor2_End, v_moveSpeed_fast, z30, tool1;
                movel p_conveyor2_End_down, v_moveSpeed_slow, fine, tool1;
                Grip_on;
                MoveL p_conveyor2_End, v_moveSpeed_slow, fine, tool1;
                MoveL p_home, v_moveSpeed_fast, z30, tool1;

                ! black = good tire -> conveyor 3 toward tool1/tool2
                ! white = defective -> straight to trash
                ! here to trash move code
                IF di04_plastic_black = 1 THEN
                    MoveL p_conveyor3_Start, v_moveSpeed_fast, z30, tool1;
                    MoveL p_conveyor3_Start_down, v_moveSpeed_slow, fine, tool1;
                    Grip_off;
                    MoveL p_conveyor3_Start, v_moveSpeed_slow, fine, tool1;
                    PulseDO\PLength:= 0.2, do03_reset_jedg;          ! reset the color-sensor judgement signal
                    PulseDO\PLength:=0.2, do09_3rd_Con_Start;        ! tell the PLC to start conveyor 3
                    MoveL p_toolBox_wayPoint, v_moveSpeed_fast, z30, tool1;

                ELSEIF di05_plastic_white = 1 THEN
                    ! count_White selects which CASE runs below - only CASE 1 (the first
                    ! defective tire) actually drops the tire in the trash right now;
                    ! CASE 2/3/4 are empty placeholders (not implemented yet), so a 2nd+
                    ! defective tire stays gripped and is never released here.
                    count_White := count_White +1;
                    TEST count_White
                    CASE 1:
                        MoveL p_whiteTrash, v_moveSpeed_fast, fine, tool1;
                        Grip_off;                                    ! drop the defective tire in the trash
                        MoveL p_whiteTrash, v_moveSpeed_fast, fine, tool1;
                    CASE 2:
                    CASE 3:
                    CASE 4:
                    ENDTEST

                    ! ends the whole production cycle for this defective tire (processRunning
                    ! := FALSE below) - a new "start"/continuous-loop pass will be needed
                    ! next, same as a normal di26 storage-complete ending.
                    PulseDO\PLength:=0.2, do05_1st_con_Start;         ! restart conveyor 1 for the next tire
                    PulseDo\PLength:=0.2, do13_ProcEnd;
                    MoveL p_home, v_moveSpeed_fast, fine, tool1;
                    processRunning := FALSE;
                    PulseDO\PLength:= 0.2, do03_reset_jedg;           ! reset the color-sensor judgement signal
                ENDIF
            ENDIF

            ! tool1 operation start
            IF di24_tool1_start = 1 THEN
                ! di24: tool1 station - pick up tool1 and coat the inside of the tire bead
                MoveJ p_toolBox_wayPoint, v_moveSpeed_fast, z30, tool1;
                MoveJ p_toolBox, v_moveSpeed_fast, z30, tool1;
                MoveL p_tool1, v_moveSpeed_fast, z30, tool1;
                MoveL p_tool1_down, v_moveSpeed_slow, fine, tool1;
                Grip_on;                                        ! pick up tool1
                MoveL p_tool1, v_moveSpeed_slow, fine, tool1;
                MoveL p_toolBox_wayPoint, v_moveSpeed_fast, z30, tool1;
                MoveL p_tool1_operation, v_moveSpeed_fast, z30, tool1;

                ! tool1 operation motion start
                MoveL p_tool1_operation_down, v_moveSpeed_slow, z30, tool1;
                ! MoveJ here (not MoveL): position doesn't change, only axis 6 spins 180 deg -
                ! MoveJ avoids the wrist-singularity jump that MoveL hits on a pure in-place turn
                MoveJ p_tool1_operation_down_180, v_moveSpeed_slow, z30, tool1;
                WaitTime 0.3;
                MoveJ p_tool1_operation_down, v_moveSpeed_slow, z30, tool1;
                MoveL p_tool1_operation, v_moveSpeed_slow, fine, tool1;
                PulseDO\PLength:=0.2, do10_tool1_End;!! Signal shoot
                ! tool1 operation motion end

                MoveL p_toolBox_wayPoint, v_moveSpeed_fast, z30, tool1;
                MoveL p_toolBox, v_moveSpeed_fast, z30, tool1;
                MoveL p_tool1, v_moveSpeed_fast, z30, tool1;
                MoveL p_tool1_down, v_moveSpeed_slow, fine, tool1;
                Grip_off;                                       ! put tool1 back
                MoveL p_tool1, v_moveSpeed_slow, fine, tool1;
                MoveL p_toolBox, v_moveSpeed_fast, z30, tool1;
            ENDIF

            ! tool 2 operation start
            IF di25_tool2_Start = 1 THEN
                ! di25: tool2 station - pick up tool2 and spray a circle on the tire
                MoveJ p_toolBox, v_moveSpeed_fast, z30, tool1;
                MoveL p_tool2, v_moveSpeed_fast, z30, tool1;
                MoveL p_tool2_down, v_moveSpeed_slow, fine, tool1;
                Grip_on;                                        ! pick up tool2
                MoveL p_tool2, v_moveSpeed_slow, fine, tool1;
                MoveL p_toolBox, v_moveSpeed_slow, fine, tool1;   ! extra clearance waypoint leaving the rack
                MoveL p_toolBox_wayPoint, v_moveSpeed_fast, z30, tool1;
                MoveL p_tool2_operation, v_moveSpeed_fast, z30, tool1;

                ! tool2 operation motion start
                ! draws one full 10mm-radius circle around p_tool2_operation_down while
                ! spraying. A single MoveC can't sweep a full 360 deg, so two MoveC arcs
                ! (each a half circle) are chained together instead. z1 (not z10) blends the
                ! join between the two halves so the small circle isn't cut across.
                MoveL p_tool2_operation_down, v_moveSpeed_slow, fine, tool1;
                SetDO do11_Tool2_Start, 1;
                MoveL RelTool(p_tool2_operation_down, sprayRadius, 0, 0), v_moveSpeed_slow, fine, tool1;                  ! go to the start point on the circle (0 deg)
                MoveC RelTool(p_tool2_operation_down, 0, sprayRadius, 0), RelTool(p_tool2_operation_down, -sprayRadius, 0, 0), v_moveSpeed_slow, z1, tool1;   ! first half: 0 -> 180 deg
                MoveC RelTool(p_tool2_operation_down, 0, -sprayRadius, 0), RelTool(p_tool2_operation_down, sprayRadius, 0, 0), v_moveSpeed_slow, fine, tool1; ! second half: 180 -> 360 deg (back to start)

                SetDO do11_Tool2_Start, 0;
                MoveL p_tool2_operation, v_moveSpeed_slow, fine, tool1;
                PulseDO\PLength:=0.2, do12_tool2_End;! Signal shoot
                ! tool2 operation motion end

                MoveL p_toolBox_wayPoint, v_moveSpeed_fast, z30, tool1;
                MoveL p_toolBox, v_moveSpeed_fast, fine, tool1;
                MoveL p_tool2, v_moveSpeed_fast, fine, tool1;
                MoveL p_tool2_down, v_moveSpeed_slow, fine, tool1;
                Grip_off;                                       ! put tool2 back
                MoveL p_tool2, v_moveSpeed_slow, fine, tool1;
                MoveJ p_toolBox, v_moveSpeed_fast, z30, tool1;
            ENDIF

            IF di26_Store_Move = 1 THEN
                ! di26: finished tire reached the end of conveyor 3 -> put it in a storage box.
                ! Count (0-3) picks which of the 4 boxes gets this tire. Once box 4 is filled
                ! (Count reaches 4), all 4 boxes are carried together to the end box and Count
                ! resets to 0 so the next batch starts filling box 1 again.

                !Temporary code
                MoveJ p_toolBox_wayPoint, v_moveSpeed_fast, z30, tool1;
                !Temporary code

                MoveJ p_conveyor3_End, v_moveSpeed_fast, z30, tool1;
                MoveL p_conveyor3_End_down, v_moveSpeed_slow, fine, tool1;
                Grip_on;                                        ! pick up the finished tire
                MoveL p_conveyor3_End, v_moveSpeed_slow, fine, tool1;
                MoveL p_repository, v_moveSpeed_fast, z30, tool1;
                Test Count
                CASE 0:
                    Count := Count + 1;
                    MoveL Offs(p_repository, -25, -25, 0), v_moveSpeed_fast, z10, tool1;   ! corner waypoint near box 1
                    MoveL p_repository1, v_moveSpeed_fast, z30, tool1;
                    MoveL p_repository1_down, v_moveSpeed_slow, fine, tool1;
                    Grip_off;                                    ! drop the tire into box 1
                    MoveL p_repository1, v_moveSpeed_slow, fine, tool1;

                CASE 1:
                    Count := Count + 1;
                    MoveL Offs(p_repository, -25, +25, 0), v_moveSpeed_fast, z10, tool1;   ! corner waypoint near box 2
                    MoveL p_repository2, v_moveSpeed_fast, z30, tool1;
                    MoveL p_repository2_down, v_moveSpeed_slow, fine, tool1;
                    Grip_off;                                    ! drop the tire into box 2
                    MoveL p_repository2, v_moveSpeed_slow, fine, tool1;

                CASE 2:
                    Count := Count + 1;
                    MoveL Offs(p_repository, +25, -25, 0), v_moveSpeed_fast, z10, tool1;   ! corner waypoint near box 3
                    MoveL p_repository3, v_moveSpeed_fast, z30, tool1;
                    MoveL p_repository3_down, v_moveSpeed_slow, fine, tool1;
                    Grip_off;                                    ! drop the tire into box 3
                    MoveL p_repository3, v_moveSpeed_slow, fine, tool1;

                CASE 3:
                    Count := Count + 1;                          ! becomes 4 -> triggers the end-box move below
                    MoveL Offs(p_repository, +25, +25, 0), v_moveSpeed_fast, z10, tool1;   ! corner waypoint near box 4
                    MoveL p_repository4, v_moveSpeed_fast, z30, tool1;
                    MoveL p_repository4_down, v_moveSpeed_slow, fine, tool1;
                    Grip_off;                                    ! drop the tire into box 4 (last one)
                    MoveL p_repository4, v_moveSpeed_slow, fine, tool1;
                EndTest

                MoveL p_repository, v_moveSpeed_fast, fine, tool1;

                if Count = 4 THEN
                    ! all 4 boxes are full - grab them as a batch (latch gripper: Grip_on = open
                    ! jaws, Grip_off = close jaws and catch the boxes) and carry them to the end box
                    Grip_on;
                    MoveL p_repository_down, v_moveSpeed_slow, fine, tool1;
                    Grip_off;                                    ! close jaws -> latch onto the boxes
                    MoveL p_repository_up, v_moveSpeed_slow, z200, tool1;
                    MoveL p_repository_Waypoint1, v_moveSpeed_fast, z200, tool1;
                    MoveL p_repository_Waypoint2, v_moveSpeed_fast, z200, tool1;
                    MoveL p_repository_Waypoint3, v_moveSpeed_fast, z200, tool1;
                    !Stopover
                    MoveL p_EndBox, v_moveSpeed_fast, z30, tool1;
                    MoveL p_EndBox_down, v_moveSpeed_slow, fine, tool1;
                    Grip_on;                                    ! open jaws -> release the boxes here
                    MoveL p_EndBox, v_moveSpeed_slow, fine, tool1;
                    count := 0;                                 ! batch done - start refilling box 1 next time
                ELSE
                    MoveJ p_toolBox_wayPoint, v_moveSpeed_fast, z30, tool1;
                ENDIF

                MoveJ p_home, v_moveSpeed_fast, z30, tool1;
                Grip_off;                                     ! shared reset for both branches above (already
                                                               ! open after CASE 0-2; closes the latch after CASE 3)
                processRunning := FALSE;                  ! this tire is fully done -> end the cycle
                PulseDO\PLength := 0.2, do05_1st_con_Start;   ! restart conveyor 1 (also done at the top of the next cycle)
                PulseDO\PLength := 0.2, do13_ProcEnd;         ! tell the PLC the cycle is complete
            ENDIF
        ENDWHILE
    ENDPROC


    PROC TEST_MOVE()
        MoveL p_toolBox_wayPoint, v50, z30, tool1;

        MoveL p_toolBox, v50, z30, tool1;
        MoveL p_tool1, v50, z30, tool1;
        MoveL p_tool1_down, v50, z30, tool1;
        MoveL p_tool1, v50, z30, tool1;
        MoveL p_toolBox, v50, z30, tool1;
        MoveL p_toolBox_wayPoint, v50, z30, tool1;
        MoveL p_tool1_operation, v50, z30, tool1;
        MoveL p_tool1_operation_down, v50, z30, tool1;
        MoveJ p_tool1_operation_down_180, v50, z30, tool1;
        MoveJ p_tool1_operation_down, v50, z30, tool1;
        MoveL p_tool1_operation, v50, z30, tool1;
        MoveL p_toolBox_wayPoint, v50, z30, tool1;
        MoveL p_toolBox, v50, z30, tool1;
        MoveL p_tool1, v50, z30, tool1;
        MoveL p_tool1_down, v50, z30, tool1;
        MoveL p_tool1, v50, z30, tool1;
        MoveL p_toolBox, v50, z30, tool1;

        MoveL p_toolBox, v50, z30, tool1;
        MoveL p_tool2, v50, z30, tool1;
        MoveL p_tool2_down, v50, z30, tool1;
        MoveL p_tool2, v50, z30, tool1;
        MoveL p_toolBox, v50, z30, tool1;
        MoveL p_toolBox_wayPoint, v50, z30, tool1;

        MoveL p_tool2_operation, v50, z30, tool1;
        MoveL p_tool2_operation_down, v50, z30, tool1;

        ! important
        ! Warning

        MoveL RelTool(p_tool2_operation_down, sprayRadius, 0, 0), v_moveSpeed_slow, fine, tool1;                  ! go to the start point on the circle (0 deg)
        MoveC RelTool(p_tool2_operation_down, 0, sprayRadius, 0), RelTool(p_tool2_operation_down, -sprayRadius, 0, 0), v_moveSpeed_slow, z1, tool1;   ! first half: 0 -> 180 deg
        MoveC RelTool(p_tool2_operation_down, 0, -sprayRadius, 0), RelTool(p_tool2_operation_down, sprayRadius, 0, 0), v_moveSpeed_slow, fine, tool1; ! second half: 180 -> 360 deg (back to start)

        !Waring
        ! Important
        MoveL p_tool2_operation, v50, z30, tool1;
        MoveL p_toolBox_wayPoint, v50, z30, tool1;
        MoveL p_toolBox_wayPoint,v50, z30, tool1;
        MoveL p_toolBox, v50, z30, tool1;
        MoveL p_tool2, v50, z30, tool1;
        MoveL p_tool2_down, v50, z30, tool1;
        MoveL p_tool2, v50, z30, tool1;
        MoveL p_toolBox, v50,  z30, tool1;

        MoveL p_conveyor3_End, v50, z30, tool1;
        MoveL p_conveyor3_End_down, v50, z30, tool1;
        MoveL p_conveyor3_End, v50, z30, tool1;

        MoveL p_repository, v50, z30, tool1;
        MoveL p_repository1, V50, z30, tool1;
        MoveL p_repository1_down, V50, z30, tool1;
        MoveL p_repository1, V50, z30, tool1;

        MoveL p_repository, V50, z30, tool1;
        MoveL p_repository2, V50, z30, tool1;
        MoveL p_repository2_down, V50, z30, tool1;
        MoveL p_repository2, V50, z30, tool1;

        MoveL p_repository, V50, z30, tool1;
        MoveL p_repository3, v_moveSpeed_slow, z30, tool1;
        MoveL p_repository3_down, v_moveSpeed_slow, z30, tool1;
        MoveL p_repository3, v_moveSpeed_slow, z30, tool1;

        MoveL p_repository, V50, z30, tool1;
        MoveL p_repository4, v_moveSpeed_slow, z30, tool1;
        MoveL p_repository4_down, v_moveSpeed_slow, z30, tool1;
        MoveL p_repository4, V50, fine, tool1;
        Grip_on;
        MoveL p_repository, V50, fine, tool1;
        MoveL p_repository_down, v10, fine, tool1;
        WaitTime 0.3;
        Grip_off;
        MoveL p_repository, V50, fine, tool1;
        MoveL p_repository_up, V50, z30, tool1;

        MoveL p_repository_Waypoint1, V50, z30, tool1;
        MoveL p_repository_Waypoint2, V50, z30, tool1;
        MoveL p_repository_Waypoint3, V50, z30, tool1;

        MoveL p_EndBox, V50, z30, tool1;
        MoveL p_EndBox_down, v10, fine, tool1;
        Grip_on;
        MoveL p_EndBox, V50, fine, tool1;
        Movel p_EndBox_waypoint, V50, z30, tool1;

        MoveL Offs(p_repository, -25, -25, 0), v_moveSpeed_fast, z10, tool1;
        MoveL Offs(p_repository, -25, +25, 0), v_moveSpeed_fast, z10, tool1;
        MoveL Offs(p_repository, +25, -25, 0), v_moveSpeed_fast, z10, tool1;
        MoveL Offs(p_repository, +25, +25, 0), v_moveSpeed_fast, z10, tool1;
    ENDPROC


    ! =====================================================================
    ! Check_For_End_Command - during continuous production, briefly (0.5s)
    ! checks if the client sent "end"; on timeout it just returns so
    ! production keeps going without waiting on the socket.
    ! =====================================================================
    PROC Check_For_End_Command()
        VAR string checkString;

        SocketReceive client_socket \Str:=checkString \Time:=0.5;
        IF checkString = "end" THEN
            ck_bit := FALSE;                                   ! "end" received -> stop the continuous loop too
        ENDIF

        ERROR
            IF ERRNO = ERR_SOCK_TIMEOUT THEN
                RETURN;                                          ! nothing received in 0.5s - normal, continue
            ENDIF
    ENDPROC


    

    ! =====================================================================
    ! Reorient_CoolingSweep - at the cooling station (p_air_down), rotates
    ! the tire through 8 tilted orientations while the cooling air is on,
    ! then returns to p_air_down. Exposes different sides of the tire to
    ! the fixed air nozzles. Call only after reaching p_air_down.
    ! =====================================================================
    PROC Reorient_CoolingSweep()
        SetDO do07_CoolingAction, 1;                        ! turn cooling air on

        MoveL p_air_move1, v_moveSpeed_slow, z30, tool1;
        MoveL p_air_move2, v_moveSpeed_slow, z30, tool1;
        MoveL p_air_move3, v_moveSpeed_slow, z30, tool1;
        MoveL p_air_move4, v_moveSpeed_slow, z30, tool1;
        MoveL p_air_move5, v_moveSpeed_slow, z30, tool1;
        MoveL p_air_move6, v_moveSpeed_slow, z30, tool1;
        MoveL p_air_move7, v_moveSpeed_slow, z30, tool1;
        MoveL p_air_move8, v_moveSpeed_slow, z30, tool1;
        MoveL p_air_down, v_moveSpeed_slow, fine, tool1;    ! return to the reference pose

        SetDO do07_CoolingAction, 0;                        ! turn cooling air off
    ENDPROC


    ! =====================================================================
    ! Trap_EStop - fires when di09_interrupt goes 0->1 (e-stop pressed).
    ! Stops the robot, notifies the client, resets Count to 0 (so the next
    ! run needs a fresh "start"), then waits until both the e-stop is
    ! released AND a client is connected before restarting Main() via
    ! ExitCycle.
    ! =====================================================================
    TRAP Trap_EStop
        VAR bool waitingForRecovery;

        StopMove;                                            ! stop all robot motion immediately

        SetDO do07_CoolingAction, 0;                        ! make sure both actuator outputs are off
        SetDO do11_Tool2_Start, 0;

        IF SocketGetStatus(client_socket) = SOCKET_CONNECTED THEN
            SocketSend client_socket \Str:="EMERGENCY STOP";    ! tell the client what happened
        ENDIF

        Count := 0;                                          ! force a fresh "start" after recovery

        waitingForRecovery := TRUE;
        WHILE waitingForRecovery DO
            IF SocketGetStatus(client_socket) <> SOCKET_CONNECTED THEN
                SocketClose client_socket;
                SocketAccept server_socket, client_socket;       ! condition 1: wait for the PC to reconnect
            ENDIF

            IF di09_interrupt = 0 THEN                          ! condition 2: e-stop physically released
                waitingForRecovery := FALSE;                     ! both conditions met -> leave the wait loop
            ELSE
                WaitTime 0.5;                                   ! still in e-stop - check again shortly
            ENDIF
        ENDWHILE

        SocketClose client_socket;                              ! close sockets (Main() rebuilds them)
        SocketClose server_socket;

        ExitCycle;                                             ! restart Main() from the top

        ERROR
            ExitCycle;                                           ! if anything above errors, restart anyway
    ENDTRAP


    PROC Grip_on()
        PulseDO\PLength:=0.2, do00_grip_on;
        WaitDI di00_grip_on_sen,1;
        WaitTime 0.1;
    ENDPROC

    PROC Grip_off()
        PulseDO\PLength:=0.2, do01_grip_off;
        WaitDI di01_grip_off_sen,1;
        WaitTime 0.1;
    ENDPROC

ENDMODULE
