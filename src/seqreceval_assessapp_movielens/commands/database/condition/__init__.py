import click
from flask import current_app

from ....extensions.database import db
from ....models.assessment import Condition
from ...utils import Echo, OrderedAppGroup


condition_cli = OrderedAppGroup("condition", help="Interact with condition data.")


@condition_cli.command("list")
def list_():
    """
    List current conditions.
    """
    Echo.info("Listing conditions in database...")
    for condition in Condition.query:
        print(f"ID = {condition.id}: {condition}")


@condition_cli.command()
def insert():
    """
    Insert condition config into database.
    """
    Echo.info("Inserting condition data...")
    conditions = current_app.config["SEQRECEVAL_ASSESSAPP_CONDITIONS"]

    for past_count, show_next in conditions:
        Condition.create(commit=False, past_count=past_count, show_next=show_next)

    Echo.info(f"Inserted {len(conditions)} conditions.")

    Echo.info("Committing transaction...")
    db.session.commit()


@condition_cli.command()
@click.argument("condition_id", type=int, nargs=-1)
def enable(condition_id):
    """
    Enable conditions specified by their IDs.
    """
    Echo.info(f"Enabling {len(condition_id)} conditions...")
    for id_ in condition_id:
        condition = Condition.query.get(id_)

        if not condition:
            raise ValueError(f"Not found: ID = {id_}.")

        if condition.is_enabled:
            Echo.warning(f"Already enabled: ID = {id_}.")
            continue

        condition.update(is_enabled=True)


@condition_cli.command()
@click.argument("condition_id", type=int, nargs=-1)
def disable(condition_id):
    """
    Disable conditions specified by their IDs.
    """
    Echo.info(f"Disabling {len(condition_id)} conditions...")
    for id_ in condition_id:
        condition = Condition.query.get(id_)

        if not condition:
            raise ValueError(f"Not found: ID = {id_}.")

        if not condition.is_enabled:
            Echo.warning(f"Already disabled: ID = {id_}.")
            continue

        condition.update(is_enabled=False)
