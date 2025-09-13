from datetime import date
from unittest.mock import MagicMock

import pytest
from allocation import models, signals

from core.logic import logic
from core.service import service


class TestAddBatch:
    def test_for_new_product(self):
        (_, ref) = signals.create_batch.send(
            sender=None, ref="b1", sku="CRUNCHY-ARMCHAIR", qty=100, eta=None
        )[0]
        assert ref == "b1"

    def test_for_existing_product(self):
        (_, ref1) = signals.create_batch.send(
            sender=None, ref="b1", sku="GARISH-RUG", qty=100, eta=None
        )[0]
        (_, ref2) = signals.create_batch.send(
            sender=None, ref="b2", sku="GARISH-RUG", qty=99, eta=None
        )[0]
        assert ref1 == "b1"
        assert ref2 == "b2"


class TestAllocate:
    def test_allocates(self):
        signals.create_batch.send(
            sender=None, ref="batch1", sku="COMPLICATED-LAMP", qty=100, eta=None
        )
        [_, quantity] = signals.allocate.send(
            sender=None, order_id="o1", sku="COMPLICATED-LAMP", qty=10
        )[0]
        assert quantity == 90

    def test_errors_for_invalid_sku(self):
        signals.create_batch.send(
            sender=None, ref="b1", sku="AREALSKU", qty=100, eta=None
        )
        with pytest.raises(service.InvalidSku, match="Invalid sku NONEXISTENTSKU"):
            signals.allocate.send(
                sender=None, order_id="o1", sku="NONEXISTENTSKU", qty=10
            )

    def test_commits(self):
        signals.create_batch.send(
            sender=None, ref="b1", sku="OMINOUS-MIRROR", qty=100, eta=None
        )
        signals.allocate.send(sender=None, order_id="o1", sku="OMINOUS-MIRROR", qty=10)
        assert True  # Django autocommits

    def test_sends_email_on_out_of_stock_error(self):
        handler = MagicMock()
        signals.out_of_stock.connect(handler)
        signals.create_batch.send(
            sender=None, ref="b1", sku="POPULAR-CURTAINS", qty=10, eta=None
        )
        signals.allocate.send(
            sender=None, order_id="o1", sku="POPULAR-CURTAINS", qty=10
        )
        handler.assert_called_once_with(
            sender=logic.allocate_from_batches,
            sku="POPULAR-CURTAINS",
            signal=signals.out_of_stock,
        )


class TestChangeBatchQuantity:
    def test_changes_available_quantity(self):
        [_, batch] = signals.create_batch.send(
            sender=None, ref="batch1", sku="ADORABLE-SETTEE", qty=100, eta=None
        )[0]
        signals.change_batch_quantity.send(sender=None, reference="batch1", quantity=50)
        assert (
            logic.get_available_quantity(models.Batch.objects.get(reference="batch1"))
            == 50
        )

    def test_reallocates_if_necessary(self):
        signals.create_batch.send(
            sender=None, ref="batch1", sku="INDIFFERENT-TABLE", qty=50, eta=None
        )
        signals.create_batch.send(
            sender=None, ref="batch2", sku="INDIFFERENT-TABLE", qty=50, eta=date.today()
        )
        signals.allocate.send(
            sender=None, order_id="order1", sku="INDIFFERENT-TABLE", qty=20
        )
        signals.allocate.send(
            sender=None, order_id="order2", sku="INDIFFERENT-TABLE", qty=20
        )
        [batch1, batch2] = models.Batch.objects.filter(
            sku="INDIFFERENT-TABLE"
        ).order_by("reference")
        batch1.refresh_from_db()
        assert batch1.quantity == 10
        assert batch2.quantity == 50

        signals.change_batch_quantity.send(sender=None, reference="batch1", quantity=25)
        batch1.refresh_from_db()
        batch2.refresh_from_db()

        # order1 or order2 will be deallocated, so we'll have 25 - 20
        assert logic.get_available_quantity(batch1) == 5
        # and 20 will be reallocated to the next batch
        assert logic.get_available_quantity(batch2) == 30
