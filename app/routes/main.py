from flask import Blueprint, render_template, request

from app.services.report_service import CATEGORIES, submit_report, validate_report


main_bp = Blueprint("main", __name__)


@main_bp.get("/")
def home():
    return render_template("home.html")


@main_bp.route("/report", methods=["GET", "POST"])
def report():
    form_data = {"category": "", "location": "", "description": ""}
    errors = {}

    if request.method == "POST":
        form_data, errors = validate_report(
            request.form.get("category", ""),
            request.form.get("location", ""),
            request.form.get("description", ""),
        )
        if not errors:
            incident, report = submit_report(**form_data)
            return render_template(
                "report_confirmation.html", incident=incident, report=report
            )

    return render_template(
        "report.html",
        categories=CATEGORIES,
        form_data=form_data,
        errors=errors,
    )
