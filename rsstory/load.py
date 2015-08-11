import rsstory.global_vars as global_vars
from random import SystemRandom

def reload_curr_id():
    global_vars.curr_id = SystemRandom().getrandbits(512)

