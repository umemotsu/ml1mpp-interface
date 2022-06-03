from ..utils import OrderedAppGroup
from .assessment import assessment_cli
from .condition import condition_cli
from .interaction import interaction_cli
from .movie import movie_cli


database_cli = OrderedAppGroup("database", help="Interact with database.")


for group in [movie_cli, interaction_cli, condition_cli, assessment_cli]:
    database_cli.add_command(group)
