! Draft ABB RAPID code for Robot 3 (R3)
! 3번 로봇(R3) ABB RAPID 코드 초안
! Reflects the upper/door plate press-forming process
! 상부·도어 플레이트 프레스 모사 공정 반영
! Separate pickup method for the finished upper and finished door
! 완성 상부·완성 도어 별도 픽업 방식
! Vision camera excluded
! 비전 카메라 제외
!
! Process assumptions
! 공정 기준
! 1. Upper plates are stacked in a magazine.
! 1. 상부 플레이트는 매거진에 적재한다.
! 2. The PLC extends the supply cylinder to push one plate from the magazine onto the conveyor.
! 2. PLC가 공급 실린더를 전진시켜 매거진의 플레이트 1장을 컨베이어로 밀어낸다.
! 3. Once the supply cylinder retracts to its home position, the conveyor starts running.
! 3. 공급 실린더가 후진 원위치로 복귀하면 컨베이어를 구동한다.
! 4. When the mold-position sensor detects the plate, the conveyor stops and the mold cylinder operates.
! 4. 금형 위치 센서가 플레이트를 감지하면 컨베이어를 정지하고 실린더 금형 동작을 구현한다.
! 5. Once the mold cylinder rises back to its home position, the conveyor runs again.
! 5. 금형 실린더가 상승 원위치로 돌아오면 컨베이어를 다시 구동한다.
! 6. Once the plate drops off the end of the conveyor, the conveyor stops.
! 6. 플레이트가 컨베이어 끝에서 아래로 배출되면 컨베이어를 정지한다.
! 7. R3 picks up a pre-prepared finished upper and places it on the upper assembly conveyor, left then right.
! 7. R3가 미리 준비된 완성 상부를 픽업해 상부 조립 컨베이어에 좌·우 순서로 적재한다.
! 8. A PLC cylinder joins the left and right upper halves.
! 8. PLC 실린더로 상부 좌·우 조립을 구현한다.
! 9. Door plates are fed, formed, and ejected the same way from a separate magazine.
! 9. 도어 플레이트도 별도 매거진에서 같은 방식으로 공급·금형 동작·배출한다.
! 10. R3 picks up a pre-prepared finished door and fits it onto the left/right position on the upper assembly conveyor.
! 10. R3가 미리 준비된 완성 도어를 픽업해 상부 조립 컨베이어의 좌·우 위치에 조립한다.
! 11. The finished body upper/door assembly moves to the end of the conveyor for inspection.
! 11. 완성된 차체 상부·도어를 컨베이어 끝으로 이동해 검수한다.
! 12. After passing inspection, the AMR actually picks it up and carries it to Robot 4's process.
! 12. 검수 합격 후 AMR가 실제로 인수해 4번 로봇 공정으로 운반한다.
!
! Do not run in automatic mode until the real coordinates, tooldata, and I/O addresses are finalized.
! 실제 좌표, tooldata, I/O 주소를 확정하기 전에는 자동운전하지 않는다.
! This is a draft for writing code, not a final version verified by compiling/testing in RobotStudio.
! RobotStudio에서 컴파일·실기 검증한 최종본이 아닌 코드 작성용 초안이다.

MODULE MainModule

    TASK PERS tooldata tool1 := [
    TRUE,
    [[0, 0, 110], [1, 0, 0, 0]],
    [0.2, [0, 0, 50], [1, 0, 0, 0], 0, 0, 0]
    ];

    PERS robtarget p_home := [
    [0, 0, 0],
    [1, 0, 0, 0],
    [0, 0, 0, 0],
    [9E+09, 9E+09, 9E+09, 9E+09, 9E+09, 9E+09]
    ];

    PERS robtarget p_safe := [
    [0, 0, 0],
    [1, 0, 0, 0],
    [0, 0, 0, 0],
    [9E+09, 9E+09, 9E+09, 9E+09, 9E+09, 9E+09]
    ];

    PERS robtarget p_upper_pick := [
    [0, 0, 0],
    [1, 0, 0, 0],
    [0, 0, 0, 0],
    [9E+09, 9E+09, 9E+09, 9E+09, 9E+09, 9E+09]
    ];

    PERS robtarget p_upper_place_left := [
    [0, 0, 0],
    [1, 0, 0, 0],
    [0, 0, 0, 0],
    [9E+09, 9E+09, 9E+09, 9E+09, 9E+09, 9E+09]
    ];

    PERS robtarget p_upper_place_right := [
    [0, 0, 0],
    [1, 0, 0, 0],
    [0, 0, 0, 0],
    [9E+09, 9E+09, 9E+09, 9E+09, 9E+09, 9E+09]
    ];

    PERS robtarget p_door_pick := [
    [0, 0, 0],
    [1, 0, 0, 0],
    [0, 0, 0, 0],
    [9E+09, 9E+09, 9E+09, 9E+09, 9E+09, 9E+09]
    ];

    PERS robtarget p_door_place_left := [
    [0, 0, 0],
    [1, 0, 0, 0],
    [0, 0, 0, 0],
    [9E+09, 9E+09, 9E+09, 9E+09, 9E+09, 9E+09]
    ];

    PERS robtarget p_door_place_right := [
    [0, 0, 0],
    [1, 0, 0, 0],
    [0, 0, 0, 0],
    [9E+09, 9E+09, 9E+09, 9E+09, 9E+09, 9E+09]
    ];

    VAR num n_upper_no := 0;
    VAR num n_door_no := 0;
    VAR bool timeout_flag := FALSE;

    CONST num T_GRIP := 5;
    CONST num T_PLATE_PROCESS := 30;
    CONST num T_PART_READY := 30;
    CONST num T_UPPER_JOIN := 20;
    CONST num T_INSPECTION := 30;
    CONST num T_AMR_READY := 60;
    CONST num T_AMR_TAKE := 40;
    CONST num T_SIGNAL_OFF := 10;


    PROC Main()
        ! Role: Program entry point.
        ! 역할: 프로그램 시작점.
        ! Process: reset outputs and acceleration once, then forever: home -> wait for the PLC
        !          start signal -> run R3_Cycle -> home -> signal done -> wait for start to drop.
        ! 과정: 출력·가속도를 한 번 초기화한 뒤, 계속 반복: 홈 -> PLC 시작 신호 대기 ->
        !       R3_Cycle 실행 -> 홈 -> 완료 신호 -> 시작 신호가 꺼질 때까지 대기.
        Init_Output;
        ! tune after real testing
        ! 실제 시험 후 조정
        AccSet 1, 1;

        WHILE TRUE DO
            MoveJ p_home, v200, fine, tool1;
            WaitDI di19_cycle_start, 1;
            SetDO do10_cycle_done, 0;

            R3_Cycle;

            MoveJ p_home, v200, fine, tool1;
            SetDO do10_cycle_done, 1;
            WaitDI di19_cycle_start, 0;
            SetDO do10_cycle_done, 0;
        ENDWHILE
    ENDPROC


    PROC R3_Cycle()
        ! Role: Full R3 work order for one car.
        ! 역할: 자동차 1대분 R3 전체 작업 순서.
        ! Process: Wait_Assembly_Conveyor_Clear -> Process_Uppers -> Join_Uppers ->
        !          Process_Doors -> Transfer_Inspect_Amr.
        ! 과정: Wait_Assembly_Conveyor_Clear -> Process_Uppers -> Join_Uppers ->
        !       Process_Doors -> Transfer_Inspect_Amr.
        Wait_Assembly_Conveyor_Clear;
        Process_Uppers;
        Join_Uppers;
        Process_Doors;
        Transfer_Inspect_Amr;
    ENDPROC


    PROC Process_Uppers()
        ! Role: Runs the upper-plate press process twice and places both finished uppers.
        ! 역할: 상부 플레이트 프레스 공정을 2회 실행하고 완성 상부 2개를 적재한다.
        ! Process: loop 2x - trigger the PLC plate process, wait done, wait finished-upper
        !          ready, pick it up, place left/right by n_upper_no, reset the PLC stage,
        !          confirm the signals are off before the next pass.
        ! 과정: 2회 반복 - PLC 플레이트 공정 트리거, 완료 대기, 완성 상부 준비 대기,
        !       픽업, n_upper_no에 따라 좌/우 적재, PLC 단계 초기화, 다음 회차 전
        !       신호 OFF 확인.
        ! Key variable: n_upper_no (1-2) - selects left vs right via IF.
        ! 주요 변수: n_upper_no (1~2) - IF로 좌/우를 고른다.
        FOR n_upper_no FROM 1 TO 2 DO
            SetDO do05_upper_process_sel, 1;
            PulseDO \PLength := 0.2, do02_plcstart;
            Wait_Upper_Process_Done;
            Wait_Upper_Ready;

            MoveJ Offs(p_upper_pick, 0, 0, 100), v200, z20, tool1;
            MoveL p_upper_pick, v50, fine, tool1;
            Grip_On;
            MoveL Offs(p_upper_pick, 0, 0, 100), v200, z20, tool1;
            MoveJ p_safe, v200, z20, tool1;

            IF n_upper_no = 1 THEN
                Place_Part p_upper_place_left;
            ELSE
                Place_Part p_upper_place_right;
            ENDIF

            PulseDO \PLength := 0.2, do03_reset_jedg;
            SetDO do05_upper_process_sel, 0;
            Wait_Upper_Process_Done_Off;
            Wait_Upper_Ready_Off;
        ENDFOR
    ENDPROC


    PROC Join_Uppers()
        ! Role: Joins the left and right uppers together with a PLC cylinder.
        ! 역할: 좌·우 상부를 PLC 실린더로 조립한다.
        ! Process: move clear of the work envelope -> trigger the join cylinder -> wait for
        !          completion, retrying via Wait_Restart on timeout -> reset the PLC stage.
        ! 과정: 작업 반경 밖으로 이동 -> 조립 실린더 트리거 -> 완료 대기(타임아웃 시
        !       Wait_Restart로 재시도) -> PLC 단계 초기화.
        MoveJ p_safe, v200, fine, tool1;
        SetDO do06_upper_join_sel, 1;
        PulseDO \PLength := 0.2, do02_plcstart;

        WHILE di12_upper_join_done = 0 DO
            timeout_flag := FALSE;
            WaitDI di12_upper_join_done, 1\MaxTime:=T_UPPER_JOIN\TimeFlag:=timeout_flag;
            IF timeout_flag THEN
                Alert_And_Wait_Restart "R3: Upper-join cylinder timed out";
            ENDIF
        ENDWHILE

        PulseDO \PLength := 0.2, do03_reset_jedg;
        SetDO do06_upper_join_sel, 0;
        Wait_Upper_Join_Done_Off;
    ENDPROC


    PROC Process_Doors()
        ! Role: Runs the door-plate press process twice and joins both finished doors.
        ! 역할: 도어 플레이트 프레스 공정을 2회 실행하고 완성 도어 2개를 조립한다.
        ! Process: same pattern as Process_Uppers, using the door plate/finished-door signals
        !          and positions.
        ! 과정: Process_Uppers와 동일한 패턴을, 도어 플레이트·완성 도어 신호/위치로 실행.
        ! Key variable: n_door_no (1-2) - selects left vs right via IF.
        ! 주요 변수: n_door_no (1~2) - IF로 좌/우를 고른다.
        FOR n_door_no FROM 1 TO 2 DO
            SetDO do07_door_process_sel, 1;
            PulseDO \PLength := 0.2, do02_plcstart;
            Wait_Door_Process_Done;
            Wait_Door_Ready;

            MoveJ Offs(p_door_pick, 0, 0, 100), v200, z20, tool1;
            MoveL p_door_pick, v50, fine, tool1;
            Grip_On;
            MoveL Offs(p_door_pick, 0, 0, 100), v200, z20, tool1;
            MoveJ p_safe, v200, z20, tool1;

            IF n_door_no = 1 THEN
                Place_Part p_door_place_left;
            ELSE
                Place_Part p_door_place_right;
            ENDIF

            PulseDO \PLength := 0.2, do03_reset_jedg;
            SetDO do07_door_process_sel, 0;
            Wait_Door_Process_Done_Off;
            Wait_Door_Ready_Off;
        ENDFOR
    ENDPROC


    PROC Transfer_Inspect_Amr()
        ! Role: Moves the finished assembly to the inspection position, waits for a pass, then
        !       hands it off to the AMR.
        ! 역할: 완성품을 검수 위치로 옮기고, 합격을 기다린 뒤, AMR에 인계한다.
        ! Process: move clear -> trigger the transfer conveyor -> wait inspection done -> wait
        !          inspection pass (blocks indefinitely on fail) -> request the AMR -> wait AMR
        !          ready -> trigger AMR loading -> wait AMR actual handoff -> reset the stage.
        ! 과정: 작업 반경 밖으로 이동 -> 이송 컨베이어 트리거 -> 검수 완료 대기 -> 검수
        !       합격 대기(불합격이면 무한 대기) -> AMR 요청 -> AMR 준비 대기 -> AMR 적재
        !       트리거 -> AMR 실제 인수 대기 -> 단계 초기화.
        ! Note: di18_amr_done only turns on once the AMR has actually loaded, the finished-part
        !       sensor is off, and the AMR has departed - it is not a simple request-received
        !       signal (see the I/O reference at the end of the file).
        ! 참고: di18_amr_done은 AMR 적재 완료 + 제품센서 OFF + AMR 출발까지 확인된 뒤에만
        !       켜진다 - 단순 요청 접수 신호가 아니다(파일 끝 I/O 정리 참고).
        MoveJ p_safe, v200, fine, tool1;
        SetDO do08_transfer_sel, 1;
        PulseDO \PLength := 0.2, do02_plcstart;

        WHILE di15_inspection_done = 0 DO
            timeout_flag := FALSE;
            WaitDI di15_inspection_done, 1\MaxTime:=T_INSPECTION\TimeFlag:=timeout_flag;
            IF timeout_flag THEN
                Alert_And_Wait_Restart "R3: Timed out waiting for finished-part inspection";
            ENDIF
        ENDWHILE

        WHILE di16_inspection_pass = 0 DO
            Alert_And_Wait_Restart "R3: Finished part failed inspection or is awaiting approval";
        ENDWHILE

        SetDO do09_amr_req, 1;

        WHILE di17_amr_ready = 0 DO
            timeout_flag := FALSE;
            WaitDI di17_amr_ready, 1\MaxTime:=T_AMR_READY\TimeFlag:=timeout_flag;
            IF timeout_flag THEN
                Alert_And_Wait_Restart "R3: Timed out waiting for the AMR to arrive";
            ENDIF
        ENDWHILE

        PulseDO \PLength := 0.2, do02_plcstart;

        WHILE di18_amr_done = 0 DO
            timeout_flag := FALSE;
            WaitDI di18_amr_done, 1\MaxTime:=T_AMR_TAKE\TimeFlag:=timeout_flag;
            IF timeout_flag THEN
                Alert_And_Wait_Restart "R3: Timed out waiting for the AMR to take the finished part";
            ENDIF
        ENDWHILE

        PulseDO \PLength := 0.2, do03_reset_jedg;
        SetDO do08_transfer_sel, 0;
        SetDO do09_amr_req, 0;
        Wait_Inspection_Done_Off;
        Wait_Inspection_Pass_Off;
        Wait_Amr_Done_Off;
        Wait_Amr_Ready_Off;
    ENDPROC


    PROC Place_Part(robtarget p_place)
        ! Role: Places whatever part is currently gripped at the given left/right position.
        ! 역할: 지금 잡고 있는 부품을 전달받은 좌/우 위치에 내려놓는다.
        ! Process: approach above p_place -> descend -> release -> retreat -> return to safe.
        ! 과정: p_place 위 접근 -> 하강 -> 놓음 -> 이탈 -> 안전 위치로 복귀.
        MoveJ Offs(p_place, 0, 0, 100), v200, z20, tool1;
        MoveL p_place, v40, fine, tool1;
        Grip_Off;
        MoveJ Offs(p_place, 0, 0, 100), v200, z20, tool1;
        MoveJ p_safe, v200, z20, tool1;
    ENDPROC


    PROC Grip_On()
        ! Role: Closes the gripper and confirms the close sensor, retrying (with timeout and
        !       Wait_Restart) until it does.
        ! 역할: 그리퍼를 닫고 닫힘 센서를 확인하며, 안 될 경우 타임아웃+Wait_Restart로 재시도.
        ! Process: loop while the sensor is off - reset the open output, pulse close, wait
        !          with timeout, alert and Wait_Restart on timeout - then settle 0.2s.
        ! 과정: 센서가 꺼져 있는 동안 반복 - 열기 출력 리셋, 닫기 펄스, 타임아웃 대기,
        !       타임아웃 시 알림+Wait_Restart -> 0.2초 안정화.
        WHILE di00_grip_on_sen = 0 DO
            SetDO do01_grip_off, 0;
            PulseDO \PLength := 0.2, do00_grip_on;
            timeout_flag := FALSE;
            WaitDI di00_grip_on_sen, 1\MaxTime:=T_GRIP\TimeFlag:=timeout_flag;
            IF timeout_flag THEN
                Alert_And_Wait_Restart "R3: Failed to confirm the gripper closed";
            ENDIF
        ENDWHILE

        WaitTime 0.2;
    ENDPROC


    PROC Grip_Off()
        ! Role: Opens the gripper and confirms the open sensor, retrying (with timeout and
        !       Wait_Restart) until it does.
        ! 역할: 그리퍼를 열고 열림 센서를 확인하며, 안 될 경우 타임아웃+Wait_Restart로 재시도.
        ! Process: loop while the sensor is off - reset the close output, pulse open, wait
        !          with timeout, alert and Wait_Restart on timeout - then settle 0.2s.
        ! 과정: 센서가 꺼져 있는 동안 반복 - 닫기 출력 리셋, 열기 펄스, 타임아웃 대기,
        !       타임아웃 시 알림+Wait_Restart -> 0.2초 안정화.
        WHILE di01_grip_off_sen = 0 DO
            SetDO do00_grip_on, 0;
            PulseDO \PLength := 0.2, do01_grip_off;
            timeout_flag := FALSE;
            WaitDI di01_grip_off_sen, 1\MaxTime:=T_GRIP\TimeFlag:=timeout_flag;
            IF timeout_flag THEN
                Alert_And_Wait_Restart "R3: Failed to confirm the gripper opened";
            ENDIF
        ENDWHILE

        WaitTime 0.2;
    ENDPROC


    PROC Wait_Assembly_Conveyor_Clear()
        ! Role: Confirms the upper assembly conveyor is empty before starting a new car.
        ! 역할: 새 자동차를 시작하기 전에 상부 조립 컨베이어가 비어 있는지 확인한다.
        ! Process: wait with timeout; on timeout, alert + Wait_Restart, then check again.
        ! 과정: 타임아웃 대기; 타임아웃 시 알림 + Wait_Restart 후 다시 확인.
        timeout_flag := FALSE;
        WaitDI di20_assembly_clear, 1\MaxTime:=T_PART_READY\TimeFlag:=timeout_flag;
        IF timeout_flag THEN
            Alert_And_Wait_Restart "R3: Failed to confirm the upper assembly conveyor is clear";
            Wait_Assembly_Conveyor_Clear;
        ENDIF
    ENDPROC


    PROC Wait_Upper_Process_Done()
        ! Role: Waits for one full upper-plate cycle (magazine feed through end-eject).
        ! 역할: 상부 플레이트 1회 공정(매거진 공급~끝단 배출)이 끝날 때까지 대기한다.
        ! Process: loop until done - if the magazine is empty, alert as a distinct material
        !          fault and re-trigger after Wait_Restart; otherwise wait with timeout and
        !          re-trigger after Wait_Restart on timeout.
        ! 과정: 완료까지 반복 - 매거진이 비었으면 별도의 재료 부족 오류로 알리고
        !       Wait_Restart 후 재트리거; 아니면 타임아웃 대기, 타임아웃 시 Wait_Restart
        !       후 재트리거.
        WHILE di10_upper_process_done = 0 DO
            IF di02_upper_mag_empty = 1 THEN
                Alert_And_Wait_Restart "R3: Upper plate magazine is empty";
                PulseDO \PLength := 0.2, do02_plcstart;
            ENDIF

            timeout_flag := FALSE;
            WaitDI di10_upper_process_done, 1\MaxTime:=T_PLATE_PROCESS\TimeFlag:=timeout_flag;

            IF timeout_flag THEN
                Alert_And_Wait_Restart "R3: Upper plate process timed out";
                PulseDO \PLength := 0.2, do02_plcstart;
            ENDIF
        ENDWHILE
    ENDPROC


    PROC Wait_Upper_Ready()
        ! Role: Waits for the finished-upper pickup-ready signal.
        ! 역할: 완성 상부 픽업 준비 신호를 대기한다.
        ! Process: wait with timeout; on timeout, alert + Wait_Restart, then check again.
        ! 과정: 타임아웃 대기; 타임아웃 시 알림 + Wait_Restart 후 다시 확인.
        timeout_flag := FALSE;
        WaitDI di11_upper_ready, 1\MaxTime:=T_PART_READY\TimeFlag:=timeout_flag;
        IF timeout_flag THEN
            Alert_And_Wait_Restart "R3: Timed out waiting for the finished upper";
            Wait_Upper_Ready;
        ENDIF
    ENDPROC


    PROC Wait_Door_Process_Done()
        ! Role: Waits for one full door-plate cycle (magazine feed through end-eject).
        ! 역할: 도어 플레이트 1회 공정(매거진 공급~끝단 배출)이 끝날 때까지 대기한다.
        ! Process: same pattern as Wait_Upper_Process_Done, for the door magazine/signals.
        ! 과정: Wait_Upper_Process_Done과 동일한 패턴을 도어 매거진/신호로 실행.
        WHILE di13_door_process_done = 0 DO
            IF di03_door_mag_empty = 1 THEN
                Alert_And_Wait_Restart "R3: Door plate magazine is empty";
                PulseDO \PLength := 0.2, do02_plcstart;
            ENDIF

            timeout_flag := FALSE;
            WaitDI di13_door_process_done, 1\MaxTime:=T_PLATE_PROCESS\TimeFlag:=timeout_flag;

            IF timeout_flag THEN
                Alert_And_Wait_Restart "R3: Door plate process timed out";
                PulseDO \PLength := 0.2, do02_plcstart;
            ENDIF
        ENDWHILE
    ENDPROC


    PROC Wait_Door_Ready()
        ! Role: Waits for the finished-door pickup-ready signal.
        ! 역할: 완성 도어 픽업 준비 신호를 대기한다.
        ! Process: wait with timeout; on timeout, alert + Wait_Restart, then check again.
        ! 과정: 타임아웃 대기; 타임아웃 시 알림 + Wait_Restart 후 다시 확인.
        timeout_flag := FALSE;
        WaitDI di14_door_ready, 1\MaxTime:=T_PART_READY\TimeFlag:=timeout_flag;
        IF timeout_flag THEN
            Alert_And_Wait_Restart "R3: Timed out waiting for the finished door";
            Wait_Door_Ready;
        ENDIF
    ENDPROC


    ! The 9 procs below all follow the same shape: confirm one signal drops to 0 within
    ! T_SIGNAL_OFF so a stale signal from the previous part/cycle can't be misread as fresh.
    ! 아래 9개 함수는 전부 같은 형태: 이전 부품/사이클의 오래된 신호를 새 신호로 착각하지
    ! 않도록, T_SIGNAL_OFF 안에 신호 하나가 0으로 꺼지는 걸 확인한다.

    PROC Wait_Upper_Process_Done_Off()
        ! Role: Confirms the upper plate completion signal is off.
        ! 역할: 상부 플레이트 완료 신호가 꺼졌는지 확인한다.
        timeout_flag := FALSE;
        WaitDI di10_upper_process_done, 0\MaxTime:=T_SIGNAL_OFF\TimeFlag:=timeout_flag;
        IF timeout_flag THEN
            Alert_And_Wait_Restart "R3: Failed to confirm upper plate completion signal OFF";
        ENDIF
    ENDPROC


    PROC Wait_Upper_Ready_Off()
        ! Role: Confirms the finished-upper ready signal is off.
        ! 역할: 완성 상부 준비 신호가 꺼졌는지 확인한다.
        timeout_flag := FALSE;
        WaitDI di11_upper_ready, 0\MaxTime:=T_SIGNAL_OFF\TimeFlag:=timeout_flag;
        IF timeout_flag THEN
            Alert_And_Wait_Restart "R3: Failed to confirm finished-upper ready signal OFF";
        ENDIF
    ENDPROC


    PROC Wait_Upper_Join_Done_Off()
        ! Role: Confirms the upper-join completion signal is off.
        ! 역할: 상부 조립 완료 신호가 꺼졌는지 확인한다.
        timeout_flag := FALSE;
        WaitDI di12_upper_join_done, 0\MaxTime:=T_SIGNAL_OFF\TimeFlag:=timeout_flag;
        IF timeout_flag THEN
            Alert_And_Wait_Restart "R3: Failed to confirm upper-join completion signal OFF";
        ENDIF
    ENDPROC


    PROC Wait_Door_Process_Done_Off()
        ! Role: Confirms the door plate completion signal is off.
        ! 역할: 도어 플레이트 완료 신호가 꺼졌는지 확인한다.
        timeout_flag := FALSE;
        WaitDI di13_door_process_done, 0\MaxTime:=T_SIGNAL_OFF\TimeFlag:=timeout_flag;
        IF timeout_flag THEN
            Alert_And_Wait_Restart "R3: Failed to confirm door plate completion signal OFF";
        ENDIF
    ENDPROC


    PROC Wait_Door_Ready_Off()
        ! Role: Confirms the finished-door ready signal is off.
        ! 역할: 완성 도어 준비 신호가 꺼졌는지 확인한다.
        timeout_flag := FALSE;
        WaitDI di14_door_ready, 0\MaxTime:=T_SIGNAL_OFF\TimeFlag:=timeout_flag;
        IF timeout_flag THEN
            Alert_And_Wait_Restart "R3: Failed to confirm finished-door ready signal OFF";
        ENDIF
    ENDPROC


    PROC Wait_Inspection_Done_Off()
        ! Role: Confirms the inspection-complete signal is off.
        ! 역할: 검수 완료 신호가 꺼졌는지 확인한다.
        timeout_flag := FALSE;
        WaitDI di15_inspection_done, 0\MaxTime:=T_SIGNAL_OFF\TimeFlag:=timeout_flag;
        IF timeout_flag THEN
            Alert_And_Wait_Restart "R3: Failed to confirm inspection-complete signal OFF";
        ENDIF
    ENDPROC


    PROC Wait_Inspection_Pass_Off()
        ! Role: Confirms the inspection-pass signal is off.
        ! 역할: 검수 합격 신호가 꺼졌는지 확인한다.
        timeout_flag := FALSE;
        WaitDI di16_inspection_pass, 0\MaxTime:=T_SIGNAL_OFF\TimeFlag:=timeout_flag;
        IF timeout_flag THEN
            Alert_And_Wait_Restart "R3: Failed to confirm inspection-pass signal OFF";
        ENDIF
    ENDPROC


    PROC Wait_Amr_Done_Off()
        ! Role: Confirms the AMR actual-handoff-complete signal is off.
        ! 역할: AMR 실제 인수 완료 신호가 꺼졌는지 확인한다.
        timeout_flag := FALSE;
        WaitDI di18_amr_done, 0\MaxTime:=T_SIGNAL_OFF\TimeFlag:=timeout_flag;
        IF timeout_flag THEN
            Alert_And_Wait_Restart "R3: Failed to confirm AMR handoff-complete signal OFF";
        ENDIF
    ENDPROC


    PROC Wait_Amr_Ready_Off()
        ! Role: Confirms the AMR ready signal is off (i.e. it has left the R3 position).
        ! 역할: AMR 준비 신호가 꺼졌는지(= R3 위치를 떠났는지) 확인한다.
        timeout_flag := FALSE;
        WaitDI di17_amr_ready, 0\MaxTime:=T_SIGNAL_OFF\TimeFlag:=timeout_flag;
        IF timeout_flag THEN
            Alert_And_Wait_Restart "R3: Failed to confirm AMR ready signal OFF";
        ENDIF
    ENDPROC


    PROC Alert_And_Wait_Restart(string msg)
        ! Role: Shows an error on the FlexPendant, sounds the buzzer, and waits for the restart
        !       button - the shared response every timeout/fault check in this file uses.
        ! 역할: FlexPendant에 오류를 표시하고 부저를 울린 뒤 재시작 버튼을 기다린다 - 이
        !       파일의 모든 타임아웃/오류 확인이 공통으로 쓰는 대응.
        TPWrite msg;
        PulseDO \PLength := 0.2, do04_buzzer;
        Wait_Restart;
    ENDPROC


    PROC Wait_Restart()
        ! Role: Confirms the restart button is pressed and released before returning control
        !       to the caller.
        ! 역할: 호출한 곳으로 돌아가기 전에 재시작 버튼을 눌렀다가 뗐는지 확인한다.
        ! Process: if already pressed, wait for release -> wait for a press -> brief debounce
        !          pause -> wait for release again.
        ! 과정: 이미 눌려 있으면 뗄 때까지 대기 -> 눌릴 때까지 대기 -> 짧은 디바운스 대기
        !       -> 다시 뗄 때까지 대기.
        WHILE di08_restart = 1 DO
            WaitTime 0.1;
        ENDWHILE

        WHILE di08_restart = 0 DO
            WaitTime 0.1;
        ENDWHILE

        WaitTime 0.2;

        WHILE di08_restart = 1 DO
            WaitTime 0.1;
        ENDWHILE
    ENDPROC


    PROC Init_Output()
        ! Role: Resets every output this module drives, before starting automatic operation.
        ! 역할: 자동운전을 시작하기 전에, 이 모듈이 다루는 모든 출력을 초기화한다.
        SetDO do00_grip_on, 0;
        SetDO do01_grip_off, 0;
        SetDO do05_upper_process_sel, 0;
        SetDO do06_upper_join_sel, 0;
        SetDO do07_door_process_sel, 0;
        SetDO do08_transfer_sel, 0;
        SetDO do09_amr_req, 0;
        SetDO do10_cycle_done, 0;
    ENDPROC

ENDMODULE


! I/O signal reference
! I/O 이름 정리
!
! Inputs (DI)
! 입력 DI
! di02_upper_mag_empty    : Upper plate magazine empty
! di02_upper_mag_empty    : 상부 플레이트 매거진 없음
! di03_door_mag_empty     : Door plate magazine empty
! di03_door_mag_empty     : 도어 플레이트 매거진 없음
! di10_upper_process_done : Upper magazine feed/press/end-eject complete
! di10_upper_process_done : 상부 매거진 1장 공급·프레스·끝단 배출 완료
! di11_upper_ready        : Finished upper ready for pickup
! di11_upper_ready        : 완성 상부 픽업 준비
! di12_upper_join_done    : Cylinder upper-join complete
! di12_upper_join_done    : 실린더 상부 조립 완료
! di13_door_process_done  : Door magazine feed/press/end-eject complete
! di13_door_process_done  : 도어 매거진 1장 공급·프레스·끝단 배출 완료
! di14_door_ready         : Finished door ready for pickup
! di14_door_ready         : 완성 도어 픽업 준비
! di15_inspection_done    : Finished body upper/door inspection complete
! di15_inspection_done    : 완성 차체 상부·도어 검수 완료
! di16_inspection_pass    : Inspection pass
! di16_inspection_pass    : 검수 합격
! di17_amr_ready          : AMR arrived at the R3 handoff position, ready to load
! di17_amr_ready          : AMR R3 인계 위치 도착·적재 준비
! di18_amr_done           : AMR actual handoff done + exit sensor off + AMR departed
! di18_amr_done           : AMR 실제 인수 + 출구센서 OFF + AMR 출발 완료
! di19_cycle_start        : PLC start for one car's worth of R3 work
! di19_cycle_start        : PLC의 R3 자동차 1대분 시작
! di20_assembly_clear     : Upper assembly conveyor clear
! di20_assembly_clear     : 상부 조립 컨베이어 비어 있음
!
! Outputs (DO)
! 출력 DO
! do05_upper_process_sel  : Select the upper magazine feed/press/eject process
! do05_upper_process_sel  : 상부 매거진 공급·프레스·배출 공정 선택
! do06_upper_join_sel     : Select the cylinder upper-join process
! do06_upper_join_sel     : 실린더 상부 조립 공정 선택
! do07_door_process_sel   : Select the door magazine feed/press/eject process
! do07_door_process_sel   : 도어 매거진 공급·프레스·배출 공정 선택
! do08_transfer_sel       : Select the finished-part conveyor transfer/inspection/AMR-load process
! do08_transfer_sel       : 완성품 컨베이어 이송·검수·AMR 적재 공정 선택
! do09_amr_req            : Request AMR transport for R3
! do09_amr_req            : R3 AMR 운반 요청
! do10_cycle_done         : R3 one-car assembly and AMR handoff complete
! do10_cycle_done         : R3 자동차 1대분 조립 및 AMR 인수 완료
!
! Conditions the PLC uses to turn on di10_upper_process_done / di13_door_process_done
! PLC에서 di10_upper_process_done / di13_door_process_done을 ON하는 조건
! 1) Confirm the magazine has plates
! 1) 매거진 플레이트 있음 확인
! 2) Confirm the supply cylinder is retracted to home
! 2) 공급 실린더 후진 원위치 확인
! 3) Extend the supply cylinder to eject one plate
! 3) 공급 실린더 전진으로 플레이트 1장 배출
! 4) Confirm the supply cylinder's extend-complete sensor
! 4) 공급 실린더 전진 완료 센서 확인
! 5) Retract the supply cylinder
! 5) 공급 실린더 후진
! 6) Confirm the supply cylinder's retract-complete sensor
! 6) 공급 실린더 후진 완료 센서 확인
! 7) Detect the plate at the conveyor entrance
! 7) 컨베이어 입구 플레이트 감지
! 8) Run the conveyor
! 8) 컨베이어 구동
! 9) Stop the conveyor at the mold-position sensor
! 9) 금형 위치 센서에서 컨베이어 정지
! 10) Confirm the mold cylinder finished descending
! 10) 금형 실린더 하강 완료
! 11) Confirm the mold cylinder rose back to home
! 11) 금형 실린더 상승 및 원위치 완료
! 12) Run the conveyor again
! 12) 컨베이어 재구동
! 13) Confirm the plate ejected at the end
! 13) 플레이트 끝단 배출 확인
! 14) Stop the conveyor
! 14) 컨베이어 정지
!
! Conditions required before feeding the next plate
! 다음 플레이트 공급 허가 조건
! - The previous plate finished ejecting at the end
! - 이전 플레이트 끝단 배출 완료
! - No existing plate at the conveyor entrance
! - 컨베이어 입구에 기존 플레이트 없음
! - Supply cylinder retracted to home
! - 공급 실린더 후진 원위치
! - The corresponding magazine has plates
! - 해당 매거진에 플레이트 있음
!
! di18_amr_done is not a simple request-received signal.
! di18_amr_done은 단순 요청 접수 신호가 아니다.
! It must only turn on after AMR loading is complete, the finished-part sensor at the inspection position is off, and the AMR has departed.
! AMR 적재 완료 + 검수 위치 제품센서 OFF + AMR 출발 확인 후 ON해야 한다.
