class TestStoreModel:
    """Test class for Store model"""

    def test_str(self, store_fixture):
        """Test the string representation of the Store model"""
        assert str(store_fixture) == f"{store_fixture.store_name}"
