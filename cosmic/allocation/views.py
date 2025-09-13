import datetime

from core.service import service
from django import http

from allocation import signals


def allocations(order_id: str):
    return service.get_allocations(order_id)


def add_batch(request: http.HttpRequest):
    eta = request.POST.get("eta")
    if eta is not None:
        eta = datetime.datetime.fromisoformat(eta).date() if eta else None
    signals.create_batch.send(
        add_batch,
        ref=request.POST["reference"],
        sku=request.POST["sku"],
        qty=int(request.POST["quantity"]),
        eta=eta,
    )
    return http.HttpResponse(status=201)


def allocate(request: http.HttpRequest):
    try:
        signals.allocate.send(
            allocate,
            order_id=request.POST.get("order_id"),
            sku=request.POST.get("sku"),
            qty=int(request.POST.get("qty", 0)),
        )
    except service.InvalidSku as e:
        return http.JsonResponse({"message": str(e)}, status=400)
    return http.HttpResponse(status=202)


def view_allocations(request: http.HttpRequest, order_id: str):
    result = allocations(order_id)
    if not result:
        return http.HttpResponseNotFound()
    return http.JsonResponse(result, safe=False)
