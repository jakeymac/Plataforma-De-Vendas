import pytest
from Products.models import Product, InitialProductState
from django.db.utils import IntegrityError

@pytest.mark.django_db
class TestProductSave:
    """ Tests the Product.save method """
    def test_normal_save(self, product_fixture):
        """ Tests a normal save """
        product, _ = product_fixture
        product.save()
        assert product.id is not None

    def test_duplicate_id_is_regenerated(self, store_fixture, mocker):
        """ Tests that a duplicate ID is regenerated """
        store = store_fixture
        product_1 = Product.objects.create(product_name="Product 1", store=store)
        
        # Try creating a second product with the same ID
        product_2 = Product(product_name="Product 2", store=store)
        product_2.id = product_1.id

        mocker.patch(
            "core.models.generate_unique_id", return_value="NEW_UNIQUE_ID"
        )

        product_2.save()  # This should regenerate the ID

        assert product_2.id == "NEW_UNIQUE_ID"  # ID should be different

    def test_duplicate_product_name(self, product_fixture, store_fixture):
        """ Tests that a duplicate product name raises an IntegrityError """
        product_1, _ = product_fixture
        store = store_fixture

        test_product = Product(product_name=product_1.product_name, store=store)
        
        with pytest.raises(IntegrityError) as error_message:
            test_product.save()
        

        assert str(error_message.value) == f"Product name '{product_1.product_name}' already exists."

    def test_save_max_attempts_reached(self, mocker, store_fixture):
        """ Tests that an IntegrityError is raised if max attempts are reached """
        store = store_fixture

        product_1 = Product(product_name="Product 1", store=store_fixture)
        product_1.id = "TEST_ID"
        product_1.save()

        product_2 = Product(product_name="Product 2", store=store_fixture)
        product_2.id = "TEST_ID"

        mocker.patch(
            "core.models.generate_unique_id", return_value="TEST_ID"
        )

        with pytest.raises(IntegrityError) as error_message:
            product_2.save()

        assert str(error_message.value) == "Could not generate a unique id after 5 attempts"

    def test_str(self, product_fixture):
        """ Tests the __str__ method """
        product, _ = product_fixture
        assert str(product) == f"{product.product_name}"

@pytest.mark.django_db
class TestInitialProductStateSave:
    """ Tests the InitialProductState.save method"""
    def test_normal_save(self, product_fixture):
        """ Tests a normal save """
        _, initial_product = product_fixture
        initial_product.save()
        assert initial_product.id is not None

    def test_duplicate_id_is_regenerated(self, product_fixture, mocker):
        """ Tests that a duplicate ID is regenerated """
        _, initial_product_1 = product_fixture
        initial_product_2 = InitialProductState(product=initial_product_1.product, original_created_at=initial_product_1.created_at)
        initial_product_2.id = initial_product_1.id

        mocker.patch(
            "core.models.generate_unique_id", return_value="NEW_UNIQUE_ID"
        )

        initial_product_2.save()
        assert initial_product_2.id == "NEW_UNIQUE_ID"

    def test_save_max_attempts_reached(self, mocker, product_fixture):
        """ Tests that an IntegrityError is raised if max attempts are reached """
        _, initial_product_1 = product_fixture
        initial_product_1.id = "TEST_ID"
        initial_product_1.save()

        initial_product_2 = InitialProductState(product=initial_product_1.product, original_created_at=initial_product_1.created_at)
        initial_product_2.id = "TEST_ID"

        mocker.patch(
            "core.models.generate_unique_id", return_value="TEST_ID"
        )

        with pytest.raises(IntegrityError) as error_message:
            initial_product_2.save()

        assert str(error_message.value) == "Could not generate a unique id after 5 attempts"
    
    def test_str(self, product_fixture):
        """ Tests the __str__ method """
        _, initial_product = product_fixture
        assert str(initial_product) == f"Initial State of {initial_product.product.product_name}"

        