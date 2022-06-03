import datetime

from flask import Blueprint, current_app, redirect, render_template, request, url_for
from flask_login import current_user as current_assessor, login_required, login_user

from ...extensions.database import db
from ...models.assessment import Assessor, Assessment, Response
from .utils import (
    assign_condition,
    assign_user,
    is_rookie,
    json_api,
    organize_items,
    parse_datetime,
    validate_completion
)


bp = Blueprint("assessor", __name__)


@bp.route("/")
def index():
    return redirect(url_for(".agreement"))


@bp.route("/agreement", methods=["GET", "POST"])
def agreement():
    if current_assessor.is_authenticated:
        return redirect(url_for(".assessment"))

    if request.method == "POST" and request.form["agreed"] == "true":
        assessor = Assessor.create()
        login_user(assessor, remember=True)

        return redirect(url_for(".assessment"))

    return render_template("assessor/agreement.html")


@bp.route("/assessment")
@login_required
def assessment():
    assessment_count = current_app.config["SEQRECEVAL_ASSESSAPP_ASSESSMENT_COUNT"]
    user = assign_user(current_assessor, assessment_count)

    if not user:
        return redirect(url_for(".close"))

    condition = assign_condition(user, assessment_count)
    past_interactions, target_movies, target_date, next_interaction = organize_items(user, condition)

    started_at = datetime.datetime.now()

    return render_template(
        "assessor/assessment.html",
        assessor=current_assessor,
        is_rookie=is_rookie(current_assessor),
        user=user,
        condition=condition,
        started_at=started_at,
        past_interactions=past_interactions,
        target_movies=target_movies,
        target_date=target_date,
        next_interaction=next_interaction
    )


@bp.route("/close")
def close():
    return render_template("assessor/close.html")


@bp.route("/assessment/skip", methods=["POST"])
@login_required
@json_api
def assessment_skip():
    json = request.json
    Assessment.create(
        assessor_id=current_assessor.id,
        user_id=json["user_id"],
        condition_id=json["condition_id"],
        is_completed=False,
        started_at=parse_datetime(json["started_at"])
    )

    return {"redirect": url_for(".assessment")}


@bp.route("/assessment/complete", methods=["POST"])
@login_required
@json_api
def assessment_compelete():
    json = request.json
    assessment = Assessment.create(
        commit=False,
        assessor_id=current_assessor.id,
        user_id=json["user_id"],
        condition_id=json["condition_id"],
        is_completed=True,
        started_at=parse_datetime(json["started_at"])
    )

    for response in json["responses"]:
        Response.create(
            commit=False,
            assessment=assessment,
            movie_id=response["movie_id"],
            user_watch_movie=response["user_watch_movie"],
            assessor_watch_movie=response["assessor_watch_movie"]
        )

    db.session.commit()

    return {"redirect": url_for(".completion", code=assessment.completion_code)}


@bp.route("/completion/<uuid:code>")
@login_required
def completion(code):
    code = str(code)

    if not validate_completion(current_assessor, code):
        code = None

    return render_template("assessor/completion.html", completion_code=code)
