MODULE Example
    !******************************************************************
    !* Station : Example machine-tending cell (reference / training file)
    !******************************************************************
    !*
    !* Purpose:
    !*   This is NOT a copy of any specific factory's real production
    !*   program - no such proprietary source is available. It is built
    !*   from ABB's own official field-engineering standard, application
    !*   manual "RAPID development guidelines for handling applications"
    !*   (Document ID 3HAC046417-001, ABB Robotics, 2013), which is the
    !*   naming/structure convention ABB-certified system integrators are
    !*   trained to use on real customer cells. This file applies that
    !*   convention to a small made-up "pick from machine -> inspect ->
    !*   sort good/reject" cell so the pattern is visible in one file.
    !*
    !* What differs from project.mod (this repo's real tire cell):
    !*   - project.mod uses long descriptive names (p_conveyor1_down).
    !*     This file uses the terser station-number convention ABB's
    !*     manual defines (p10, p11, mv10_11 ...) - both are legitimate,
    !*     this file exists so you have seen the "official" style too.
    !*   - project.mod's targets are VAR robtarget (re-teachable by
    !*     jogging + Modify Position without reloading the module).
    !*     Here they are CONST robtarget, per the manual - safer against
    !*     accidental overwrite, but re-teaching needs a module reload.
    !*   - Error handling here uses RAISE + CONST errnum + an ERROR
    !*     handler (see Production and GripperClose/Open below), which
    !*     project.mod currently does not use anywhere.
    !*
    !* Naming prefixes used below (from the manual's naming table):
    !*   b = bool, n = num, p = robtarget, v = speeddata, t = tooldata,
    !*   w = wobjdata, di/do = digital in/out, ir = intnum (interrupt),
    !*   er = errnum, st = string, mvStart_End = movement routine.
    !*
    !* See RobotStudio/SETUP_LOG.md for the VSCode/extension side of the
    !* RAPID setup (why ENDMODULE/ENDIF suggestions work the way they do).
    !******************************************************************

    !**********************************************************
    !* Boolean declarations
    !**********************************************************
    ! Flag: operator requested "stop at end of cycle" (PLC panel or FlexPendant)
    VAR bool bProgEnd := FALSE;
    ! Flag: the part just inspected failed the check
    VAR bool bReject := FALSE;

    !**********************************************************
    !* Numeric declarations
    !**********************************************************
    ! How many rejects in a row before the cell pauses itself for an operator
    CONST num nMaxConsecutiveRejects := 3;
    VAR num nConsecutiveRejects := 0;

    ! User error numbers - the manual reserves 1-90 for RAISE in user code
    CONST errnum erGripperTimeout := 1;
    CONST errnum erTooManyRejects := 2;

    !**********************************************************
    !* Interrupt declarations
    !**********************************************************
    ! Fires when the PLC/FlexPendant asks for a controlled stop
    VAR intnum irCycleStop;

    !**********************************************************
    !* Tool / work object / speed data
    !**********************************************************
    PERS tooldata tGripper := [TRUE, [[0, 0, 130], [1, 0, 0, 0]], [5, [0, 0, 50], [1, 0, 0, 0], 0, 0, 0]];
    PERS wobjdata wStation1 := [FALSE, TRUE, "", [[0, 0, 0], [1, 0, 0, 0]], [[0, 0, 0], [1, 0, 0, 0]]];

    CONST speeddata vApproach := [1000, 500, 5000, 1000];    ! fast travel between prelim. positions
    CONST speeddata vPick := [200, 100, 5000, 1000];         ! careful speed for the actual pick/place move

    !**********************************************************
    !* Positions
    !*
    !* Naming: pXX = station XX. p99 = home, always last in the chain.
    !*   10 : Preliminary position at the machine door
    !*   11 : Pick position inside the machine
    !*   20 : Preliminary position at the inspection camera
    !*   21 : Inspection position (part held in front of camera)
    !*   60 : Preliminary position at the reject chute
    !*   61 : Place position at the reject chute
    !*   70 : Preliminary position at the good-part conveyor
    !*   71 : Place position at the good-part conveyor
    !*   99 : Home position
    !*
    !* NOTE: the coordinates below are placeholders (not taught on a real
    !* robot). Before running this on an actual controller you would jog
    !* to each position and use Modify Position, exactly like the points
    !* in project.mod were taught.
    !**********************************************************
    CONST robtarget p10 := [[600, 0, 600], [0, 0.7071068, 0.7071068, 0], [0, 0, 0, 0], [9E9, 9E9, 9E9, 9E9, 9E9, 9E9]];
    CONST robtarget p11 := [[600, 0, 400], [0, 0.7071068, 0.7071068, 0], [0, 0, 0, 0], [9E9, 9E9, 9E9, 9E9, 9E9, 9E9]];
    CONST robtarget p20 := [[300, 500, 600], [0, 0.7071068, 0.7071068, 0], [0, 0, 0, 0], [9E9, 9E9, 9E9, 9E9, 9E9, 9E9]];
    CONST robtarget p21 := [[300, 500, 500], [0, 0.7071068, 0.7071068, 0], [0, 0, 0, 0], [9E9, 9E9, 9E9, 9E9, 9E9, 9E9]];
    CONST robtarget p60 := [[0, 700, 600], [0, 0.7071068, 0.7071068, 0], [0, 0, 0, 0], [9E9, 9E9, 9E9, 9E9, 9E9, 9E9]];
    CONST robtarget p61 := [[0, 700, 450], [0, 0.7071068, 0.7071068, 0], [0, 0, 0, 0], [9E9, 9E9, 9E9, 9E9, 9E9, 9E9]];
    CONST robtarget p70 := [[0, -700, 600], [0, 0.7071068, 0.7071068, 0], [0, 0, 0, 0], [9E9, 9E9, 9E9, 9E9, 9E9, 9E9]];
    CONST robtarget p71 := [[0, -700, 450], [0, 0.7071068, 0.7071068, 0], [0, 0, 0, 0], [9E9, 9E9, 9E9, 9E9, 9E9, 9E9]];
    CONST robtarget p99 := [[0, 0, 900], [0, 0.7071068, 0.7071068, 0], [0, 0, 0, 0], [9E9, 9E9, 9E9, 9E9, 9E9, 9E9]];

    !**********************************************************
    !* Message strings
    !**********************************************************
    CONST string stStopCycle := "Stop at end of cycle requested";
    CONST string stTooManyRejects := "Too many consecutive rejects - cell paused, check part quality";
    CONST string stGripperTimeout := "Gripper sensor timeout - check air supply and finger sensors";

    !**********************************************************
    !* Procedure main
    !*
    !* Description:
    !*   Entry point. Runs one-time setup, then repeats Production
    !*   until the operator requests "stop at end of cycle".
    !**********************************************************
    PROC main()
        Init;
        mv99_10;

        WHILE NOT bProgEnd DO
            Production;
        ENDWHILE

        mv10_99;
        Stop;
    ENDPROC

    !**********************************************************
    !* Procedure Init
    !*
    !* Description:
    !*   One-time setup - outputs, flags and the cycle-stop interrupt.
    !**********************************************************
    PROC Init()
        Reset doGripperClose;
        Reset doCellError;

        bProgEnd := FALSE;
        nConsecutiveRejects := 0;

        IDelete irCycleStop;
        CONNECT irCycleStop WITH T_CycleStop;
        ISignalDI diCycleStopRequest, 1, irCycleStop;
    ENDPROC

    !**********************************************************
    !* Procedure Production
    !*
    !* Description:
    !*   One full pick -> inspect -> sort cycle. Uses RAISE/ERROR
    !*   instead of nesting the reject/good-part branches inside
    !*   more IFs, so both paths fall through to the same recovery
    !*   point if something goes wrong mid-cycle.
    !**********************************************************
    PROC Production()
        WaitDI diMachineReady, 1;

        mv10_11;
        GripperClose;
        mv11_10;

        mv10_20;
        mv20_21;
        InspectPart;
        mv21_20;

        IF bReject THEN
            nConsecutiveRejects := nConsecutiveRejects + 1;
            IF nConsecutiveRejects >= nMaxConsecutiveRejects THEN
                RAISE erTooManyRejects;
            ENDIF

            mv20_60;
            mv60_61;
            GripperOpen;
            mv61_60;
            mv60_10;
        ELSE
            nConsecutiveRejects := 0;

            mv20_70;
            mv70_71;
            GripperOpen;
            mv71_70;
            mv70_10;
        ENDIF

        RETURN;

    ERROR
        IF ERRNO = erTooManyRejects THEN
            TPWrite stTooManyRejects;
            SetDO doCellError, 1;
            bProgEnd := TRUE;
            TRYNEXT;
        ENDIF
    ENDPROC

    !**********************************************************
    !* Procedure InspectPart
    !*
    !* Description:
    !*   Reads the inspection sensor result and stores it in
    !*   bReject for Production to act on.
    !**********************************************************
    PROC InspectPart()
        WaitTime 0.2;
        bReject := diPartIsScrap = high;
    ENDPROC

    !**********************************************************
    !* Procedure GripperClose / GripperOpen
    !*
    !* Description:
    !*   Wraps the gripper I/O with a timeout so a stuck sensor
    !*   cannot hang the cell forever - see the known-issue list in
    !*   project.mod's CLAUDE.md for what happens when this guard
    !*   is missing (Grip_on/Grip_off there currently wait forever).
    !**********************************************************
    PROC GripperClose()
        SetDO doGripperClose, 1;
        WaitDI diGripperClosed, 1 \MaxTime:=2;

    ERROR
        IF ERRNO = ERR_WAIT_MAXTIME THEN
            TPWrite stGripperTimeout;
            RAISE erGripperTimeout;
        ENDIF
    ENDPROC

    PROC GripperOpen()
        Reset doGripperClose;
        WaitDI diGripperClosed, 0 \MaxTime:=2;

    ERROR
        IF ERRNO = ERR_WAIT_MAXTIME THEN
            TPWrite stGripperTimeout;
            RAISE erGripperTimeout;
        ENDIF
    ENDPROC

    !**********************************************************
    !* Movement routines
    !*
    !* Naming: mvStart_End. The first move of every routine is
    !* guarded by "IF OpMode() <> OP_AUTO" at reduced speed, so a
    !* worker free-running the routine from the FlexPendant in
    !* manual mode cannot fling the arm across the cell at full
    !* production speed - this exact guard is the pattern the ABB
    !* manual uses for every movement routine in its sample program.
    !**********************************************************
    PROC mv99_10()
        !From: Home position
        !To  : Preliminary position at the machine door
        IF OpMode() <> OP_AUTO MoveJ p99, v200, z10, tGripper \WObj:=wStation1;
        MoveJ p10, vApproach, z10, tGripper \WObj:=wStation1;
    ENDPROC

    PROC mv10_99()
        !From: Preliminary position at the machine door
        !To  : Home position
        IF OpMode() <> OP_AUTO MoveJ p10, v200, z10, tGripper \WObj:=wStation1;
        MoveJ p99, vApproach, z10, tGripper \WObj:=wStation1;
    ENDPROC

    PROC mv10_11()
        !From: Preliminary position at the machine door
        !To  : Pick position inside the machine
        IF OpMode() <> OP_AUTO MoveJ p10, v200, z10, tGripper \WObj:=wStation1;
        MoveL p11, vPick, fine, tGripper \WObj:=wStation1;
    ENDPROC

    PROC mv11_10()
        !From: Pick position inside the machine
        !To  : Preliminary position at the machine door
        MoveL p10, vApproach, z10, tGripper \WObj:=wStation1;
    ENDPROC

    PROC mv10_20()
        !From: Preliminary position at the machine door
        !To  : Preliminary position at the inspection camera
        MoveJ p20, vApproach, z10, tGripper \WObj:=wStation1;
    ENDPROC

    PROC mv20_21()
        !From: Preliminary position at the inspection camera
        !To  : Inspection position
        MoveL p21, vPick, fine, tGripper \WObj:=wStation1;
    ENDPROC

    PROC mv21_20()
        !From: Inspection position
        !To  : Preliminary position at the inspection camera
        MoveL p20, vApproach, z10, tGripper \WObj:=wStation1;
    ENDPROC

    PROC mv20_60()
        !From: Preliminary position at the inspection camera
        !To  : Preliminary position at the reject chute
        MoveJ p60, vApproach, z10, tGripper \WObj:=wStation1;
    ENDPROC

    PROC mv60_61()
        !From: Preliminary position at the reject chute
        !To  : Place position at the reject chute
        MoveL p61, vPick, fine, tGripper \WObj:=wStation1;
    ENDPROC

    PROC mv61_60()
        !From: Place position at the reject chute
        !To  : Preliminary position at the reject chute
        MoveL p60, vApproach, z10, tGripper \WObj:=wStation1;
    ENDPROC

    PROC mv60_10()
        !From: Preliminary position at the reject chute
        !To  : Preliminary position at the machine door
        MoveJ p10, vApproach, z10, tGripper \WObj:=wStation1;
    ENDPROC

    PROC mv20_70()
        !From: Preliminary position at the inspection camera
        !To  : Preliminary position at the good-part conveyor
        MoveJ p70, vApproach, z10, tGripper \WObj:=wStation1;
    ENDPROC

    PROC mv70_71()
        !From: Preliminary position at the good-part conveyor
        !To  : Place position at the good-part conveyor
        MoveL p71, vPick, fine, tGripper \WObj:=wStation1;
    ENDPROC

    PROC mv71_70()
        !From: Place position at the good-part conveyor
        !To  : Preliminary position at the good-part conveyor
        MoveL p70, vApproach, z10, tGripper \WObj:=wStation1;
    ENDPROC

    PROC mv70_10()
        !From: Preliminary position at the good-part conveyor
        !To  : Preliminary position at the machine door
        MoveJ p10, vApproach, z10, tGripper \WObj:=wStation1;
    ENDPROC

    !**********************************************************
    !* Trap: cycle-stop request
    !*
    !* Description:
    !*   The PLC/FlexPendant sets diCycleStopRequest to ask for a
    !*   controlled stop after the part in progress is placed,
    !*   instead of an abrupt Stop that could leave a part mid-air.
    !**********************************************************
    TRAP T_CycleStop
        TPWrite stStopCycle;
        bProgEnd := TRUE;
    ENDTRAP
ENDMODULE
