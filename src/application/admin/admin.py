from src import database as db
from src.application.carts import carts
from src.application.inventory import inventory


def reset_progress():
    """DANGER: Resets the shop progress"""
    with db.get_session() as sess, sess.begin():
        carts.reset_progress(sess)
        inventory.reset_progress(sess)
    return "OK"
