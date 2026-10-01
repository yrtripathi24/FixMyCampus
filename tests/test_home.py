from app import create_app


def test_home_page_loads():
    app = create_app({"TESTING": True})

    response = app.test_client().get("/")

    assert response.status_code == 200
    assert b"FixMyCampus" in response.data
