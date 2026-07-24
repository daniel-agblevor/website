def test_admin_login_success(client):
    """Test admin login returns access token"""
    res = client.post('/api/admin/login', json={
        "email": "admin@example.com",
        "password": "admin123"
    })
    assert res.status_code == 200
    data = res.get_json()
    assert "access_token" in data


def test_admin_login_failure(client):
    """Test admin login with wrong password"""
    res = client.post('/api/admin/login', json={
        "email": "admin@example.com",
        "password": "wrongpassword"
    })
    assert res.status_code == 401


def test_get_leads_unauthorized(client):
    """Verify fetching leads requires JWT token"""
    res = client.get('/api/admin/leads')
    assert res.status_code == 401


def test_get_and_update_leads_authorized(client, admin_token):
    """Test authorized admin can retrieve leads and update lead status"""
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # 1. Create a lead via public contact endpoint
    client.post('/api/contact', json={
        "name": "Ama Serwaa",
        "email": "ama@example.com",
        "message": "Interested in Power BI dashboard integration for HR."
    })

    # 2. Get leads list
    res = client.get('/api/admin/leads', headers=headers)
    assert res.status_code == 200
    leads = res.get_json()
    assert len(leads) >= 1
    lead_id = leads[0]["id"]

    # 3. Update status to 'contacted'
    patch_res = client.patch(f'/api/admin/leads/{lead_id}', json={"status": "contacted"}, headers=headers)
    assert patch_res.status_code == 200
    assert patch_res.get_json()["lead"]["status"] == "contacted"
