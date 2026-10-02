from flask import Blueprint, abort, render_template, request

from app.repositories.incidents import (
    count_incident_reports,
    get_incident,
    list_incidents,
)
from app.repositories.reports import (
    attach_report_to_incident,
    create_report,
    get_incident_reports,
    get_report,
)
from app.services.duplicate_detector import (
    DUPLICATE_THRESHOLD,
    calculate_similarity,
    find_duplicate_candidates,
)
from app.services.report_service import (
    CATEGORIES,
    create_incident_for_report,
    validate_report,
)


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
            report = create_report(**form_data)
            candidates = find_duplicate_candidates(
                report, list_incidents(status="OPEN")
            )
            candidate = next(
                (item for item in candidates if item.score >= DUPLICATE_THRESHOLD),
                None,
            )
            if candidate is not None:
                return render_template(
                    "duplicate_confirmation.html",
                    candidate=candidate,
                    report=report,
                    report_count=count_incident_reports(candidate.incident.id),
                )

            incident = create_incident_for_report(report)
            attach_report_to_incident(report.id, incident.id)
            return render_template(
                "report_confirmation.html", incident=incident, report=report
            )

    return render_template(
        "report.html",
        categories=CATEGORIES,
        form_data=form_data,
        errors=errors,
    )


@main_bp.post("/report/decision")
def report_decision():
    action = request.form.get("action")
    try:
        report_id = int(request.form.get("report_id", ""))
        incident_id = int(request.form.get("incident_id", ""))
    except ValueError:
        abort(400)

    report = get_report(report_id)
    incident = get_incident(incident_id)
    if report is None or report.incident_id is not None or incident is None:
        abort(400)

    if action == "same":
        if (
            incident.status != "OPEN"
            or calculate_similarity(report, incident) < DUPLICATE_THRESHOLD
        ):
            abort(400)
        attach_report_to_incident(report.id, incident.id)
    elif action == "new":
        incident = create_incident_for_report(report)
        attach_report_to_incident(report.id, incident.id)
    else:
        abort(400)

    return render_template("report_confirmation.html", incident=incident, report=report)


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
