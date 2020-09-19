from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
import json

from .forms import RecipeForm
from .models import Amount, Cart, Follow, Favorite, Ingredient, Recipe, User, Follow 
from .utils import get_ingredients, create_amount


def index(request):
    filters = request.GET.getlist('filters')
    if filters:
        recipe_list = Recipe.objects.filter(
            tags__value__in=filters).distinct()
    else:
        recipe_list = Recipe.objects.all()

    frecipe_ids = []

    if request.user.is_authenticated:
        favor = Favorite.objects.filter(user=request.user).all()
        frecipe_ids = favor.values_list('recipe', flat=True)

    paginator = Paginator(recipe_list, 6)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'index.html', {'recipe_list': recipe_list, 
                                            'page': page,
                                            'paginator': paginator, 
                                            'frecipe_ids': frecipe_ids, })

@login_required
def new_recipe(request):
    ing_dict = get_ingredients(request)
    header = 'Создание рецепта'
    button = 'Создать рецепт'
    if request.method == 'POST':
        form = RecipeForm(request.POST or None, files=request.FILES or None)

        if form.is_valid():
            recipe = form.save(commit=False)
            recipe.author = request.user
            recipe.save()
            create_amount(ing_dict, recipe)
            form.save_m2m()
            return redirect('recipes:index')

    form = RecipeForm()
    return render(request, 'RecipeNew.html', {'form': form, 'header':header,
                                              'button': button, })

def recipe_edit(request, username, recipe_id):
    profile = get_object_or_404(User, username=username)
    recipe = get_object_or_404(Recipe, pk=recipe_id, author=profile)
    ing_dict = get_ingredients(request)
    header = 'Редактирование рецепта'
    button = 'Сохранить'
    if request.user != profile:
        return redirect(
            'recipes:single_recipe', username=username, recipe_id=recipe_id)

    if request.method == 'POST':
        form = RecipeForm(
            request.POST or None, files=request.FILES or None, instance=recipe)

        if form.is_valid():
            recipe=form.save(commit=False)
            recipe.author = request.user
            recipe.save()
            create_amount(ing_dict, recipe)
            form.save_m2m()
            return redirect(
                'recipes:single_recipe', username=username, recipe_id=recipe_id)

    form = RecipeForm(instance=recipe)
    for tag in recipe.tags.all():
        form.instance.tags.add(tag)
    return render(request, 'recipeNew.html', {'form': form, 'header':header,
                                              'button': button, 'recipe': recipe})

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
    is_favorite = None

    if request.user.is_authenticated:
        is_favorite = Favorite.objects.filter(
            user=request.user, recipe=recipe).exists()
        is_follow = Follow.objects.filter(
            user=request.user, author=profile).exists()

    return render(request, 'singleRecipe.html', {'recipe': recipe, 
                                                 'profile': profile, 
                                                 'is_follow': is_follow,
                                                 'is_favorite': is_favorite })

def profile(request, username):

    profile = get_object_or_404(User, username=username)
    is_follow = None
    frecipe_ids = []

    if request.user.is_authenticated:
        favor = profile.favorites.all()
        frecipe_ids = favor.values_list('recipe', flat=True)

        is_follow = Follow.objects.filter(
            user=request.user, author=profile).exists()

    filters = request.GET.getlist('filters')
    
    if filters:
        recipe_list = Recipe.objects.filter(
            tags__value__in=filters, author=profile).distinct()
    else:
        recipe_list = Recipe.objects.filter(author=profile).all()
        
    paginator = Paginator(recipe_list, 6)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'profile.html', {'page': page,
                                            'paginator': paginator,
                                            'frecipe_ids': frecipe_ids,
                                            'profile': profile,
                                            'is_follow': is_follow, })

@login_required
def my_follow(request):
    sub_list = Follow.objects.filter(user=request.user)
    recipe_list = []

    for fitem in sub_list:
        recipe_list.extend(fitem.author.recipes.all()[:3:])

    paginator = Paginator(sub_list, 6)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    return render(request, 'myFollow.html', {'page': page,
                                             'recipe_list': recipe_list})

@login_required
def favorites_view(request):
    filters = request.GET.getlist('filters')

    if filters:
        favorite_list = Favorite.objects.filter(
            user=request.user, recipe__tags__value__in=filters
            ).select_related('recipe').distinct().all()
    else:
        favorite_list = Favorite.objects.filter(
            user=request.user).select_related('recipe').all()

    frecipe_ids = favorite_list.values_list('recipe', flat=True)
    recipe_list = []

    for item in favorite_list:
        recipe_list.append(item.recipe)

    paginator = Paginator(recipe_list, 6)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    return render(request, 'myFavorites.html', {'page': page,
                                                'paginator': paginator, 
                                                'frecipe_ids': frecipe_ids})

@login_required
def cart_view(request):
    cart = Cart.objects.filter(user=request.user).all()
    return render(request, 'shopList.html', {'cart': cart})

@login_required
def download(request):
    cart = Cart.objects.filter(user=request.user).all()
    ingredients_dict = {}

    for item in cart:

        for amount in item.recipe.amounts.all():

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
    text = request.GET['query']
    ing_list = Ingredient.objects.filter(title__startswith=text).order_by('title')
    result = [{"title": item.title, "dimension": item.dimension} for item in ing_list]
    return JsonResponse(result, safe=False)


class FollowApi(LoginRequiredMixin, View):

    def post(self, request):

        username = json.loads(request.body)['id']
        follow = get_object_or_404(User, username=username)
        follower = get_object_or_404(User, username=request.user.username)
        favorite_object = Follow.objects.filter(
            user=follower, author=follow).exists()

        if not favorite_object and follow != follower:
            Follow.objects.create(user=follower, author=follow)
            return JsonResponse({'success':'True'})
        else:
            return JsonResponse({'success':'False'})

    def delete(self, request, username):
        follow = get_object_or_404(User, username=username)
        follower = get_object_or_404(User, username=request.user.username)
        Follow.objects.filter(user=follower, author=follow).delete()
        return JsonResponse({'success':'True'})


class FavoritesApi(LoginRequiredMixin, View):

    def post(self, request):
        recipe_id = json.loads(request.body)['id']
        recipe = get_object_or_404(Recipe, id=recipe_id)
        is_favorite = Favorite.objects.filter(
            user=request.user, recipe=recipe).exists()

        if is_favorite:
            return JsonResponse({'success':'False'})
        else:
            Favorite.objects.create(user=request.user, recipe=recipe)
            return JsonResponse({'success':'True'})

    def delete(self, request, recipe_id):
        recipe = get_object_or_404(Recipe, id=recipe_id)
        Favorite.objects.filter(user=request.user, recipe=recipe).delete()
        return JsonResponse({'success':'True'})


class CartApi(LoginRequiredMixin, View):

    def post(self, request):
        recipe_id = json.loads(request.body)['id']
        recipe = get_object_or_404(Recipe, id=recipe_id)
        is_in_cart = Cart.objects.filter(
            user=request.user, recipe=recipe).exists()

        if is_in_cart:
            return JsonResponse({'success':'False'})
        else:
            Cart.objects.create(user=request.user, recipe=recipe)
            return JsonResponse({'success':'True'})

    def delete(self, request, recipe_id):
        recipe = get_object_or_404(Recipe, id=recipe_id)
        Cart.objects.filter(user=request.user, recipe=recipe).delete()
        return JsonResponse({'success':'True'})






