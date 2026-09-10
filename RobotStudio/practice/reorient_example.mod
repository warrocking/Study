MODULE MainModule
    ! =====================================================================
    ! reorient_example.mod - Reorientation(재지향) 동작 확인용 예제
    !
    ! 목적: 같은 위치(p_air_center)에서 방향(orientation)만 바꿔가며
    !       여러 면이 순서대로 같은 방향(예: 에어 노즐 쪽)을 향하게 하는
    !       동작을 확인하기 위한 예제.
    !
    ! RelTool(기준점, dx, dy, dz \Rx:=각도 \Ry:=각도 \Rz:=각도)
    !   기준점의 위치는 그대로 두고, 툴 자신의 축(X/Y/Z) 기준으로 회전만 준
    !   새로운 robtarget을 계산해주는 함수. Offs()는 위치만 옮기고 회전은
    !   못 주지만, RelTool()은 회전(그리고 필요하면 위치 오프셋도 같이)이
    !   가능해서 지금 이 용도(제자리 회전)에 정확히 맞음.
    !
    ! 아래 tiltAngle 값만 바꿔서 실행해보면 기울어지는 정도를 바로 확인할 수 있음
    ! =====================================================================

    PERS tooldata tool1:=[TRUE,[[0,0,110],[1,0,0,0]],[0.2,[0,0,50],[1,0,0,0],0,0,0]];

    VAR robtarget p_air_center := [[508.13,121.36,44.96],[0.00049446,0.458239,-0.888829,-0.000356638],[0,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    VAR speeddata v_moveSpeed_slow := v50;
    VAR num tiltAngle := 30;    ! 몇 도 기울일지 - 이 값만 바꿔서 테스트 가능

    PROC Main()
        MoveJ p_air_center, v_moveSpeed_slow, fine, tool1;   ! 기준 위치로 먼저 이동

        MoveL RelTool(p_air_center, 0, 0, 0 \Rx:=tiltAngle),  v_moveSpeed_slow, fine, tool1; ! 방향 1 (X축 기준 +tiltAngle)
        WaitTime 1;                                            ! 눈으로 방향 확인할 시간
        MoveL RelTool(p_air_center, 0, 0, 0 \Ry:=tiltAngle),  v_moveSpeed_slow, fine, tool1; ! 방향 2 (Y축 기준 +tiltAngle)
        WaitTime 1;
        MoveL RelTool(p_air_center, 0, 0, 0 \Rx:=-tiltAngle), v_moveSpeed_slow, fine, tool1; ! 방향 3 (X축 기준 -tiltAngle)
        WaitTime 1;
        MoveL RelTool(p_air_center, 0, 0, 0 \Ry:=-tiltAngle), v_moveSpeed_slow, fine, tool1; ! 방향 4 (Y축 기준 -tiltAngle)
        WaitTime 1;

        MoveJ p_air_center, v_moveSpeed_slow, fine, tool1;   ! 기준 방향으로 복귀
    ENDPROC

ENDMODULE
