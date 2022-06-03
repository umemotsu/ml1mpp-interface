import abc
import dataclasses
import typing


class InteractionReaderABC(abc.ABC):
    def __init__(self, inter_file):
        self._inter_file = inter_file

    def __iter__(self):
        # Skip header
        next(self._inter_file)

        for line in self._inter_file:
            user_id_str, movie_field = line.rstrip("\n").split("\t")

            yield int(user_id_str), self._parse_movie_field(movie_field)

    def read(self):
        interactions = {}

        for user, record_or_records in self:
            interactions[user] = record_or_records

        return interactions

    @abc.abstractmethod
    def _parse_movie_field(self, string):
        pass


class SingleInteractionReader(InteractionReaderABC):
    def _parse_movie_field(self, movie_id_str):
        return Record(int(movie_id_str))


class MultipleInteractionReader(InteractionReaderABC):
    def _parse_movie_field(self, movie_ids_str):
        return [Record(int(movie_id_str)) for movie_id_str in movie_ids_str.split(",")]


@dataclasses.dataclass
class Record:
    movie: int

    @classmethod
    def from_dict(cls, d):
        names = set(f.name for f in dataclasses.fields(cls))
        d = {k: v for k, v in d.items() if k in names}

        return cls(**d)


@dataclasses.dataclass
class Interaction:
    user: int
    past: typing.List[Record]
    positive: Record
    negative: typing.List[Record]
    predicted: typing.List[Record]
    next: Record

    @classmethod
    def from_dict(cls, d):
        d = d.copy()

        for singleton_key in ["positive", "next"]:
            d[singleton_key] = Record.from_dict(d[singleton_key])

        for list_key in ["past", "negative", "predicted"]:
            d[list_key] = list(map(Record.from_dict, d[list_key]))

        return cls(**d)


@dataclasses.dataclass
class EnrichedRecord(Record):
    timestamp: int
    rating: int

@dataclasses.dataclass
class EnrichedInteraction(Interaction):
    past: typing.List[EnrichedRecord]
    positive: EnrichedRecord
    next: EnrichedRecord

    @classmethod
    def from_dict(cls, d):
        ei = super().from_dict(d)

        for e_singleton_key in ["positive", "next"]:
            er = EnrichedRecord.from_dict(d[e_singleton_key])
            setattr(ei, e_singleton_key, er)

        for e_list_key in ["past"]:
            er_list = list(map(EnrichedRecord.from_dict, d[e_list_key]))
            setattr(ei, e_list_key, er_list)

        return ei


class MovieLensInteraction:
    def __init__(self, inter_file):
        self.user_to_enriched_records = self._construct_reverse_sequences(inter_file)

    def _construct_reverse_sequences(self, inter_file):
        user_to_records = {}

        for line in inter_file:
            user, movie, rating, timestamp = list(map(int, line.rstrip("\n").split("\t")))
            record = EnrichedRecord(movie, timestamp, rating)
            items = user_to_records.setdefault(user, [])
            items.append(record)

        for items in user_to_records.values():
            items.sort(key=lambda r: r.timestamp, reverse=True)

        return user_to_records

    def enrich(self, interaction):
        user = interaction.user
        e_records = self.user_to_enriched_records[user]

        next_, e_records = self._find_single(interaction.next, e_records)
        positive, e_records = self._find_single(interaction.positive, e_records)
        past, e_records = self._find_multiple(interaction.past, e_records)

        return EnrichedInteraction(
            user,
            past,
            positive,
            interaction.negative,
            interaction.predicted,
            next_
        )

    def _find_single(self, record, e_records):
        e_records = e_records.copy()

        for i, e_record in enumerate(e_records):
            if e_record.movie == record.movie:
                target = e_records.pop(i)

                return target, e_records

        raise KeyError(f"No record for movie = {record.movie}.")

    def _find_multiple(self, records, e_records):
        targets = []

        for record in records[::-1]:
            target, e_records = self._find_single(record, e_records)
            targets.append(target)

        return targets[::-1], e_records
