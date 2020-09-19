from django.urls import path

from . import views
from .views import FavoritesApi, FollowApi, CartApi

app_name = "recipes"

urlpatterns = [
    path('', views.index, name='index'),
    path('recipes/new/', views.new_recipe, name='recipe_new'),
    path('my_favorites/', views.favorites_view, name='favorites_view'),
    path('my_follow/', views.my_follow, name='my_follow'),
    path('cart/', views.cart_view, name='cart_view'),
    path('download/', views.download, name='download'),

    path('api/favorites', FavoritesApi.as_view(), name='favorites_add'),
    path('api/favorites/<int:recipe_id>', FavoritesApi.as_view(), name='favorites_delete'),
    path('api/subscriptions', FollowApi.as_view(), name='subscriptions_add'),
    path('api/subscriptions/<username>', FollowApi.as_view(), name='subsriptions_delete'),
    path('api/purchases', CartApi.as_view(), name='purchases_add'),
    path('api/purchases/<int:recipe_id>', CartApi.as_view(), name='purchases_delete'),
    path('api/ingredients', views.ingredient_hints, name='ingredient_hints'),

    path('<username>/', views.profile, name='profile'),
    path('<username>/<int:recipe_id>', views.single_recipe, name='single_recipe'),
    path('<username>/<int:recipe_id>/edit', views.recipe_edit, name='recipe_edit'),
    path('<username>/<int:recipe_id>/delete', views.recipe_delete, name='recipe_delete'),
]