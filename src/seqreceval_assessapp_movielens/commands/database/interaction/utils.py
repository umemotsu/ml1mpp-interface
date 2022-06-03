import dataclasses
import datetime

from ....models.interaction import (
    User,
    Movie,
    NegativeInteraction,
    NextInteraction,
    PastInteraction,
    PositiveInteraction,
    PredictedInteraction
)


@dataclasses.dataclass
class InsertionCount:
    total: int = 0
    success: int = 0

    @property
    def ratio(self):
        return self.success / self.total

    def __add__(self, other):
        if not isinstance(other, InsertionCount):
            return NotImplemented

        return InsertionCount(self.total + other.total, self.success + other.success)

    def __iadd__(self, other):
        if not isinstance(other, InsertionCount):
            return NotImplemented

        self.total += other.total
        self.success += other.success

        return self

    def increment(self, is_success):
        if is_success:
            self.succeed()
        else:
            self.fail()

    def succeed(self):
        self.total += 1
        self.success += 1

    def fail(self):
        self.total += 1


def create_user(ml_user_id):
    return User.create(commit=False, movie_lens_id=ml_user_id)


def create_past_interactions(user, e_records):
    count = InsertionCount()

    for timepoint, e_record in enumerate(e_records, start=1):
        movie = _get_movie(e_record.movie)

        if not movie:
            count.fail()
            continue

        PastInteraction.create(
            commit=False,
            user=user,
            movie=movie,
            timepoint=timepoint,
            interacted_at=_parse_datetime(e_record.timestamp),
            rating=e_record.rating
        )
        count.succeed()

    return count


def create_positive_interaction(user, e_record):
    movie = _get_movie(e_record.movie)

    if not movie:
        return False

    PositiveInteraction.create(
        commit=False,
        user=user,
        movie=movie,
        interacted_at=_parse_datetime(e_record.timestamp),
        rating=e_record.rating
    )

    return True


def create_negative_interactions(user, records):
    count = InsertionCount()

    for record in records:
        movie = _get_movie(record.movie)

        if not movie:
            count.fail()
            continue

        NegativeInteraction.create(commit=False, user=user, movie=movie)
        count.succeed()

    return count


def create_predicted_interactions(user, records):
    count = InsertionCount()

    for record in records:
        movie = _get_movie(record.movie)

        if not movie:
            count.fail()
            continue

        PredictedInteraction.create(commit=False, user=user, movie=movie)
        count.succeed()

    return count


def create_next_interaction(user, e_record):
    movie = _get_movie(e_record.movie)

    if not movie:
        return False

    NextInteraction.create(
        commit=False,
        user=user,
        movie=movie,
        interacted_at=_parse_datetime(e_record.timestamp),
        rating=e_record.rating
    )

    return True


def _get_movie(ml_movie_id):
    return Movie.get_by({"movie_lens_id": ml_movie_id})


def _parse_datetime(timestamp):
    return datetime.datetime.fromtimestamp(timestamp)
