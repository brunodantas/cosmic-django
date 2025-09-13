from django.db import models


class Batch(models.Model):
    reference = models.CharField(max_length=255, unique=True)
    sku = models.CharField(max_length=255)
    quantity = models.IntegerField()
    eta = models.DateField(null=True, blank=True)
    purchased_quantity = models.IntegerField()

    allocations: models.Manager["Allocation"]

    def __repr__(self):
        return f"Batch {self.reference}"

    def __eq__(self, other):
        return isinstance(other, Batch) and self.reference == other.reference

    def __lt__(self, other):
        if self.eta is None:
            return True
        if other.eta is None:
            return False
        return self.eta < other.eta

    def __hash__(self) -> int:
        return hash(self.reference)

    def save(self, *args, **kwargs):
        """Set purchased_quantity if not set and save the batch."""
        if not self.purchased_quantity:
            self.purchased_quantity = self.quantity
        super().save(*args, **kwargs)


class OrderLine(models.Model):
    order_id = models.CharField(max_length=255)
    sku = models.CharField(max_length=255)
    quantity = models.IntegerField()


class Allocation(models.Model):
    batch = models.ForeignKey(
        Batch, on_delete=models.CASCADE, related_name="allocations"
    )
    line = models.ForeignKey(
        OrderLine, on_delete=models.CASCADE, related_name="allocations"
    )
