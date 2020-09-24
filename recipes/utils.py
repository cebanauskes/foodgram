import csv

from django.http import HttpResponse

from .models import Amount, Ingredient

def get_ingredients(request):
    ing_dict = {}
    for key in request.POST:
        if key.startswith('nameIngredient'):
            value = key[15:]
            ing_dict[request.POST[key]] = request.POST['valueIngredient_' + value]
    return ing_dict

def create_amount(ing_dict, recipe):
    for key in ing_dict:
        Amount.objects.create(
            quantity=ing_dict[key],
            ingredient=Ingredient.objects.get(title=key),
            recipe=recipe,
        )

    
class ExportCsvMixin:
    def export_as_csv(self, request, queryset):

        meta = self.model._meta
        field_names = [field.name for field in meta.fields]

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="tags.csv"'
        writer = csv.writer(response)

        writer.writerow(field_names)
        for obj in queryset:
            row = writer.writerow([getattr(obj, field) for field in field_names])

        return response

    export_as_csv.short_description = "Export Selected"