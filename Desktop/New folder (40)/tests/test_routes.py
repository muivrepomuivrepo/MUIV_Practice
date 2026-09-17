from app.domain.contact_message import ContactMessage


def test_public_pages_have_navigation_and_breadcrumbs(client):
    for url in ["/", "/services", "/projects", "/workflow", "/reviews", "/about", "/contacts", "/faq", "/privacy"]:
        response = client.get(url)
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        assert html.count('<nav class="main-nav"') == 1
        assert html.count('<nav class="breadcrumbs"') == 1
        assert "Kuleshov Nikita Vyacheslavovich" in html


def test_contact_form_saves_message(app, client):
    response = client.post(
        "/contacts",
        data={
            "name": "Иван Петров",
            "email": "ivan@example.com",
            "phone": "+7 900 555-44-33",
            "message": "Прошу связаться для консультации.",
            "consent": "yes",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert "Сообщение #2 принято" in response.get_data(as_text=True)
    with app.app_context():
        saved = ContactMessage.query.filter_by(email="ivan@example.com").one()
        assert saved.status == "new"
