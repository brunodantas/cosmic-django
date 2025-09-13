from datetime import date, timedelta
from unittest.mock import MagicMock

from allocation import signals
from allocation.models import Batch, OrderLine

from core.logic.logic import allocate_from_batches

today = date.today()
tomorrow = today + timedelta(days=1)
later = tomorrow + timedelta(days=10)


def test_prefers_warehouse_batches_to_shipments():
    in_stock_batch = Batch.objects.create(
        reference="in-stock-batch", sku="RETRO-CLOCK", quantity=100, eta=None
    )
    shipment_batch = Batch.objects.create(
        reference="shipment-batch", sku="RETRO-CLOCK", quantity=100, eta=tomorrow
    )
    batches = [in_stock_batch, shipment_batch]
    line = OrderLine.objects.create(order_id="oref", sku="RETRO-CLOCK", quantity=10)

    allocate_from_batches("RETRO-CLOCK", line, batches)

    assert in_stock_batch.quantity == 90
    assert shipment_batch.quantity == 100


def test_prefers_earlier_batches():
    earliest = Batch.objects.create(
        reference="speedy-batch", sku="MINIMALIST-SPOON", quantity=100, eta=today
    )
    medium = Batch.objects.create(
        reference="normal-batch", sku="MINIMALIST-SPOON", quantity=100, eta=tomorrow
    )
    latest = Batch.objects.create(
        reference="slow-batch", sku="MINIMALIST-SPOON", quantity=100, eta=later
    )
    line = OrderLine.objects.create(
        order_id="order1", sku="MINIMALIST-SPOON", quantity=10
    )

    allocate_from_batches("MINIMALIST-SPOON", line, [medium, earliest, latest])

    assert earliest.quantity == 90
    assert medium.quantity == 100
    assert latest.quantity == 100


def test_returns_allocated_batch_ref():
    in_stock_batch = Batch.objects.create(
        reference="in-stock-batch-ref", sku="HIGHBROW-POSTER", quantity=100, eta=None
    )
    shipment_batch = Batch.objects.create(
        reference="shipment-batch-ref",
        sku="HIGHBROW-POSTER",
        quantity=100,
        eta=tomorrow,
    )
    line = OrderLine.objects.create(order_id="oref", sku="HIGHBROW-POSTER", quantity=10)
    allocation = allocate_from_batches(
        "HIGHBROW-POSTER", line, [in_stock_batch, shipment_batch]
    )
    assert allocation == (in_stock_batch.reference, 1)


def test_outputs_allocated_event():
    handler = MagicMock()
    signals.allocated.connect(handler)
    batch = Batch.objects.create(
        reference="batchref", sku="RETRO-LAMPSHADE", quantity=100, eta=None
    )
    line = OrderLine.objects.create(order_id="oref", sku="RETRO-LAMPSHADE", quantity=10)
    allocate_from_batches("RETRO-LAMPSHADE", line, [batch])
    handler.assert_called_once_with(
        sender=allocate_from_batches,
        order_id="oref",
        sku="RETRO-LAMPSHADE",
        quantity=10,
        batch_reference="batchref",
        signal=signals.allocated,
    )


def test_records_out_of_stock_event_if_cannot_allocate():
    handler = MagicMock()
    signals.out_of_stock.connect(handler)
    batch = Batch.objects.create(
        reference="batch1", sku="SMALL-FORK", quantity=10, eta=today
    )
    allocate_from_batches(
        "SMALL-FORK",
        OrderLine.objects.create(order_id="order1", sku="SMALL-FORK", quantity=10),
        [batch],
    )
    allocate_from_batches(
        "SMALL-FORK",
        OrderLine.objects.create(order_id="order2", sku="SMALL-FORK", quantity=1),
        [batch],
    )
    handler.assert_called_with(
        sender=allocate_from_batches, sku="SMALL-FORK", signal=signals.out_of_stock
    )


def test_increments_version_number():
    line = OrderLine.objects.create(order_id="oref", sku="SCANDI-PEN", quantity=10)
    assert ("b1", 8) == allocate_from_batches(
        "SCANDI-PEN",
        line,
        [
            Batch.objects.create(
                reference="b1", sku="SCANDI-PEN", quantity=100, eta=None
            )
        ],
        version_number=7,
    )
