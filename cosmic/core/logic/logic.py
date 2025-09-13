"""File for business logic functions
as a middle ground between
the Active Record and Domain Model patterns."""

from allocation import signals
from allocation.models import Batch, OrderLine
from allocation.signals import allocated, out_of_stock
from ensures import precondition

from core.service import service


def get_allocated_quantity(batch: Batch) -> int:
    return sum(allocation.line.quantity for allocation in batch.allocations.all())


def get_available_quantity(batch: Batch) -> int:
    return batch.purchased_quantity - get_allocated_quantity(batch)


def can_allocate(batch: Batch, line: OrderLine):
    return (
        batch.sku == line.sku and batch.quantity >= line.quantity
        if not service.is_allocated(batch, line)
        else False
    )


@precondition(can_allocate)
def allocate(batch: Batch, line: OrderLine):
    batch.quantity -= line.quantity
    service.save_allocation(batch, line)
    service.save_batch(batch)
    return batch


def allocate_from_batches(
    sku: str, line: OrderLine, batches: list[Batch], version_number: int = 0
) -> tuple[str | None, int]:
    try:
        batch = next(b for b in sorted(batches) if can_allocate(b, line))
        allocate(batch, line)
        version_number += 1
        allocated.send(
            sender=allocate_from_batches,
            order_id=line.order_id,
            sku=sku,
            quantity=line.quantity,
            batch_reference=batch.reference,
        )
        if batch.quantity == 0:
            out_of_stock.send(sender=allocate_from_batches, sku=line.sku)
        return batch.reference, version_number
    except StopIteration:
        out_of_stock.send(sender=allocate_from_batches, sku=line.sku)
        return None, version_number


def change_batch_quantity(batch: Batch, new_quantity: int):
    batch.purchased_quantity = new_quantity
    service.save_batch(batch)
    while get_available_quantity(batch) < 0:
        line = service.deallocate_one(batch)
        if isinstance(line, OrderLine):
            signals.deallocated.send(
                sender=change_batch_quantity,
                order_id=line.order_id,
                sku=line.sku,
                quantity=line.quantity,
            )
