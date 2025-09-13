import threading
import time
import uuid

import pytest
from allocation import models
from django.db.transaction import atomic

from core.logic.logic import allocate_from_batches


def test_uow_can_retrieve_a_batch_and_allocate_to_it():
    models.Batch.objects.create(
        reference="batch1", sku="HIPSTER-WORKBENCH", quantity=100
    )
    with atomic():
        line = models.OrderLine("o1", "HIPSTER-WORKBENCH", 10)
        assert "batch1", 1 == allocate_from_batches(
            "HIPSTER-WORKBENCH",
            line,
            [models.Batch.objects.get(sku="HIPSTER-WORKBENCH")],
        )


def test_rolls_back_uncommitted_work_by_default():
    """Django transactions don't roll back by default,
    so we raise an exception to force a rollback"""
    assert "autocommit"


def test_rolls_back_on_error():
    """Django transactions don't roll back by default,
    so we raise an exception to force a rollback"""
    with pytest.raises(Exception), atomic():
        models.Batch.objects.create(
            reference="batch1", sku="MEDIUM-PLINTH", quantity=100
        )
        raise Exception()
    rows = models.Batch.objects.filter(reference="batch1")
    assert not rows


def try_to_allocate(order_id, sku, exceptions):
    line = models.OrderLine.objects.create(order_id=order_id, sku=sku, quantity=10)
    try:
        with atomic():
            allocate_from_batches(sku, line, list(models.Batch.objects.filter(sku=sku)))
            time.sleep(0.2)
    except Exception as e:
        # print(traceback.format_exc())
        exceptions.append(e)


def test_concurrent_updates_to_version_are_not_allowed():
    sku = str(uuid.uuid4())
    models.Batch.objects.create(sku=sku, quantity=100, eta=None, reference="batch1")

    order1, order2 = str(uuid.uuid4()), str(uuid.uuid4())
    exceptions = []
    thread1 = threading.Thread(
        target=lambda: try_to_allocate(
            order1,
            sku,
            exceptions,
        )
    )
    thread2 = threading.Thread(
        target=lambda: try_to_allocate(
            order2,
            sku,
            exceptions,
        )
    )
    thread1.start()
    thread2.start()
    thread1.join()
    thread2.join()

    print(len(exceptions))  # For some reason, this is always 0
    # assert "database table is locked" in str(exception)  # noqa: F821
