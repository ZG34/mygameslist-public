""" TO GET TO WORK: Uncomment everything commented, enter whatever email/password you want to use """

import inspect
from time import time

from flask import session, request
import jwt

from app import app
from flask_mail import Mail, Message
from admintools.loggers import function_logger, logger_setup

logger = logger_setup(__name__, "log.log")

sender = 'admin email address'

# app.config.update(
#     MAIL_SERVER='smtp.gmail.com',
#     MAIL_PORT=465,
#     MAIL_USE_SSL=True,
#     MAIL_USERNAME=sender,
#     MAIL_PASSWORD='enter a password if you want to test'
# )
#
# mail = Mail(app)


def send_recovery_email(recipient, user):
    function_logger(logger, session, inspect.stack()[0][3], request.referrer)

    print("EMAIL FUNCTION COMMENTED OUT FOR PUBLIC RELEASE")

    # def get_reset_token(expires=500):
    #     return jwt.encode({'reset_password': user.name, 'exp': time() + expires}, key='gigatesting')
    #
    # token = get_reset_token()
    #
    # msg = Message()
    # msg.subject = 'MyGamesList Password Recovery'
    # msg.sender = sender
    # msg.recipients = [recipient]
    # msg.body = f"'{user.name}' has requested a password reset on MyGamesList.com. \n"\
    #             '----------------------- \n'\
    #             f"https://127.0.0.1:5000/reset/{token} \n" \
    #
    # mail.send(msg)

    return 'mail sent'