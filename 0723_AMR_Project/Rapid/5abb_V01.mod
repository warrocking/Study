MODULE MainModule
    ! TCP tool data for the gripper - placeholder values, calibrate against the real tool before running
    ! 그리퍼 TCP 툴 데이터 - 아직 placeholder 값, 실제 툴로 캘리브레이션 필요
    ! TCP tool data for the gripper - placeholder values, calibrate against the real tool before running
    ! ??? TCP ? ??? - ?? placeholder ?, ?? ?? ?????? ??
    TASK PERS tooldata tool1 := [
    TRUE,
    [[3.25653, -2.2499, 106.27], [1, 0, 0, 0]],
    [0.2, [0, 0, 50], [1, 0, 0, 0], 0, 0, 0]
    ];

    ! Home / safe position the cycle starts and rests at
    ! ???? ?????? ?(??) ??
    PERS robtarget p_home := [[375.37,20.48,540.81],[2.15925E-05,-0.419202,0.907893,6.67298E-05],[0,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    ! Central build fixture - the axle is set down here, and everything else stacks onto it
    ! ?? ?? ??? - ?? ?? ???? ???? ?? ? ?? ??
    PERS robtarget p_assembly := [[497.19,-127.66,442.32],[1.93662E-05,0.436476,-0.899716,0.000120992],[-1,-1,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    ! Axle supply position - approach point above
    ! ? ?? ?? - ? ???
    PERS robtarget p_axle_pickup := [[-93.43,363.19,228.64],[2.49217E-05,0.436469,-0.899719,4.2493E-05],[1,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    ! Axle supply position - actual grip height
    ! ? ?? ?? - ?? ?? ??
    PERS robtarget p_axle_pickdown := [[-93.42,363.15,197.04],[3.51739E-05,0.436476,-0.899716,0.000107992],[1,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    ! Approach point above the axle's spot in the assembly fixture
    ! ?? ????? ?? ??? ?? ? ???
    PERS robtarget p_axle_assem_up := [[493.53,-123.08,343.25],[4.4257E-05,0.390388,0.92065,-0.000111341],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    ! Actual place height where the axle is set down and clamped
    ! ??? ?? ???? ???? ??
    PERS robtarget p_axle_assem_down := [[493.52,-123.08,324.11],[2.95257E-05,0.39039,0.92065,-0.000114433],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    ! Fixed pickup point where the PLC ejects one tire at a time - approach
    ! PLC? ???? ? ?? ???? ?? ?? ?? - ???
    PERS robtarget p_tier_up := [[229.09,-577.34,258.19],[1.09686E-05,0.384535,0.92311,-1.12421E-05],[-1,-1,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    ! Fixed tire pickup point - actual grip height
    ! ?? ??? ?? ?? - ?? ?? ??
    PERS robtarget p_tier_down := [[229.08,-577.33,234.38],[5.67595E-06,-0.384535,-0.92311,-5.66128E-06],[-1,-1,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    ! Axle mount position 1 - approach
    ! ? ?? ?? 1 - ???
    PERS robtarget p_tier_link_1 := [[427.21,-261.75,262.54],[0.278778,-0.278757,-0.649775,-0.649899],[-1,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    ! Axle mount position 1 - actual insert height
    ! ? ?? ?? 1 - ?? ??? ??
    PERS robtarget p_tier_link_1_down := [[427.20,-229.84,262.54],[0.278794,-0.278759,-0.649769,-0.649899],[-1,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    ! Axle mount position 2 - approach
    ! ? ?? ?? 2 - ???
    PERS robtarget p_tier_link_2 := [[424.46,0.32,261.96],[0.282732,0.282723,0.648113,-0.648135],[0,-1,1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    ! Axle mount position 2 - actual insert height
    ! ? ?? ?? 2 - ?? ??? ??
    PERS robtarget p_tier_link_2_down := [[424.45,-24.67,261.96],[0.28272,0.282716,0.648107,-0.64815],[0,-1,1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    ! Axle mount position 3 - approach
    ! ? ?? ?? 3 - ???
    PERS robtarget p_tier_link_3 := [[523.55,-282.33,262.53],[0.278738,-0.278767,-0.649802,-0.649885],[-1,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    ! Axle mount position 3 - actual insert height
    ! ? ?? ?? 3 - ?? ??? ??
    PERS robtarget p_tier_link_3_down := [[523.54,-228.32,262.54],[0.278765,-0.278763,-0.649792,-0.649886],[-1,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    ! Axle mount position 4 - approach
    ! ? ?? ?? 4 - ???
    PERS robtarget p_tier_link_4 := [[522.37,13.48,261.41],[0.282741,0.282741,0.648121,-0.648116],[0,-1,1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    ! Axle mount position 4 - actual insert height
    ! ? ?? ?? 4 - ?? ??? ??
    PERS robtarget p_tier_link_4_down := [[522.37,-24.15,261.42],[0.282735,0.282741,0.648112,-0.648128],[0,-1,1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    ! ===== Lower body station (chassis supply location) =====
    ! ===== ??? ???? (?? ?? ?? ??) =====
    ! Lower body chassis supply position - approach
    ! ?? ?? ?? ?? - ???
    PERS robtarget p_Lower_body_pickup := [
    [342.30, -38.16, 327.52],
    [1.20614E-05, 0.456804, -0.889567, -5.42704E-06],
    [-1, -1, -1, 0],
    [9E+09, 9E+09, 9E+09, 9E+09, 9E+09, 9E+09]
    ];

    ! Lower body chassis supply position - actual grip height
    ! ?? ?? ?? ?? - ?? ?? ??
    PERS robtarget p_Lower_body_pickdown := [
    [342.30, -38.16, 327.52],
    [1.20614E-05, 0.456804, -0.889567, -5.42704E-06],
    [-1, -1, -1, 0],
    [9E+09, 9E+09, 9E+09, 9E+09, 9E+09, 9E+09]
    ];

    ! Where the lower body is set on the axle+tire assembly - approach. Also reused in Sender() as
    ! the point the finished assembly is grabbed by suction (see the Sender header comment).
    ! ?+??? ??? ?? ???? ???? ?? - ???. Sender()?? ?? ???? ????
    ! ?? ????? ????(Sender ?? ?? ??).
    PERS robtarget p_Lower_body_link := [[497.22,-132.60,373.77],[6.32019E-05,0.361509,-0.932368,0.000105993],[-1,-1,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    ! Where the lower body is set on the axle+tire assembly - actual place/grip height
    ! ?+??? ??? ?? ???? ???? ?? - ?? ??/?? ??
    PERS robtarget p_Lower_body_link_down := [[497.23,-132.60,342.88],[8.79376E-05,0.361499,-0.932372,8.08897E-05],[-1,-1,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    ! ===== Bakttery station (battery supply location) =====
    ! ===== ??? ???? (??? ?? ??) =====
    ! Battery supply position - approach
    ! ??? ?? ?? - ???
    PERS robtarget p_battery_pickup := [[141.98,-423.64,211.57],[8.71375E-06,0.398495,-0.917171,-6.43323E-05],[-1,-1,-2,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    ! Battery supply position - actual grip height
    ! ??? ?? ?? - ?? ?? ??
    PERS robtarget p_battery_pickdown := [[141.99,-423.67,191.53],[8.94231E-06,0.398496,-0.91717,-4.50033E-05],[-1,-1,-2,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    ! Where the battery is set on the lower body - approach
    ! ??? ?? ???? ???? ?? - ???
    PERS robtarget p_battery_link_up := [[468.42,-134.21,358.67],[3.597E-05,0.403279,-0.915077,0.000111412],[-1,-1,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    ! Where the battery is set on the lower body - actual place height
    ! ??? ?? ???? ???? ?? - ?? ?? ??
    PERS robtarget p_battery_link_down := [[468.42,-134.21,344.08],[5.26814E-05,0.403281,-0.915076,9.55054E-05],[-1,-1,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    ! ===== Motor station =====
    ! ===== ?? ???? =====
    ! Motor supply position - approach
    ! ?? ?? ?? - ???
    PERS robtarget p_motor_pickup := [
    [342.30, -38.16, 327.52],
    [1.20614E-05, 0.456804, -0.889567, -5.42704E-06],
    [-1, -1, -1, 0],
    [9E+09, 9E+09, 9E+09, 9E+09, 9E+09, 9E+09]
    ];

    ! Motor supply position - actual grip height
    ! ?? ?? ?? - ?? ?? ??
    PERS robtarget p_motor_pickdown := [
    [342.30, -38.16, 327.52],
    [1.20614E-05, 0.456804, -0.889567, -5.42704E-06],
    [-1, -1, -1, 0],
    [9E+09, 9E+09, 9E+09, 9E+09, 9E+09, 9E+09]
    ];

    ! Where the motor is mounted on the assembly - approach
    ! ???? ??? ???? ?? - ???
    PERS robtarget p_motor_linkup := [
    [342.30, -38.16, 327.52],
    [1.20614E-05, 0.456804, -0.889567, -5.42704E-06],
    [-1, -1, -1, 0],
    [9E+09, 9E+09, 9E+09, 9E+09, 9E+09, 9E+09]
    ];

    ! Where the motor is mounted on the assembly - actual mount height
    ! ???? ??? ???? ?? - ?? ?? ??
    PERS robtarget p_motor_linkdown := [
    [342.30, -38.16, 327.52],
    [1.20614E-05, 0.456804, -0.889567, -5.42704E-06],
    [-1, -1, -1, 0],
    [9E+09, 9E+09, 9E+09, 9E+09, 9E+09, 9E+09]
    ];

    ! Not referenced anywhere in this module yet - reserved for future use
    ! ?? ? ??? ?? ????? ???? ?? - ??? ?? ??? ??
    PERS robtarget p_assembly_pickup := [[492.53,-129.07,373.47],[1.7566E-05,0.403268,-0.915082,0.000127229],[-1,-1,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    ! Not referenced anywhere in this module yet - reserved for future use
    ! ?? ? ??? ?? ????? ???? ?? - ??? ?? ??? ??
    PERS robtarget p_assembly_pickdown := [[492.53,-129.06,338.88],[3.95473E-05,0.403272,-0.91508,0.000107178],[-1,-1,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    ! ===== Exit conveyor =====
    ! ===== ?? ???? =====
    ! Exit conveyor - approach
    ! ?? ???? - ???
    PERS robtarget p_conveyor_Exit_up := [[327.17,287.76,286.86],[4.46812E-05,0.403294,-0.91507,0.000139668],[0,-1,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    ! Exit conveyor - actual place height where the finished assembly is set down
    ! ?? ???? - ???? ???? ?? ??
    PERS robtarget p_conveyor_Exit_down := [[327.18,287.76,260.85],[7.22898E-05,0.403284,-0.915075,0.000144839],[0,-1,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];


    ! Travel speed for empty or long moves
    ! 빈 상태 이동이나 장거리 이동에 쓰는 속도
    VAR speeddata v_fast := v200;
    ! Careful (slow) speed for pick/place moves
    ! 픽업/배치 동작에 쓰는 신중한(느린) 속도
    VAR speeddata v_slow := v50;

    PROC Main()
        ! Role: Entry point - runs one-time setup, then executes one full assembly cycle.
        ! 역할: 진입점 - 최초 설정을 한 번 실행한 뒤, 조립 사이클을 한 번 수행한다.
        ! Process: Init (accel + home + clear outputs) -> [server placeholder] -> Run_Assembly_Cycle.
        ! 과정: Init(가속도 설정 + 홈 이동 + 출력 초기화) -> [서버 자리표시자] -> Run_Assembly_Cycle.
        Init;

        ! Placeholder: TCP server code goes here (not implemented yet)
        ! 자리표시자: TCP 서버 코드를 넣을 자리 (아직 미구현)

        ! Placeholder: end of server section
        ! 자리표시자: 서버 구역 끝

        Run_Assembly_Cycle;
    ENDPROC

    PROC Init()
        ! Role: One-time setup before the cycle starts.
        ! 역할: 사이클 시작 전 최초 설정.
        ! Process: set acceleration -> move to home -> release the gripper -> reset the axle
        !          cylinder/tire-start/axle-gripper outputs left on from a previous run.
        ! 과정: 가속도 설정 -> 홈으로 이동 -> 그리퍼 열기 -> 이전 실행에서 남은 축 실린더/
        !       타이어 시작/축 그리퍼 출력을 초기화.
        AccSet 1, 1;
        MoveL p_home, v_fast, fine, tool1;

        Grip_Off;
        SetDO do05_Axle_Cylinder_Forward, 0;
        SetDO do06_Tier_Start, 0;
        SetDO do07_Axle_Gripper_On, 0;
    ENDPROC

    PROC Run_Assembly_Cycle()
        ! Role: Runs the full build sequence for one AMR chassis, station by station.
        ! 역할: AMR 섀시 1대분 전체 조립 순서를 스테이션별로 실행한다.
        ! Process: Axle -> Lower_Body -> Welding -> Battery -> Motor -> Tier_Linked -> Sender,
        !          returning to p_assembly between every station.
        ! 과정: Axle -> Lower_Body -> Welding -> Battery -> Motor -> Tier_Linked -> Sender,
        !       스테이션마다 사이에 p_assembly로 복귀.
        Axle;
        MoveJ p_assembly, v_fast, z30, tool1;

        Lower_Body;
        MoveJ p_assembly, v_fast, z30, tool1;

        Welding;
        MoveJ p_assembly, v_fast, z30, tool1;

        Battery;
        MoveJ p_assembly, v_fast, z30, tool1;

        Motor;
        MoveJ p_assembly, v_fast, z30, tool1;

        Tier_Linked;
        MoveJ p_assembly, v_fast, z30, tool1;

        Sender;
        MoveJ p_assembly, v_fast, z30, tool1;
    ENDPROC

    PROC Axle()
        ! Role: Picks up the axle and places it in the assembly fixture, handing it off to the
        !       PLC's clamp.
        ! 역할: 축을 집어서 조립 고정구에 놓고, PLC 클램프가 잡도록 넘긴다.
        ! Process: pick up from p_axle_pickup/pickdown -> carry to p_assembly -> place at
        !          p_axle_assem_down -> the PLC's axle-gripper clamp takes over holding it.
        ! 과정: p_axle_pickup/pickdown에서 픽업 -> p_assembly로 이동 -> p_axle_assem_down에
        !       내려놓음 -> PLC의 축 그리퍼 클램프가 이어서 고정.
        SetDO do05_Axle_Cylinder_Forward, 1;
        MoveJ p_axle_pickup, v_fast, z30, tool1;
        MoveL p_axle_pickdown, v_slow, fine, tool1;
        Grip_On;
        SetDO do05_Axle_Cylinder_Forward, 0;
        MoveL p_axle_pickup, v_slow, fine, tool1;

        MoveL p_assembly, v_fast, z30, tool1;
        MoveL p_axle_assem_up, v_fast, z30, tool1;
        MoveL p_axle_assem_down, v_slow, fine, tool1;
        SetDO do07_Axle_Gripper_On, 1;
        Grip_Off;
        MoveL p_axle_assem_up, v_slow, fine, tool1;
    ENDPROC

    PROC Lower_Body()
        ! Role: Picks up the lower body chassis and sets it on top of the axle+tire assembly.
        ! 역할: 차체 하부를 집어서 축+타이어 조립체 위에 얹는다.
        ! Process: pick up from p_Lower_body_pickup/pickdown -> place at
        !          p_Lower_body_link/_down.
        ! 과정: p_Lower_body_pickup/pickdown에서 픽업 -> p_Lower_body_link/_down에 배치.
        MoveJ p_Lower_body_pickup, v_fast, z30, tool1;
        MoveL p_Lower_body_pickdown, v_slow, fine, tool1;
        Grip_On;
        MoveL p_Lower_body_pickup, v_slow, fine, tool1;

        MoveL p_assembly, v_fast, z30, tool1;
        MoveL p_Lower_body_link, v_fast, z30, tool1;
        MoveL p_Lower_body_link_down, v_slow, fine, tool1;
        Grip_Off;
        MoveL p_Lower_body_link, v_slow, fine, tool1;
    ENDPROC

    PROC Tier_Linked()
        ! Role: Picks up the 4 tires the PLC delivers one at a time and inserts each into its
        !       axle mount.
        ! 역할: PLC가 하나씩 공급하는 타이어 4개를 집어서 축의 각 장착 위치에 끼워 넣는다.
        ! Process: kick off the PLC tire-feed ladder once -> loop 4x (move to the tire pickup
        !          approach point, wait for arrival, descend and pick up, insert at the
        !          matching mount) -> return to the assembly point.
        ! 과정: PLC 타이어 공급 래더를 한 번 시작 -> 4번 반복(타이어 픽업 접근점으로 이동,
        !       도착 대기, 내려가서 집기, 해당 장착 위치에 끼우기) -> 조립 지점으로 복귀.
        ! Key variable: n_tireIndex (1-4) - selects which axle mount (p_tier_link_1~4) to use
        !               via TEST/CASE.
        ! 주요 변수: n_tireIndex (1~4) - TEST/CASE로 어떤 축 장착 위치(p_tier_link_1~4)를
        !            쓸지 고른다.
        VAR num n_tireIndex := 0;
        PulseDO \PLength := 0.2, do06_Tier_Start;

        FOR n_tireIndex FROM 1 TO 4 DO
            MoveJ p_tier_up, v_fast, z30, tool1;
            WaitDI di05_Tier_Arrive, 1;
            MoveL p_tier_down, v_slow, fine, tool1;
            ! Pick up the tire the PLC just delivered
            ! PLC가 방금 공급한 타이어를 집음
            Grip_On;
            MoveL p_tier_up, v_slow, fine, tool1;
            MoveJ p_assembly, v_fast, z30, tool1;

            TEST n_tireIndex
            CASE 1:
                MoveJ p_tier_link_1, v_fast, z30, tool1;
                MoveL p_tier_link_1_down, v_slow, fine, tool1;
                Grip_Off;
                MoveL p_tier_link_1, v_slow, fine, tool1;
            CASE 2:
                MoveJ p_tier_link_2, v_fast, z30, tool1;
                MoveL p_tier_link_2_down, v_slow, fine, tool1;
                Grip_Off;
                MoveL p_tier_link_2, v_slow, fine, tool1;
            CASE 3:
                MoveJ p_tier_link_3, v_fast, z30, tool1;
                MoveL p_tier_link_3_down, v_slow, fine, tool1;
                Grip_Off;
                MoveL p_tier_link_3, v_slow, fine, tool1;
            CASE 4:
                MoveJ p_tier_link_4, v_fast, z30, tool1;
                MoveL p_tier_link_4_down, v_slow, fine, tool1;
                Grip_Off;
                MoveL p_tier_link_4, v_slow, fine, tool1;
            ENDTEST
            MoveJ p_assembly, v_fast, z30, tool1;
            !MoveJ p_home, v_fast, z30, tool1;
        ENDFOR
    ENDPROC

    PROC Battery()
        ! Role: Picks up the battery and places it on the lower body.
        ! 역할: 배터리를 집어서 하부체 위에 놓는다.
        ! Process: pre-feed pulse to the PLC -> pick up from p_battery_pickup/pickdown ->
        !          place at p_battery_link_up/_down.
        ! 과정: PLC에 미리 공급 펄스 전송 -> p_battery_pickup/pickdown에서 픽업 ->
        !       p_battery_link_up/_down에 배치.
        PulseDO \PLength := 0.2, do08_Battery_Cylinder_Forward;

        MoveL p_battery_pickup, v_fast, z30, tool1;
        MoveL p_battery_pickdown, v_slow, fine, tool1;
        Grip_On;
        MoveL p_battery_pickup, v_slow, fine, tool1;

        MoveL p_assembly, v_fast, z30, tool1;
        MoveL p_battery_link_up, v_fast, z30, tool1;
        MoveL p_battery_link_down, v_slow, fine, tool1;
        Grip_Off;
        MoveL p_battery_link_up, v_slow, fine, tool1;
    ENDPROC

    PROC Motor()
        ! Role: Picks up the motor and mounts it on the assembly.
        ! 역할: 모터를 집어서 조립체에 장착한다.
        ! Process: pulse the PLC's motor signal -> pick up from p_motor_pickup/pickdown ->
        !          place at p_motor_linkup/linkdown.
        ! 과정: PLC 모터 신호 펄스 전송 -> p_motor_pickup/pickdown에서 픽업 ->
        !       p_motor_linkup/linkdown에 배치.
        PulseDO \PLength := 0.2, do10_motor;

        MoveL p_motor_pickup, v_fast, z30, tool1;
        MoveL p_motor_pickdown, v_slow, fine, tool1;
        Grip_On;
        MoveL p_motor_pickup, v_slow, fine, tool1;

        MoveL p_assembly, v_fast, z30, tool1;

        MoveL p_motor_linkup, v_fast, z30, tool1;
        MoveL p_motor_linkdown, v_slow, fine, tool1;
        Grip_Off;
        MoveL p_motor_linkup, v_slow, fine, tool1;
    ENDPROC

    PROC Welding()
        ! TODO: not implemented yet - no welding-station work exists for this cell
        ! TODO: 미구현 - 이 셀에는 아직 용접 스테이션 작업이 없음
    ENDPROC

    PROC Sender()
        ! Role: Picks up the whole finished assembly by suction and hands it off at the exit
        !       conveyor.
        ! 역할: 완성된 조립체 전체를 흡착으로 집어서 출하 컨베이어에 인계한다.
        ! Process: return to the lower-body grip point -> release the axle-gripper clamp as
        !          suction starts -> Grip_On confirms suction attached -> move to the exit
        !          conveyor -> release.
        ! 과정: 하부체 파지 지점으로 복귀 -> 흡착 시작과 동시에 축 그리퍼 클램프 해제 ->
        !       Grip_On으로 흡착 확인 -> 출하 컨베이어로 이동 -> 내려놓음.
        MoveL p_assembly_pickup, v_fast, z30, tool1;
        MoveL p_assembly_pickdown, v_slow, fine, tool1;
        Grip_On;
        SetDO do07_Axle_Gripper_On, 0;
        MoveL Offs(p_assembly_pickup, 0, 0, 150), v_slow, fine, tool1;

        MoveJ p_conveyor_Exit_up, v_fast, z30, tool1;
        MoveL p_conveyor_Exit_down, v_slow, fine, tool1;
        Grip_Off;
        MoveL p_conveyor_Exit_up, v_slow, fine, tool1;
        PulseDO \PLength := 0.2, do20_Exit_Conveyor;
    ENDPROC

    PROC Grip_On()
        ! Role: Closes the gripper and waits for the close-confirmed sensor.
        ! 역할: 그리퍼를 닫고 닫힘 확인 센서를 기다린다.
        ! Process: pulse do00_grip_on -> wait for di00_grip_on_sen -> settle 0.1s.
        ! 과정: do00_grip_on 펄스 -> di00_grip_on_sen 대기 -> 0.1초 안정화.
        PulseDO \PLength := 0.2, do00_grip_on;
        WaitDI di00_grip_on_sen, 1;
        WaitTime 0.1;
    ENDPROC

    PROC Grip_Off()
        ! Role: Opens the gripper and waits for the open-confirmed sensor.
        ! 역할: 그리퍼를 열고 열림 확인 센서를 기다린다.
        ! Process: pulse do01_grip_off -> wait for di01_grip_off_sen -> settle 0.1s.
        ! 과정: do01_grip_off 펄스 -> di01_grip_off_sen 대기 -> 0.1초 안정화.
        PulseDO \PLength := 0.2, do01_grip_off;
        WaitDI di01_grip_off_sen, 1;
        WaitTime 0.1;
    ENDPROC

ENDMODULE
