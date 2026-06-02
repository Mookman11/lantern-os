from bettersafe.sensor_policy import (
    SensorClass,
    SensorRequest,
    SubjectClass,
    evaluate_sensor_request,
)



def test_operator_push_to_talk_allowed():
    request = SensorRequest(
        subject=SubjectClass.OPERATOR,
        sensor=SensorClass.PUSH_TO_TALK,
        explicit_consent=True,
    )

    result = evaluate_sensor_request(request)

    assert result.allowed is True
    assert result.mode == "operator_allowed"



def test_operator_background_audio_requires_controls():
    request = SensorRequest(
        subject=SubjectClass.OPERATOR,
        sensor=SensorClass.BACKGROUND_AUDIO,
        explicit_consent=True,
        local_first=True,
        visible_status=False,
        hard_off_switch=False,
    )

    result = evaluate_sensor_request(request)

    assert result.allowed is False
    assert "missing_visible_status" in result.blockers
    assert "missing_hard_off_switch" in result.blockers



def test_operator_background_audio_allowed_with_controls():
    request = SensorRequest(
        subject=SubjectClass.OPERATOR,
        sensor=SensorClass.BACKGROUND_AUDIO,
        explicit_consent=True,
        local_first=True,
        visible_status=True,
        hard_off_switch=True,
        summary_over_raw=True,
    )

    result = evaluate_sensor_request(request)

    assert result.allowed is True
    assert result.mode == "operator_reviewed_sensor"



def test_third_party_without_consent_blocked():
    request = SensorRequest(
        subject=SubjectClass.THIRD_PARTY,
        sensor=SensorClass.BACKGROUND_AUDIO,
        explicit_consent=False,
    )

    result = evaluate_sensor_request(request)

    assert result.allowed is False
    assert "missing_non_operator_consent" in result.blockers



def test_raw_credentials_blocked():
    request = SensorRequest(
        subject=SubjectClass.OPERATOR,
        sensor=SensorClass.RAW_CREDENTIAL,
        explicit_consent=True,
    )

    result = evaluate_sensor_request(request)

    assert result.allowed is False
    assert "raw_credentials_not_allowed" in result.blockers
