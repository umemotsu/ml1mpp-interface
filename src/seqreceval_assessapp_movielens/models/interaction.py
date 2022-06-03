from ..extensions.database import db
from .utils import Model, create_secondary_table


class Movie(Model):
    movie_lens_id = db.Column(db.Integer(), unique=True, nullable=False)
    tmdb_id = db.Column(db.Integer(), unique=True)
    imdb_id = db.Column(db.String(15), unique=True)
    title = db.Column(db.String(255), nullable=False)
    release = db.Column(db.Date(), index=True)
    runtime = db.Column(db.Integer())
    poster_path = db.Column(db.String(63))


    def __str__(self):
        return f"Movie(title={repr(self.title)})"


class Genre(Model):
    name = db.Column(db.String(63), unique=True, nullable=False)

    def __str__(self):
        return f"Genre(name={repr(self.name)})"


movie_genre_links = create_secondary_table("movie_genre_links", Movie, Genre)
Movie.genres = Movie._create_relationship(Genre, secondary=movie_genre_links)


class User(Model):
    movie_lens_id = db.Column(db.Integer(), unique=True, nullable=False)


class PastInteraction(Model):
    __table_args__ = Model._update_table_args(
        db.UniqueConstraint("user_id", "movie_id", "timepoint")
    )

    user_id = db.Column(db.Integer(), db.ForeignKey(User.id), index=True, nullable=False)
    movie_id = db.Column(db.Integer(), db.ForeignKey(Movie.id), index=True, nullable=False)
    timepoint = db.Column(db.Integer(), index=True, nullable=False)
    interacted_at = db.Column(db.DateTime(), nullable=False)
    rating = db.Column(db.Integer(), nullable=False)

    @db.declared_attr
    def user(cls):
        return cls._create_relationship(User)

    @db.declared_attr
    def movie(cls):
        return cls._create_relationship(Movie)


class PositiveInteraction(Model):
    user_id = db.Column(db.Integer(), db.ForeignKey(User.id), unique=True, nullable=False)
    movie_id = db.Column(db.Integer(), db.ForeignKey(Movie.id), index=True, nullable=False)
    interacted_at = db.Column(db.DateTime(), nullable=False)
    rating = db.Column(db.Integer(), nullable=False)

    @db.declared_attr
    def user(cls):
        return cls._create_relationship(
            User,
            backref_name=cls.__tablename__[:-1],
            backref_uselist=False
        )

    @db.declared_attr
    def movie(cls):
        return cls._create_relationship(Movie)


class NegativeInteraction(Model):
    __table_args__ = Model._update_table_args(
        db.UniqueConstraint("user_id", "movie_id")
    )

    user_id = db.Column(db.Integer(), db.ForeignKey(User.id), index=True, nullable=False)
    movie_id = db.Column(db.Integer(), db.ForeignKey(Movie.id), index=True, nullable=False)

    @db.declared_attr
    def user(cls):
        return cls._create_relationship(User)

    @db.declared_attr
    def movie(cls):
        return cls._create_relationship(Movie)


class PredictedInteraction(Model):
    __table_args__ = Model._update_table_args(
        db.UniqueConstraint("user_id", "movie_id")
    )

    user_id = db.Column(db.Integer(), db.ForeignKey(User.id), index=True, nullable=False)
    movie_id = db.Column(db.Integer(), db.ForeignKey(Movie.id), index=True, nullable=False)

    @db.declared_attr
    def user(cls):
        return cls._create_relationship(User)

    @db.declared_attr
    def movie(cls):
        return cls._create_relationship(Movie)


class NextInteraction(Model):
    user_id = db.Column(db.Integer(), db.ForeignKey(User.id), unique=True, nullable=False)
    movie_id = db.Column(db.Integer(), db.ForeignKey(Movie.id), index=True, nullable=False)
    interacted_at = db.Column(db.DateTime(), nullable=False)
    rating = db.Column(db.Integer(), nullable=False)

    @db.declared_attr
    def user(cls):
        return cls._create_relationship(
            User,
            backref_name=cls.__tablename__[:-1],
            backref_uselist=False
        )

    @db.declared_attr
    def movie(cls):
        return cls._create_relationship(Movie)
