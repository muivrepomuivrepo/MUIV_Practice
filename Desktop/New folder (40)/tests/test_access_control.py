def test_guest_is_redirected_from_protected_page(client):
    response = client.get("/client/dashboard")
    assert response.status_code == 302
    assert "/auth/login" in response.headers["Location"]


def test_manager_cannot_create_client_request(client, login):
    login("manager", "manager1234")
    response = client.get("/client/requests/new")
    assert response.status_code == 403


def test_client_cannot_open_admin_settings(client, login):
    login("client", "client1234")
    response = client.get("/admin/settings")
    assert response.status_code == 403
