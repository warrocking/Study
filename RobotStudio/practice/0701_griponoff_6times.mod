MODULE MainModule
    TASK PERS tooldata tool1:=[TRUE,[[3.25653,-2.2499,106.27],[1,0,0,0]],[0.2,[0,0,50],[1,0,0,0],0,0,0]];
    CONST robtarget p10:=[[334.20,-11.32,525.02],[9.04603E-06,0.270992,-0.962582,5.28781E-06],[-1,-1,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget p30:=[[212.79,-579.55,18.20],[0.000286847,0.0895321,-0.995983,-0.00130719],[-1,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget p20:=[[210.93,-467.30,20.23],[0.00051597,0.153581,0.988135,0.00154666],[-1,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget p50:=[[101.52,-470.00,16.01],[0.000292501,0.0895438,-0.995982,-0.00135767],[-1,-1,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget p40:=[[101.52,-579.52,18.59],[0.000290565,0.0895324,-0.995983,-0.00135831],[-1,-1,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget p70:=[[-9.05,-580.97,18.66],[0.000288419,0.0895356,-0.995983,-0.00135524],[-2,-1,-2,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget p60:=[[-9.05,-470.01,16.95],[0.000285944,0.0895363,-0.995983,-0.00134158],[-2,-1,-2,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget p90:=[[413.36,1.13,645.95],[0.512531,-0.48714,0.512549,-0.487135],[0,0,-1,1],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget p80:=[[413.36,1.13,645.95],[0.512531,-0.48714,0.512549,-0.487135],[0,0,-1,1],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST jointtarget jpos10:=[[90,0,0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    VAR num user_num:=0;
    CONST robtarget p110:=[[212.80,-579.57,107.54],[0.000278942,0.0895328,-0.995983,-0.00127572],[-1,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget p100:=[[210.93,-467.29,181.94],[0.000519007,0.153543,0.988141,0.00155278],[-1,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    VAR num user_moyang:=0;
    CONST robtarget p130:=[[101.52,-470.02,98.37],[0.000286735,0.0895395,-0.995982,-0.00132206],[-1,-1,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget p120:=[[101.53,-579.55,140.18],[0.000285993,0.0895315,-0.995983,-0.00131725],[-1,-1,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget p150:=[[-9.05,-580.97,160.07],[0.000293245,0.08955,-0.995981,-0.00133306],[-2,-1,-2,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget p140:=[[-9.05,-470.04,123.13],[0.000292124,0.0895336,-0.995983,-0.00130197],[-2,-1,-2,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget p170:=[[460.93,-254.55,720.18],[0.639774,-0.318278,0.630744,-0.302574],[-1,-1,0,1],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget p160:=[[460.93,-254.55,720.18],[0.639774,-0.318278,0.630744,-0.302574],[-1,-1,0,1],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget p200:=[[603.00,-437.66,521.01],[0.000337117,0.153518,0.988144,0.00163893],[-1,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget p210:=[[605.16,-437.68,330.77],[0.000347656,0.153537,0.988142,0.00162846],[-1,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    
    !p10 : Home(Origin) location
    !p20 : Plate object1 location
    !p30 : Plate object2 location
    !p40 : Plate object3 location
    !p50 : Plate object4 location
    !p60 : Plate object5 location
    !p70 : Plate object6 location
    
    !p100 : Plate object1 midle location
    !p110 : Plate object2 midle location
    !p120 : Plate object3 midle location
    !p130 : Plate object4 midle location
    !p140 : Plate object5 midle location
    !p150 : Plate object6 midle location
    
    !p200 : Megazine midle route location
    !p210 : Megazine input location
    VAR robtarget p_array1{6}:=[p20, p30, p40, p50, p60, p70];
    VAR robtarget p_array2{6}:=[p100, p110, p120, p130, p140, p150];
    PROC main()
        WHILE index = 6 DO
            IF di02_ma_none = 1THEN
            pickup_put;
        ELSE
            WaitTime := 5;
        ENDIF
    ENDWHILE
ENDPROC

PROC pickup_put()
    gripOff;
    MOVEJ p10, v200, fine, tool1;
    MoveL p20, v200, fine, tool1;
    MoveJ Offs(p20, 0, 0, -30), v50, fine, tool1;
    gripOn;
    MoveJ Offs(p20, 0, 0, +30), v50, fine, tool1;
    MoveL p30, v50, fine, tool1;
    MoveL Offs(p30, 0, 0, -30), v50, fine, tool1;
    gripOff;
    MoveL Offs(p30, 0, 0, +30), v50, fine, tool1;
    
ENDPROC


PROC gripOn()
    PulseDO\PLength:=0.2, do01_grip_on;
    WaitDI do01_grip_on, 1;
ENDPROC
PROC gripOff()
    PulseDO\PLength:=0.2, do01_grip_off;
    WaitDI do01_grip_off, 1;
ENDPROC


ENDMODULE