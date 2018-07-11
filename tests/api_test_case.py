import os

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist

from rest_framework.test import APITestCase


class GroutAPITestCase(APITestCase):
    """ Extend api client for grout-specific test code

    Adds some helper fields to the TestCase instance:
     - user: superuser django django.contrib.auth.models.User object
     - files_dir: root directory where test files are stored

    Also automatically authenticates all requests made via self.client with user
    This can be overridden with a different user in the subclass setUp() method by calling
    self.client.force_authenticate() again with a different user object.

    """
    def setUp(self):
        super(GroutAPITestCase, self).setUp()

        try:
            self.user = User.objects.get(username='admin')
        except ObjectDoesNotExist:
            self.user = User.objects.create_user('admin',
                                                 'grout@azavea.com',
                                                 '123')
            self.user.is_superuser = True
            self.user.is_staff = True
            self.user.save()

        # TODO: Set test specific users for authentication that aren't admins?
        self.client.force_authenticate(user=self.user)

        self.files_dir = os.path.join('tests', 'files')

    def tearDown(self):
        super(GroutAPITestCase, self).tearDown()
