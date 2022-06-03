import click
import jsonlines
import tqdm

from ....models.interaction import Genre, Movie
from ....extensions.database import db
from ...utils import Echo, OrderedAppGroup
from .utils import parse_date, parse_optional


movie_cli = OrderedAppGroup("movie", help="Interact with movie data.")


@movie_cli.command()
@click.argument("movie_data_file", type=click.File("r"))
def insert_movie_lens(movie_data_file):
    """
    Insert MovieLens data in MOVIE_DATA_FILE into database.
    """
    def create_movie(data):
        # Defaults to None when other falsy values represent missing data.
        movie_lens_id = data["movieId"]
        tmdb_id = data["tmdbMovieId"] or None
        imdb_id = parse_optional(data["imdbMovieId"], lambda s: "tt" + s)
        title = data["title"]
        release = parse_optional(data["releaseDate"], parse_date)
        runtime = data["runtime"] or None
        poster_path = data["posterPath"] or None
        movie = Movie.create(
            commit=False,
            movie_lens_id=movie_lens_id,
            tmdb_id=tmdb_id,
            imdb_id=imdb_id,
            title=title,
            release=release,
            runtime=runtime,
            poster_path=poster_path
        )

        return movie

    def get_or_create_genres(data):
        genres = [
            Genre.get_by_or_create({"name": name}, commit=False, name=name)
            for name in data["genres"]
            if name
        ]

        return genres

    total_count = 0
    skip_count = 0

    Echo.info("Inserting movie data...")
    with jsonlines.Reader(movie_data_file) as reader:
        for i, data in enumerate(tqdm.tqdm(reader)):
            total_count += 1

            if not data:
                skip_count += 1
                Echo.warning(f"Skip {i}-th data as it is empty.")
                continue

            movie = create_movie(data)
            movie.genres = get_or_create_genres(data)

        Echo.info("Committing transaction...")
        db.session.commit()

    Echo.info(f"Inserted data for {total_count - skip_count} out of {total_count} movies.")


@movie_cli.command()
@click.argument("movie_data_file", type=click.File("r"))
@click.argument("movie_id_pair_file", type=click.File("r"))
def insert_tmdb(movie_data_file, movie_id_pair_file):
    """
    Insert TMDB data in MOVIE_DATA_FILE into database.
    Additional argument MOVIE_ID_PAIR_FILE contains correspondence
    between MovieLens ID and TMDB ID in TSV format.
    """
    def create_movie(data, mapping):
        # Defaults to None when other falsy values represent missing data.
        tmdb_id = data["id"]
        movie_lens_id = mapping[tmdb_id]
        imdb_id = data["imdb_id"] or None
        title = data["title"]
        release = parse_optional(data["release_date"], parse_date)
        runtime = data["runtime"] or None
        poster_path = data["poster_path"] or None
        movie = Movie.create(
            commit=False,
            movie_lens_id=movie_lens_id,
            tmdb_id=tmdb_id,
            imdb_id=imdb_id,
            title=title,
            release=release,
            runtime=runtime,
            poster_path=poster_path
        )

        return movie

    def get_or_create_genres(data):
        genres = [
            Genre.get_by_or_create({"name": genre_data["name"]}, commit=False, name=genre_data["name"])
            for genre_data in data["genres"]
        ]

        return genres

    Echo.info("Creating mapping between MovieLens and TMDB...")
    mapping = {}
    total_count = 0
    skip_count = 0

    for line in movie_id_pair_file:
        total_count += 1
        movie_lens_id, tmdb_id = line.rstrip("\n").split("\t")

        if not tmdb_id:
            skip_count += 1
            Echo.warning(f"Skip MovieLens ID = {movie_lens_id} for which TMDB doesn't have movie data.")
            continue

        mapping[int(tmdb_id)] = int(movie_lens_id)

    Echo.info(f"Created mapping for {total_count - skip_count} out of {total_count} MovieLens IDs.")

    total_count = 0
    skip_count = 0

    Echo.info("Inserting movie data...")
    with jsonlines.Reader(movie_data_file) as reader:
        for i, data in enumerate(tqdm.tqdm(reader)):
            total_count += 1

            if not data:
                skip_count += 1
                Echo.warning(f"Skip {i}-th data as it is empty.")
                continue

            movie = create_movie(data, mapping)
            movie.genres = get_or_create_genres(data)

        Echo.info("Committing transaction...")
        db.session.commit()

    Echo.info(f"Inserted data for {total_count - skip_count} out of {total_count} movies.")
