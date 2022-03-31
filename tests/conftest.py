import pytest

from django.core import cache as django_cache
from django.contrib.auth.models import User


@pytest.fixture(autouse=True)
def cache():
    django_cache.cache.clear()
    yield django_cache.cache


@pytest.fixture
def assert_redirect():
    def inner(response, expected):
        assert response.status_code == 302
        assert response["Location"] == expected

    return inner


@pytest.fixture
def fake_user(db):
    return User.objects.create_user(
        username="test", password="test", email="test@test.com"
    )


@pytest.fixture
def fake_admin(db):
    return User.objects.create_user(
        username="admin",
        email="admin@admin.com",
        password="test",
        is_superuser=True,
        is_staff=True,
    )


@pytest.fixture
def admin_client(client, fake_admin):
    assert client.login(username="admin", password="test") is True
    return client


@pytest.fixture
def user_client(client, fake_user):
    assert client.login(username="test", password="test") is True
    return client


@pytest.fixture
def henri(db):
    return User.objects.create_user(
        username="henri", password="test", email="henri@henri.com"
    )


@pytest.fixture
def henri_client(client, henri):
    assert client.login(username="henri", password="test") is True
    return client
