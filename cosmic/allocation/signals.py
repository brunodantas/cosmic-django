from django.dispatch import Signal


# Signals
allocated = Signal()
deallocated = Signal()
out_of_stock = Signal()


# Commands
create_batch = Signal()
allocate = Signal()
change_batch_quantity = Signal()
