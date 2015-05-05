from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from oauth2_provider.models import Application


class Command(BaseCommand):
    """ Programmatically create the default ashlar ouath2 application

    TODO: Arguments for client_type/grant_type/redirect_uris
    TODO: Create superuser in all cases by passing username/password/email if it doesn't exist

    """
    help = 'Adds the Ashlar ouath2 application programmatically'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Superuser username that manages the app')

    def handle(self, *args, **options):
        username = options['username']
        app_name = 'Ashlar'

        apps = Application.objects.filter(name=app_name)
        if len(apps) > 0:
            self.stdout.write('Application {} already exists.'.format(app_name))
            return

        superuser = self.get_or_create_superuser(options)
        Application.objects.create(
            user=superuser,
            name='Ashlar',
            client_type=Application.CLIENT_CONFIDENTIAL,
            authorization_grant_type=Application.GRANT_PASSWORD
        )

        self.stdout.write('Added application {} for user {}'.format(app_name, username))

    def get_or_create_superuser(self, options):
        """ Get user object for passed username

        Create one if we're in develop mode and one doesn't exist

        """
        username = options['username']
        try:
            return User.objects.get(username=username)
        except User.DoesNotExist as e:
            if settings.DEVELOP:
                # Create one automatically, so we can continue
                user = User.objects.create_user(username, 'admin@ashlar', username)
                user.is_superuser = True
                user.is_staff = True
                user.save()
                return user
            else:
                raise CommandError('User {} does not exist'.format(username))