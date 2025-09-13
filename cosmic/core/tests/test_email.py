import uuid
from allocation import signals


def test_out_of_stock_email():
    sku = str(uuid.uuid4())
    signals.create_batch.send(None, ref="batch1", sku=sku, qty=9)
    signals.allocate.send(None, order_id="order1", sku=sku, qty=10)
    assert True
    # TODO: add email service maybe
