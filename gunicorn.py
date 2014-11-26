import multiprocessing

bind = "127.0.0.1:8081"
pidfile = "/var/log/gunicorn/pds.pid"
workers = multiprocessing.cpu_count() * 2 + 1
accesslog = "/var/log/gunicorn/pds_access.log"
errorlog = "/var/log/gunicorn/pds_error.log"
loglevel = "debug"