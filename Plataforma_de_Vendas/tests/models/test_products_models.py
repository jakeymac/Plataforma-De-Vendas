import pytest
from django.db.utils import IntegrityError
from Products.models import (
    InitialProductImage,
    Product,
    ProductImage,
    ProductInOrder,
    ProductTopSubcategory,
)


@pytest.mark.django_db
class TestProductModel:
    """Tests the Product.save method"""

    def test_normal_save(self, product_fixture):
        """Tests a normal save"""
        product, _ = product_fixture
        product.save()
        assert product.id is not None

    def test_duplicate_product_name(self, product_fixture, store_fixture):
        """Tests that a duplicate product name raises an IntegrityError"""
        product_1, _ = product_fixture
        store = store_fixture

        test_product = Product(product_name=product_1.product_name, store=store)

        with pytest.raises(IntegrityError) as error_message:
            test_product.save()

        assert (
            str(error_message.value) == f"Product name '{product_1.product_name}' already exists."
        )

    def test_str(self, product_fixture):
        """Tests the __str__ method"""
        product, _ = product_fixture
        assert str(product) == f"{product.product_name}"


@pytest.mark.django_db
class TestInitialProductStateModel:
    """Tests the InitialProductState.save method"""

    def test_normal_save(self, product_fixture):
        """Tests a normal save"""
        _, initial_product = product_fixture
        initial_product.save()
        assert initial_product.id is not None

    def test_str(self, product_fixture):
        """Tests the __str__ method"""
        _, initial_product = product_fixture
        assert str(initial_product) == f"Initial State of {initial_product.product.product_name}"


@pytest.mark.django_db
class TestProductImageModel:
    """Tests the ProductImage.save method"""

    def test_normal_save(self, product_fixture, mock_image):
        """Tests a normal save"""
        product_fixture, _ = product_fixture
        product_image = ProductImage(
            product=product_fixture,
            image=mock_image,
        )
        product_image.save()
        assert product_image.id is not None
        assert product_image.s3_key is not None

    def test_str(self, product_fixture, mock_image):
        """Tests the __str__ method"""
        product, _ = product_fixture
        product_image = ProductImage.objects.get(product=product)
        assert str(product_image) == f"Image for {product.product_name} - {product_image.order}"


@pytest.mark.django_db
class TestInitialProductImage:
    """Tests the InitialProductImage model"""

    def test_normal_save(self, product_fixture, mock_image):
        """Tests a normal save"""
        _, initial_product = product_fixture
        initial_product_image = InitialProductImage(
            initial_product=initial_product,
            image=mock_image,
            original_created_at=initial_product.original_created_at,
            order=7,
        )
        initial_product_image.save()
        assert initial_product_image.id is not None

    def test_str(self, product_fixture, mock_image):
        """Tests the __str__ method"""
        _, initial_product = product_fixture

        initial_product_image = InitialProductImage.objects.get(initial_product=initial_product)
        assert (
            str(initial_product_image) == f"Initial Image of {initial_product.product.product_name}"
        )


@pytest.mark.django_db
class TestProductInOrderModel:
    """Tests the ProductInOrder model"""

    def test_normal_save(self, product_fixture, order_fixture):
        """Tests a normal save"""
        product, _ = product_fixture
        order = order_fixture
        product_in_order = ProductInOrder(order=order, product=product, quantity=5, price=25.0)
        product_in_order.save()
        assert product_in_order.id is not None
        assert product_in_order.order == order

    def test_str(self, product_fixture, order_fixture):
        """Tests the __str__ method"""
        product, _ = product_fixture
        order = order_fixture
        product_in_order = ProductInOrder.objects.get(product=product, order=order)
        assert str(product_in_order) == f"{product.product_name} - {product_in_order.quantity}"


@pytest.mark.django_db
class TestProductCategoryModel:
    """Tests the ProductCategory model"""

    def test_normal_save(self, category_fixture):
        """Tests a normal save"""
        product_category = category_fixture
        product_category.save()
        assert product_category.id is not None

    def test_str(self, category_fixture):
        """Tests the __str__ method"""
        product_category = category_fixture
        assert str(product_category) == f"{product_category.category_name}"


@pytest.mark.django_db
class TestProductSubcategoryModel:
    """Tests the ProductSubcategory model"""

    def test_normal_save(self, subcategory_fixture):
        """Tests a normal save"""
        product_subcategory = subcategory_fixture
        product_subcategory.save()
        assert product_subcategory.id is not None

    def test_str(self, subcategory_fixture):
        """Tests the __str__ method"""
        product_subcategory = subcategory_fixture
        assert str(product_subcategory) == f"{product_subcategory.subcategory_name}"


@pytest.mark.django_db
class TestProductTopSubcategoryModel:
    """Tests the ProductTopSubcategory model"""

    def test_normal_save(self, subcategory_fixture):
        """Tests a normal save"""
        product_top_subcategory = ProductTopSubcategory.objects.get(subcategory=subcategory_fixture)
        product_top_subcategory.save()
        assert product_top_subcategory.id is not None

    def test_str(self, subcategory_fixture):
        """Tests the __str__ method"""
        product_top_subcategory = ProductTopSubcategory.objects.get(subcategory=subcategory_fixture)
        assert (
            str(product_top_subcategory)
            == f"{product_top_subcategory.subcategory} - {product_top_subcategory.order}"
        )
