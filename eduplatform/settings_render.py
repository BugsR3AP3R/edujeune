# ─────────────────────────────────────────────────────────────
#  settings_render.py  —  paramètres de production pour Render
# ─────────────────────────────────────────────────────────────
from .settings import *          # on part des settings normaux
import os
import dj_database_url

# ── Sécurité ──────────────────────────────────────────────────
SECRET_KEY  = os.environ.get('SECRET_KEY', SECRET_KEY)
DEBUG       = False
ALLOWED_HOSTS = ['*']            # Render gère le domaine, on laisse * ici

# ── Base de données PostgreSQL (fournie par Render) ───────────
DATABASE_URL = os.environ.get('DATABASE_URL', '')
if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            ssl_require=True,
        )
    }

# ── Redis pour les WebSockets ─────────────────────────────────
REDIS_URL = os.environ.get('REDIS_URL', '')
if REDIS_URL:
    CHANNEL_LAYERS = {
        'default': {
            'BACKEND': 'channels_redis.core.RedisChannelLayer',
            'CONFIG':  {'hosts': [REDIS_URL]},
        }
    }
# Si pas de Redis (plan gratuit), on garde InMemoryChannelLayer
# Le chat fonctionne mais se remet à zéro si le serveur redémarre

# ── Fichiers statiques avec WhiteNoise ────────────────────────
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

# ── Médias ────────────────────────────────────────────────────
MEDIA_URL  = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ── Logs ──────────────────────────────────────────────────────
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {'console': {'class': 'logging.StreamHandler'}},
    'root': {'handlers': ['console'], 'level': 'INFO'},
}
