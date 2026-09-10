MODULE MainModule
    
    TASK PERS tooldata tool1:=[TRUE,[[0,0,110],[1,0,0,0]],[0.2,[0,0,50],[1,0,0,0],0,0,0]];
    
    ! abb home point
    CONST robtarget p_point:=[[340,-5,160],[0.0,0.0,-1.0,0.0],[-1,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    
    ! abb pickup raw place / 1 : (0, 0, 0) / 2 : ( , , ) / 3 : ( , , ) / 4 : ( , , ) / 5 : ( , , ) / 6 : ( , , )
    CONST robtarget p_pickup_raw                :=[[213.73,-466.16,39.55],[3.14844E-05,-3.63293E-05,-1,-6.89212E-05],[-1,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    ! ??? offc(p_pickup_raw, ?, ? , ?) ??? ?? ?? ?? ?.
    CONST robtarget p_pickup_raw_temporary1     :=[[213.73,-466.16,40.13],[2.94219E-05,-4.47796E-05,-1,-6.75883E-05],[-1,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget p_pickup_raw_temporary2     :=[[104.48,-466.51,40.74],[0.0,0.0,-1.0,0.0],[-1,-1,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget p_pickup_raw_temporary3     :=[[-4.29,-467.17,40.91],[0.0,0.0,-1.0,0.0],[-2,-1,-2,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget p_pickup_raw_temporary4     :=[[216.45,-575.61,40.37],[0.0,0.0,-1.0,0.0],[-1,-1,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget p_pickup_raw_temporary5     :=[[103.56,-577.21,40.98],[0.0,0.0,-1.0,0.0],[-1,-1,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget p_pickup_raw_temporary6     :=[[-4.53,-577.28,40.45],[0.000204855,-5.02679E-06,-1,-0.000155955],[-1,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    
    !CONST robtarget p_pickup_raw_temporary7     :=[[605.53,-439.28,40.45],[0.000204855,-5.02679E-06,-1,-0.000155955],[-1,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    
    ! abb drop raw place
    CONST robtarget p_drop_raw                  :=[[606.33,-438.25,434.09],[8.35411E-05,9.55021E-06,-1,-6.83441E-05],[-1,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget p_drop_raw_temporary        :=[[606.33,-438.25,330.55],[9.67099E-05,1.08391E-05,-1,-7.72665E-05],[-1,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    
    ! abb pickup sorted place
    CONST robtarget p_pickup_sorted             :=[[610.42,9.32,174.55],[0.000202736,4.15373E-05,-1,3.19925E-06],[0,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    ! ?? ? ?? ?.
    CONST robtarget p_pickup_sorted_temporary1  :=[[610.46,9.66,135.93],[0.000215641,4.44557E-05,-1,4.11293E-06],[0,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    
    ! abb drop sorted place / 1 : (0, 0, 0) / 2 : ( , , ) / 3 : ( , , )
    CONST robtarget p_drop_sorted               :=[[302.76,-467.40,400.35],[0.0,0.0,-1.0,0.0],[-1,-1,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    ! metal box : ??? p_drop_sorted? ??? (0, 0, 0) ?? ???? ? ??.
    CONST robtarget p_drop_sorted_temporary1     :=[[359.42,-98.82,104.68],[0.000133037,2.77034E-05,-1,4.50672E-06],[-1,-1,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    ! plastic black box : ??? p_drop_sorted? ??? (0, 0, 0) ?? ???? ? ??.
    CONST robtarget p_drop_sorted_temporary2     :=[[359.32,-11.11,104.68],[0.000134435,1.3173E-05,-1,3.8947E-06],[-1,-1,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    ! plastic white box : ??? p_drop_sorted? ??? (0, 0, 0) ?? ???? ? ??.
    CONST robtarget p_drop_sorted_temporary3     :=[[359.31,74.45,104.68],[0.000147833,9.23906E-07,-1,6.14298E-06],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    
    
    ! speed parameter
    CONST speeddata v_moveSpeed_fast := v150;
    CONST speeddata v_moveSpeed_slow := v30;
    
    PROC main()
        !moveL p_point, v_moveSpeed_slow, fine, tool1;
        
        !moveL p_pickup_raw, v100, fine, tool1;
        
        !moveL p_pickup_raw_temporary1, v_moveSpeed_slow, fine, tool1;
        !moveL p_pickup_raw_temporary2, v_moveSpeed_slow, fine, tool1;
        !moveL p_pickup_raw_temporary3, v_moveSpeed_slow, fine, tool1;
        !moveL p_pickup_raw_temporary4, v_moveSpeed_slow, fine, tool1;
        !moveL p_pickup_raw_temporary5, v_moveSpeed_slow, fine, tool1;
        !moveL p_pickup_raw_temporary6, v_moveSpeed_slow, fine, tool1;
        
        !moveL p_drop_raw, v_moveSpeed_slow, fine, tool1;
        !moveL p_drop_raw_temporary, v_moveSpeed_slow, fine, tool1;
        
        
        !moveL p_pickup_sorted, v_moveSpeed_slow, fine, tool1;
        !moveL p_pickup_sorted_temporary1, v_moveSpeed_slow, fine, tool1;
        
        !moveL p_drop_sorted, v_moveSpeed_slow, fine, tool1;
        !moveL p_drop_sorted_temporary1, v_moveSpeed_slow, fine, tool1;
        !moveL p_drop_sorted_temporary2, v_moveSpeed_slow, fine, tool1;
        !moveL p_drop_sorted_temporary3, v_moveSpeed_slow, fine, tool1;
        
        
        AccSet 1, 1;
        MoveJ p_point, v_moveSpeed_fast, fine, tool1;
        
        WHILE TRUE DO
            
            IF di02_ma_none =1 THEN
                Pickup_Raw;
                PulseDO\PLength:=0.2, do02_plcstart;
            ENDIF
            
            IF di06_arrive = 1 THEN
                Pickup_Sorted;
                
                IF di03_metal = 1 THEN
                    Drop_sorted 1;
                ELSEIF di04_plastic_black = 1 THEN
                    Drop_sorted 2;
                ELSEIF di05_plastic_white = 1 THEN
                    Drop_sorted 3;
                ENDIF
                
                PulseDO\PLength:=0.2, do03_reset_jedg;
                
            ENDIF
        ENDWHILE
        ! ?? ????
        MoveJ p_point, v_moveSpeed_fast, fine, tool1;
    ENDPROC
    
    
    ! movement function
    PROC Pickup_Raw()
        
        VAR num pointX := 0;
        VAR num pointY := 0;
        
        VAR num add_pointX := -110;
        VAR num add_pointY := -110;
        
        VAR num position_high := -25;
        
        FOR moveY FROM 1 TO 2 DO
            FOR moveX FROM 1 TO 3 DO
                MoveJ offs(p_pickup_raw, pointX+add_pointX*(moveX-1), pointY+add_pointY*(moveY-1), 0), v_moveSpeed_fast, fine, tool1;
                MoveJ offs(p_pickup_raw, pointX+add_pointX*(moveX-1), pointY+add_pointY*(moveY-1), position_high), v_moveSpeed_fast, fine, tool1;
                GripOn;
                MoveJ offs(p_pickup_raw, pointX+add_pointX*(moveX-1), pointY+add_pointY*(moveY-1), 0), v_moveSpeed_fast, fine, tool1;
                Drop_Raw;
                
                IF di02_ma_none = 1 THEN
                    EmergencyStop;
                    RETURN;
                ENDIF
                
            ENDFOR
        ENDFOR
    ENDPROC
    
    PROC Drop_Raw()
        VAR num posision_z := -60;
        MoveJ offs(p_drop_raw, 0, 0, 0), v_moveSpeed_fast, fine, tool1;
        MoveJ offs(p_drop_raw, 0, 0, posision_z), v_moveSpeed_slow, fine, tool1;
        GripOff;
        MoveJ offs(p_drop_raw, 0, 0, 0), v_moveSpeed_slow, fine, tool1;
    ENDPROC
    
    PROC Pickup_Sorted()
        MoveL p_pickup_sorted, v_moveSpeed_fast, fine, tool1;
        MoveL offs(p_pickup_sorted, 0, 0, -45), v_moveSpeed_slow, fine, tool1;
        GripOn;
        MoveL offs(p_pickup_sorted, 0, 0, 0), v_moveSpeed_slow, fine, tool1;
        
        
    ENDPROC
    
    PROC Drop_Sorted(num sortedType)
        ! metal
        if sortedType = 1 THEN
            MoveJ p_drop_sorted_temporary1, v_moveSpeed_fast, fine, tool1;
            !MoveL offs(p_drop_sorted_temporary1, 0, 0, -50), v_moveSpeed_slow, fine, tool1;
            GripOff;
            ! plastic black
        ELSEIF sortedType = 2 THEN
            MoveJ p_drop_sorted_temporary2, v_moveSpeed_fast, fine, tool1;
            !MoveL offs(p_drop_sorted_temporary2, 0, 0, -50), v_moveSpeed_slow, fine, tool1;
            GripOff;
            ! plastic white
        ELSEIF sortedType = 3 THEN
            MoveJ p_drop_sorted_temporary3, v_moveSpeed_fast, fine, tool1;
            !MoveL offs(p_drop_sorted_temporary3, 0, 0, -50), v_moveSpeed_slow, fine, tool1;
            GripOff;
        ENDIF
    ENDPROC
    
    ! movement grip function
    PROC GripOn()
        PulseDO\PLength:=0.2,do00_grip_on;
        WaitDI di00_grip_on_sen,1;
        WaitTime 0.2;
    ENDPROC
    
    PROC GripOff()
        PulseDO\PLength:=0.2,do01_grip_off;
        WaitDI di01_grip_off_sen,1;
        WaitTime 0.2;
    ENDPROC
    
    PROC EmergencyStop()
        MoveJ p_point, v_moveSpeed_fast, fine, tool1;
        PulseDO\PLength:=0.2, do04_buzzer;
        waitDI di08_restart, 1;
        RETURN;
    ENDPROC
    
ENDMODULE