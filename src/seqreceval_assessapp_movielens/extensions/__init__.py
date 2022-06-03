from .database import db
from .login import login_manager


extensions = [db, login_manager]
