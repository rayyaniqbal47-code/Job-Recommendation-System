from django.apps import AppConfig


class TutConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tut'

    def ready(self):
        import tut.signals



