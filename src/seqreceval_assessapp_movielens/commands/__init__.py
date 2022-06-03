from .utils import OrderedAppGroup
from .database import database_cli
from .preprocess import preprocess_cli


custom_cli = OrderedAppGroup("custom", help="Custom commands for the app.")


for group in [preprocess_cli, database_cli]:
    custom_cli.add_command(group)
