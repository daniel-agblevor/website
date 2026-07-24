def test_get_features_defaults(client):
    """Test fetching public feature toggles defaults"""
    response = client.get('/api/features')
    assert response.status_code == 200
    flags = response.get_json()
    assert flags.get("services") is True
    assert flags.get("portfolio") is True
    assert flags.get("case_studies") is True
    assert flags.get("testimonials") is True
    assert flags.get("blog") is True


def test_toggle_feature_flag_protected(client):
    """Verify unauthorized access to toggle feature flags is blocked"""
    response = client.patch('/api/admin/features/services', json={"is_enabled": False})
    assert response.status_code == 401


def test_toggle_feature_flag_success(client, admin_token):
    """Verify authenticated admin can toggle feature flag off and public route reflects it"""
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Toggle portfolio off
    patch_res = client.patch('/api/admin/features/portfolio', json={"is_enabled": False}, headers=headers)
    assert patch_res.status_code == 200

    # Verify public features endpoint reflects change
    feat_res = client.get('/api/features')
    flags = feat_res.get_json()
    assert flags.get("portfolio") is False

    # Verify portfolio content endpoint returns empty array when toggled off
    port_res = client.get('/api/portfolio')
    assert port_res.status_code == 200
    assert port_res.get_json() == []
