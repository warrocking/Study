MODULE RwsMailbox
    ! Persistent mailbox for supervised RWS exercises.
    ! Python increments gCmdSeq only after writing the other command fields.

    PERS num gCmdSeq := 0;
    PERS string gCmdName := "NONE";
    PERS string gCmdArg := "";
    PERS num gAckSeq := 0;
    PERS string gAckState := "IDLE";

    VAR num gLastSeq := 0;

    PROC main()
        WHILE TRUE DO
            IF gCmdSeq <> gLastSeq THEN
                HandleMailbox;
                gLastSeq := gCmdSeq;
                gAckSeq := gCmdSeq;
            ENDIF
            WaitTime 0.10;
        ENDWHILE
    ENDPROC

    PROC HandleMailbox()
        gAckState := "RUNNING";
        TEST gCmdName
        CASE "PING":
            TPWrite "RWS mailbox PING";
            gAckState := "DONE";
        CASE "RESET":
            gAckState := "DONE";
        DEFAULT:
            gAckState := "REJECTED";
        ENDTEST
    ERROR
        gAckState := "ERROR";
        RAISE;
    ENDPROC
ENDMODULE

