import click
import jsonlines
import tqdm

from ....extensions.database import db
from ...preprocess.interaction.utils import EnrichedInteraction
from ...utils import Echo, OrderedAppGroup
from .utils import (
    InsertionCount,
    create_negative_interactions,
    create_next_interaction,
    create_past_interactions,
    create_positive_interaction,
    create_predicted_interactions,
    create_user
)


interaction_cli = OrderedAppGroup("interaction", help="Interact with interaction data.")


@interaction_cli.command()
@click.argument("enriched_interaction_file", type=click.File("r"))
def insert(enriched_interaction_file):
    """
    Insert enriched interaction data into database.
    """
    def report_multiple(name, counts):
        mean_ratio = sum(c.ratio for c in counts) / len(counts)
        worst_success = min(c.success for c in counts)
        n_worst_successes = sum(1 for c in counts if c.success == worst_success)

        Echo.info(
            f"{name} interactions: mean_ratio = {mean_ratio:.6f}, "
            f"worst_success = {worst_success} (N = {n_worst_successes})."
        )

    def report_single(name, count):
        Echo.info(f"{name} interactions: ratio = {count.ratio:.6f}.")

    Echo.info("Reading enriched interaction data...")
    interactions = []

    with jsonlines.Reader(enriched_interaction_file) as reader:
        for obj in reader:
            interaction = EnrichedInteraction.from_dict(obj)
            interactions.append(interaction)

    Echo.info("Inserting enriched interaction data...")
    past_insertion_counts = []
    positive_insertion_count = InsertionCount()
    negative_insertion_counts = []
    predicted_insertion_counts = []
    next_interaction_count = InsertionCount()

    for interaction in tqdm.tqdm(interactions):
        user = create_user(interaction.user)

        count = create_past_interactions(user, interaction.past)
        past_insertion_counts.append(count)

        is_success = create_positive_interaction(user, interaction.positive)
        positive_insertion_count.increment(is_success)

        count = create_negative_interactions(user, interaction.negative)
        negative_insertion_counts.append(count)

        count = create_predicted_interactions(user, interaction.predicted)
        predicted_insertion_counts.append(count)

        is_success = create_next_interaction(user, interaction.next)
        next_interaction_count.increment(is_success)

    Echo.info("Committing transaction...")
    db.session.commit()

    Echo.info("Reporting insertion count stats...")
    report_multiple("Past", past_insertion_counts)
    report_single("Positive", positive_insertion_count)
    report_multiple("Negative", negative_insertion_counts)
    report_multiple("Predicted", predicted_insertion_counts)
    report_single("Next", next_interaction_count)
