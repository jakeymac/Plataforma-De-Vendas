import pytest
from Products.models import Product, InitialProductState, ProductImage
from django.db.utils import IntegrityError

@pytest.mark.django_db
class TestProductModel:
    """ Tests the Product.save method """
    def test_normal_save(self, product_fixture):
        """ Tests a normal save """
        product, _ = product_fixture
        product.save()
        assert product.id is not None

    def test_duplicate_product_name(self, product_fixture, store_fixture):
        """ Tests that a duplicate product name raises an IntegrityError """
        product_1, _ = product_fixture
        store = store_fixture

        test_product = Product(product_name=product_1.product_name, store=store)
        
        with pytest.raises(IntegrityError) as error_message:
            test_product.save()

        assert str(error_message.value) == f"Product name '{product_1.product_name}' already exists."

    def test_str(self, product_fixture):
        """ Tests the __str__ method """
        product, _ = product_fixture
        assert str(product) == f"{product.product_name}"

@pytest.mark.django_db
class TestInitialProductStateModel:
    """ Tests the InitialProductState.save method"""
    def test_normal_save(self, product_fixture):
        """ Tests a normal save """
        _, initial_product = product_fixture
        initial_product.save()
        assert initial_product.id is not None
    
    def test_str(self, product_fixture):
        """ Tests the __str__ method """
        _, initial_product = product_fixture
        assert str(initial_product) == f"Initial State of {initial_product.product.product_name}"

@pytest.mark.django_db
class TestProductImageModel:
    """ Tests the ProductImage.save method """
    def test_normal_save(self, product_fixture, mock_image):
        """ Tests a normal save """
        product_fixture, _ = product_fixture
        product_image = ProductImage(
            product=product_fixture,
            image=mock_image,
        )
        product_image.save()
        assert product_image.id is not None
        assert product_image.s3_key is not None
    

    
    