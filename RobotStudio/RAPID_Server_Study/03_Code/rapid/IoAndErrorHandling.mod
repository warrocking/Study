MODULE IoAndErrorHandling
    VAR signaldo gDoGrip;
    VAR signaldi gDiPartReady;
    VAR bool gTimedOut;

    PROC main()
        ConfigureAliases;
        WaitForPart;
        IF NOT gTimedOut THEN
            SetDO gDoGrip, 1;
            WaitTime 0.20;
            SetDO gDoGrip, 0;
        ENDIF
    ERROR
        TPWrite "I/O exercise failed. Check configured signal names.";
        RAISE;
    ENDPROC

    PROC ConfigureAliases()
        AliasIO "doGrip", gDoGrip;
        AliasIO "diPartReady", gDiPartReady;
    ENDPROC

    PROC WaitForPart()
        gTimedOut := FALSE;
        WaitDI gDiPartReady, 1\MaxTime:=5\TimeFlag:=gTimedOut;
        IF gTimedOut THEN
            TPWrite "No part detected within five seconds.";
        ENDIF
    ENDPROC
ENDMODULE

