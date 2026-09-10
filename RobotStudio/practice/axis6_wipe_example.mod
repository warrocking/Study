MODULE MainModule
    ! =====================================================================
    ! axis6_wipe_example.mod - 6축만 움직여서 타이어 안쪽을 닦는 동작 예제
    !
    ! MoveAbsJ + jointtarget으로 6개 관절 각도를 직접 지정합니다.
    ! 현재 자세(j_base)를 그대로 복사한 뒤 rax_6(6축)만 좌우로 바꿔서
    ! 이동시키므로, 1~5축은 전혀 움직이지 않고 손목(6축)만 왔다갔다 돌면서
    ! 닦는 듯한 동작을 만듭니다.
    !
    ! wipeAngle(왕복 각도), wipeCount(왕복 횟수) 값만 바꿔서 바로 테스트 가능
    ! =====================================================================

    PERS tooldata tool1:=[TRUE,[[0,0,110],[1,0,0,0]],[0.2,[0,0,50],[1,0,0,0],0,0,0]];

    VAR speeddata v_moveSpeed_slow := v50;
    VAR num wipeAngle := 45;    ! 6축을 기준 자세에서 얼마나 좌우로 돌릴지 (도)
    VAR num wipeCount := 3;     ! 왕복 횟수

    PROC Main()
        VAR jointtarget j_base;
        VAR jointtarget j_target;

        j_base := CJointT();      ! 지금 로봇이 서 있는 자세(6축 전부)를 기준으로 저장

        FOR i FROM 1 TO wipeCount DO
            j_target := j_base;                              ! 1~5축은 기준 자세 그대로 복사
            j_target.robax.rax_6 := j_base.robax.rax_6 + wipeAngle;
            MoveAbsJ j_target, v_moveSpeed_slow, fine, tool1; ! 6축만 +wipeAngle 만큼 회전

            j_target.robax.rax_6 := j_base.robax.rax_6 - wipeAngle;
            MoveAbsJ j_target, v_moveSpeed_slow, fine, tool1; ! 6축만 -wipeAngle 만큼 회전
        ENDFOR

        MoveAbsJ j_base, v_moveSpeed_slow, fine, tool1;       ! 원래 자세로 복귀
    ENDPROC

ENDMODULE
