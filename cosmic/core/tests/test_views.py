from datetime import date

from allocation import signals, views

today = date.today()


def test_allocations_view():
    signals.create_batch.send(
        sender=None, ref="sku1batch", sku="sku1", qty=50, eta=None
    )
    signals.create_batch.send(
        sender=None, ref="sku2batch", sku="sku2", qty=50, eta=today
    )
    signals.allocate.send(sender=None, order_id="order1", sku="sku1", qty=20)
    signals.allocate.send(sender=None, order_id="order1", sku="sku2", qty=20)
    # add a spurious batch and order to make sure we're getting the right ones
    signals.create_batch.send(
        sender=None, ref="sku1batch-later", sku="sku1", qty=50, eta=today
    )
    signals.allocate.send(sender=None, order_id="otherorder", sku="sku1", qty=30)
    signals.allocate.send(sender=None, order_id="otherorder", sku="sku2", qty=10)

    assert views.allocations("order1") == [
        {"sku": "sku1", "batchref": "sku1batch"},
        {"sku": "sku2", "batchref": "sku2batch"},
    ]


def test_deallocation():
    signals.create_batch.send(None, ref="b1", sku="sku1", qty=50, eta=None)
    signals.create_batch.send(None, ref="b2", sku="sku1", qty=50, eta=today)
    signals.allocate.send(None, order_id="o1", sku="sku1", qty=40)
    signals.change_batch_quantity.send(None, reference="b1", quantity=10)

    assert views.allocations("o1") == [
        {"sku": "sku1", "batchref": "b2"},
    ]
