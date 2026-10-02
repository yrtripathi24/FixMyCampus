from io import BytesIO

from app.repositories.reports import get_report


def test_report_photo_is_saved_and_displayed_on_incident_detail(app):
    response = app.test_client().post(
        "/report",
        data={
            "category": "Electrical",
            "location": "Block C Entrance",
            "description": "Streetlight needs repair",
            "photo": (BytesIO(b"\x89PNG\r\n\x1a\nphoto evidence"), "../../lamp.png"),
        },
        content_type="multipart/form-data",
    )

    assert response.status_code == 200
    report = get_report(1)
    assert report.photo_filename
    assert "lamp.png" not in report.photo_filename

    detail = app.test_client().get("/incidents/1")
    image = app.test_client().get(f"/uploads/{report.photo_filename}")
    assert b"Photo evidence for this report" in detail.data
    assert image.status_code == 200
