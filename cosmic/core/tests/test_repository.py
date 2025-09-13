from allocation.models import Batch


def test_we_use_django_orm_like_normal_people():
    """Test that we're using Django ORM directly like civilized developers"""

    # Create a batch the Django way (not through a repository!)
    Batch.objects.create(reference="BATCH-001", sku="WIDGET", quantity=100)

    # Query it the Django way (not through a repository!)
    found_batch = Batch.objects.get(reference="BATCH-001")

    assert found_batch.reference == "BATCH-001"
    assert found_batch.sku == "WIDGET"
    assert "Why do programmers prefer dark mode? Because light attracts bugs."
