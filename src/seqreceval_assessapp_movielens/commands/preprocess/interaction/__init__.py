import dataclasses
import click
import jsonlines

from ...utils import Echo, OrderedAppGroup
from .utils import (
    Interaction,
    MovieLensInteraction,
    MultipleInteractionReader,
    SingleInteractionReader
)


interaction_cli = OrderedAppGroup("interaction", help="Preprocess interaction data.")


@interaction_cli.command()
@click.argument("past_interaction_file", type=click.File("r"))
@click.argument("positive_interaction_file", type=click.File("r"))
@click.argument("negative_interaction_file", type=click.File("r"))
@click.argument("predicted_interaction_file", type=click.File("r"))
@click.argument("next_interaction_file", type=click.File("r"))
@click.argument("converted_interaction_file", type=click.File("w"))
def convert(
    past_interaction_file,
    positive_interaction_file,
    negative_interaction_file,
    predicted_interaction_file,
    next_interaction_file,
    converted_interaction_file
):
    """
    Convert original (past, positive, negative, predicted, and next)
    interaction files in TSV format into a single JSONL file.
    """
    Echo.info("Reading original interactions...")
    past_interactions = MultipleInteractionReader(past_interaction_file).read()
    positive_interactions = SingleInteractionReader(positive_interaction_file).read()
    negative_interactions = MultipleInteractionReader(negative_interaction_file).read()
    predicted_interactions = MultipleInteractionReader(predicted_interaction_file).read()
    next_interactions = SingleInteractionReader(next_interaction_file).read()

    users = set(past_interactions)
    if not (
        users
        == set(positive_interactions)
        == set(negative_interactions)
        == set(predicted_interactions)
        == set(next_interactions)
    ):
        raise ValueError("Different interaction files have different user sets.")
    Echo.info(f"Read interactions of {len(users)} users.")

    Echo.info("Writing converted interactions...")
    with jsonlines.Writer(converted_interaction_file) as writer:
        for user in users:
            interaction = Interaction(
                user=user,
                past=past_interactions[user],
                positive=positive_interactions[user],
                negative=negative_interactions[user],
                predicted=predicted_interactions[user],
                next=next_interactions[user]
            )
            obj = dataclasses.asdict(interaction)
            writer.write(obj)


@interaction_cli.command()
@click.argument("movie_lens_interaction_file", type=click.File("r"))
@click.argument("src_interaction_file", type=click.File("r"))
@click.argument("dst_interaction_file", type=click.File("w"))
def enrich(movie_lens_interaction_file, src_interaction_file, dst_interaction_file):
    """
    Enrich interactions in JSONL-fomatted SRC_INTERACTION_FILE
    with additional data in TSV-fomatted MOVIE_LENS_INTERACTION_FILE
    and save enriched interactions to JSONL-fomatted DST_INTERACTION_FILE
    """
    Echo.info("Reading MovieLens interaction file...")
    movie_lens = MovieLensInteraction(movie_lens_interaction_file)

    Echo.info("Enriching interactions...")
    with jsonlines.Reader(src_interaction_file) as reader, \
         jsonlines.Writer(dst_interaction_file) as writer:
        for obj in reader:
            interaction = Interaction.from_dict(obj)
            enriched_interaction = movie_lens.enrich(interaction)
            obj = dataclasses.asdict(enriched_interaction)
            writer.write(obj)
