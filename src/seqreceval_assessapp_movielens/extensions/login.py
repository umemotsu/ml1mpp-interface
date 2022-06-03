from flask import redirect, url_for
from flask_login import LoginManager


login_manager = LoginManager()


@login_manager.user_loader
def load_assessor(user_id):
    from ..models.assessment import Assessor

    assessor_id = int(user_id)

    return Assessor.query.get(assessor_id)


@login_manager.unauthorized_handler
def unauthorized():
    return redirect(url_for("assessor.index"))
