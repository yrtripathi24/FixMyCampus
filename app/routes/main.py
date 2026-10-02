from flask import Blueprint, abort, render_template, request

from app.repositories.incidents import (
    count_incident_reports,
    get_incident,
    list_incidents,
)
from app.repositories.reports import get_incident_reports
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


@main_bp.get("/incidents")
def incidents():
    category = request.args.get("category", "").strip()
    status = request.args.get("status", "").strip()
    if category not in CATEGORIES:
        category = ""
    if status not in {"OPEN", "IN_PROGRESS", "RESOLVED"}:
        status = ""

    incident_list = list_incidents(category=category, status=status)
    report_counts = {
        incident.id: count_incident_reports(incident.id)
        for incident in incident_list
    }
    return render_template(
        "incidents.html",
        incidents=incident_list,
        report_counts=report_counts,
        categories=CATEGORIES,
        statuses=("OPEN", "IN_PROGRESS", "RESOLVED"),
        selected_category=category,
        selected_status=status,
    )


@main_bp.get("/incidents/<int:incident_id>")
def incident_detail(incident_id):
    incident = get_incident(incident_id)
    if incident is None:
        abort(404)
    return render_template(
        "incident_detail.html",
        incident=incident,
        reports=get_incident_reports(incident.id),
    )
