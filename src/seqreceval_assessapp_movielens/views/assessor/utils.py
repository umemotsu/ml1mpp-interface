import datetime
import functools
import http
import random

from flask import jsonify

from ...extensions.database import db
from ...models.assessment import Assessment, Condition
from ...models.interaction import (
    Movie,
    NegativeInteraction,
    NextInteraction,
    PastInteraction,
    PositiveInteraction,
    PredictedInteraction,
    User
)


def is_rookie(assessor):
    assessment_ids = (
        db.session
        .query(Assessment.id)
        .filter(Assessment.assessor_id == assessor.id)
    )

    return assessment_ids.first() is None


def assign_user(assessor, assessment_count):
    user_ids_assessed = (
        db.session
        .query(Assessment.user_id)
        .filter(Assessment.assessor_id == assessor.id)
    )
    user_ids_done_per_enabled_condition_subquery = (
        db.session
        .query(Assessment.user_id)
        .join(Condition)
        .filter(Assessment.is_completed == db.true(), Condition.is_enabled == db.true())
        .group_by(Assessment.user_id, Assessment.condition_id)
        .having(db.func.count() >= assessment_count)
        .subquery()
    )
    enabled_condition_count = (
        db.session
        .query(Condition)
        .filter(Condition.is_enabled == db.true())
        .count()
    )
    user_ids_done = (
        db.session
        .query(user_ids_done_per_enabled_condition_subquery.c.user_id)
        .group_by(user_ids_done_per_enabled_condition_subquery.c.user_id)
        .having(db.func.count() >= enabled_condition_count)
    )
    user_ids_assessed_or_done = user_ids_assessed.union(user_ids_done)
    users_assignable = (
        db.session
        .query(User)
        .filter(User.id.not_in(user_ids_assessed_or_done))
    )

    return _select_random_one(users_assignable)


def assign_condition(user, assessment_count):
    condition_ids_done = (
        db.session
        .query(Assessment.condition_id)
        .filter(Assessment.user_id == user.id, Assessment.is_completed == db.true())
        .group_by(Assessment.condition_id)
        .having(db.func.count() >= assessment_count)
    )
    enabled_conditions_assignable = (
        db.session
        .query(Condition)
        .filter(Condition.is_enabled == db.true(), Condition.id.not_in(condition_ids_done))
    )

    return _select_random_one(enabled_conditions_assignable)


def _select_random_one(query):
    try:
        return query.order_by(db.func.random()).first()
    except:
        pass

    try:
        return query.order_by(db.func.rand()).first()
    except:
        pass

    return random.choice(query.all())


def organize_items(user, condition):
    past_interactions = (
        db.session
        .query(PastInteraction)
        .filter(PastInteraction.user_id == user.id)
        .order_by(PastInteraction.timepoint)
        .all()
    )[-condition.past_count:]

    positive_interaction = (
        db.session
        .query(PositiveInteraction)
        .filter(PositiveInteraction.user_id == user.id)
        .one_or_none()
    )
    negative_movies = (
        db.session
        .query(Movie)
        .join(NegativeInteraction)
        .filter(NegativeInteraction.user_id == user.id)
        .all()
    )
    predicted_movies = (
        db.session
        .query(Movie)
        .join(PredictedInteraction)
        .filter(PredictedInteraction.user_id == user.id)
        .all()
    )
    target_movies, target_date = _merge_target_items(positive_interaction, negative_movies, predicted_movies)

    next_interaction = (
        db.session
        .query(NextInteraction)
        .filter(NextInteraction.user_id == user.id)
        .one_or_none()
    ) if condition.show_next else None

    return past_interactions, target_movies, target_date, next_interaction


def _merge_target_items(positive_interaction, negative_movies, predicted_movies):
    movie_ids = set()
    movies = []
    date = None

    if positive_interaction:
        positive_movie = positive_interaction.movie
        movie_ids.add(positive_movie.id)
        movies.append(positive_movie)
        date = positive_interaction.interacted_at.date()

    for movie in negative_movies + predicted_movies:
        if movie.id not in movie_ids:
            movie_ids.add(movie.id)
            movies.append(movie)

    random.shuffle(movies)

    return movies, date


def json_api(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        try:
            jsonable = f(*args, **kwargs)
            code = http.HTTPStatus.OK
        except Exception as e:
            jsonable = {
                'type': e.__class__.__name__,
                'message': str(e)
            }
            code = http.HTTPStatus.INTERNAL_SERVER_ERROR

        return jsonify(**jsonable), code

    return wrapper


def parse_datetime(string):
    return datetime.datetime.strptime(string, "%Y-%m-%d %H:%M:%S.%f")


def validate_completion(assessor, code):
    assessment_count = (
        db.session
        .query(Assessment)
        .filter(Assessment.assessor_id == assessor.id, Assessment.completion_code == code)
        .count()
    )

    return assessment_count > 0
