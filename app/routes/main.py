from flask import (
    Blueprint,
    abort,
    current_app,
    redirect,
    render_template,
    request,
    send_from_directory,
    url_for,
)
from pathlib import Path

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
from app.repositories.locations import get_location, list_locations
from app.services.duplicate_detector import (
    DUPLICATE_THRESHOLD,
    calculate_similarity,
    find_duplicate_candidates,
)
from app.services.admin_service import (
    InvalidStatusTransition,
    get_admin_dashboard,
    transition_incident_status,
)
from app.services.report_service import (
    CATEGORIES,
    create_incident_for_report,
    refresh_incident_priority,
    validate_report,
)
from app.services.photo_service import PhotoValidationError, save_photo
from app.services.analytics_service import get_analytics


main_bp = Blueprint("main", __name__)


@main_bp.get("/")
def home():
    return render_template("home.html")


@main_bp.get("/health")
def health():
    return {"status": "ok"}


@main_bp.get("/analytics")
def analytics():
    return render_template("analytics.html", **get_analytics())


@main_bp.get("/uploads/<path:filename>")
def uploaded_photo(filename):
    if Path(filename).name != filename:
        abort(404)
    return send_from_directory(current_app.config["UPLOAD_FOLDER"], filename)


@main_bp.get("/admin/incidents")
def admin_incidents():
    return render_template("admin_dashboard.html", **get_admin_dashboard())


@main_bp.post("/admin/incidents/<int:incident_id>/status")
def admin_update_status(incident_id):
    incident = get_incident(incident_id)
    if incident is None:
        abort(404)
    try:
        transition_incident_status(incident, request.form.get("status", ""))
    except InvalidStatusTransition:
        abort(400)
    return redirect(url_for("main.admin_incidents"))


@main_bp.route("/report", methods=["GET", "POST"])
def report():
    form_data = {
        "category": "",
        "location": "",
        "location_id": "",
        "location_detail": "",
        "description": "",
    }
    errors = {}

    if request.method == "POST":
        location_id_value = request.form.get("location_id", "").strip()
        location_id = None
        location = request.form.get("location", "")
        if location_id_value:
            try:
                location_id = int(location_id_value)
            except ValueError:
                errors["location"] = "Choose a valid campus location."
            selected_location = get_location(location_id) if location_id else None
            if selected_location is None:
                errors["location"] = "Choose a valid campus location."
            else:
                location = f"{selected_location.building} - {selected_location.area}"

        form_data, errors = validate_report(
            request.form.get("category", ""),
            location,
            request.form.get("description", ""),
            location_id,
            request.form.get("location_detail", ""),
        )
        if "location" in errors and location_id_value:
            errors["location"] = "Choose a valid campus location."
        if not errors:
            try:
                photo_filename = save_photo(
                    request.files.get("photo"), current_app.config["UPLOAD_FOLDER"]
                )
            except PhotoValidationError as error:
                errors["photo"] = str(error)
            if errors:
                return render_template(
                    "report.html",
                    categories=CATEGORIES,
                    locations=list_locations(),
                    form_data=form_data,
                    errors=errors,
                )

            report = create_report(**form_data, photo_filename=photo_filename)
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
            if not attach_report_to_incident(report.id, incident.id):
                abort(409)
            return render_template(
                "report_confirmation.html", incident=incident, report=report
            )

    return render_template(
        "report.html",
        categories=CATEGORIES,
        locations=list_locations(),
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
        if not attach_report_to_incident(report.id, incident.id):
            abort(409)
        incident = refresh_incident_priority(incident.id)
    elif action == "new":
        incident = create_incident_for_report(report)
        if not attach_report_to_incident(report.id, incident.id):
            abort(409)
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
