import os

import click
import jsonlines
import tqdm

from ...utils import Echo, OrderedAppGroup
from .utils import MovieLensAPI, TheMovieDatabaseAPI


movie_cli = OrderedAppGroup("movie", help="Collect movie data from sites.")


@movie_cli.command()
@click.option(
    "-u", "--username",
    prompt=True, prompt_required=False,
    show_default="use MOVIELENS_USERNAME env var",
    help="Username of MovieLens account."
)
@click.option(
    "-p", "--password",
    prompt=True, prompt_required=False, hide_input=True,
    show_default="use MOVIELENS_PASSWORD env var",
    help="Password of MovieLens account."
)
@click.option(
    "-i", "--interval",
    type=float,
    default=1, show_default=True,
    help='Time interval (in seconds) between successive API requests.'
)
@click.argument("movie_id_file", type=click.File("r"))
@click.argument("movie_data_file", type=click.File("w"))
def movie_lens(username, password, interval, movie_id_file, movie_data_file):
    """
    Collect details for each movie in MOVIE_ID_FILE (one MovieLens ID per line)
    and save them to MOVIE_DATA_FILE in JSONL format.
    """
    if not username:
        try:
            username = os.environ["MOVIELENS_USERNAME"]
        except KeyError:
            raise click.UsageError("Username must be set via option or env var.")

    if not password:
        try:
            password = os.environ["MOVIELENS_PASSWORD"]
        except KeyError:
            raise click.UsageError("Password must be set via option or env var.")

    api = MovieLensAPI(username, password, interval)
    movie_ids = [int(line.rstrip("\n")) for line in movie_id_file]

    total_count = len(movie_ids)
    error_count = 0

    Echo.info(f"Collecting movie details from MovieLens...")

    with jsonlines.Writer(movie_data_file, sort_keys=True) as writer:
        for movie_id in tqdm.tqdm(movie_ids):
            try:
                movie_json = api.movie(movie_id)
            except Exception:
                movie_json = {}
                error_count += 1
                Echo.warning(f"Failed to collect movie details: ID = {movie_id}")

            writer.write(movie_json)

    Echo.info(f"Collected details for {total_count - error_count} out of {total_count} movies.")


@movie_cli.command()
@click.option(
    "-a", "--access_token",
    prompt=True, prompt_required=False, hide_input=True,
    show_default="use TMDB_ACCESS_TOKEN env var",
    help="Access token of TMDB account."
)
@click.option(
    "-l", "--language",
    default="en-US", show_default=True,
    help='Language code that may be used by API.'
)
@click.option(
    "-i", "--interval",
    type=float,
    default=1, show_default=True,
    help='Time interval (in seconds) between successive API requests.'
)
@click.argument("movie_id_file", type=click.File("r"))
@click.argument("movie_data_file", type=click.File("w"))
def tmdb(access_token, language, interval, movie_id_file, movie_data_file):
    """
    Collect details for each movie in MOVIE_ID_FILE (one TMDB ID per line)
    and save them to MOVIE_DATA_FILE in JSONL format.
    """
    if not access_token:
        try:
            access_token = os.environ["TMDB_ACCESS_TOKEN"]
        except KeyError:
            raise click.UsageError("Access token must be set via option or env var.")

    api = TheMovieDatabaseAPI(access_token, language, interval)
    movie_ids = [int(line.rstrip("\n")) for line in movie_id_file]

    total_count = len(movie_ids)
    error_count = 0

    Echo.info(f"Collecting movie details from TMDB...")

    with jsonlines.Writer(movie_data_file, sort_keys=True) as writer:
        for movie_id in tqdm.tqdm(movie_ids):
            try:
                movie_json = api.movie(movie_id)
            except Exception:
                movie_json = {}
                error_count += 1
                Echo.warning(f"Failed to collect movie details: ID = {movie_id}")

            writer.write(movie_json)

    Echo.info(f"Collected details for {total_count - error_count} out of {total_count} movies.")
