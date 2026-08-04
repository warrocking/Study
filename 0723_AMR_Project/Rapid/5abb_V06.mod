MODULE MainModule

    ! ?? ?? - ??
! di00_Axle_Cylinder_FDone          : ? ?? ??
! di01_Axle_Gripper_Off             : ? ?? off
! di02_Axle_Gripper_On              : ? ?? of
! di03_Tier_Supply_Done             : ??? ?? ??
! di04_Battery_Supply_Done          : ??? ?? ??
! di05_Assembly_Cylinder_Forward    : ?? ? ?? ??
! di06_Assembly_Cylinder_Back       : ?? ? ?? ??
! di07_Motor_Supply_Done            : ?? ????

! ?? ?? - ??
! do00_First_AD_On                  : ??? ??
! do01_Second_AD_ON                 : ??? ??
! do02_Process_Start                : ???? ??
! do03_Axle_Supply_Forward          : ? ?? ?? ??
! do04_Axle_Supply_Back             : ? ?? ?? ??
! do05_Assembly_Cylinder_Forward    : ?? ??? ??
! do06_Assembly_Cylinder_Back       : ?? ??? ??
! do07_Tier_Supply                  : ??? ?? ??
! do08_Axle_Gripper_On              : ? ?? ?? ??
! do09_Axle_Gripper_Off             : ? ?? ?? ??
! do10_Battery_Supply               : ??? ?? ??
! do11_Motor_Supply                 : ?? ?? ??
!



    ! TCP tool data for the gripper - placeholder values, calibrate against the real tool before running
    ! ??? TCP ? ??? - ?? placeholder ?, ?? ?? ?????? ??


    ! Uniform approach height above every taught contact point (axle/tire-feed/lower-body/
    ! battery/motor/exit-conveyor). Individually taught gaps ranged ~15-35mm; this collapses them
    ! to one number the code author can retune in one place.
    ! ?? ?? ?? ?? ?? ?? ?? (?/??? ??/???/???/??/??
    ! ????). ?? ??? ??? 15~35mm ??? ???????, ? ? ??? ????
    ! ?? ???? ? ??? ??? ? ?? ?.
    CONST num OFS_APPROACH := 25;

    ! Y-axis offset used only for the 4 tire axle mounts, since inserting a tire is a sideways
    ! slide onto the axle rather than a straight vertical descent (see p_tier_link_N).
    ! ??? 4? ? ???? ?? Y? ??? - ???? ?? ??? ??? ?? ??? ???
    ! ??? ?????? ????? (p_tier_link_N ??).
    CONST num OFS_TIRE_LINK := 20;

    ! Home / safe position the cycle starts and rests at
    ! ???? ?????? ?(??) ??
    PERS robtarget p_home := [[375.37,20.48,540.81],[2.15925E-05,-0.419202,0.907893,6.67298E-05],[0,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    ! Central build fixture - the axle is set down here, and everything else stacks onto it
    ! ?? ?? ??? - ?? ?? ???? ???? ?? ? ?? ??
    PERS robtarget p_assembly := [[483.42,-128.61,396.52],[3.32078E-05,-0.391804,0.920049,-2.49801E-05],[-1,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    ! ===== Axle station =====
    ! ===== ? ???? =====
    ! Axle supply position - actual grip height. Approach = Offs(this, 0, 0, OFS_APPROACH).
    ! ? ?? ?? - ?? ?? ??. ??? = Offs(? ??, 0, 0, OFS_APPROACH).
    PERS robtarget p_axle_pick := [[230.09,-216.34,170.95],[6.43192E-05,-0.378543,-0.925584,0.000120746],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    ! Actual place height where the axle is set down and clamped in the assembly fixture.
    ! ??? ?? ?? ???? ???? ???? ??.
    PERS robtarget p_axle_assembly := [[493.52,-123.08,324.11],[2.95257E-05,0.39039,0.92065,-0.000114433],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    ! ===== Tire feed point (PLC ejects one tire at a time here) =====
    ! ===== ??? ?? ?? (PLC? ??? ???? ? ?? ???) =====
    ! Fixed tire pickup point - actual grip height.
    ! ?? ??? ?? ?? - ?? ?? ??.
    PERS robtarget p_tier := [[233.42,-577.36,176.15],[3.31494E-06,-0.424953,-0.905216,0.000109129],[-1,-1,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    ! ===== Axle mounts (facing the axle from the front = looking at the car's rear) =====
    ! ===== ? ?? ?? 4? (?? ???? ???? = ??? ??? ?? ??) =====
    ! Mount 1 (rear-left) - actual insert height. X shared with mount 2 (rear pair),
    ! Y shared with mount 3 (left pair) - both averaged from the 4 taught points.
    ! ?? 1(?-??) - ?? ??? ??. X? 2?(?? ?)?, Y? 3?(?? ?)? ?? -
    ! ? ? ??? 4? ?? ???? ????.
    !PERS robtarget p_tier_1_link := [[425.83,-229.08,262.12],[0.278794,-0.278759,-0.649769,-0.649899],[-1,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    ! Mount 2 (rear-right) - actual insert height. X shared with mount 1, Y shared with mount 4.
    ! ?? 2(?-???) - ?? ??? ??. X? 1??, Y? 4?? ??.
    !PERS robtarget p_tier_link_2 := [[425.83,-24.41,262.12],[0.28272,0.282716,0.648107,-0.64815],[0,-1,1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    ! Mount 3 (front-left) - actual insert height. X shared with mount 4, Y shared with mount 1.
    ! ?? 3(?-??) - ?? ??? ??. X? 4??, Y? 1?? ??.
    !PERS robtarget p_tier_link_3 := [[522.96,-229.08,262.12],[0.278765,-0.278763,-0.649792,-0.649886],[-1,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    ! Mount 4 (front-right) - actual insert height. X shared with mount 3, Y shared with mount 2.
    ! ?? 4(?-???) - ?? ??? ??. X? 3??, Y? 2?? ??.
    !PERS robtarget p_tier_link_4 := [[522.96,-24.41,262.12],[0.282735,0.282741,0.648112,-0.648128],[0,-1,1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    ! ===== Tire insertion swing points (via-point for MoveC on the way into each mount) =====
    ! ===== ??? ?? ?? ??? (? ?? ??? ??? ? MoveC? ???? ?) =====
    ! One via-point per mount, roughly halfway between p_assembly and that mount in both
    ! position and orientation, so MoveC sweeps the tire from horizontal to vertical along
    ! a single smooth arc instead of snapping straight to the mount's orientation.
    ! NOT YET TAUGHT (placeholder = p_assembly's value for now - re-teach for real use).
    ! ?? ???? ??? ??? - p_assembly? ?? ?? ??? ??? ?? ??/????
    ! ???, MoveC? ???? ???? ???? ??? ???? ???? ??? ?.
    ! ?? ?? ? ?(placeholder = ??? p_assembly ? ??? - ?? ?? ? ??? ??).
    PERS robtarget p_tier_link_1_swing := [[483.42,-128.61,396.52],[3.32078E-05,-0.391804,0.920049,-2.49801E-05],[-1,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_tier_link_3_swing := [[483.42,-128.61,396.52],[3.32078E-05,-0.391804,0.920049,-2.49801E-05],[-1,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_tier_link_4_swing := [[522.26,-55.29,296.20],[0.164304,0.341149,0.832786,-0.403844],[0,-1,1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    ! ===== Mount 2's swing-in via-points (Tier_2_Swing_In/Out) =====
    ! ===== 2? ?? ?? ??? (Tier_2_Swing_In/Out?? ??) =====
    ! Two taught via-points between p_assembly (0 deg, tire hole horizontal) and mount 2's
    ! 90-degree approach point - roughly 30 deg and 60 deg turned. Position AND orientation
    ! both change gradually across p_assembly -> swing30 -> swing60 -> the mount, so the
    ! whole sweep looks like one continuous turn instead of snapping straight to 90 deg.
    ! NOT YET TAUGHT (placeholder = p_assembly's value for now - re-teach for real use).
    ! p_assembly(0?, ??? ??? ??)? 2? ?? 90? ??? ??? ??? ???
    ! 2? - ?? 30?, 60? ?? ??. p_assembly -> swing30 -> swing60 -> ?? ???
    ! ??? ??/??? ??? ????, ??? 90?? ?? ??? ?? ??? ????
    ! ???? ??? ?. ?? ?? ? ?(placeholder = ??? p_assembly ? ??? -
    ! ?? ?? ? ??? ??).
    PERS robtarget p_tier_link_2_swing30 := [[483.42,-128.61,396.52],[3.32078E-05,-0.391804,0.920049,-2.49801E-05],[-1,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_tier_link_2_swing60 := [[483.42,-128.61,396.52],[3.32078E-05,-0.391804,0.920049,-2.49801E-05],[-1,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    ! ===== Lower body station (chassis supply location) =====
    ! ===== ??? ???? (?? ?? ?? ??) =====
    ! Lower body chassis supply position - actual grip height. NOT YET TAUGHT (placeholder).
    ! ?? ?? ?? ?? - ?? ?? ??. ?? ?? ? ?(placeholder).
    PERS robtarget p_Lower_body_pick := [
    [342.30, -38.16, 327.52],
    [1.20614E-05, 0.456804, -0.889567, -5.42704E-06],
    [-1, -1, -1, 0],
    [9E+09, 9E+09, 9E+09, 9E+09, 9E+09, 9E+09]
    ];

    ! Where the lower body is set on the axle+tire assembly - actual place/gripi height.
    ! ?+??? ??? ?? ???? ???? ?? - ?? ??/?? ??.
    PERS robtarget p_Lower_body_link := [[497.23,-132.60,342.88],[8.79376E-05,0.361499,-0.932372,8.08897E-05],[-1,-1,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    ! ===== Battery station (battery supply location) =====
    ! ===== ??? ???? (??? ?? ??) =====
    ! Battery supply position - actual grip height.
    ! ??? ?? ?? - ?? ?? ??.
    PERS robtarget p_battery_pick := [[141.99,-423.67,191.53],[8.94231E-06,0.398496,-0.91717,-4.50033E-05],[-1,-1,-2,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    ! Where the battery is set on the lower body - actual place height.
    ! ??? ?? ???? ???? ?? - ?? ?? ??.
    PERS robtarget p_battery_link := [[468.42,-134.21,344.08],[5.26814E-05,0.403281,-0.915076,9.55054E-05],[-1,-1,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    ! ===== Motor station =====
    ! ===== ?? ???? =====
    ! Motor supply position - actual grip height. NOT YET TAUGHT (placeholder).
    ! ?? ?? ?? - ?? ?? ??. ?? ?? ? ?(placeholder).
    PERS robtarget p_motor_pick := [
    [342.30, -38.16, 327.52],
    [1.20614E-05, 0.456804, -0.889567, -5.42704E-06],
    [-1, -1, -1, 0],
    [9E+09, 9E+09, 9E+09, 9E+09, 9E+09, 9E+09]
    ];

    ! Where the motor is mounted on the assembly - actual mount height. NOT YET TAUGHT (placeholder).
    ! ???? ??? ???? ?? - ?? ?? ??. ?? ?? ? ?(placeholder).
    PERS robtarget p_motor_link := [
    [342.30, -38.16, 327.52],
    [1.20614E-05, 0.456804, -0.889567, -5.42704E-06],
    [-1, -1, -1, 0],
    [9E+09, 9E+09, 9E+09, 9E+09, 9E+09, 9E+09]
    ];

    ! ===== Final suction pickup (used in Sender to lift the whole finished assembly) =====
    ! ===== ?? ?? ?? (Sender?? ?? ??? ??? ???? ? ?) =====
    ! Actual grip height for the suction pickup of the whole finished assembly.
    ! ?? ??? ??? ???? ?? ?? ??.
    PERS robtarget p_assembly_pick := [[492.53,-129.06,338.88],[3.95473E-05,0.403272,-0.91508,0.000107178],[-1,-1,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    ! ===== Exit conveyor =====
    ! ===== ?? ???? =====
    ! Exit conveyor - actual place height where the finished assembly is set down.
    ! ?? ???? - ???? ???? ?? ??.
    PERS robtarget p_conveyor_Exit := [[327.18,287.76,260.85],[7.22898E-05,0.403284,-0.915075,0.000144839],[0,-1,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    ! Travel speed for empty or long moves
    ! ? ?? ???? ??? ??? ?? ??
    VAR speeddata v_fast := v200;
    ! Careful (slow) speed for pick/place moves
    ! ??/?? ??? ?? ???(??) ??
    VAR speeddata v_slow := v50;

    ! ===== Socket server settings (edit these two when reusing this block on another robot) =====
    ! ===== ?? ?? ?? (?? ??? ? ??? ???? ? ? ? ?? ??) =====
    ! IP/port this ABB controller's socket server binds to.
    ! ? ABB ????? ?? ??? ???? IP/??.
    CONST string ROBOT_IP := "192.168.3.3";
    CONST num ROBOT_PORT := 5000;

    PERS robtarget p_tier_1_Set:= [[429.70,-210.20,280.23],[2.23864E-05,0.367494,0.930026,7.99124E-06],[-1,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_tier_1_15 := [[429.70,-210.20,280.23],[0.147489,-0.368498,-0.887163,-0.235367],[-1,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_tier_1_30 := [[429.70,-210.20,280.23],[0.229467,-0.350747,-0.851801,-0.314257],[-1,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_tier_1_45 := [[429.70,-210.20,280.23],[0.229625,-0.353793,-0.812087,-0.403258],[-1,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_tier_1_60 := [[429.70,-210.20,280.23],[0.270611,-0.334972,-0.787527,-0.440867],[-1,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_tier_1_75 := [[429.70,-210.20,280.23],[0.297597,-0.321358,-0.726748,-0.529152],[-1,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_tier_1_90 := [[426.91,-213.96,262.85],[0.31262,-0.312576,-0.634218,-0.634297],[-1,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_tier_1_link := [[426.89,-167.42,262.86],[0.312652,-0.312574,-0.634202,-0.634298],[-1,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    ! ===== Tire 1 - evenly re-spaced via-points (Set/90/link kept exactly as taught; only
    !       15/30/45/60/75 recomputed by splitting the Set->90 rotation into 6 equal steps) =====
    ! ===== 타이어 1 - 균등 재배치 경유점 (Set/90/link은 원래 티칭값 그대로; 15/30/45/60/75만
    !       Set->90 사이 회전을 6등분해서 다시 계산함) =====
    PERS robtarget p_tier_1_15_New := [[429.24,-210.83,277.33],[-0.057740,0.374226,0.918088,0.117199],[-1,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_tier_1_30_New := [[428.77,-211.45,274.44],[-0.114506,0.374500,0.890306,0.232367],[-1,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_tier_1_45_New := [[428.31,-212.08,271.54],[-0.169296,0.368310,0.847158,0.343525],[-1,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_tier_1_60_New := [[427.84,-212.71,268.64],[-0.221164,0.355764,0.789391,0.448754],[-1,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_tier_1_75_New := [[427.38,-213.33,265.75],[-0.269215,0.337079,0.718000,0.546239],[-1,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    PERS robtarget p_tier_2_Set:= [[529.62,-198.77,284.17],[4.14626E-05,0.412101,0.911138,-3.3956E-06],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_tier_2_15 := [[529.63,-192.53,291.42],[0.0656852,-0.414923,-0.902171,-0.0980439],[-1,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_tier_2_30 := [[529.62,-192.53,291.41],[0.125579,-0.411086,-0.878018,-0.210529],[-1,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_tier_2_45 := [[529.64,-200.05,293.26],[0.181652,-0.398016,-0.840699,-0.319077],[-1,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_tier_2_60 := [[529.63,-208.62,284.61],[0.210605,-0.33483,-0.819965,-0.413754],[-1,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_tier_2_75 := [[529.63,-208.62,284.61],[0.265602,-0.31464,-0.759136,-0.504153],[-1,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_tier_2_90 := [[527.70,-215.10,265.72],[0.312805,-0.312804,-0.634156,-0.634155],[-1,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_tier_2_link := [[527.69,-167.24,265.73],[0.312821,-0.312798,-0.634153,-0.634153],[-1,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    ! ===== Tire 2 - evenly re-spaced via-points (same method as tire 1) =====
    ! ===== 타이어 2 - 균등 재배치 경유점 (타이어 1과 같은 방식) =====
    PERS robtarget p_tier_2_15_New := [[529.30,-201.49,281.10],[-0.057715,0.412553,0.901533,0.117075],[-1,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_tier_2_30_New := [[528.98,-204.21,278.02],[-0.114482,0.405936,0.876480,0.232147],[-1,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_tier_2_45_New := [[528.66,-206.94,274.95],[-0.169287,0.392363,0.836408,0.343242],[-1,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_tier_2_60_New := [[528.34,-209.66,271.87],[-0.221191,0.372067,0.782003,0.448454],[-1,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_tier_2_75_New := [[528.02,-212.38,268.80],[-0.269306,0.345395,0.714199,0.545983],[-1,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    PERS robtarget p_tier_3_Set := [[448.57,-51.96,281.64],[5.97862E-06,0.904843,-0.425745,-2.54304E-05],[-1,0,-2,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_tier_3_15 := [[448.57,-51.96,281.64],[0.137715,0.892183,-0.429293,0.0274059],[0,-1,-2,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_tier_3_30 := [[448.59,-49.12,288.80],[0.206212,0.887889,-0.392487,0.122818],[0,-1,-2,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_tier_3_45 := [[448.60,-43.92,287.36],[0.346594,0.838667,-0.389461,0.157577],[0,-1,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_tier_3_60 := [[448.55,-39.95,287.36],[0.45429,0.784147,-0.393141,0.155484],[0,-1,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_tier_3_75 := [[448.55,-39.95,274.75],[0.51371,0.74543,-0.344448,0.248579],[0,-1,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_tier_3_90 := [[448.63,-41.48,260.50],[0.650839,0.650831,-0.27643,0.276431],[0,-1,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_tier_3_link := [[448.63,-85.01,260.51],[0.650859,0.650819,-0.276427,0.276417],[0,-1,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    ! ===== Tire 3 - evenly re-spaced via-points (same method as tire 1) =====
    ! ===== 타이어 3 - 균등 재배치 경유점 (타이어 1과 같은 방식) =====
    PERS robtarget p_tier_3_15_New := [[448.58,-50.21,278.12],[0.120168,0.899207,-0.417592,0.051015],[0,-1,-2,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_tier_3_30_New := [[448.59,-48.47,274.59],[0.238271,0.878157,-0.402280,0.101181],[0,-1,-2,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_tier_3_45_New := [[448.60,-46.72,271.07],[0.352289,0.842053,-0.380072,0.149612],[0,-1,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_tier_3_60_New := [[448.61,-44.97,267.55],[0.460267,0.791515,-0.351349,0.195479],[0,-1,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_tier_3_75_New := [[448.62,-43.23,264.02],[0.560356,0.727408,-0.316603,0.237995],[0,-1,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    PERS robtarget p_tier_4_Set := [[551.42,-51.98,281.62],[5.45519E-06,0.904848,-0.425734,-1.62566E-05],[-1,0,-2,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_tier_4_15 := [[551.42,-44.47,290.40],[0.149784,0.901531,-0.396078,0.0890465],[0,-1,-2,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_tier_4_30 := [[551.42,-44.47,290.40],[0.279561,0.868069,-0.393538,0.115891],[0,-1,-2,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_tier_4_45 := [[551.42,-44.47,290.41],[0.384006,0.82682,-0.374523,0.169234],[0,-1,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_tier_4_60 := [[551.41,-44.47,279.72],[0.492931,0.763351,-0.357758,0.21523],[0,-1,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_tier_4_75 := [[551.41,-44.47,288.58],[0.490481,0.769026,-0.352652,0.208958],[0,-1,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_tier_4_90 := [[551.37,-37.25,261.75],[0.643237,0.643265,-0.293615,0.293677],[0,-1,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_tier_4_link := [[551.35,-84.17,261.77],[0.64328,0.643239,-0.29361,0.293646],[0,-1,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    ! ===== Tire 4 - evenly re-spaced via-points (same method as tire 1) =====
    ! ===== 타이어 4 - 균등 재배치 경유점 (타이어 1과 같은 방식) =====
    PERS robtarget p_tier_4_15_New := [[551.41,-49.52,278.31],[0.118743,0.897749,-0.420725,0.054197],[0,-1,-2,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_tier_4_30_New := [[551.40,-47.07,275.00],[0.235449,0.875287,-0.408515,0.107484],[0,-1,-2,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_tier_4_45_New := [[551.39,-44.61,271.69],[0.348125,0.837845,-0.389315,0.158930],[0,-1,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_tier_4_60_New := [[551.39,-42.16,268.37],[0.454844,0.786065,-0.363452,0.207657],[0,-1,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget p_tier_4_75_New := [[551.38,-39.70,265.06],[0.553779,0.720833,-0.331369,0.252831],[0,-1,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];


    ! Server-side socket handles and receive buffer shared by Run_Socket_Server/Start_Server/
    ! Close_All_Sockets/Handle_Command below. The "srv_" prefix keeps these names from
    ! clashing with the production-cycle variables declared above.
    ! ?? Run_Socket_Server/Start_Server/Close_All_Sockets/Handle_Command? ???? ??
    ! ??? ?? ??? ?? ??. "srv_" ???? ?? ?? ??? ???? ???
    ! ??? ?? ?.
    VAR socketdev srv_server_socket;
    VAR socketdev srv_client_socket;
    VAR string srv_received_string;
    VAR bool srv_keep_listening := TRUE;
    TASK PERS tooldata tool3:=[TRUE,[[0,0,160],[1,0,0,0]],[0.1,[0,0,80],[1,0,0,0],0,0,0]];

    PROC Main()
        ! Role: Entry point - runs one-time setup, then waits for socket commands forever.
        ! ??: ??? - ?? ??? ? ? ??? ?, ?? ??? ??? ????.
        ! Process: Init (accel + home + clear outputs) -> Run_Socket_Server (accepts a
        !          connector and runs Run_Assembly_Cycle whenever it receives "Start").
        ! ??: Init(??? ?? + ? ?? + ?? ???) -> Run_Socket_Server(???
        !       ??? ?? "Start"? ?? ??? Run_Assembly_Cycle? ??).
        Init;
        MoveL p_assembly, v1000, z50, tool3;

        !Run_Assembly_Cycle;
        Run_Socket_Server;
    ENDPROC

    PROC Init()
        ! Role: One-time setup before the socket server starts.
        ! ??: ?? ??? ???? ? ?? ??.
        ! Process: set acceleration -> move to home -> release both suction pads
        !          (Absorption_Off 3) -> clear every other output (axle supply, assembly
        !          cylinder forward/back, tire supply, axle gripper on/off, battery
        !          supply, motor supply) left on from a previous run.
        ! ??: ??? ?? -> ??? ?? -> ?? ?? ?? ??(Absorption_Off 3) ->
        !       ?? ???? ?? ??? ??(? ??, ?? ??? ??/??, ???
        !       ??, ? ??? On/Off, ??? ??, ?? ??)? ?? ???.
        AccSet 1, 1;
        MoveL p_home, v_fast, fine, tool3;

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
        ! ??: ??? ??? ?????, ??? ?? ??? Handle_Command? ???.
        !       ??? ??? ?? ???.
        ! Process: Start_Server once -> WHILE(accept a connector -> WHILE(receive a
        !          command -> Handle_Command)) -> ERROR: retry on timeout, rebuild+retry
        !          on socket-closed, else log and stop.
        ! ??: Start_Server ? ? ?? -> WHILE(??? ?? ?? -> WHILE(?? ?? ->
        !       Handle_Command)) -> ERROR: ????? ???, ?? ??? ??? ?
        !       ???, ? ?? ?? ??? ??.
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
        ! ??: ??? ip/port? ?? ??? ???? ?? ???.
        Close_All_Sockets;
        SocketCreate srv_server_socket;
        SocketBind srv_server_socket, ip, port;
        SocketListen srv_server_socket;
    ENDPROC

    PROC Close_All_Sockets()
        ! Role: Best-effort close - a socket that was never created raises an error here;
        !       TRYNEXT just skips to the next line instead of stopping the program.
        ! ??: ??? ?? ??? ?? - ?? ? ?? ??? ? ?? ??? ??? ??
        !       ??? ??? ???, TRYNEXT? ????? ??? ?? ?? ?? ????.
        SocketClose srv_server_socket;
        SocketClose srv_client_socket;
        ERROR
            TRYNEXT;
    ENDPROC

    PROC Handle_Command(string cmd)
        ! Role: Decides what to do for one received command - the only PROC to edit when
        !       reusing this socket-server block on a different robot/module.
        ! ??: ?? ?? ??? ?? ??? ?? ???? - ? ?? ?? ??? ??
        !       ??/??? ???? ? ???? ??? ?? PROC.
        ! Process: "Start"/"start" runs the full assembly cycle; "End"/"END" and
        !          "Emergency" are reserved for later and do nothing yet.
        ! ??: "Start"/"start"? ?? ?? ???? ??; "End"/"END"? "Emergency"?
        !       ?? ??? ?? ??? ??? ??? ?? ?? ??? ?? ??.
        !IF (StrLen(cmd) >= 5) AND (StrPart(cmd, 1, 5) = "Start") THEN
        !        !MoveL p_assembly, v_moveSpeed, fine, tool3;
        !        TPWrite "Move done";
        !        Run_Assembly_Cycle;

        !ELSEIF (StrLen(cmd) >= 3) AND (StrPart(cmd, 1, 3) = "End") THEN
            ! ??

        !ELSEIF (StrLen(cmd) >= 9) AND (StrPart(cmd, 1, 9) = "Emergency") THEN
            ! ??
        !ENDIF
        IF cmd = "Start" OR cmd = "start" THEN
            TPWrite "Move Start";
            Run_Assembly_Cycle;
        ELSEIF cmd = "End" OR cmd = "END" THEN
            !??
        ELSEIF cmd = "Emergency" THEN
            !??
        ENDIF
    ENDPROC

    PROC Run_Assembly_Cycle()
        ! Role: Runs the full build sequence for one AMR chassis, station by station.
        ! ??: AMR ?? 1?? ?? ?? ??? ?????? ????.
        ! Process: Axle -> Lower_Body -> Welding -> Battery -> Motor -> Tier_Linked -> Sender,
        !          returning to p_assembly between every station.
        ! ??: Axle -> Lower_Body -> Welding -> Battery -> Motor -> Tier_Linked -> Sender,
        !       ?????? ??? p_assembly? ??.
        Axle;
        MoveJ p_assembly, v_fast, z30, tool3;

        Lower_Body;
        MoveJ p_assembly, v_fast, z30, tool3;

        Welding;
        MoveJ p_assembly, v_fast, z30, tool3;

        Battery;
        MoveJ p_assembly, v_fast, z30, tool3;

        Motor;
        MoveJ p_assembly, v_fast, z30, tool3;

        Tier_Linked;
        MoveJ p_assembly, v_fast, z30, tool3;

        Sender;
        MoveJ p_assembly, v_fast, z30, tool3;
    ENDPROC

    PROC Axle()
        ! Role: Picks up the axle and places it in the assembly fixture, handing it off to the
        !       PLC's clamp.
        ! ??: ?? ??? ?? ???? ??, PLC ???? ??? ???.
        ! Process: pulse do03_Axle_Supply to request an axle -> approach p_axle_pick and
        !          wait for di00_Axle_Cylinder_FDone -> descend and grab by suction ->
        !          pulse do08_Axle_Gripper_Off and wait for di01_Axle_Gripper_Off to
        !          release the supply-side fixture -> carry to p_assembly -> place at
        !          p_axle_assembly -> pulse do07_Axle_Gripper_On and wait for
        !          di02_Axle_Gripper_On so the PLC's clamp takes over -> release suction.
        ! ??: do03_Axle_Supply ??? ? ?? ?? -> p_axle_pick?? ????
        !       di00_Axle_Cylinder_FDone ?? -> ???? ???? ?? ->
        !       do08_Axle_Gripper_Off ?? + di01_Axle_Gripper_Off ??? ??? ???
        !       ?? -> p_assembly? ?? -> p_axle_assembly? ?? ->
        !       do07_Axle_Gripper_On ?? + di02_Axle_Gripper_On ??? PLC ????
        !       ???? ? -> ?? ??.
        PulseDO\PLength := 0.2,  do03_Axle_Supply_Forward;
        MoveJ Offs(p_axle_pick, 0, 0, OFS_APPROACH), v_fast, z30, tool3;
        WaitDI di00_Axle_Cylinder_FDone, 1;
        MoveL p_axle_pick, v_slow, fine, tool3;
        Absorption_On 3;
        PulseDo\PLength := 0.2, do09_Axle_Gripper_Off;
        WaitDI di01_Axle_Gripper_Off, 1;
        MoveL Offs(p_axle_pick, 0, 0, OFS_APPROACH), v_slow, fine, tool3;
        PulseDO\PLength := 0.2,  do04_Axle_Supply_Back;

        MoveL p_assembly, v_fast, z30, tool3;
        MoveL Offs(p_axle_assembly, 0, 0, OFS_APPROACH), v_fast, z30, tool3;
        MoveL p_axle_assembly, v_slow, fine, tool3;
        PulseDO\PLength := 0.2, do08_Axle_Gripper_On;
        WaitDI di02_Axle_Gripper_On, 1;
        Absorption_Off 3;
        MoveL Offs(p_axle_assembly, 0, 0, OFS_APPROACH), v_slow, fine, tool3;
    ENDPROC

    PROC Lower_Body()
        ! Role: Picks up the lower body chassis and sets it on top of the axle+tire assembly.
        ! ??: ?? ??? ??? ?+??? ??? ?? ???.
        ! Process: pick up from p_Lower_body_pick by suction -> place at p_Lower_body_link
        !          (approach points via Offs+OFS_APPROACH on both ends).
        ! ??: p_Lower_body_pick?? ???? ?? -> p_Lower_body_link? ??
        !       (?? ??? ?? Offs+OFS_APPROACH ??).
        MoveJ Offs(p_Lower_body_pick, 0, 0, OFS_APPROACH), v_fast, z30, tool3;
        MoveL p_Lower_body_pick, v_slow, fine, tool3;
        Absorption_On 3;
        MoveL Offs(p_Lower_body_pick, 0, 0, OFS_APPROACH), v_slow, fine, tool3;

        MoveL p_assembly, v_fast, z30, tool3;
        MoveL Offs(p_Lower_body_link, 0, 0, OFS_APPROACH), v_fast, z30, tool3;
        MoveL p_Lower_body_link, v_slow, fine, tool3;
        Absorption_Off 3;
        MoveL Offs(p_Lower_body_link, 0, 0, OFS_APPROACH), v_slow, fine, tool3;
    ENDPROC

    PROC Tier_Linked()
        ! Role: Picks up the 4 tires the PLC delivers one at a time and inserts each into its
        !       axle mount.
        ! ??: PLC? ??? ???? ??? 4?? ??? ?? ? ?? ??? ?? ???.
        ! Process: kick off the PLC tire-feed ladder once -> loop 4x (approach p_tier via
        !          Offs+OFS_APPROACH, wait for di03_Tier_Supply_Done, descend and pick up
        !          by suction, return to p_assembly, then call that mount's Tier_N_Swing
        !          PROC to sweep in - insert - sweep back out) -> return to assembly.
        ! ??: PLC ??? ?? ??? ? ? ?? -> 4? ??(Offs+OFS_APPROACH? p_tier
        !       ??, di03_Tier_Supply_Done ??, ???? ???? ??, p_assembly?
        !       ?? ? ?? ??? Tier_N_Swing PROC? ??? ??-??-?? ??) -> ??
        !       ???? ??.
        ! Key variable: n_tireIndex (1-4) - selects which axle mount (p_tier_1_link~4)
        !               to use via TEST/CASE. Odd (1,3)=left side, so the Y approach offset is
        !               negative; even (2,4)=right side, so it is positive.
        ! ?? ??: n_tireIndex (1~4) - TEST/CASE? ?? ? ?? ??? ?? ???. ??
        !            (1,3)=???? Y ?? ???? ??, ??(2,4)=????? ??.
        VAR num n_tireIndex := 0;
        PulseDO \PLength := 0.2, do07_Tier_Supply;

        FOR n_tireIndex FROM 1 TO 4 DO
            MoveJ Offs(p_tier, 0, 0, OFS_APPROACH), v_fast, z30, tool3;
            WaitDI di03_Tier_Supply_Done, 1;
            MoveL p_tier, v_slow, fine, tool3;
            ! Pick up the tire the PLC just delivered
            ! PLC? ?? ??? ???? ??
            Absorption_On 1;
            MoveL Offs(p_tier, 0, 0, OFS_APPROACH), v_slow, fine, tool3;
            MoveJ p_assembly, v_fast, z30, tool3;

            TEST n_tireIndex
            CASE 1:
                Tier_1_Swing;
            CASE 2:
                Tier_2_Swing;
            CASE 3:
                Tier_3_Swing;
            CASE 4:
                Tier_4_Swing;
            ENDTEST
            MoveJ p_assembly, v_fast, z30, tool3;
            !MoveJ p_home, v_fast, z30, tool3;
        ENDFOR
    ENDPROC

    PROC Tier_1_Swing()
        ! Role: Full swing-in/insert/swing-out for mount 1, using the evenly re-spaced
        !       _New via-points and a soft z50 zone throughout, to test whether that
        !       removes the stop-and-go feel from the original hand-taught version.
        ! 역할: 1번 장착의 스윙-삽입-스윙아웃 전체 - 균등 재배치된 _New 경유점과, 전
        !       구간 z50(부드러운 존)을 써서 원래 손으로 하나씩 찍었던 버전의 뚝뚝
        !       끊기는 느낌이 없어지는지 테스트한다.
        ! Process: p_tier_1_Set -> 15_New -> 30_New -> 45_New -> 60_New -> 75_New ->
        !          p_tier_1_90 -> p_tier_1_link (fine - the actual axle contact, kept
        !          precise on purpose) -> Absorption_Off -> back out in reverse order.
        ! 과정: p_tier_1_Set -> 15_New -> 30_New -> 45_New -> 60_New -> 75_New ->
        !       p_tier_1_90 -> p_tier_1_link(실제 축 접촉 지점이라 여기만 일부러
        !       fine로 정밀하게 유지) -> Absorption_Off -> 역순으로 후퇴.
        MoveL p_tier_1_Set, v_slow, z50, tool3;
        MoveL p_tier_1_15_New, v_slow, z50, tool3;
        MoveL p_tier_1_30_New, v_slow, z50, tool3;
        MoveL p_tier_1_45_New, v_slow, z50, tool3;
        MoveL p_tier_1_60_New, v_slow, z50, tool3;
        MoveL p_tier_1_75_New, v_slow, z50, tool3;
        MoveL p_tier_1_90, v_slow, z50, tool3;
        MoveL p_tier_1_link, v_slow, fine, tool3;
        Absorption_Off 1;
        MoveL p_tier_1_90, v_slow, z50, tool3;
        MoveL p_tier_1_75_New, v_slow, z50, tool3;
        MoveL p_tier_1_60_New, v_slow, z50, tool3;
        MoveL p_tier_1_45_New, v_slow, z50, tool3;
        MoveL p_tier_1_30_New, v_slow, z50, tool3;
        MoveL p_tier_1_15_New, v_slow, z50, tool3;
        MoveL p_tier_1_Set, v_slow, z50, tool3;
    ENDPROC

    PROC Tier_2_Swing()
        ! Role: Same as Tier_1_Swing, for mount 2.
        ! 역할: Tier_1_Swing과 동일, 2번 장착용.
        ! Process: p_tier_2_Set -> 15_New -> 30_New -> 45_New -> 60_New -> 75_New ->
        !          p_tier_2_90 -> p_tier_2_link (fine) -> Absorption_Off -> reverse back out.
        ! 과정: p_tier_2_Set -> 15_New -> 30_New -> 45_New -> 60_New -> 75_New ->
        !       p_tier_2_90 -> p_tier_2_link(fine) -> Absorption_Off -> 역순 후퇴.
        MoveL p_tier_2_Set, v_slow, z50, tool3;
        MoveL p_tier_2_15_New, v_slow, z50, tool3;
        MoveL p_tier_2_30_New, v_slow, z50, tool3;
        MoveL p_tier_2_45_New, v_slow, z50, tool3;
        MoveL p_tier_2_60_New, v_slow, z50, tool3;
        MoveL p_tier_2_75_New, v_slow, z50, tool3;
        MoveL p_tier_2_90, v_slow, z50, tool3;
        MoveL p_tier_2_link, v_slow, fine, tool3;
        Absorption_Off 1;
        MoveL p_tier_2_90, v_slow, z50, tool3;
        MoveL p_tier_2_75_New, v_slow, z50, tool3;
        MoveL p_tier_2_60_New, v_slow, z50, tool3;
        MoveL p_tier_2_45_New, v_slow, z50, tool3;
        MoveL p_tier_2_30_New, v_slow, z50, tool3;
        MoveL p_tier_2_15_New, v_slow, z50, tool3;
        MoveL p_tier_2_Set, v_slow, z50, tool3;
    ENDPROC

    PROC Tier_3_Swing()
        ! Role: Same as Tier_1_Swing, for mount 3.
        ! 역할: Tier_1_Swing과 동일, 3번 장착용.
        ! Process: p_tier_3_Set -> 15_New -> 30_New -> 45_New -> 60_New -> 75_New ->
        !          p_tier_3_90 -> p_tier_3_link (fine) -> Absorption_Off -> reverse back out.
        ! 과정: p_tier_3_Set -> 15_New -> 30_New -> 45_New -> 60_New -> 75_New ->
        !       p_tier_3_90 -> p_tier_3_link(fine) -> Absorption_Off -> 역순 후퇴.
        MoveL p_tier_3_Set, v_slow, z50, tool3;
        MoveL p_tier_3_15_New, v_slow, z50, tool3;
        MoveL p_tier_3_30_New, v_slow, z50, tool3;
        MoveL p_tier_3_45_New, v_slow, z50, tool3;
        MoveL p_tier_3_60_New, v_slow, z50, tool3;
        MoveL p_tier_3_75_New, v_slow, z50, tool3;
        MoveL p_tier_3_90, v_slow, z50, tool3;
        MoveL p_tier_3_link, v_slow, fine, tool3;
        Absorption_Off 1;
        MoveL p_tier_3_90, v_slow, z50, tool3;
        MoveL p_tier_3_75_New, v_slow, z50, tool3;
        MoveL p_tier_3_60_New, v_slow, z50, tool3;
        MoveL p_tier_3_45_New, v_slow, z50, tool3;
        MoveL p_tier_3_30_New, v_slow, z50, tool3;
        MoveL p_tier_3_15_New, v_slow, z50, tool3;
        MoveL p_tier_3_Set, v_slow, z50, tool3;
    ENDPROC

    PROC Tier_4_Swing()
        ! Role: Same as Tier_1_Swing, for mount 4.
        ! 역할: Tier_1_Swing과 동일, 4번 장착용.
        ! Process: p_tier_4_Set -> 15_New -> 30_New -> 45_New -> 60_New -> 75_New ->
        !          p_tier_4_90 -> p_tier_4_link (fine) -> Absorption_Off -> reverse back out.
        ! 과정: p_tier_4_Set -> 15_New -> 30_New -> 45_New -> 60_New -> 75_New ->
        !       p_tier_4_90 -> p_tier_4_link(fine) -> Absorption_Off -> 역순 후퇴.
        MoveL p_tier_4_Set, v_slow, z50, tool3;
        MoveL p_tier_4_15_New, v_slow, z50, tool3;
        MoveL p_tier_4_30_New, v_slow, z50, tool3;
        MoveL p_tier_4_45_New, v_slow, z50, tool3;
        MoveL p_tier_4_60_New, v_slow, z50, tool3;
        MoveL p_tier_4_75_New, v_slow, z50, tool3;
        MoveL p_tier_4_90, v_slow, z50, tool3;
        MoveL p_tier_4_link, v_slow, fine, tool3;
        Absorption_Off 1;
        MoveL p_tier_4_90, v_slow, z50, tool3;
        MoveL p_tier_4_75_New, v_slow, z50, tool3;
        MoveL p_tier_4_60_New, v_slow, z50, tool3;
        MoveL p_tier_4_45_New, v_slow, z50, tool3;
        MoveL p_tier_4_30_New, v_slow, z50, tool3;
        MoveL p_tier_4_15_New, v_slow, z50, tool3;
        MoveL p_tier_4_Set, v_slow, z50, tool3;
    ENDPROC

    PROC Battery()
        ! Role: Picks up the battery and places it on the lower body.
        ! ??: ???? ??? ??? ?? ???.
        ! Process: pre-feed pulse to the PLC (do09_Battery_Supply) -> approach and wait
        !          for di04_Battery_Supply_Done -> pick up from p_battery_pick by suction
        !          -> place at p_battery_link (approach points via Offs+OFS_APPROACH).
        ! ??: PLC? ?? ?? ?? ??(do09_Battery_Supply) -> ?? ?
        !       di04_Battery_Supply_Done ?? -> p_battery_pick?? ???? ?? ->
        !       p_battery_link? ?? (???? Offs+OFS_APPROACH).
        PulseDO \PLength := 0.2, do10_Battery_Supply;

        MoveL Offs(p_battery_pick, 0, 0, OFS_APPROACH), v_fast, z30, tool3;
        WaitDI di04_Battery_Supply_Done, 1;
        MoveL p_battery_pick, v_slow, fine, tool3;
        Absorption_On 3;
        MoveL Offs(p_battery_pick, 0, 0, OFS_APPROACH), v_slow, fine, tool3;

        MoveL p_assembly, v_fast, z30, tool3;
        MoveL Offs(p_battery_link, 0, 0, OFS_APPROACH), v_fast, z30, tool3;
        MoveL p_battery_link, v_slow, fine, tool3;
        Absorption_Off 3;
        MoveL Offs(p_battery_link, 0, 0, OFS_APPROACH), v_slow, fine, tool3;
    ENDPROC

    PROC Motor()
        ! Role: Picks up the motor and mounts it on the assembly.
        ! ??: ??? ??? ???? ????.
        ! Process: pulse the PLC's motor signal (do10_motor) -> approach and wait for
        !          di07_Motor_Supply_Done -> pick up from p_motor_pick by suction -> place
        !          at p_motor_link (approach points via Offs+OFS_APPROACH).
        ! ??: PLC ?? ?? ?? ??(do10_motor) -> ?? ? di07_Motor_Supply_Done
        !       ?? -> p_motor_pick?? ???? ?? -> p_motor_link? ?? (????
        !       Offs+OFS_APPROACH).
        PulseDO \PLength := 0.2, do11_Motor_Supply;

        MoveL Offs(p_motor_pick, 0, 0, OFS_APPROACH), v_fast, z30, tool3;
        WaitDI di07_Motor_Supply_Done, 1;
        MoveL p_motor_pick, v_slow, fine, tool3;
        Absorption_On 3;
        MoveL Offs(p_motor_pick, 0, 0, OFS_APPROACH), v_slow, fine, tool3;

        MoveL p_assembly, v_fast, z30, tool3;

        MoveL Offs(p_motor_link, 0, 0, OFS_APPROACH), v_fast, z30, tool3;
        MoveL p_motor_link, v_slow, fine, tool3;
        Absorption_Off 3;
        MoveL Offs(p_motor_link, 0, 0, OFS_APPROACH), v_slow, fine, tool3;
    ENDPROC

    PROC Welding()
        ! TODO: not implemented yet - no welding-station work exists for this cell
        ! TODO: ??? - ? ??? ?? ?? ???? ??? ??
    ENDPROC

    PROC Sender()
        ! Role: Picks up the whole finished assembly by suction and hands it off at the exit
        !       conveyor.
        ! ??: ??? ??? ??? ???? ??? ?? ????? ????.
        ! Process: approach/grab p_assembly_pick by suction -> release the axle-gripper
        !          clamp as suction starts -> retreat extra high (OFS_APPROACH + 150) to
        !          clear the fixture -> move to the exit conveyor -> release.
        ! ??: p_assembly_pick? ???? ??/?? -> ?? ??? ??? ? ???
        !       ??? ?? -> ???? ????? ???? ??(OFS_APPROACH + 150)
        !       ?? -> ?? ????? ?? -> ????.
        MoveL Offs(p_assembly_pick, 0, 0, OFS_APPROACH), v_fast, z30, tool3;
        MoveL p_assembly_pick, v_slow, fine, tool3;
        Absorption_On 1;
        !SetDO do07, 0;
        MoveL Offs(p_assembly_pick, 0, 0, OFS_APPROACH + 150), v_slow, fine, tool3;

        MoveJ Offs(p_conveyor_Exit, 0, 0, OFS_APPROACH), v_fast, z30, tool3;
        MoveL p_conveyor_Exit, v_slow, fine, tool3;
        Absorption_Off 1;
        MoveL Offs(p_conveyor_Exit, 0, 0, OFS_APPROACH), v_slow, fine, tool3;
        !PulseDO \PLength := 0.2, do20_Exit_Conveyor;
    ENDPROC

    PROC Absorption_On(num SetNum)
        ! Role: Turns on one or both suction pads to grab a part.
        ! ??: ?? ?? ?? ?? ? ? ?? ??? ????.
        ! Process: SetNum selects which pad(s) - 1 = first pad only, 2 = second pad only,
        !          3 = both pads - then settles 0.3s for the vacuum to build.
        ! ??: SetNum?? ?? ??? ?? ?? - 1=??? ???, 2=??? ???,
        !       3=? ? - ? ? ??? ????? 0.3? ??.
        ! Key variable: SetNum (1-3) - 1/2 use a single pad, 3 uses both together.
        ! ?? ??: SetNum (1~3) - 1/2? ?? ???, 3? ? ? ?? ??.
        IF SetNum = 1 THEN
            SetDo do00_First_AD_On, 1;
            WaitTime 0.3;
        ELSEIF SetNum = 2 THEN
            SetDo do01_Second_AD_ON, 1;
            WaitTime 0.3;
        ELSEIF SetNum = 3 THEN
            SetDo do00_First_AD_On, 1;
            SetDo do01_Second_AD_ON, 1;
            WaitTime 0.3;
        ENDIF
    ENDPROC

    PROC Absorption_Off(num SetNum)
        ! Role: Turns off one or both suction pads to release a part.
        ! ??: ?? ?? ?? ?? ? ? ?? ??? ???.
        ! Process: SetNum selects which pad(s) - 1 = first pad only, 2 = second pad only,
        !          3 = both pads - then settles 0.3s.
        ! ??: SetNum?? ?? ??? ?? ?? - 1=??? ???, 2=??? ???,
        !       3=? ? - ? ? 0.3? ??.
        ! Key variable: SetNum (1-3) - 1/2 use a single pad, 3 uses both together.
        ! ?? ??: SetNum (1~3) - 1/2? ?? ???, 3? ? ? ?? ??.
        IF SetNum = 1 THEN
            SetDo do00_First_AD_On, 0;
            WaitTime 0.3;
        ELSEIF SetNum = 2 THEN
            SetDo do01_Second_AD_ON, 0;
            WaitTime 0.3;
        ELSEIF SetNum = 3 THEN
            SetDo do00_First_AD_On, 0;
            SetDo do01_Second_AD_ON, 0;
            WaitTime 0.3;
        ENDIF
    ENDPROC

ENDMODULE
