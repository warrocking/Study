MODULE MainModule
    TASK PERS tooldata tool1:=[TRUE,[[3.25653,-2.2499,106.27],[1,0,0,0]],[0.2,[0,0,50],[1,0,0,0],0,0,0]];

    
    VAR robtarget p_repository_first :=[[0,0,0],[1,0,0,0],[0,0,0,0],[9E9,9E9,9E9,9E9,9E9,9E9]];
    VAR robtarget p_repository_secend :=[[0,0,0],[1,0,0,0],[0,0,0,0],[9E9,9E9,9E9,9E9,9E9,9E9]];
    VAR robtarget p_repository_third :=[[0,0,0],[1,0,0,0],[0,0,0,0],[9E9,9E9,9E9,9E9,9E9,9E9]];


    VAR robtarget p_repository :=[[-43.81,576.39,111.28],[0.392055,-0.56705,0.580331,0.433546],[1,0,0,1],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]]; ! ?? ?? ?? (?? ??) 
    VAR robtarget p_repository_1 :=[[-41.09,599.69,103.48],[0.392066,-0.567035,0.580326,0.433564],[1,0,0,1],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]]; ! ?? ?? ?? 1 (?? ??)
    VAR robtarget p_repository_2 :=[[0,0,0],[1,0,0,0],[0,0,0,0],[9E9,9E9,9E9,9E9,9E9,9E9]]; ! ?? ?? ?? 1 (?? ??)
    VAR robtarget p_repository_3 :=[[0,0,0],[1,0,0,0],[0,0,0,0],[9E9,9E9,9E9,9E9,9E9,9E9]]; ! ?? ?? ?? 1 (?? ??)
    VAR robtarget p_repository_4 :=[[0,0,0],[1,0,0,0],[0,0,0,0],[9E9,9E9,9E9,9E9,9E9,9E9]]; ! ?? ?? ?? 1 (?? ??)
    VAR robtarget p_repository_5 :=[[0,0,0],[1,0,0,0],[0,0,0,0],[9E9,9E9,9E9,9E9,9E9,9E9]]; ! ?? ?? ?? 1 (?? ??)
    VAR robtarget p_repository_6 :=[[0,0,0],[1,0,0,0],[0,0,0,0],[9E9,9E9,9E9,9E9,9E9,9E9]]; ! ?? ?? ?? 1 (?? ??)
    VAR robtarget p_repository_7 :=[[0,0,0],[1,0,0,0],[0,0,0,0],[9E9,9E9,9E9,9E9,9E9,9E9]]; ! ?? ?? ?? 1 (?? ??)
    VAR robtarget p_repository_8 :=[[0,0,0],[1,0,0,0],[0,0,0,0],[9E9,9E9,9E9,9E9,9E9,9E9]]; ! ?? ?? ?? 1 (?? ??)
    VAR robtarget p_repository_9 :=[[0,0,0],[1,0,0,0],[0,0,0,0],[9E9,9E9,9E9,9E9,9E9,9E9]]; ! ?? ?? ?? 1 (?? ??)

    VAR robtarget p_sensor := [[0,0,0],[1,0,0,0],[0,0,0,0],[9E9,9E9,9E9,9E9,9E9,9E9]]; ! ?? ?? (?? ??)
    VAR robtarget p_sensor_under := [[0,0,0],[1,0,0,0],[0,0,0,0],[9E9,9E9,9E9,9E9,9E9,9E9]]; ! ?? ?? ?? (?? ??)

    VAR robtarget p_Genuine := [[0,0,0],[1,0,0,0],[0,0,0,0],[9E9,9E9,9E9,9E9,9E9,9E9]]; ! ?? ?? ?? (?? ??)
    VAR robtarget p_Defective := [[0,0,0],[1,0,0,0],[0,0,0,0],[9E9,9E9,9E9,9E9,9E9,9E9]]; ! ?? ?? ?? (?? ??)
    VAR robtarget p_Processed := [[0,0,0],[1,0,0,0],[0,0,0,0],[9E9,9E9,9E9,9E9,9E9,9E9]]; ! ?? ?? ?? (?? ??)

    VAR robtarget p_Unprocessed_Magazine_up := [[0,0,0],[1,0,0,0],[0,0,0,0],[9E9,9E9,9E9,9E9,9E9,9E9]]; ! ??? ?? ?? (?? ??)
    VAR robtarget p_Unprocessed_Magazine_down := [[0,0,0],[1,0,0,0],[0,0,0,0],[9E9,9E9,9E9,9E9,9E9,9E9]]; ! ??? ?? ?? (?? ??)

    VAR robtarget p_Processed_pickup_up := [[0,0,0],[1,0,0,0],[0,0,0,0],[9E9,9E9,9E9,9E9,9E9,9E9]]; ! ?? ?? ?? ?? (?? ??)
    VAR robtarget p_Processed_pickup_down := [[0,0,0],[1,0,0,0],[0,0,0,0],[9E9,9E9,9E9,9E9,9E9,9E9]]; ! ?? ?? ?? ?? (?? ??)

    VAR robtarget p_AGV_pickup_up := [[0,0,0],[1,0,0,0],[0,0,0,0],[9E9,9E9,9E9,9E9,9E9,9E9]]; ! AGV ?? ?? (?? ??)
    VAR robtarget p_AGV_pickup_down := [[0,0,0],[1,0,0,0],[0,0,0,0],[9E9,9E9,9E9,9E9,9E9,9E9]]; ! AGV ?? ?? (?? ??)


    VAR speeddata v_moveSpeed_fast := v200;
    VAR speeddata v_moveSpeed_slow := v50;
    var num count := 0;

    PROC Main()
        AccSet 1,1;                                     
        MoveL p_repository, v_moveSpeed_fast, fine, tool1;      
        MoveL p_repository_1, v_moveSpeed_fast, fine, tool1;      
        MoveL p_repository_2, v_moveSpeed_fast, fine, tool1;
        MoveL p_repository_3, v_moveSpeed_fast, fine, tool1;
        MoveL p_repository_4, v_moveSpeed_fast, fine, tool1;
        MoveL p_repository_5, v_moveSpeed_fast, fine, tool1;
        MoveL p_repository_6, v_moveSpeed_fast, fine, tool1;
        MoveL p_repository_7, v_moveSpeed_fast, fine, tool1;
        MoveL p_repository_8, v_moveSpeed_fast, fine, tool1;
        movel p_repository_9, v_moveSpeed_fast, fine, tool1;

        movel p_sensor, v_moveSpeed_fast, fine, tool1;
        movel p_sensor_under, v_moveSpeed_fast, fine, tool1;

        movel p_Genuine, v_moveSpeed_fast, fine, tool1;
        movel p_Defective, v_moveSpeed_fast, fine, tool1;
        movel p_Processed, v_moveSpeed_fast, fine, tool1;

        movel p_Unprocessed_Magazine_down, v_moveSpeed_fast, fine, tool1;
        movel p_Unprocessed_Magazine_up, v_moveSpeed_fast, fine, tool1;
        movel p_Processed_pickup_down, v_moveSpeed_fast, fine, tool1;
        movel p_Processed_pickup_up, v_moveSpeed_fast, fine, tool1;
        movel p_AGV_pickup_down, v_moveSpeed_fast, fine, tool1;
        movel p_AGV_pickup_up, v_moveSpeed_fast, fine, tool1;


        
        IF di20_repositoryReady = 1 THEN
            WHILE True DO
                PickupRepository(count);
                count := count + 1;

            
                if di20_repositoryReady = 1 THEN
                    if di22_goodProduct = 1 THEN
                        MoveL Offs(p_Genuine,0,0,0), v_moveSpeed_fast, z20, tool1;
                        MoveL offs(p_Genuine,0, 0, -100), v_moveSpeed_slow, fine, tool1;
                        Grip_off;

                    elseif di23_defectiveProduct = 1 THEN
                        MoveL Offs(p_Defective,0,0,0), v_moveSpeed_fast, z20, tool1;
                        MoveL offs(p_Defective,0, 0, -100), v_moveSpeed_slow, fine, tool1;
                        Grip_off;
                    elseif di24_unprocessedProduct = 1 THEN
                        MoveL offs(p_Unprocessed_Magazine_up,0,0,0), v_moveSpeed_fast, z20, tool1;
                        MoveL offs(p_Unprocessed_Magazine_down,0, 0, -100), v_moveSpeed_slow, fine, tool1;
                        Grip_off;
                    ENDIF




                ENDIF  

                !IF  = 0 THEN
                    ! while ? ??
                !    movel p_AGV_pickup_up, v_moveSpeed_fast, fine, tool1;

                !ENDIF  

                




            ENDWHILE

        else
            MoveL Offs(p_AGV_pickup_up,0,0,0), v_moveSpeed_fast, fine, tool1;
            ! ?? ?? ?? ???.

        ENDIF

    ENDPROC

    PROC PickupRepository(num count)
        var num x_pos := 35;
        var num y_pos := 75;

        var num diff := 0;

        VAR num position_x := 0;
        VAR num position_y := 0;
        position_x := count/3;
        position_y := count MOD 3;

        MoveL Offs(p_repository, position_x*x_pos, position_y*y_pos, 0), v_moveSpeed_fast, z20, tool1;        
        MoveL Offs(p_repository, position_x*x_pos, position_y*y_pos, diff), v_moveSpeed_slow, fine, tool1;
        Grip_on;
        MoveL Offs(p_repository, position_x*x_pos, position_y*y_pos, 0), v_moveSpeed_slow, fine, tool1;
        MoveToSensor;
    ENDPROC




    PROC MoveToSensor()
        MoveL Offs(p_sensor, 0, 0, 0), v_moveSpeed_fast, fine, tool1;
        MoveL offs(p_sensor_under, 0, 0, 0), v_moveSpeed_slow, fine, tool1;
        PulseDO\PLength:=0.2, do05_sensor;        
        
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