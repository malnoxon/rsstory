import rsstory.global_vars as global_vars
import os, natsort

def reload_global_index():
    files = os.listdir(os.path.join(os.getcwd(), 'rsstory', 'static', 'rssitems'))
    if files == []:
        global_vars.global_index = 1
    else:
        sorted_files = natsort.natsorted(files, key=lambda y: y.lower())
        global_vars.global_index = int(sorted_files[-1].split(sep=".")[0][8:]) + 1

