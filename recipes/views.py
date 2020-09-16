from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
import json

from .forms import RecipeForm
from .models import Amount, Cart, Follow, Favorite, Ingredient, Recipe, User, Follow 


def index(request):
    if 'filters' in request.GET:
        filters = request.GET.getlist('filters')
        recipe_list = Recipe.objects.filter(tags__value__in=filters).distinct()
    else:
        recipe_list = Recipe.objects.order_by('-pub_date').all()
    frecipe_titles = []

    if request.user.is_authenticated:
        favor = Favorite.objects.filter(user=request.user).all()

        for item in favor:
            frecipe_titles.append(item.recipe.title)

    paginator = Paginator(recipe_list, 6)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'index.html', {'recipe_list': recipe_list,  'page': page,
                                            'paginator': paginator, 'frecipe_titles': frecipe_titles, })

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

@login_required
def new_recipe(request):
    ing_dict = get_ingredients(request)
    header = 'Создание рецепта'
    button = 'Создать рецепт'
    if request.method == 'POST':
        print(request.POST)
        form = RecipeForm(request.POST or None, files=request.FILES or None)

        if form.is_valid():
            recipe = form.save(commit=False)
            recipe.author = request.user
            recipe.save()
            create_amount(ing_dict, recipe)
            form.save_m2m()
            return redirect('recipes:index')

    form = RecipeForm()
    return render(request, 'RecipeNew.html', {'form': form, 'header':header, 'button': button})

def recipe_edit(request, username, recipe_id):
    profile = get_object_or_404(User, username=username)
    recipe = get_object_or_404(Recipe, pk=recipe_id, author=profile)
    ing_dict = get_ingredients(request)
    header = 'Редактирование рецепта'
    button = 'Сохранить'
    if request.user != profile:
        return redirect('recipes:single_recipe', username=username, recipe_id=recipe_id)

    if request.method == 'POST':
        form = RecipeForm(request.POST or None, files=request.FILES or None, instance=recipe)

        if form.is_valid():
            recipe=form.save(commit=False)
            recipe.author = request.user
            recipe.save()
            create_amount(ing_dict, recipe)
            form.save_m2m()
            return redirect('recipes:single_recipe', username=username, recipe_id=recipe_id)

    form = RecipeForm(instance=recipe)
    for tag in recipe.tags.all():
        form.instance.tags.add(tag)
    return render(request, 'RecipeNew.html', {'form': form, 'header':header, 'button': button, 'recipe': recipe})


@login_required
def recipe_delete(request, username, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    if request.user == recipe.author:
        recipe.delete()
    return redirect('recipes:index')



def single_recipe(request, username, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    profile = get_object_or_404(User, username=username)
    is_follow = None
    frecipe_titles = []

    if request.user.is_authenticated:
        favor = Favorite.objects.filter(user=request.user).all()
        is_follow = Follow.objects.filter(user=request.user, author=profile)

        for item in favor:
            frecipe_titles.append(item.recipe.title)

    return render(request, 'singleRecipe.html', {'recipe': recipe, 'profile': profile, 
                                                'is_follow': is_follow, 'frecipe_titles': frecipe_titles })


def profile(request, username):

    profile = get_object_or_404(User, username=username)
    is_follow = None
    frecipe_titles = []

    if request.user.is_authenticated:
        favor = Favorite.objects.filter(user=request.user).all()
        
        for item in favor:
            frecipe_titles.append(item.recipe.title)

        is_follow = Follow.objects.filter(user=request.user, author=profile)

    if 'filters' in request.GET:
        filters = request.GET.getlist('filters')
        recipe_list = Recipe.objects.filter(tags__value__in=filters, author=profile).order_by('-pub_date').distinct()
    else:
        recipe_list = Recipe.objects.filter(author=profile).order_by('-pub_date').all()
        
    paginator = Paginator(recipe_list, 6)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'profile.html', {'page': page, 'paginator': paginator, 'frecipe_titles': frecipe_titles,
                                             'profile': profile, 'is_follow': is_follow, })

@login_required
def my_follow(request):
    sub_list = Follow.objects.filter(user=request.user)
    recipe_list = []

    for fitem in sub_list:
        i = 0

        for item in fitem.author.recipe.all():
            recipe_list.append(item)
            i += 1

            if i == 3:
                break

    paginator = Paginator(sub_list, 6)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    return render(request, 'myFollow.html', {'page': page, 'recipe_list': recipe_list})

@login_required
def favorites_view(request):
    favorite_list = Favorite.objects.filter(user=request.user)
    recipe_list = []
    frecipe_titles = []
    
    if 'filters' in request.GET:
        filters = request.GET.getlist('filters')

    for item in favorite_list:
        if 'filters' in request.GET:
            for tag in item.recipe.tags.all():
                if tag.value in filters:
                    recipe_list.append(item.recipe)
        else:
            recipe_list.append(item.recipe)
        frecipe_titles.append(item.recipe.title)

    paginator = Paginator(recipe_list, 6)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    return render(request, 'myFavorites.html', {'page': page, 'paginator': paginator, 
                                                'frecipe_titles': frecipe_titles})

@login_required
def cart_view(request):
    cart = Cart.objects.filter(user=request.user).all()
    return render(request, 'shopList.html', {'cart': cart})

def download(request):
    cart = Cart.objects.filter(user=request.user).all()
    ingredients_dict = {}

    for item in cart:

        for amount in item.recipe.amount.all():

            title = f'{amount.ingredient.title} {amount.ingredient.dimension}'
            quantity = amount.quantity

            if title in ingredients_dict.keys():
                ingredients_dict[title] += quantity
            else:
                ingredients_dict[title] = quantity

    ingredients_list = []

    for key, value in ingredients_dict.items():
        ingredients_list.append(f'{key} - {value}, ')
    
    response = HttpResponse(ingredients_list, content_type='text/txt')
    response['Content-Disposition'] = 'attachment; filename="cart.txt"'
    return response
    
@login_required
def ingredient_hints(request):
    text = request.GET.__getitem__('query')
    ing_list = Ingredient.objects.filter(title__startswith=text).order_by('title')
    result = [{"title": item.title, "dimension": item.dimension} for item in ing_list]
    return JsonResponse(result, safe=False)


class FollowApi(LoginRequiredMixin, View):

    def post(self, request):

        username = json.loads(request.body)['id']
        follow = get_object_or_404(User, username=username)
        follower = get_object_or_404(User, username=request.user.username)
        favorite_object = Follow.objects.filter(user=follower, author=follow).count()

        if not favorite_object and follow != follower:
            Follow.objects.create(user=follower, author=follow)
            return JsonResponse({'Success':'True'})
        else:
            return JsonResponse({'Success':'False'})

    def delete(self, request, username):
        follow = get_object_or_404(User, username=username)
        follower = get_object_or_404(User, username=request.user.username)
        Follow.objects.filter(user=follower, author=follow).delete()
        return JsonResponse({'Success':'True'})


class FavoritesApi(LoginRequiredMixin, View):

    def post(self, request):
        recipe_id = json.loads(request.body)['id']
        recipe = get_object_or_404(Recipe, id=recipe_id)
        is_favorite = Favorite.objects.filter(user=request.user, recipe=recipe)

        if is_favorite:
            return JsonResponse({'Success':'False'})
        else:
            Favorite.objects.create(user=request.user, recipe=recipe)
            return JsonResponse({'Success':'True'})

    def delete(self, request, recipe_id):
        recipe = get_object_or_404(Recipe, id=recipe_id)
        Favorite.objects.filter(user=request.user, recipe=recipe).delete()
        return JsonResponse({'Success':'True'})


class CartApi(LoginRequiredMixin, View):

    def post(self, request):
        recipe_id = json.loads(request.body)['id']
        recipe = get_object_or_404(Recipe, id=recipe_id)
        is_in_cart = Cart.objects.filter(user=request.user, recipe=recipe)

        if is_in_cart:
            return JsonResponse({'Success':'False'})
        else:
            Cart.objects.create(user=request.user, recipe=recipe)
            return JsonResponse({'Success':'True'})

    def delete(self, request, recipe_id):
        recipe = get_object_or_404(Recipe, id=recipe_id)
        Cart.objects.filter(user=request.user, recipe=recipe).delete()
        return JsonResponse({'Success':'True'})






