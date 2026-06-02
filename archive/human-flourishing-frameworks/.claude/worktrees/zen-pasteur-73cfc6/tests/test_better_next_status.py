from app import app


def test_better_next_status_endpoint_reports_safe_runtime_limits():
    client = app.test_client()

    response = client.get('/api/better-next/status')
    assert response.status_code == 200

    data = response.get_json()

    assert data['status'] == 'ok'
    assert data['public_name'] == 'Better Next'

    assert 'Shield Protocol' in data['protocols']['shield_protocol']
    assert 'Brave Reprotocol' in data['protocols']['brave_reprotocol']

    limits = data['limits']

    assert limits['payments'] is False
    assert limits['financial_authority'] is False
    assert limits['medical_authority'] is False
    assert limits['legal_authority'] is False
    assert limits['physical_world_control'] is False
    assert limits['hidden_telemetry'] is False
