import time

from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user, login_user, logout_user

from ..models.assessment import Assessor
from ..models.interaction import Movie


bp = Blueprint("sandbox", __name__, url_prefix="/sandbox")


@bp.route("/assessment")
def assessment():
    past_movies = Movie.query[1:20]
    past_movies.insert(0, Movie.query.filter(Movie.poster_path.is_(None)).first())
    target_movies = Movie.query[20:30]
    next_movie = Movie.query[30]

    return render_template(
        "sandbox/assessment.html",
        past_movies=past_movies,
        target_movies=target_movies,
        next_movie=next_movie
    )


@bp.route("/session")
def session():
    return render_template("sandbox/session.html")


@bp.route("/session/login", methods=["POST"])
def session_login():
    if current_user.is_authenticated:
        flash("既にログインしています。")
    else:
        assessor = Assessor.create()
        login_user(assessor, remember=True)
        flash("ログインしました。")

    return redirect(url_for(".session"))


@bp.route("/session/logout", methods=["POST"])
def session_logout():
    logout_user()
    flash("ログアウトしました。")

    return redirect(url_for(".session"))


@bp.route("/session/user")
def session_user():
    if current_user.is_authenticated:
        flash("ユーザページです。")
    else:
        flash("ユーザページにアクセスするにはログインが必要です。")

    return redirect(url_for(".session"))


@bp.route("/sleep")
@bp.route("/sleep/<int:seconds>")
def sleep(seconds=10):
    time.sleep(seconds)

    return f"Sleeped for {seconds} seconds."
