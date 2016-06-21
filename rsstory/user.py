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

def update_user_feeds(feed_id, title, time_between):
    feed = DBSession.query(Feed).filter_by(id=feed_id).first()
    feed.title = title
    feed.time_between_posts = time_between * 60
    
    
