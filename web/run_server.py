# -*- coding: utf-8 -*-
from web_app import app

if __name__ == '__main__':
    import logging
    from logging.handlers import RotatingFileHandler
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    app_log = RotatingFileHandler('./play.log', maxBytes=100*1024*1024, backupCount=3)
    app_log.setFormatter(formatter)
    app_log.setLevel(logging.INFO)
    app.logger.addHandler(app_log)
    app.logger.setLevel(logging.INFO)


    access_log = open('./access.log', "a")
    error_log = open('./error.log', "a")

    from gevent.wsgi import WSGIServer
    http_server = WSGIServer(('0.0.0.0', 44399),
                             app,
                             log=access_log,
                             error_log=error_log)
    http_server.serve_forever()
