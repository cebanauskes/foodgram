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