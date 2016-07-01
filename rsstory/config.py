from authomatic.providers import oauth2, oauth1, openid
import os
import logging

log = logging.getLogger(__name__)
try:
    keys = {}
    # import pdb; pdb.set_trace();
    with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'secret', 'secrets.keys'), 'r') as f:
        _ = f.readline()
        name, key, secret = f.readline().split(",")
        keys[name] = (key.strip(), secret.strip())
except:
    log.error("The file containing the secret keys was not located")

CONFIG = {
        'google': {
            # also, https://console.developers.google.com/apis/credentials/oauthclient/513100890007-jd02kbncueeons32v6rbc739locv0tnl.apps.googleusercontent.com?project=rsstory-1329 
            # cause we will need to add the right redirect uris
            # look at why when login it gives email=None

            'class_': oauth2.Google,

            # Facebook is an AuthorizationProvider too.
            'consumer_key': keys['google'][0],
            'consumer_secret': keys['google'][1],

            # But it is also an OAuth 2.0 provider and it needs scope.
            'scope': ['email'],
            },

        'oi': {

            # OpenID provider dependent on the python-openid package.
            'class_': openid.OpenID,
            }

        }
