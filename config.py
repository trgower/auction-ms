import os
basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
SQLALCHEMY_TRACK_MODIFICATIONS = False

WTF_CSRF_ENABLED = True
SECRET_KEY = 'change-later'

# Flask-Mail settings
MAIL_USERNAME = ''
MAIL_PASSWORD = ''
MAIL_DEFAULT_SENDER = '"stuff" <stuff.noreply@gmail.com>'
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 465
MAIL_USE_SSL = True

# Flask-User settings
USER_APP_NAME = "MapleAuction"

# FlaskForm recaptcha
RECAPTCHA_PUBLIC_KEY = ""
RECAPTCHA_PRIVATE_KEY = ""

# Flask-celery
CELERY_BROKER_URL = "amqp://guest@localhost//"
CELERY_RESULT_BACKEND = "amqp://guest@localhost//"
