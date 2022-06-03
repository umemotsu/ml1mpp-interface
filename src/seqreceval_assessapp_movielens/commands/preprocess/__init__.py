from ..utils import OrderedAppGroup
from .interaction import interaction_cli
from .movie import movie_cli


preprocess_cli = OrderedAppGroup("preprocess", help="Preprocess data.")


for group in [movie_cli, interaction_cli]:
    preprocess_cli.add_command(group)
