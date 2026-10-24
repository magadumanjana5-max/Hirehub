def test_health_endpoint(app_client):
    response = app_client.get('/health')
    assert response.status_code == 200


def test_register_and_login(app_client):
    response = app_client.post(
        '/register',
        data={'email': 'newuser@example.com', 'password': 'password123', 'first_name': 'New', 'last_name': 'User', 'role': 'candidate'},
        follow_redirects=False,
    )
    assert response.status_code == 302

    login_response = app_client.post(
        '/login',
        data={'email': 'newuser@example.com', 'password': 'password123'},
        follow_redirects=False,
    )
    assert login_response.status_code == 302
