from typing import Dict, Iterable, List, Optional

from allocation import models, signals
from django.dispatch import receiver

from core.logic import logic


class InvalidSku(Exception):
    pass


def is_allocated(batch: models.Batch, line: models.OrderLine) -> bool:
    return models.Allocation.objects.filter(batch=batch, line=line).exists()


def save_allocation(batch: models.Batch, line: models.OrderLine) -> None:
    models.Allocation.objects.create(batch=batch, line=line)


def save_batch(batch: models.Batch) -> None:
    batch.save()


def get_batch(reference: str) -> Optional[models.Batch]:
    return models.Batch.objects.filter(reference=reference).first()


def is_valid_sku(sku: str, batches: Iterable[models.Batch]) -> bool:
    return sku in {b.sku for b in batches}


@receiver(signals.create_batch)
def add_batch(sender, **kwargs):
    ref = kwargs["ref"]
    sku = kwargs["sku"]
    qty = kwargs["qty"]
    eta = kwargs.get("eta", None)
    batch = models.Batch.objects.create(reference=ref, sku=sku, quantity=qty, eta=eta)
    return batch.reference


@receiver(signals.allocate)
def allocate(
    sender,
    **kwargs,
):
    order_id = kwargs["order_id"]
    sku = kwargs["sku"]
    qty = kwargs["qty"]
    line = models.OrderLine.objects.create(order_id=order_id, sku=sku, quantity=qty)
    batches = models.Batch.objects.all()
    if not is_valid_sku(sku, batches):
        raise InvalidSku(f"Invalid sku {sku}")
    logic.allocate_from_batches(sku, line, list(batches))
    return batches[0].quantity


@receiver(signals.deallocated)
def reallocate(sender, **kwargs):
    order_id = kwargs["order_id"]
    sku = kwargs["sku"]
    quantity = kwargs["quantity"]
    signals.allocate.send(reallocate, order_id=order_id, sku=sku, qty=quantity)


def deallocate_one(batch: models.Batch) -> models.OrderLine | None:
    allocation = batch.allocations.last()
    if isinstance(allocation, models.Allocation):
        line = allocation.line
        allocation.delete()
        return line


@receiver(signals.change_batch_quantity)
def change_batch_quantity(sender, **kwargs):
    reference = kwargs["reference"]
    quantity = kwargs["quantity"]
    batch = models.Batch.objects.get(reference=reference)
    return logic.change_batch_quantity(batch, quantity)


def get_allocations(order_id: str) -> List[Dict]:
    """
    Return the optimized view for read-only data of allocations

    :param order_id: Description
    :type order_id: str
    """
    return [
        dict(batchref=ref, sku=sku)
        for ref, sku in models.Allocation.objects.filter(
            line__order_id=order_id
        ).values_list("batch__reference", "line__sku")
    ]
