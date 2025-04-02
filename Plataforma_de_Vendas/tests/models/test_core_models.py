import pytest
from django.db.utils import IntegrityError
from Products.models import Product


@pytest.mark.django_db
class TestUniqueIDModel:
    """Tests the UniqueIDModel.save method"""

    def test_new_save(self):
        """Tests a normal save"""
        product = Product(product_name="Product 1")
        product.save()
        assert product.id is not None
        assert product.id != ""

    def test_no_id(self):
        """Tests that an ID is generated if not provided"""
        product = Product(product_name="Product 1", id=None)
        product.save()
        assert product.id is not None
        assert product.id != ""

    def test_duplicate_id_is_regenerated(self, store_fixture, mocker):
        """Tests that a duplicate ID is regenerated"""
        store = store_fixture
        product_1 = Product.objects.create(product_name="Product 1", store=store)

        # Try creating a second product with the same ID
        product_2 = Product(product_name="Product 2", store=store)
        product_2.id = product_1.id

        mocker.patch("core.models.generate_unique_id", return_value="NEW_UNIQUE_ID")

        product_2.save()  # This should regenerate the ID

        assert product_2.id == "NEW_UNIQUE_ID"  # ID should be different

    def test_save_max_attempts_reached(self, mocker, store_fixture):
        """Tests that an IntegrityError is raised if max attempts are reached"""
        store = store_fixture
        product_1 = Product(product_name="Product 1", store=store)
        product_1.id = "TEST_ID"
        product_1.save()

        product_2 = Product(product_name="Product 2", store=store)
        product_2.id = "TEST_ID"

        mocker.patch("core.models.generate_unique_id", return_value="TEST_ID")

        with pytest.raises(IntegrityError) as error_message:
            product_2.save()

        assert str(error_message.value) == "Could not generate a unique id after 5 attempts"
