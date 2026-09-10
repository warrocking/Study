MODULE MainModule
    
    TASK PERS tooldata tool1:=[TRUE,[[0,0,110],[1,0,0,0]],[0.2,[0,0,50],[1,0,0,0],0,0,0]];
    
    CONST robtarget p10:=[[-33.37,-467.64,17.01],[2.31631E-07,-0.0652829,-0.997867,-1.14154E-05],[-2,-1,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget p20:=[[427.50,-418.02,467.46],[2.40732E-06,0.0652894,0.997866,7.06127E-06],[-1,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget p30:=[[608.63,-466.49,348.59],[2.07859E-05,-0.065286,-0.997867,-2.22305E-05],[-1,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget pHome:=[[399.02,-9.59,322.72],[1.9983E-06,0.0652577,0.997868,4.89162E-06],[-1,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    
    CONST robtarget p_pickup:=[[608.63,-466.49,348.59],[2.07859E-05,-0.065286,-0.997867,-2.22305E-05],[-1,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget p_metal:=[[608.63,-466.49,348.59],[2.07859E-05,-0.065286,-0.997867,-2.22305E-05],[-1,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget p_bpla:=[[608.63,-466.49,348.59],[2.07859E-05,-0.065286,-0.997867,-2.22305E-05],[-1,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget p_wpla:=[[608.63,-466.49,348.59],[2.07859E-05,-0.065286,-0.997867,-2.22305E-05],[-1,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    VAR num works :=0;
    VAR intnum interrupt_sign :=0;
    
    
    PROC main()
        CONNECT interrupt_sign WITH E_STOP;
        ! interrupt_sign 인터럽트 번호를 아래 TRAP E_STOP과 연결 (0702.mod엔 없는 인터럽트 방식 긴급정지)
        
        ISignalDI di09_interrupt, high, interrupt_sign;
        ! di09_interrupt가 1이 되면 interrupt_sign 인터럽트가 발생하도록 등록
        
        IWatch interrupt_sign;
        ! 등록한 인터럽트 감시 시작 (이 줄이 없으면 실제로 동작 안 함)
        
        AccSet 1, 1;
        
        
        MoveJ pHome, v200, fine, tool1;
        !??
        WHILE TRUE DO
            IF di02_ma_none = 1 AND di07_running = 0 THEN
                put_ma;
                PulseDO\PLength:=0.2, do02_plcstart;
            ENDIF
            
            IF di06_arrive = 1 THEN
                pick_up;
                
                IF di03_metal = 1 THEN
                    works :=1;
                ELSEIF di04_plastic_black = 1 THEN
                    works :=2;
                ELSEIF di05_plastic_white = 1 THEN
                    works :=3;
                ENDIF
                PulseDO\PLength:=0.2, do03_reset_jedg;
                
                IF works = 1 THEN
                    metal_box;
                ELSEIF works = 2 THEN
                    black_box;
                ELSEIF works = 3 THEN
                    white_box;
                ENDIF
                works :=0;
            ENDIF
        ENDWHILE
        
        
    ENDPROC
    
    TRAP E_STOP ! di09_interrupt 발생 시 실행 위치와 상관없이 즉시 호출되는 트랩
        VAR robtarget e_stop_pos; ! 정지된 순간의 위치를 저장할 변수
        StopMove; ! 진행 중이던 이동을 즉시 정지
        StorePath; ! 정지 시점의 이동 경로 저장 (복원용)
        e_stop_pos:= CRobT(); ! 정지된 현재 위치 좌표 기억
        MoveJ phome, v200, z50, tool1; ! 홈 위치로 대피 (0702.mod의 EmergencyStop과 동일하게 원점 복귀)
        WaitDI di08_restart,1; ! 재시작 신호 대기 (0702.mod와 동일한 신호)
        MoveL e_stop_pos, v100, fine, tool1; ! 재시작 후 정지했던 원래 위치로 복귀
        RestoPath; ! 저장해둔 이동 경로 복원
        StartMove; ! 복원한 경로에서 이동 재개 (0702.mod엔 없는 자동 복귀/재개 기능)
    ENDTRAP
    
    
    
    PROC put_ma()
        VAR num x_pos := 0;
        VAR num y_pos := 0;
        
        FOR cty FROM 1 TO 2 DO
            FOR ctx FROM 1 TO 3 DO
                MoveJ offs(p10,x_pos,y_pos,100), v200, z20, tool1;
                MoveL offs(p10,x_pos,y_pos,0), v50, fine, tool1;
                
                grip_on;
                
                MoveL offs(p10,x_pos,y_pos,100), v200, z20, tool1;
                
                MoveJ p20, v200, z20, tool1;
                
                MoveJ offs(p30,0,0,100), v200, z20, tool1;
                MoveL offs(p30,0,0,0), v50, fine, tool1;
                
                grip_off;
                MoveL offs(p30,0,0,100), v200, z20, tool1;
                MoveJ p20, v200, z20, tool1;
                
                ! 원료 없음 감지 시 부저만 울리고 그 자리에서 대기
                ! (0702.mod의 EmergencyStop과 달리 홈 위치로 이동하지 않음)
                IF di02_ma_none = 1 THEN
                    PulseDO\PLength:=0.2, do04_buzzer;
                    WaitDI di08_restart,1;
                    RETURN;
                ENDIF
                
                x_pos := x_pos+110;
            ENDFOR
            x_pos := 0;
            y_pos := y_pos-110;
        ENDFOR
        
    ENDPROC
    
    PROC grip_on()
        PulseDO\PLength:=0.2, do00_grip_on;
        WaitDI di00_grip_on_sen,1;
        WaitTime 0.2;
    ENDPROC
    
    PROC grip_off()
        PulseDO\PLength:=0.2, do01_grip_off;
        WaitDI di01_grip_off_sen,1;
        WaitTime 0.2;
    ENDPROC
    
    PROC pick_up()
        MoveJ offs(p_pickup,x_pos,y_pos,100), v200, z20, tool1;
        MoveL offs(p_pickup,x_pos,y_pos,0), v50, fine, tool1;
        
        grip_on;
        
        MoveL offs(p_pickup,x_pos,y_pos,100), v200, z20, tool1;
    ENDPROC
    
    PROC metal_box()
        MoveJ offs(p_metal,x_pos,y_pos,100), v200, z20, tool1;
        MoveL offs(p_metal,x_pos,y_pos,0), v50, fine, tool1;
        
        grip_off;
        
        MoveL offs(p_metal,x_pos,y_pos,100), v200, z20, tool1;
    ENDPROC
    
    PROC black_box()
        MoveJ offs(p_bpla,x_pos,y_pos,100), v200, z20, tool1;
        MoveL offs(p_bpla,x_pos,y_pos,0), v50, fine, tool1;
        
        grip_off;
        
        MoveL offs(p_bpla,x_pos,y_pos,100), v200, z20, tool1;
    ENDPROC
    
    PROC white_box()
        MoveJ offs(p_wpla,x_pos,y_pos,100), v200, z20, tool1;
        MoveL offs(p_wpla,x_pos,y_pos,0), v50, fine, tool1;
        
        grip_off;
        
        MoveL offs(p_wpla,x_pos,y_pos,100), v200, z20, tool1;
    ENDPROC
    
    
ENDMODULE