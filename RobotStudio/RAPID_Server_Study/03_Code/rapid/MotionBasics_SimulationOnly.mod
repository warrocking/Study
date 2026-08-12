MODULE MotionBasics_SimulationOnly
    ! Replace targets, tooldata and workobject only after RobotStudio validation.
    ! This module intentionally refuses to move until the learner changes the guard.

    PERS bool gSimulationReviewed := FALSE;
    CONST robtarget pHome := [[500,0,600],[1,0,0,0],[0,0,0,0],[9E9,9E9,9E9,9E9,9E9,9E9]];
    CONST robtarget pApproach := [[600,0,400],[1,0,0,0],[0,0,0,0],[9E9,9E9,9E9,9E9,9E9,9E9]];
    CONST robtarget pWork := [[600,0,300],[1,0,0,0],[0,0,0,0],[9E9,9E9,9E9,9E9,9E9,9E9]];

    PROC main()
        IF NOT gSimulationReviewed THEN
            TPWrite "Review tool, workobject, targets and cell safety first.";
            Stop;
        ENDIF

        MoveJ pHome, v100, fine, tool0\WObj:=wobj0;
        MoveJ pApproach, v100, z50, tool0\WObj:=wobj0;
        MoveL pWork, v50, fine, tool0\WObj:=wobj0;
        MoveL pApproach, v50, z20, tool0\WObj:=wobj0;
        MoveJ pHome, v100, fine, tool0\WObj:=wobj0;
    ENDPROC
ENDMODULE

