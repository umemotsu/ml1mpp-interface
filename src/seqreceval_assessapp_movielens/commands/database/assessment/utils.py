import dataclasses
import enum
import typing

from ....models.interaction import User


@dataclasses.dataclass
class Target:
    positive: typing.Optional[int]
    negative: typing.List[int]
    predicted: typing.List[int]


class UserWatchMovie(enum.Enum):
    YES = 1
    NO = 0
    UNCERTAIN = -1


class AssessorWatchMovie(enum.Enum):
    YES = 2
    NO_BUT_KNOW = 1
    NO_AND_NOT_KNOW = 0


@dataclasses.dataclass
class Response:
    movie: int
    user_watch_movie: UserWatchMovie
    assessor_watch_movie: AssessorWatchMovie

    @classmethod
    def from_dict(cls, d):
        d = d.copy()
        d["user_watch_movie"] = UserWatchMovie[d["user_watch_movie"]]
        d["assessor_watch_movie"] = AssessorWatchMovie[d["assessor_watch_movie"]]

        return cls(**d)


@dataclasses.dataclass
class Assessment:
    assessor: int
    condition: int
    time: int
    responses: typing.List[Response]

    @classmethod
    def from_dict(cls, d):
        d = d.copy()
        d["responses"] = list(map(Response.from_dict, d["responses"]))

        return cls(**d)


@dataclasses.dataclass
class DumpedRecord:
    user: int
    target: Target
    assessments: typing.List[Assessment]

    @classmethod
    def from_dict(cls, d):
        d = d.copy()
        d["target"] = Target(**d["target"])
        d["assessments"] = list(map(Assessment.from_dict, d["assessments"]))

        return cls(**d)


class DumpedRecordLoader:
    def __len__(self):
        return User.query.count()

    def __iter__(self):
        for user in User.query:
            target = self._load_target(user)
            assessments = self._load_assessments(user)

            yield DumpedRecord(user.movie_lens_id, target, assessments)

    def _load_target(self, user):
        if user.positive_interaction:
            positive = user.positive_interaction.movie.movie_lens_id
        else:
            positive = None

        negative = [ni.movie.movie_lens_id for ni in user.negative_interactions]
        predicted = [pi.movie.movie_lens_id for pi in user.predicted_interactions]

        return Target(positive, negative, predicted)

    def _load_assessments(self, user):
        return [
            Assessment(
                assessment.assessor_id,
                assessment.condition_id,
                self._measure_time(assessment),
                self._load_responses(assessment)
            )
            for assessment in user.assessments
            if assessment.is_completed
        ]

    def _measure_time(self, assessment):
        delta = assessment.finished_at - assessment.started_at

        return round(delta.total_seconds())

    def _load_responses(self, assessment):
        return [
            Response(
                response.movie.movie_lens_id,
                UserWatchMovie(response.user_watch_movie),
                AssessorWatchMovie(response.assessor_watch_movie)
            )
            for response in assessment.responses
        ]


def dictify_with_enum_name(data):
    def convert(value):
        if isinstance(value, enum.Enum):
            return value.name
        else:
            return value

    return {name: convert(value) for name, value in data}
