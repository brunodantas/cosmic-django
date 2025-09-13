from datetime import date

from allocation.models import Batch, OrderLine
from ensures import Success

from core.logic.logic import allocate, can_allocate


def test_allocating_to_a_batch_reduces_the_available_quantity():
    batch = Batch.objects.create(
        reference="batch-001", sku="SMALL-TABLE", quantity=20, eta=date.today()
    )
    line = OrderLine.objects.create(order_id="order-ref", sku="SMALL-TABLE", quantity=2)
    result = allocate(batch, line)

    assert isinstance(result, Success)
    assert result.value.quantity == 18


def make_batch_and_line(sku, batch_qty, line_qty):
    return (
        Batch.objects.create(
            reference="batch-001", sku=sku, quantity=batch_qty, eta=date.today()
        ),
        OrderLine.objects.create(order_id="order-123", sku=sku, quantity=line_qty),
    )


def test_can_allocate_if_available_greater_than_required():
    large_batch, small_line = make_batch_and_line("ELEGANT-LAMP", 20, 2)
    assert can_allocate(large_batch, small_line)


def test_cannot_allocate_if_available_smaller_than_required():
    small_batch, large_line = make_batch_and_line("ELEGANT-LAMP", 2, 20)
    assert not can_allocate(small_batch, large_line)


def test_can_allocate_if_available_equal_to_required():
    batch, line = make_batch_and_line("ELEGANT-LAMP", 2, 2)
    assert can_allocate(batch, line)


def test_cannot_allocate_if_skus_do_not_match():
    batch = Batch.objects.create(
        reference="batch-001", sku="UNCOMFORTABLE-CHAIR", quantity=100, eta=None
    )
    different_sku_line = OrderLine.objects.create(
        order_id="order-123", sku="EXPENSIVE-TOASTER", quantity=10
    )
    assert not can_allocate(batch, different_sku_line)


def test_allocation_is_idempotent():
    batch, line = make_batch_and_line("ANGULAR-DESK", 20, 2)
    allocate(batch, line)
    allocate(batch, line)
    assert batch.quantity == 18
