import logging


from .models import (
    DBSession,
    Feed,
    User,
    )

log = logging.getLogger(__name__)


def get_user_feeds(user_id):
    feeds = DBSession.query(Feed).filter_by(user=user_id)
    return feeds
    
