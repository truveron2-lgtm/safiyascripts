from django.shortcuts import get_object_or_404
from django.apps import apps
from django.shortcuts import render

def universal_detail(request, model_name, pk):
    model = apps.get_model(app_label=None, model_name=model_name)
    obj = get_object_or_404(model, pk=pk)

    return render(request, "universal_detail.html", {"object": obj})
