MODULE MainModule
    TASK PERS tooldata tool1:=[TRUE,[[3.25653,-2.2499,106.27],[1,0,0,0]],[0.2,[0,0,50],[1,0,0,0],0,0,0]];

    
    VAR robtarget p_target_up := [[342.30,-38.16,327.52],[1.20614E-05,0.456804,-0.889567,-5.42704E-06],[-1,-1,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    VAR robtarget p_target_down := [[342.30,-38.16,327.52],[1.20614E-05,0.456804,-0.889567,-5.42704E-06],[-1,-1,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    
    
    VAR robtarget p_targetZone_up := [[342.30,-38.16,327.52],[1.20614E-05,0.456804,-0.889567,-5.42704E-06],[-1,-1,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    VAR robtarget p_targetZone_down := [[342.30,-38.16,327.52],[1.20614E-05,0.456804,-0.889567,-5.42704E-06],[-1,-1,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    
    
    
    VAR robtarget p_tier_1_up := [[342.30,-38.16,327.52],[1.20614E-05,0.456804,-0.889567,-5.42704E-06],[-1,-1,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    VAR robtarget p_tier_1_down := [[342.30,-38.16,327.52],[1.20614E-05,0.456804,-0.889567,-5.42704E-06],[-1,-1,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    VAR robtarget p_tier_2_up := [[342.30,-38.16,327.52],[1.20614E-05,0.456804,-0.889567,-5.42704E-06],[-1,-1,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    VAR robtarget p_tier_2_down := [[342.30,-38.16,327.52],[1.20614E-05,0.456804,-0.889567,-5.42704E-06],[-1,-1,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    VAR robtarget p_tier_3_up := [[342.30,-38.16,327.52],[1.20614E-05,0.456804,-0.889567,-5.42704E-06],[-1,-1,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    VAR robtarget p_tier_3_down := [[342.30,-38.16,327.52],[1.20614E-05,0.456804,-0.889567,-5.42704E-06],[-1,-1,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    VAR robtarget p_tier_4_up := [[342.30,-38.16,327.52],[1.20614E-05,0.456804,-0.889567,-5.42704E-06],[-1,-1,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    VAR robtarget p_tier_4_down := [[342.30,-38.16,327.52],[1.20614E-05,0.456804,-0.889567,-5.42704E-06],[-1,-1,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    
    PROC Main()
        Grip_Off;
        MoveL p_target_up, v200, fine, tool1;
        MoveL p_target_down, v50, fine, tool1;
        
        Grip_On;
        MoveL p_target_up, v50, fine, tool1;
        
        MoveL p_targetZone_up, v200, fine, tool1;
        MoveL p_targetZone_down, v50, fine, tool1;
        Grip_Off;

        

    ENDPROC


    PROC Grip_On()
        PulseDO\PLength:=0.2, do00_grip_on;
        WaitDI di00_grip_on_sen,1;
        WaitTime 0.1;
    ENDPROC

    PROC Grip_Off()
        PulseDO\PLength:=0.2, do01_grip_off;
        WaitDI di01_grip_off_sen,1;
        WaitTime 0.1;
    ENDPROC

ENDMODULE