import logging


def routing_logger(logger, session, environ):
    logger.info(f"user_id:[{session['user_id'] if 'user_id' in session else None}] "
                f"ROUTING: target "
                f"[{environ.get('RAW_URI')}] - accessed via: "
                f"[{environ.get('HTTP_REFERER', 'external')}]"
    )

def function_logger(logger, session, funcname, referrer):
    logger.info(f"user_id:[{session['user_id'] if 'user_id' in session else None}] "
                f"FUNCTION: called [{funcname}] VIA [{referrer}]")


def logger_setup(name, log_file, level=logging.INFO):
    formatter = logging.Formatter(
        "[%(levelname)s], [%(asctime)s], [%(name)s] [%(filename)s], caller [%(funcName)s], '%(message)s'"
    )

    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    return logger