MODULE MainModule

    !------------------------------------------------------------------
    ! 실제 TCP, 그리퍼 무게, 무게중심으로 수정
    !------------------------------------------------------------------
    TASK PERS tooldata tool1:=
    [TRUE,
         [[0,0,110],[1,0,0,0]],
         [0.2,[0,0,50],[1,0,0,0],0,0,0]
    ];


    !------------------------------------------------------------------
    ! 모든 좌표는 임시값
    ! RobotStudio 또는 FlexPendant에서 실제 위치를 티칭해야 함
    !------------------------------------------------------------------

    PERS robtarget pHome:=
        [[0,0,0],[1,0,0,0],[0,0,0,0],
         [9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    ! 컨베이어와 지그 사이를 이동할 때 사용하는 공통 안전 위치
    PERS robtarget pSafe:=
        [[0,0,0],[1,0,0,0],[0,0,0,0],
         [9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];


    !------------------------------------------------------------------
    ! 차체 상부 좌표
    ! 상부 좌우 모두 같은 픽업·컨베이어·스템핑 위치 사용
    ! 조립 위치만 좌측/우측으로 구분
    !------------------------------------------------------------------

    PERS robtarget pUpperPick:=
        [[0,0,0],[1,0,0,0],[0,0,0,0],
         [9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    PERS robtarget pUpperConPlace:=
        [[0,0,0],[1,0,0,0],[0,0,0,0],
         [9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    PERS robtarget pUpperStampPick:=
        [[0,0,0],[1,0,0,0],[0,0,0,0],
         [9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    PERS robtarget pUpperPlaceLeft:=
        [[0,0,0],[1,0,0,0],[0,0,0,0],
         [9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    PERS robtarget pUpperPlaceRight:=
        [[0,0,0],[1,0,0,0],[0,0,0,0],
         [9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];


    !------------------------------------------------------------------
    ! 도어 좌표
    ! 도어 좌우 모두 같은 픽업·컨베이어·스템핑 위치 사용
    ! 조립 위치만 좌측/우측으로 구분
    !------------------------------------------------------------------

    PERS robtarget pDoorPick:=
        [[0,0,0],[1,0,0,0],[0,0,0,0],
         [9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    PERS robtarget pDoorConPlace:=
        [[0,0,0],[1,0,0,0],[0,0,0,0],
         [9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    PERS robtarget pDoorStampPick:=
        [[0,0,0],[1,0,0,0],[0,0,0,0],
         [9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    PERS robtarget pDoorPlaceLeft:=
        [[0,0,0],[1,0,0,0],[0,0,0,0],
         [9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    PERS robtarget pDoorPlaceRight:=
        [[0,0,0],[1,0,0,0],[0,0,0,0],
         [9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];


    !------------------------------------------------------------------
    ! 결합 완료품과 R3 출구 위치
    !------------------------------------------------------------------

    PERS robtarget pUpperFinishedPick:=
        [[0,0,0],[1,0,0,0],[0,0,0,0],
         [9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    PERS robtarget pOutPlace:=
        [[0,0,0],[1,0,0,0],[0,0,0,0],
         [9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];


    !------------------------------------------------------------------
    ! 변수와 시간 제한
    !------------------------------------------------------------------

    VAR num upper_no:=0;
    VAR num door_no:=0;
    VAR bool timeout_flag:=FALSE;

    ! 실제 장비 동작시간을 확인한 뒤 조정
    CONST num T_GRIP:=5;
    CONST num T_PART_READY:=30;
    CONST num T_STAMP:=20;
    CONST num T_WELD:=20;
    CONST num T_AMR_READY:=60;
    CONST num T_AMR_TAKE:=40;
    CONST num T_SIGNAL_OFF:=10;


    !==================================================================
    ! main
    !==================================================================
    PROC main()

        init_output;
        AccSet 1,1;

        WHILE TRUE DO

            MoveJ pHome,v200,fine,tool1;

            ! PLC가 R3 자동차 1대분 시작을 허가할 때까지 대기
            WaitDI di19_cycle_start,1;

            SetDO do10_cycle_done,0;

            ! 자동차 1대분 상부·도어 조립과 AMR 인수
            r3_cycle;

            MoveJ pHome,v200,fine,tool1;

            ! AMR가 실제로 제품을 가져간 뒤에만 완료 출력
            SetDO do10_cycle_done,1;

            ! PLC가 완료를 확인하고 시작 신호를 내릴 때까지 대기
            WaitDI di19_cycle_start,0;

            SetDO do10_cycle_done,0;

        ENDWHILE

    ENDPROC


    !==================================================================
    ! 자동차 1대분 전체 순서
    !==================================================================
    PROC r3_cycle()

        ! 조립 지그가 사용 가능한지 확인
        wait_assembly_ready;

        process_uppers;
        process_doors;
        weld_upper_doors;
        move_upper_to_amr;

    ENDPROC


    !==================================================================
    ! 차체 상부 2개 처리
    !==================================================================
    PROC process_uppers()

        FOR upper_no FROM 1 TO 2 DO

            ! 공통 픽업 위치에 상부 한 개가 들어올 때까지 대기
            wait_upper_ready;

            ! 공급 위치에서 상부 픽업
            MoveJ Offs(pUpperPick,0,0,100),v200,z20,tool1;
            MoveL pUpperPick,v50,fine,tool1;
            grip_on;
            MoveL Offs(pUpperPick,0,0,100),v200,z20,tool1;
            MoveJ pSafe,v200,z20,tool1;

            ! 상부 컨베이어에 적재
            MoveJ Offs(pUpperConPlace,0,0,100),v200,z20,tool1;
            MoveL pUpperConPlace,v50,fine,tool1;
            grip_off;
            MoveL Offs(pUpperConPlace,0,0,100),v200,z20,tool1;
            MoveJ pSafe,v200,z20,tool1;

            ! PLC 상부 스템핑 공정 시작
            SetDO do05_upper_sel,1;
            PulseDO\PLength:=0.2,do02_plcstart;

            ! 스템핑 완료 대기
            wait_upper_done;

            ! 스템핑 완료 위치에서 다시 픽업
            MoveJ Offs(pUpperStampPick,0,0,100),v200,z20,tool1;
            MoveL pUpperStampPick,v50,fine,tool1;
            grip_on;
            MoveL Offs(pUpperStampPick,0,0,100),v200,z20,tool1;
            MoveJ pSafe,v200,z20,tool1;

            ! 첫 번째 상부는 좌측, 두 번째 상부는 우측
            IF upper_no=1 THEN
                place_part pUpperPlaceLeft;
            ELSE
                place_part pUpperPlaceRight;
            ENDIF

            ! PLC 상부 공정 초기화
            PulseDO\PLength:=0.2,do03_reset_jedg;
            SetDO do05_upper_sel,0;

            ! 다음 상부 전에 이전 Ready/Done 신호 OFF 확인
            wait_upper_done_off;
            wait_upper_ready_off;

        ENDFOR

    ENDPROC


    !==================================================================
    ! 도어 2개 처리
    !==================================================================
    PROC process_doors()

        FOR door_no FROM 1 TO 2 DO

            wait_door_ready;

            ! 공통 도어 픽업 위치
            MoveJ Offs(pDoorPick,0,0,100),v200,z20,tool1;
            MoveL pDoorPick,v50,fine,tool1;
            grip_on;
            MoveL Offs(pDoorPick,0,0,100),v200,z20,tool1;
            MoveJ pSafe,v200,z20,tool1;

            ! 도어 컨베이어에 적재
            MoveJ Offs(pDoorConPlace,0,0,100),v200,z20,tool1;
            MoveL pDoorConPlace,v50,fine,tool1;
            grip_off;
            MoveL Offs(pDoorConPlace,0,0,100),v200,z20,tool1;
            MoveJ pSafe,v200,z20,tool1;

            ! PLC 도어 스템핑 공정 시작
            SetDO do06_door_sel,1;
            PulseDO\PLength:=0.2,do02_plcstart;

            wait_door_done;

            ! 스템핑 완료 도어 픽업
            MoveJ Offs(pDoorStampPick,0,0,100),v200,z20,tool1;
            MoveL pDoorStampPick,v50,fine,tool1;
            grip_on;
            MoveL Offs(pDoorStampPick,0,0,100),v200,z20,tool1;
            MoveJ pSafe,v200,z20,tool1;

            ! 첫 번째 도어는 좌측, 두 번째 도어는 우측
            IF door_no=1 THEN
                place_part pDoorPlaceLeft;
            ELSE
                place_part pDoorPlaceRight;
            ENDIF

            PulseDO\PLength:=0.2,do03_reset_jedg;
            SetDO do06_door_sel,0;

            wait_door_done_off;
            wait_door_ready_off;

        ENDFOR

    ENDPROC


    !==================================================================
    ! 상부와 도어 결합 공정
    !==================================================================
    PROC weld_upper_doors()

        ! PLC에서 안착센서, 로봇 이탈, 실린더 원위치를 확인한 뒤
        ! 결합 동작을 실행하도록 구성
        SetDO do07_weld_sel,1;
        PulseDO\PLength:=0.2,do02_plcstart;

        WHILE di15_weld_done=0 DO

            timeout_flag:=FALSE;
            WaitDI di15_weld_done,1
                \MaxTime:=T_WELD
                \TimeFlag:=timeout_flag;

            IF timeout_flag THEN
                TPWrite "R3: 상부·도어 결합 시간 초과";
                PulseDO\PLength:=0.2,do04_buzzer;
                wait_restart;
            ENDIF

        ENDWHILE

        PulseDO\PLength:=0.2,do03_reset_jedg;
        SetDO do07_weld_sel,0;

        wait_weld_done_off;

    ENDPROC


    !==================================================================
    ! 완성 상부를 R3 출구에 놓고 AMR 실제 인수까지 대기
    !==================================================================
    PROC move_upper_to_amr()

        ! 출구가 비어 있고 사용할 수 있는지 확인
        WHILE di16_out_ready=0 DO

            timeout_flag:=FALSE;
            WaitDI di16_out_ready,1
                \MaxTime:=T_PART_READY
                \TimeFlag:=timeout_flag;

            IF timeout_flag THEN
                TPWrite "R3: 완성품 출구 준비 시간 초과";
                PulseDO\PLength:=0.2,do04_buzzer;
                wait_restart;
            ENDIF

        ENDWHILE

        ! 결합 완료품 픽업
        MoveJ Offs(pUpperFinishedPick,0,0,100),v200,z20,tool1;
        MoveL pUpperFinishedPick,v50,fine,tool1;
        grip_on;
        MoveL Offs(pUpperFinishedPick,0,0,100),v200,z20,tool1;
        MoveJ pSafe,v200,z20,tool1;

        ! R3 출구 위치에 적재
        MoveJ Offs(pOutPlace,0,0,100),v200,z20,tool1;
        MoveL pOutPlace,v50,fine,tool1;
        grip_off;
        MoveL Offs(pOutPlace,0,0,100),v200,z20,tool1;
        MoveJ pSafe,v200,z20,tool1;

        ! AMR 호출
        SetDO do09_amr_req,1;

        ! AMR가 R3 위치에 도착하고 적재 준비될 때까지 대기
        WHILE di17_amr_ready=0 DO

            timeout_flag:=FALSE;
            WaitDI di17_amr_ready,1
                \MaxTime:=T_AMR_READY
                \TimeFlag:=timeout_flag;

            IF timeout_flag THEN
                TPWrite "R3: AMR 도착 대기 시간 초과";
                PulseDO\PLength:=0.2,do04_buzzer;
                wait_restart;
            ENDIF

        ENDWHILE

        ! R3 출구 컨베이어/AMR 적재 시작
        SetDO do08_out_sel,1;
        PulseDO\PLength:=0.2,do02_plcstart;

        ! 단순 요청 접수가 아니라 실제 인수 완료까지 대기
        ! PLC ON 조건:
        ! 1) AMR 적재 완료
        ! 2) R3 출구 제품센서 OFF
        ! 3) AMR 도킹 해제 또는 출발
        WHILE di18_amr_done=0 DO

            timeout_flag:=FALSE;
            WaitDI di18_amr_done,1
                \MaxTime:=T_AMR_TAKE
                \TimeFlag:=timeout_flag;

            IF timeout_flag THEN
                TPWrite "R3: AMR 완성품 인수 시간 초과";
                PulseDO\PLength:=0.2,do04_buzzer;
                wait_restart;
            ENDIF

        ENDWHILE

        PulseDO\PLength:=0.2,do03_reset_jedg;

        SetDO do08_out_sel,0;
        SetDO do09_amr_req,0;

        wait_amr_done_off;
        wait_amr_ready_off;

    ENDPROC


    !==================================================================
    ! 전달받은 조립 위치에 부품 내려놓기
    !==================================================================
    PROC place_part(robtarget pPlace)

        MoveJ Offs(pPlace,0,0,100),v200,z20,tool1;
        MoveL pPlace,v40,fine,tool1;
        grip_off;
        MoveL Offs(pPlace,0,0,100),v200,z20,tool1;
        MoveJ pSafe,v200,z20,tool1;

    ENDPROC


    !==================================================================
    ! 그리퍼 닫기
    !==================================================================
    PROC grip_on()

        WHILE di00_grip_on_sen=0 DO

            SetDO do01_grip_off,0;
            PulseDO\PLength:=0.2,do00_grip_on;

            timeout_flag:=FALSE;
            WaitDI di00_grip_on_sen,1
                \MaxTime:=T_GRIP
                \TimeFlag:=timeout_flag;

            IF timeout_flag THEN
                TPWrite "R3: 그리퍼 닫힘 확인 실패";
                PulseDO\PLength:=0.2,do04_buzzer;
                wait_restart;
            ENDIF

        ENDWHILE

        WaitTime 0.2;

    ENDPROC


    !==================================================================
    ! 그리퍼 열기
    !==================================================================
    PROC grip_off()

        WHILE di01_grip_off_sen=0 DO

            SetDO do00_grip_on,0;
            PulseDO\PLength:=0.2,do01_grip_off;

            timeout_flag:=FALSE;
            WaitDI di01_grip_off_sen,1
                \MaxTime:=T_GRIP
                \TimeFlag:=timeout_flag;

            IF timeout_flag THEN
                TPWrite "R3: 그리퍼 열림 확인 실패";
                PulseDO\PLength:=0.2,do04_buzzer;
                wait_restart;
            ENDIF

        ENDWHILE

        WaitTime 0.2;

    ENDPROC


    !==================================================================
    ! 입력 ON 대기
    !==================================================================
    PROC wait_assembly_ready()

        WHILE di14_assembly_ready=0 DO

            timeout_flag:=FALSE;
            WaitDI di14_assembly_ready,1
                \MaxTime:=T_PART_READY
                \TimeFlag:=timeout_flag;

            IF timeout_flag THEN
                TPWrite "R3: 조립 지그 준비 시간 초과";
                PulseDO\PLength:=0.2,do04_buzzer;
                wait_restart;
            ENDIF

        ENDWHILE

    ENDPROC


    PROC wait_upper_ready()

        WHILE di10_upper_ready=0 DO

            timeout_flag:=FALSE;
            WaitDI di10_upper_ready,1
                \MaxTime:=T_PART_READY
                \TimeFlag:=timeout_flag;

            IF timeout_flag THEN
                TPWrite "R3: 상부 공급 시간 초과";
                PulseDO\PLength:=0.2,do04_buzzer;
                wait_restart;
            ENDIF

        ENDWHILE

    ENDPROC


    PROC wait_upper_done()

        WHILE di11_upper_done=0 DO

            timeout_flag:=FALSE;
            WaitDI di11_upper_done,1
                \MaxTime:=T_STAMP
                \TimeFlag:=timeout_flag;

            IF timeout_flag THEN
                TPWrite "R3: 상부 스템핑 시간 초과";
                PulseDO\PLength:=0.2,do04_buzzer;
                wait_restart;
            ENDIF

        ENDWHILE

    ENDPROC


    PROC wait_door_ready()

        WHILE di12_door_ready=0 DO

            timeout_flag:=FALSE;
            WaitDI di12_door_ready,1
                \MaxTime:=T_PART_READY
                \TimeFlag:=timeout_flag;

            IF timeout_flag THEN
                TPWrite "R3: 도어 공급 시간 초과";
                PulseDO\PLength:=0.2,do04_buzzer;
                wait_restart;
            ENDIF

        ENDWHILE

    ENDPROC


    PROC wait_door_done()

        WHILE di13_door_done=0 DO

            timeout_flag:=FALSE;
            WaitDI di13_door_done,1
                \MaxTime:=T_STAMP
                \TimeFlag:=timeout_flag;

            IF timeout_flag THEN
                TPWrite "R3: 도어 스템핑 시간 초과";
                PulseDO\PLength:=0.2,do04_buzzer;
                wait_restart;
            ENDIF

        ENDWHILE

    ENDPROC


    !==================================================================
    ! 이전 Ready/Done OFF 확인
    !==================================================================
    PROC wait_upper_ready_off()

        timeout_flag:=FALSE;
        WaitDI di10_upper_ready,0
            \MaxTime:=T_SIGNAL_OFF
            \TimeFlag:=timeout_flag;

        IF timeout_flag THEN
            TPWrite "R3: 상부 Ready OFF 확인 실패";
            PulseDO\PLength:=0.2,do04_buzzer;
            wait_restart;
        ENDIF

    ENDPROC


    PROC wait_upper_done_off()

        timeout_flag:=FALSE;
        WaitDI di11_upper_done,0
            \MaxTime:=T_SIGNAL_OFF
            \TimeFlag:=timeout_flag;

        IF timeout_flag THEN
            TPWrite "R3: 상부 Done OFF 확인 실패";
            PulseDO\PLength:=0.2,do04_buzzer;
            wait_restart;
        ENDIF

    ENDPROC


    PROC wait_door_ready_off()

        timeout_flag:=FALSE;
        WaitDI di12_door_ready,0
            \MaxTime:=T_SIGNAL_OFF
            \TimeFlag:=timeout_flag;

        IF timeout_flag THEN
            TPWrite "R3: 도어 Ready OFF 확인 실패";
            PulseDO\PLength:=0.2,do04_buzzer;
            wait_restart;
        ENDIF

    ENDPROC


    PROC wait_door_done_off()

        timeout_flag:=FALSE;
        WaitDI di13_door_done,0
            \MaxTime:=T_SIGNAL_OFF
            \TimeFlag:=timeout_flag;

        IF timeout_flag THEN
            TPWrite "R3: 도어 Done OFF 확인 실패";
            PulseDO\PLength:=0.2,do04_buzzer;
            wait_restart;
        ENDIF

    ENDPROC


    PROC wait_weld_done_off()

        timeout_flag:=FALSE;
        WaitDI di15_weld_done,0
            \MaxTime:=T_SIGNAL_OFF
            \TimeFlag:=timeout_flag;

        IF timeout_flag THEN
            TPWrite "R3: 결합 Done OFF 확인 실패";
            PulseDO\PLength:=0.2,do04_buzzer;
            wait_restart;
        ENDIF

    ENDPROC


    PROC wait_amr_done_off()

        timeout_flag:=FALSE;
        WaitDI di18_amr_done,0
            \MaxTime:=T_SIGNAL_OFF
            \TimeFlag:=timeout_flag;

        IF timeout_flag THEN
            TPWrite "R3: AMR 인수 완료 신호 OFF 실패";
            PulseDO\PLength:=0.2,do04_buzzer;
            wait_restart;
        ENDIF

    ENDPROC


    PROC wait_amr_ready_off()

        timeout_flag:=FALSE;
        WaitDI di17_amr_ready,0
            \MaxTime:=T_SIGNAL_OFF
            \TimeFlag:=timeout_flag;

        IF timeout_flag THEN
            TPWrite "R3: AMR 준비 신호 OFF 실패";
            PulseDO\PLength:=0.2,do04_buzzer;
            wait_restart;
        ENDIF

    ENDPROC


    !==================================================================
    ! 작업자 재시작 버튼
    !==================================================================
    PROC wait_restart()

        WHILE di08_restart=1 DO
            WaitTime 0.1;
        ENDWHILE

        WHILE di08_restart=0 DO
            WaitTime 0.1;
        ENDWHILE

        WaitTime 0.2;

        WHILE di08_restart=1 DO
            WaitTime 0.1;
        ENDWHILE

    ENDPROC


    !==================================================================
    ! 출력 초기화
    !==================================================================
    PROC init_output()

        SetDO do00_grip_on,0;
        SetDO do01_grip_off,0;

        SetDO do05_upper_sel,0;
        SetDO do06_door_sel,0;
        SetDO do07_weld_sel,0;
        SetDO do08_out_sel,0;

        SetDO do09_amr_req,0;
        SetDO do10_cycle_done,0;

    ENDPROC

ENDMODULE
