import logging
from rsstory.scheduler import scheduler


from .models import (
    DBSession,
    Feed,
    User,
    )

log = logging.getLogger(__name__)

def get_user_feeds(user_id):
    feeds = DBSession.query(Feed).filter_by(user=user_id)
    return feeds

''' Updates the title and time between posts for the noted feed. authenticated_user_id passed in MUST be the authenticated_userid of the current user for security'''
def update_user_feeds(feed_id, title, time_between, authenticated_user_id):
    feed = DBSession.query(Feed).filter_by(id=feed_id, user=authenticated_user_id).first()
    feed.title = title
    feed.time_between_posts = int(time_between) * 60 * 24
    log.debug("Trying to update job {} to run every {} seconds".format(feed_id, feed.time_between_posts))

    scheduler.reschedule_job(feed.id, trigger='interval', seconds=feed.time_between_posts)
    
def update_place_in_feed(feed_id, page_id, authenticated_user_id):
    feed = DBSession.query(Feed).filter_by(id=feed_id, user=authenticated_user_id).first()
    feed.most_recent_page = page_id
    print("feed id: {} page id: {}".format(feed_id, page_id))

def delete_feed(feed_id, authenticated_user_id):
    feed = DBSession.query(Feed).filter_by(id=feed_id, user=authenticated_user_id)
    scheduler.remove_job(feed_id)
    feed.delete()
    log.debug("Feed id: {} was deleted".format(feed_id))

