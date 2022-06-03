import dataclasses

import click
import jsonlines
import tqdm

from ...utils import Echo, OrderedAppGroup
from .utils import DumpedRecordLoader, dictify_with_enum_name


assessment_cli = OrderedAppGroup("assessment", help="Interact with assessment data.")


@assessment_cli.command()
@click.argument("assessment_file", type=click.File("w"))
def dump(assessment_file):
    """
    Dump assessment data to ASSESSMENT_FILE in JSONL format.
    """
    Echo.info("Dumping assessment data from database...")
    with jsonlines.Writer(assessment_file) as writer:
        for record in tqdm.tqdm(DumpedRecordLoader()):
            obj = dataclasses.asdict(record, dict_factory=dictify_with_enum_name)
            writer.write(obj)
