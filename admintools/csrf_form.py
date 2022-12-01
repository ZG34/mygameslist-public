from os import urandom

from flask import current_app, session
from flask_admin._compat import text_type
from flask_admin.form import BaseForm

from app import csrf

class SessionCSRF():
    def generate_csrf_token(self):
        csrf.generate_new_token()

    def validate_csrf_token(self):
        csrf.validate()


class SecureForm(BaseForm):
    """
        BaseForm with CSRF token generation and validation support.

        Requires WTForms 2+
    """
    class Meta:
        csrf = True
        csrf_class = SessionCSRF
        _csrf_secret = urandom(24)

        @property
        def csrf_secret(self):
            secret = current_app.secret_key or self._csrf_secret
            if isinstance(secret, text_type):
                secret = secret.encode('utf-8')
            return secret

        @property
        def csrf_context(self):
            return session


