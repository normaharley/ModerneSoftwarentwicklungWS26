import pytest
from django.apps import apps
from django.urls import reverse


def test_polls_app_is_installed():
    assert apps.is_installed("polls")


@pytest.mark.django_db
def test_admin_login_page_loads(client):
    response = client.get(reverse("admin:login"))
    assert response.status_code == 200
