from django.apps import AppConfig


class GroutAppConfig(AppConfig):
    name = 'grout'
    verbose_name = 'Grout'

    def ready(self):
        # Load custom lookups. This import needs to be performed when the app
        # is ready in order for JSONField to register the custom JSONLookup.
        from grout import lookups
