from django.contrib.auth.models import Group, User
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from test_project.testapp.models import UserAccount


class UserAccountTestCase(APITestCase):
    def setUp(self):
        UserAccount.objects.all().delete()
        User.objects.all().delete()
        Group.objects.all().delete()

    def test_create_allowed(self):
        admin_group = Group.objects.create(name="admin")
        admin_user = User.objects.create()
        admin_user.groups.add(admin_group)
        self.client.force_authenticate(user=admin_user)

        url = reverse("account-list")

        response = self.client.post(
            url,
            {"username": "fred", "first_name": "Fred", "last_name": "Rogers"},
            format="json",
        )

        self.assertEqual(response.status_code, 201)

    def test_retrieve_denied(self):
        account = UserAccount.objects.create(
            username="fred", first_name="Fred", last_name="Rogers"
        )
        banned_group = Group.objects.create(name="banned")
        banned_user = User.objects.create()
        banned_user.groups.add(banned_group)
        self.client.force_authenticate(user=banned_user)

        url = reverse("account-detail", args=[account.id])

        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, 403)

    def test_set_password_should_be_allowed(self):
        account = UserAccount.objects.create(
            username="fred", first_name="Fred", last_name="Rogers"
        )
        regular_users_group = Group.objects.create(name="regular_users")
        user = User.objects.create()
        user.groups.add(regular_users_group)
        self.client.force_authenticate(user=user)

        url = reverse("account-set-password", args=[account.id])

        response = self.client.post(url, format="json")
        self.assertEqual(response.status_code, 200)

    def test_set_password_should_be_denied(self):
        account = UserAccount.objects.create(
            username="fred", first_name="Fred", last_name="Rogers"
        )
        user = User.objects.create()
        self.client.force_authenticate(user=user)

        url = reverse("account-set-password", args=[account.id])
        response = self.client.post(url, format="json")
        self.assertEqual(response.status_code, 403)
