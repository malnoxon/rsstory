from apscheduler.schedulers.background import BackgroundScheduler
scheduler = BackgroundScheduler()

# sched.configure(options_from_ini_file) TODO
scheduler.start()
