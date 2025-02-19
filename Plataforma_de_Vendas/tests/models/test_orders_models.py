import pytest


@pytest.mark.django_db
class TestOrderModels:
    def test_order_str(self, store_fixture, order_fixture):
        assert (
            str(order_fixture)
            == f"{str(order_fixture.user)} - {order_fixture.created_at} - {order_fixture.total}"
        )
