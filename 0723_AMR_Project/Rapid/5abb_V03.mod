! 신호 체계 - 입력
! di00_Axle_Cylinder_FDone          : 축 출고 완료
! di01_Axle_Gripper_Off             : 축 고정 off
! di02_Axle_Gripper_On              : 축 고정 of
! di03_Tier_Supply_Done             : 타이어 공급 완료
! di04_Battery_Supply_Done          : 배터리 공급 완료
! di05_Assembly_Cylinder_Forward    : 조립 축 전진 완료
! di06_Assembly_Cylinder_Back       : 조립 축 후진 완료
! di07_Motor_Supply_Done            : 모터 공급완료

! 신호 체계 - 출력
! do00_First_AD_On                  : 첫번째 흡착
! do01_Second_AD_ON                 : 두번째 흡착
! do02_Process_Start                : 공정시작 신호
! do03_Axle_Supply_Forward          : 축 공급 전진 명령
! do04_Axle_Supply_Back             : 축 공급 후진 명령
! do05_Assembly_Cylinder_Forward    : 조립 실린더 전진
! do06_Assembly_Cylinder_Back       : 조립 실린더 후진
! do07_Tier_Supply                  : 타이어 공급 명령
! do08_Axle_Gripper_On              : 축 고정 실행 명령
! do09_Axle_Gripper_Off             : 축 고정 해제 명령
! do10_Battery_Supply               : 배터리 공급 명령
! do11_Motor_Supply                 : 모터 공급 명령
! 

MODULE MainModule
    ! TCP tool data for the gripper - placeholder values, calibrate against the real tool before running
    ! 그리퍼 TCP 툴 데이터 - 아직 placeholder 값, 실제 툴로 캘리브레이션 필요
    TASK PERS tooldata tool1 := [
    TRUE,
    [[3.25653, -2.2499, 106.27], [1, 0, 0, 0]],
    [0.2, [0, 0, 50], [1, 0, 0, 0], 0, 0, 0]
    ];

    ! Uniform approach height above every taught contact point (axle/tire-feed/lower-body/
    ! battery/motor/exit-conveyor). Individually taught gaps ranged ~15-35mm; this collapses them
    ! to one number the code author can retune in one place.
    ! 모든 접촉 지점 위의 공통 접근 높이 (축/타이어 피드/하부체/배터리/모터/출하
    ! 컨베이어). 개별 티칭된 간격이 15~35mm 정도로 제각각이었는데, 이 값 하나로 통일해서
    ! 코드 작성자가 한 곳에서 조정할 수 있게 함.
    CONST num OFS_APPROACH := 25;

    ! Y-axis offset used only for the 4 tire axle mounts, since inserting a tire is a sideways
    ! slide onto the axle rather than a straight vertical descent (see p_tier_link_N).
    ! 타이어 4개 축 장착에만 쓰는 Y축 오프셋 - 타이어를 축에 끼우는 동작은 수직 하강이 아니라
    ! 옆으로 미끄러뜨리는 동작이라서 (p_tier_link_N 참고).
    CONST num OFS_TIRE_LINK := 20;

    ! Home / safe position the cycle starts and rests at
    ! 사이클이 시작·대기하는 홈(안전) 위치
    PERS robtarget p_home := [[375.37,20.48,540.81],[2.15925E-05,-0.419202,0.907893,6.67298E-05],[0,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    ! Central build fixture - the axle is set down here, and everything else stacks onto it
    ! 중앙 조립 고정구 - 축을 여기 내려놓고 나머지가 모두 그 위에 쌓임
    PERS robtarget p_assembly := [[497.19,-127.66,442.32],[1.93662E-05,0.436476,-0.899716,0.000120992],[-1,-1,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    ! ===== Axle station =====
    ! ===== 축 스테이션 =====
    ! Axle supply position - actual grip height. Approach = Offs(this, 0, 0, OFS_APPROACH).
    ! 축 공급 위치 - 실제 집는 높이. 접근점 = Offs(이 지점, 0, 0, OFS_APPROACH).
    PERS robtarget p_axle_pick := [[-93.42,363.15,197.04],[3.51739E-05,0.436476,-0.899716,0.000107992],[1,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    ! Actual place height where the axle is set down and clamped in the assembly fixture.
    ! 실제로 축을 조립 고정구에 내려놓고 고정하는 높이.
    PERS robtarget p_axle_assembly := [[493.52,-123.08,324.11],[2.95257E-05,0.39039,0.92065,-0.000114433],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    ! ===== Tire feed point (PLC ejects one tire at a time here) =====
    ! ===== 타이어 공급 지점 (PLC가 여기로 타이어를 한 개씩 배출함) =====
    ! Fixed tire pickup point - actual grip height.
    ! 고정 타이어 픽업 지점 - 실제 집는 높이.
    PERS robtarget p_tier := [[229.08,-577.33,234.38],[5.67595E-06,-0.384535,-0.92311,-5.66128E-06],[-1,-1,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    ! ===== Axle mounts (facing the axle from the front = looking at the car's rear) =====
    ! ===== 축 장착 위치 4개 (축을 정면에서 바라보면 = 자동차 후면을 보는 방향) =====
    ! Mount 1 (rear-left) - actual insert height. X shared with mount 2 (rear pair),
    ! Y shared with mount 3 (left pair) - both averaged from the 4 taught points.
    ! 장착 1(뒤-왼쪽) - 실제 끼우는 높이. X는 2번(뒤쪽 쌍)과, Y는 3번(왼쪽 쌍)과 공유 -
    ! 둘 다 티칭된 4개 값의 평균으로 최적화함.
    PERS robtarget p_tier_link_1 := [[425.83,-229.08,262.12],[0.278794,-0.278759,-0.649769,-0.649899],[-1,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    ! Mount 2 (rear-right) - actual insert height. X shared with mount 1, Y shared with mount 4.
    ! 장착 2(뒤-오른쪽) - 실제 끼우는 높이. X는 1번과, Y는 4번과 공유.
    PERS robtarget p_tier_link_2 := [[425.83,-24.41,262.12],[0.28272,0.282716,0.648107,-0.64815],[0,-1,1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    ! Mount 3 (front-left) - actual insert height. X shared with mount 4, Y shared with mount 1.
    ! 장착 3(앞-왼쪽) - 실제 끼우는 높이. X는 4번과, Y는 1번과 공유.
    PERS robtarget p_tier_link_3 := [[522.96,-229.08,262.12],[0.278765,-0.278763,-0.649792,-0.649886],[-1,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    ! Mount 4 (front-right) - actual insert height. X shared with mount 3, Y shared with mount 2.
    ! 장착 4(앞-오른쪽) - 실제 끼우는 높이. X는 3번과, Y는 2번과 공유.
    PERS robtarget p_tier_link_4 := [[522.96,-24.41,262.12],[0.282735,0.282741,0.648112,-0.648128],[0,-1,1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    ! ===== Lower body station (chassis supply location) =====
    ! ===== 하부체 스테이션 (차체 하부 공급 위치) =====
    ! Lower body chassis supply position - actual grip height. NOT YET TAUGHT (placeholder).
    ! 차체 하부 공급 위치 - 실제 집는 높이. 아직 티칭 안 됨(placeholder).
    PERS robtarget p_Lower_body_pick := [
    [342.30, -38.16, 327.52],
    [1.20614E-05, 0.456804, -0.889567, -5.42704E-06],
    [-1, -1, -1, 0],
    [9E+09, 9E+09, 9E+09, 9E+09, 9E+09, 9E+09]
    ];

    ! Where the lower body is set on the axle+tire assembly - actual place/grip height.
    ! 축+타이어 조립체 위에 하부체를 내려놓는 자리 - 실제 배치/파지 높이.
    PERS robtarget p_Lower_body_link := [[497.23,-132.60,342.88],[8.79376E-05,0.361499,-0.932372,8.08897E-05],[-1,-1,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    ! ===== Battery station (battery supply location) =====
    ! ===== 배터리 스테이션 (배터리 공급 위치) =====
    ! Battery supply position - actual grip height.
    ! 배터리 공급 위치 - 실제 집는 높이.
    PERS robtarget p_battery_pick := [[141.99,-423.67,191.53],[8.94231E-06,0.398496,-0.91717,-4.50033E-05],[-1,-1,-2,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    ! Where the battery is set on the lower body - actual place height.
    ! 하부체 위에 배터리를 내려놓는 자리 - 실제 배치 높이.
    PERS robtarget p_battery_link := [[468.42,-134.21,344.08],[5.26814E-05,0.403281,-0.915076,9.55054E-05],[-1,-1,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    ! ===== Motor station =====
    ! ===== 모터 스테이션 =====
    ! Motor supply position - actual grip height. NOT YET TAUGHT (placeholder).
    ! 모터 공급 위치 - 실제 집는 높이. 아직 티칭 안 됨(placeholder).
    PERS robtarget p_motor_pick := [
    [342.30, -38.16, 327.52],
    [1.20614E-05, 0.456804, -0.889567, -5.42704E-06],
    [-1, -1, -1, 0],
    [9E+09, 9E+09, 9E+09, 9E+09, 9E+09, 9E+09]
    ];

    ! Where the motor is mounted on the assembly - actual mount height. NOT YET TAUGHT (placeholder).
    ! 조립체에 모터를 장착하는 자리 - 실제 장착 높이. 아직 티칭 안 됨(placeholder).
    PERS robtarget p_motor_link := [
    [342.30, -38.16, 327.52],
    [1.20614E-05, 0.456804, -0.889567, -5.42704E-06],
    [-1, -1, -1, 0],
    [9E+09, 9E+09, 9E+09, 9E+09, 9E+09, 9E+09]
    ];

    ! ===== Final suction pickup (used in Sender to lift the whole finished assembly) =====
    ! ===== 최종 흡착 지점 (Sender에서 완성 조립체 전체를 들어올릴 때 씀) =====
    ! Actual grip height for the suction pickup of the whole finished assembly.
    ! 완성 조립체 전체를 흡착으로 집는 실제 높이.
    PERS robtarget p_assembly_pick := [[492.53,-129.06,338.88],[3.95473E-05,0.403272,-0.91508,0.000107178],[-1,-1,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    ! ===== Exit conveyor =====
    ! ===== 출하 컨베이어 =====
    ! Exit conveyor - actual place height where the finished assembly is set down.
    ! 출하 컨베이어 - 완성품을 내려놓는 실제 높이.
    PERS robtarget p_conveyor_Exit := [[327.18,287.76,260.85],[7.22898E-05,0.403284,-0.915075,0.000144839],[0,-1,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    ! Travel speed for empty or long moves
    ! 빈 상태 이동이나 장거리 이동에 쓰는 속도
    VAR speeddata v_fast := v200;
    ! Careful (slow) speed for pick/place moves
    ! 픽업/배치 동작에 쓰는 신중한(느린) 속도
    VAR speeddata v_slow := v50;

    ! ===== Socket server settings (edit these two when reusing this block on another robot) =====
    ! ===== 소켓 서버 설정 (다른 로봇에 이 블록을 재사용할 때 이 두 값만 수정) =====
    ! IP/port this ABB controller's socket server binds to.
    ! 이 ABB 컨트롤러의 소켓 서버가 바인딩할 IP/포트.
    CONST string ROBOT_IP := "192.168.3.3";
    CONST num ROBOT_PORT := 5000;

    ! Server-side socket handles and receive buffer shared by Run_Socket_Server/Start_Server/
    ! Close_All_Sockets/Handle_Command below. The "srv_" prefix keeps these names from
    ! clashing with the production-cycle variables declared above.
    ! 아래 Run_Socket_Server/Start_Server/Close_All_Sockets/Handle_Command가 공용으로 쓰는
    ! 서버측 소켓 핸들과 수신 버퍼. "srv_" 접두사로 위쪽 조립 사이클 변수들과 이름이
    ! 겹치지 않게 함.
    VAR socketdev srv_server_socket;
    VAR socketdev srv_client_socket;
    VAR string srv_received_string;
    VAR bool srv_keep_listening := TRUE;

    PROC Main()
        ! Role: Entry point - runs one-time setup, then waits for socket commands forever.
        ! 역할: 진입점 - 최초 설정을 한 번 실행한 뒤, 소켓 명령을 영원히 기다린다.
        ! Process: Init (accel + home + clear outputs) -> Run_Socket_Server (accepts a
        !          connector and runs Run_Assembly_Cycle whenever it receives "Start").
        ! 과정: Init(가속도 설정 + 홈 이동 + 출력 초기화) -> Run_Socket_Server(중계기
        !       접속을 받고 "Start"를 받을 때마다 Run_Assembly_Cycle을 실행).
        Init;

        !Run_Assembly_Cycle;
        Run_Socket_Server;
    ENDPROC

    PROC Init()
        ! Role: One-time setup before the socket server starts.
        ! 역할: 소켓 서버가 시작되기 전 최초 설정.
        ! Process: set acceleration -> move to home -> release both suction pads
        !          (Absorption_Off 3) -> clear every other output (axle supply, assembly
        !          cylinder forward/back, tire supply, axle gripper on/off, battery
        !          supply, motor supply) left on from a previous run.
        ! 과정: 가속도 설정 -> 홈으로 이동 -> 양쪽 흡착 패드 해제(Absorption_Off 3) ->
        !       이전 실행에서 남은 나머지 출력(축 공급, 조립 실린더 전진/후진, 타이어
        !       공급, 축 그리퍼 On/Off, 배터리 공급, 모터 공급)을 전부 초기화.
        AccSet 1, 1;
        MoveL p_home, v_fast, fine, tool1;

        Absorption_Off 3; !SetDo do00, do01 0
        
        SetDo do03_Axle_Supply_Forward, 0;
        SetDo do04_Axle_Supply_Back, 0;
        SetDO do05_Assembly_Cylinder_Forward, 0;
        SetDo do06_Assembly_Cylinder_Back, 0;
        SetDo do07_Tier_Supply, 0;
        SetDo do08_Axle_Gripper_On, 0;
        SetDo do09_Axle_Gripper_Off, 0;
        SetDo do10_Battery_Supply, 0;
        SetDo do11_Motor_Supply, 0;
        
    ENDPROC

    PROC Run_Socket_Server()
        ! Role: Waits for a connector to connect, then repeatedly waits for a command and
        !       dispatches it to Handle_Command. Rebuilds the connection if it drops.
        ! 역할: 중계기 접속을 기다렸다가, 명령을 받을 때마다 Handle_Command로 넘긴다.
        !       연결이 끊기면 다시 만든다.
        ! Process: Start_Server once -> WHILE(accept a connector -> WHILE(receive a
        !          command -> Handle_Command)) -> ERROR: retry on timeout, rebuild+retry
        !          on socket-closed, else log and stop.
        ! 과정: Start_Server 한 번 실행 -> WHILE(중계기 접속 대기 -> WHILE(명령 수신 ->
        !       Handle_Command)) -> ERROR: 타임아웃은 재시도, 소켓 끊김은 재구성 후
        !       재시도, 그 외는 로그 남기고 정지.
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
        ! 역할: 주어진 ip/port로 서버 소켓을 처음부터 다시 만든다.
        Close_All_Sockets;
        SocketCreate srv_server_socket;
        SocketBind srv_server_socket, ip, port;
        SocketListen srv_server_socket;
    ENDPROC

    PROC Close_All_Sockets()
        ! Role: Best-effort close - a socket that was never created raises an error here;
        !       TRYNEXT just skips to the next line instead of stopping the program.
        ! 역할: 최선을 다해 닫기를 시도 - 아직 한 번도 생성된 적 없는 소켓을 닫으려 하면
        !       여기서 에러가 나는데, TRYNEXT로 프로그램을 멈추지 않고 다음 줄로 넘어간다.
        SocketClose srv_server_socket;
        SocketClose srv_client_socket;
        ERROR
            TRYNEXT;
    ENDPROC

    PROC Handle_Command(string cmd)
        ! Role: Decides what to do for one received command - the only PROC to edit when
        !       reusing this socket-server block on a different robot/module.
        ! 역할: 받은 명령 하나에 대해 무엇을 할지 결정한다 - 이 소켓 서버 블록을 다른
        !       로봇/모듈에 재사용할 때 유일하게 고치면 되는 PROC.
        ! Process: "Start"/"start" runs the full assembly cycle; "End"/"END" and
        !          "Emergency" are reserved for later and do nothing yet.
        ! 과정: "Start"/"start"는 전체 조립 사이클을 실행; "End"/"END"와 "Emergency"는
        !       추후 사용을 위해 자리만 잡아둔 상태로 아직 아무 동작도 하지 않음.
        !IF (StrLen(cmd) >= 5) AND (StrPart(cmd, 1, 5) = "Start") THEN
        !        !MoveL p_assembly, v_moveSpeed, fine, tool1;
        !        TPWrite "Move done";
        !        Run_Assembly_Cycle;

        !ELSEIF (StrLen(cmd) >= 3) AND (StrPart(cmd, 1, 3) = "End") THEN
            ! 미정

        !ELSEIF (StrLen(cmd) >= 9) AND (StrPart(cmd, 1, 9) = "Emergency") THEN
            ! 미정
        !ENDIF
        IF cmd = "Start" OR cmd = "start" THEN
            TPWrite "Move Start";
            Run_Assembly_Cycle;
        ELSEIF cmd = "End" OR cmd = "END" THEN
            !미정
        ELSEIF cmd = "Emergency" THEN
            !미정
        ENDIF
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
        ! Process: pulse do03_Axle_Supply to request an axle -> approach p_axle_pick and
        !          wait for di00_Axle_Cylinder_FDone -> descend and grab by suction ->
        !          pulse do08_Axle_Gripper_Off and wait for di01_Axle_Gripper_Off to
        !          release the supply-side fixture -> carry to p_assembly -> place at
        !          p_axle_assembly -> pulse do07_Axle_Gripper_On and wait for
        !          di02_Axle_Gripper_On so the PLC's clamp takes over -> release suction.
        ! 과정: do03_Axle_Supply 펄스로 축 공급 요청 -> p_axle_pick으로 접근하며
        !       di00_Axle_Cylinder_FDone 대기 -> 내려가서 흡착으로 집음 ->
        !       do08_Axle_Gripper_Off 펄스 + di01_Axle_Gripper_Off 대기로 공급측 고정을
        !       해제 -> p_assembly로 이동 -> p_axle_assembly에 배치 ->
        !       do07_Axle_Gripper_On 펄스 + di02_Axle_Gripper_On 대기로 PLC 클램프가
        !       이어받게 함 -> 흡착 해제.
        PulseDO\PLength := 0.2,  do03_Axle_Supply_Forward;
        MoveJ Offs(p_axle_pick, 0, 0, OFS_APPROACH), v_fast, z30, tool1;
        WaitDI di00_Axle_Cylinder_FDone, 1;
        MoveL p_axle_pick, v_slow, fine, tool1;
        Absorption_On 3;
        PulseDo\PLength := 0.2, do09_Axle_Gripper_Off;
        WaitDI di01_Axle_Gripper_Off, 1;
        MoveL Offs(p_axle_pick, 0, 0, OFS_APPROACH), v_slow, fine, tool1;
        PulseDO\PLength := 0.2,  do04_Axle_Supply_Back;

        MoveL p_assembly, v_fast, z30, tool1;
        MoveL Offs(p_axle_assembly, 0, 0, OFS_APPROACH), v_fast, z30, tool1;
        MoveL p_axle_assembly, v_slow, fine, tool1;
        PulseDO\PLength := 0.2, do08_Axle_Gripper_On;
        WaitDI di02_Axle_Gripper_On, 1;
        Absorption_Off 3;
        MoveL Offs(p_axle_assembly, 0, 0, OFS_APPROACH), v_slow, fine, tool1;
    ENDPROC

    PROC Lower_Body()
        ! Role: Picks up the lower body chassis and sets it on top of the axle+tire assembly.
        ! 역할: 차체 하부를 집어서 축+타이어 조립체 위에 얹는다.
        ! Process: pick up from p_Lower_body_pick by suction -> place at p_Lower_body_link
        !          (approach points via Offs+OFS_APPROACH on both ends).
        ! 과정: p_Lower_body_pick에서 흡착으로 픽업 -> p_Lower_body_link에 배치
        !       (양쪽 접근점 모두 Offs+OFS_APPROACH 사용).
        MoveJ Offs(p_Lower_body_pick, 0, 0, OFS_APPROACH), v_fast, z30, tool1;
        MoveL p_Lower_body_pick, v_slow, fine, tool1;
        Absorption_On 3;
        MoveL Offs(p_Lower_body_pick, 0, 0, OFS_APPROACH), v_slow, fine, tool1;

        MoveL p_assembly, v_fast, z30, tool1;
        MoveL Offs(p_Lower_body_link, 0, 0, OFS_APPROACH), v_fast, z30, tool1;
        MoveL p_Lower_body_link, v_slow, fine, tool1;
        Absorption_Off 3;
        MoveL Offs(p_Lower_body_link, 0, 0, OFS_APPROACH), v_slow, fine, tool1;
    ENDPROC

    PROC Tier_Linked()
        ! Role: Picks up the 4 tires the PLC delivers one at a time and inserts each into its
        !       axle mount.
        ! 역할: PLC가 하나씩 공급하는 타이어 4개를 집어서 축의 각 장착 위치에 끼워 넣는다.
        ! Process: kick off the PLC tire-feed ladder once -> loop 4x (approach p_tier via
        !          Offs+OFS_APPROACH, wait for di03_Tier_Supply_Done, descend and pick up
        !          by suction, insert at the matching mount via Offs+OFS_TIRE_LINK on the
        !          Y axis) -> return to assembly.
        ! 과정: PLC 타이어 공급 래더를 한 번 시작 -> 4번 반복(Offs+OFS_APPROACH로 p_tier
        !       접근, di03_Tier_Supply_Done 대기, 내려가서 흡착으로 집기,
        !       Offs+OFS_TIRE_LINK로 Y축 방향에서 해당 장착 위치에 끼우기) -> 조립
        !       지점으로 복귀.
        ! Key variable: n_tireIndex (1-4) - selects which axle mount (p_tier_link_1~4)
        !               to use via TEST/CASE. Odd (1,3)=left side, so the Y approach offset is
        !               negative; even (2,4)=right side, so it is positive.
        ! 주요 변수: n_tireIndex (1~4) - TEST/CASE로 어떤 축 장착 위치를 쓸지 고른다. 홀수
        !            (1,3)=왼쪽이라 Y 접근 오프셋이 음수, 짝수(2,4)=오른쪽이라 양수.
        VAR num n_tireIndex := 0;
        PulseDO \PLength := 0.2, do07_Tier_Supply;

        FOR n_tireIndex FROM 1 TO 4 DO
            MoveJ Offs(p_tier, 0, 0, OFS_APPROACH), v_fast, z30, tool1;
            WaitDI di03_Tier_Supply_Done, 1;
            MoveL p_tier, v_slow, fine, tool1;
            ! Pick up the tire the PLC just delivered
            ! PLC가 방금 공급한 타이어를 집음
            Absorption_On 1;
            MoveL Offs(p_tier, 0, 0, OFS_APPROACH), v_slow, fine, tool1;
            MoveJ p_assembly, v_fast, z30, tool1;

            TEST n_tireIndex
            CASE 1:
                MoveJ Offs(p_tier_link_1, 0, -OFS_TIRE_LINK, 0), v_fast, z30, tool1;
                MoveL p_tier_link_1, v_slow, fine, tool1;
                Absorption_Off 1;
                MoveL Offs(p_tier_link_1, 0, -OFS_TIRE_LINK, 0), v_slow, fine, tool1;
            CASE 2:
                MoveJ Offs(p_tier_link_2, 0, OFS_TIRE_LINK, 0), v_fast, z30, tool1;
                MoveL p_tier_link_2, v_slow, fine, tool1;
                Absorption_Off 1;
                MoveL Offs(p_tier_link_2, 0, OFS_TIRE_LINK, 0), v_slow, fine, tool1;
            CASE 3:
                MoveJ Offs(p_tier_link_3, 0, -OFS_TIRE_LINK, 0), v_fast, z30, tool1;
                MoveL p_tier_link_3, v_slow, fine, tool1;
                Absorption_Off 1;
                MoveL Offs(p_tier_link_3, 0, -OFS_TIRE_LINK, 0), v_slow, fine, tool1;
            CASE 4:
                MoveJ Offs(p_tier_link_4, 0, OFS_TIRE_LINK, 0), v_fast, z30, tool1;
                MoveL p_tier_link_4, v_slow, fine, tool1;
                Absorption_Off 1;
                MoveL Offs(p_tier_link_4, 0, OFS_TIRE_LINK, 0), v_slow, fine, tool1;
            ENDTEST
            MoveJ p_assembly, v_fast, z30, tool1;
            !MoveJ p_home, v_fast, z30, tool1;
        ENDFOR
    ENDPROC

    PROC Battery()
        ! Role: Picks up the battery and places it on the lower body.
        ! 역할: 배터리를 집어서 하부체 위에 놓는다.
        ! Process: pre-feed pulse to the PLC (do09_Battery_Supply) -> approach and wait
        !          for di04_Battery_Supply_Done -> pick up from p_battery_pick by suction
        !          -> place at p_battery_link (approach points via Offs+OFS_APPROACH).
        ! 과정: PLC에 미리 공급 펄스 전송(do09_Battery_Supply) -> 접근 후
        !       di04_Battery_Supply_Done 대기 -> p_battery_pick에서 흡착으로 픽업 ->
        !       p_battery_link에 배치 (접근점은 Offs+OFS_APPROACH).
        PulseDO \PLength := 0.2, do10_Battery_Supply;

        MoveL Offs(p_battery_pick, 0, 0, OFS_APPROACH), v_fast, z30, tool1;
        WaitDI di04_Battery_Supply_Done, 1;
        MoveL p_battery_pick, v_slow, fine, tool1;
        Absorption_On 3;
        MoveL Offs(p_battery_pick, 0, 0, OFS_APPROACH), v_slow, fine, tool1;

        MoveL p_assembly, v_fast, z30, tool1;
        MoveL Offs(p_battery_link, 0, 0, OFS_APPROACH), v_fast, z30, tool1;
        MoveL p_battery_link, v_slow, fine, tool1;
        Absorption_Off 3;
        MoveL Offs(p_battery_link, 0, 0, OFS_APPROACH), v_slow, fine, tool1;
    ENDPROC

    PROC Motor()
        ! Role: Picks up the motor and mounts it on the assembly.
        ! 역할: 모터를 집어서 조립체에 장착한다.
        ! Process: pulse the PLC's motor signal (do10_motor) -> approach and wait for
        !          di07_Motor_Supply_Done -> pick up from p_motor_pick by suction -> place
        !          at p_motor_link (approach points via Offs+OFS_APPROACH).
        ! 과정: PLC 모터 신호 펄스 전송(do10_motor) -> 접근 후 di07_Motor_Supply_Done
        !       대기 -> p_motor_pick에서 흡착으로 픽업 -> p_motor_link에 배치 (접근점은
        !       Offs+OFS_APPROACH).
        PulseDO \PLength := 0.2, do11_Motor_Supply;

        MoveL Offs(p_motor_pick, 0, 0, OFS_APPROACH), v_fast, z30, tool1;
        WaitDI di07_Motor_Supply_Done, 1;
        MoveL p_motor_pick, v_slow, fine, tool1;
        Absorption_On 3;
        MoveL Offs(p_motor_pick, 0, 0, OFS_APPROACH), v_slow, fine, tool1;

        MoveL p_assembly, v_fast, z30, tool1;

        MoveL Offs(p_motor_link, 0, 0, OFS_APPROACH), v_fast, z30, tool1;
        MoveL p_motor_link, v_slow, fine, tool1;
        Absorption_Off 3;
        MoveL Offs(p_motor_link, 0, 0, OFS_APPROACH), v_slow, fine, tool1;
    ENDPROC

    PROC Welding()
        ! TODO: not implemented yet - no welding-station work exists for this cell
        ! TODO: 미구현 - 이 셀에는 아직 용접 스테이션 작업이 없음
    ENDPROC

    PROC Sender()
        ! Role: Picks up the whole finished assembly by suction and hands it off at the exit
        !       conveyor.
        ! 역할: 완성된 조립체 전체를 흡착으로 집어서 출하 컨베이어에 인계한다.
        ! Process: approach/grab p_assembly_pick by suction -> release the axle-gripper
        !          clamp as suction starts -> retreat extra high (OFS_APPROACH + 150) to
        !          clear the fixture -> move to the exit conveyor -> release.
        ! 과정: p_assembly_pick을 흡착으로 접근/파지 -> 흡착 시작과 동시에 축 그리퍼
        !       클램프 해제 -> 고정구를 벗어나도록 평소보다 높이(OFS_APPROACH + 150)
        !       이탈 -> 출하 컨베이어로 이동 -> 내려놓음.
        MoveL Offs(p_assembly_pick, 0, 0, OFS_APPROACH), v_fast, z30, tool1;
        MoveL p_assembly_pick, v_slow, fine, tool1;
        Absorption_On 1;
        SetDO do07_Axle_Gripper_On, 0;
        MoveL Offs(p_assembly_pick, 0, 0, OFS_APPROACH + 150), v_slow, fine, tool1;

        MoveJ Offs(p_conveyor_Exit, 0, 0, OFS_APPROACH), v_fast, z30, tool1;
        MoveL p_conveyor_Exit, v_slow, fine, tool1;
        Absorption_Off 1;
        MoveL Offs(p_conveyor_Exit, 0, 0, OFS_APPROACH), v_slow, fine, tool1;
        PulseDO \PLength := 0.2, do20_Exit_Conveyor;
    ENDPROC

    PROC Absorption_On(num SetNum)
        ! Role: Turns on one or both suction pads to grab a part.
        ! 역할: 흡착 패드 하나 또는 둘 다 켜서 부품을 붙잡는다.
        ! Process: SetNum selects which pad(s) - 1 = first pad only, 2 = second pad only,
        !          3 = both pads - then settles 0.3s for the vacuum to build.
        ! 과정: SetNum으로 어떤 패드를 켤지 선택 - 1=첫번째 패드만, 2=두번째 패드만,
        !       3=둘 다 - 켠 뒤 진공이 형성되도록 0.3초 대기.
        ! Key variable: SetNum (1-3) - 1/2 use a single pad, 3 uses both together.
        ! 주요 변수: SetNum (1~3) - 1/2는 패드 하나만, 3은 둘 다 함께 사용.
        IF SetNum = 1 THEN
            SetDo do00_First_AD_On, 1;
            WaitTime 0.3;
        ELSEIF SetNum = 2 THEN
            SetDo do01_Secend_AD_On, 1;
            WaitTime 0.3;
        ELSEIF SetNum = 3 THEN
            SetDo do00_First_AD_On, 1;
            SetDo do01_Secend_AD_On, 1;
            WaitTime 0.3;
        ENDIF
    ENDPROC

    PROC Absorption_Off(num SetNum)
        ! Role: Turns off one or both suction pads to release a part.
        ! 역할: 흡착 패드 하나 또는 둘 다 꺼서 부품을 놓는다.
        ! Process: SetNum selects which pad(s) - 1 = first pad only, 2 = second pad only,
        !          3 = both pads - then settles 0.3s.
        ! 과정: SetNum으로 어떤 패드를 끌지 선택 - 1=첫번째 패드만, 2=두번째 패드만,
        !       3=둘 다 - 끈 뒤 0.3초 대기.
        ! Key variable: SetNum (1-3) - 1/2 use a single pad, 3 uses both together.
        ! 주요 변수: SetNum (1~3) - 1/2는 패드 하나만, 3은 둘 다 함께 사용.
        IF SetNum = 1 THEN
            SetDo do00_First_AD_On, 0;
            WaitTime 0.3;
        ELSEIF SetNum = 2 THEN
            SetDo do01_Secend_AD_On, 0;
            WaitTime 0.3;
        ELSEIF SetNum = 3 THEN
            SetDo do00_First_AD_On, 0;
            SetDo do01_Secend_AD_On, 0;
            WaitTime 0.3;
        ENDIF
    ENDPROC

ENDMODULE
