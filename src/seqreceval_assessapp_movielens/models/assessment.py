import datetime
import uuid

from flask_login import UserMixin

from ..extensions.database import db
from .interaction import Movie, User
from .utils import Model


class Assessor(UserMixin, Model):
    created_at = db.Column(db.DateTime(), nullable=False)

    def __init__(self, **kwargs):
        kwargs["created_at"] = datetime.datetime.now()
        super().__init__(**kwargs)


class Condition(Model):
    __table_args__ = Model._update_table_args(
        db.UniqueConstraint("past_count", "show_next")
    )

    past_count = db.Column(db.Integer(), nullable=False)
    show_next = db.Column(db.Boolean(), nullable=False)
    is_enabled = db.Column(db.Boolean(), nullable=False)

    def __init__(self, **kwargs):
        kwargs["is_enabled"] = True
        super().__init__(**kwargs)

    def __str__(self):
        return f"Condition(past_count={self.past_count}, show_next={self.show_next}, is_enabled={self.is_enabled})"


class Assessment(Model):
    __table_args__ = Model._update_table_args(
        db.UniqueConstraint("assessor_id", "user_id")
    )

    assessor_id = db.Column(db.Integer(), db.ForeignKey(Assessor.id), index=True, nullable=False)
    user_id = db.Column(db.Integer(), db.ForeignKey(User.id), index=True, nullable=False)
    condition_id = db.Column(db.Integer(), db.ForeignKey(Condition.id), index=True, nullable=False)
    is_completed = db.Column(db.Boolean(), nullable=False)
    completion_code = db.Column(db.String(63), index=True)
    started_at = db.Column(db.DateTime(), nullable=False)
    finished_at = db.Column(db.DateTime(), nullable=False)

    @db.declared_attr
    def assessor(cls):
        return cls._create_relationship(Assessor)

    @db.declared_attr
    def user(cls):
        return cls._create_relationship(User)

    @db.declared_attr
    def condition(cls):
        return cls._create_relationship(Condition)

    def __init__(self, **kwargs):
        kwargs["completion_code"] = str(uuid.uuid4()) if kwargs["is_completed"] else None
        kwargs["finished_at"] = datetime.datetime.now()
        super().__init__(**kwargs)


class Response(Model):
    __table_args__ = Model._update_table_args(
        db.UniqueConstraint("assessment_id", "movie_id")
    )

    assessment_id = db.Column(db.Integer(), db.ForeignKey(Assessment.id), index=True, nullable=False)
    movie_id = db.Column(db.Integer(), db.ForeignKey(Movie.id), index=True, nullable=False)
    user_watch_movie = db.Column(db.Integer(), nullable=False)
    assessor_watch_movie = db.Column(db.Integer(), nullable=False)

    @db.declared_attr
    def assessment(cls):
        return cls._create_relationship(Assessment)

    @db.declared_attr
    def movie(cls):
        return cls._create_relationship(Movie)
