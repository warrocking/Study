MODULE SocketBridgeClient
    ! Educational TCP client for the Python bridge.
    ! The protocol is one CRLF-terminated ASCII frame per command.
    ! Run against the Mock Controller first. Do not use as a safety channel.

    CONST string SERVER_IP := "127.0.0.1";
    CONST num SERVER_PORT := 9100;
    VAR socketdev gBridgeSocket;
    VAR string gReply;

    PROC main()
        ConnectBridge;
        SendPing;
        SocketClose gBridgeSocket;
    ERROR
        TPWrite "Socket demo stopped. Check IP, port and server.";
        SocketClose gBridgeSocket;
        RAISE;
    ENDPROC

    PROC ConnectBridge()
        SocketCreate gBridgeSocket;
        SocketConnect gBridgeSocket, SERVER_IP, SERVER_PORT;
        TPWrite "Connected to Python bridge";
    ENDPROC

    PROC SendPing()
        ! ABB Socket Messaging sends a byte stream. CRLF is our frame boundary.
        SocketSend gBridgeSocket \Str:="PING|rapid-001\0D\0A";
        SocketReceive gBridgeSocket \Str:=gReply;
        TPWrite gReply;
    ENDPROC
ENDMODULE

