import uuid

from django.test import client


def test_happy_path_returns_202_and_batch_is_allocated():
    order_id = uuid.uuid4()
    sku, othersku = uuid.uuid4(), uuid.uuid4()
    earlybatch = uuid.uuid4()
    laterbatch = uuid.uuid4()
    otherbatch = uuid.uuid4()
    c = client.Client()
    c.post(
        "/batches/add",
        {"reference": laterbatch, "sku": sku, "quantity": 100, "eta": "2011-01-02"},
    ).status_code
    c.post(
        "/batches/add",
        {"reference": earlybatch, "sku": sku, "quantity": 100, "eta": "2011-01-01"},
    )
    c.post(
        "/batches/add",
        {"reference": otherbatch, "sku": othersku, "quantity": 100, "eta": ""},
    )

    r = c.post("/allocations/add", dict(order_id=order_id, sku=sku, qty=3))
    assert r.status_code == 202

    r = c.get(f"/allocations/{order_id}")
    assert r.status_code == 200
    assert r.json() == [
        {"sku": str(sku), "batchref": str(earlybatch)},
    ]


def test_unhappy_path_returns_400_and_error_message():
    unknown_sku, order_id = uuid.uuid4(), uuid.uuid4()
    c = client.Client()
    r = c.post("/allocations/add", dict(order_id=order_id, sku=unknown_sku, qty=20))
    assert r.status_code == 400
    assert r.json()["message"] == f"Invalid sku {unknown_sku}"

    r = c.get(f"/allocations/{order_id}")
    assert r.status_code == 404
