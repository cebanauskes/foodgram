from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Recipe, Tag, Ingredient, Amount, Favorite, Follow, Cart, User
from .utils import ExportCsvMixin


class AmountInLine(admin.TabularInline):
    model = Amount
    extra = 1


class UserAdmin(BaseUserAdmin):
    list_filter = ('first_name', 'email')

class RecipeAdmin(admin.ModelAdmin):

    def favorites_count(self, obj):
        favorite = Favorite.objects.filter(recipe=obj).count()
        return favorite
    
    favorites_count.short_description = 'Количество добавлений в избранное'

    list_display= ('pk', 'title', 'duration', 'pub_date', 'description', 'author', )
    search_fields = ('description', 'title',)
    list_filter = ('pub_date', 'title')
    empty_value_display = '-пусто-'
    inlines = (AmountInLine, )
    readonly_fields = ('favorites_count',)


class TagAdmin(admin.ModelAdmin, ExportCsvMixin):
    list_display = ('pk','title',)
    actions = ["export_as_csv"]
        


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('pk', 'title', 'dimension',)
    search_fields = ('title',)
    list_filter = ('title',)


class AmountAdmin(admin.ModelAdmin):
    fields = ('ingredient', 'recipe', 'quantity',)
    search_fields = ('recipe', 'ingredient', )


class FavoriteAdmin(admin.ModelAdmin):
    fields = ('recipe', 'user')
    search_fields = ('recipe', 'user')


class FollowAdmin(admin.ModelAdmin):
    list_display = ('user', 'author')


class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Amount, AmountAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(Follow, FollowAdmin)
admin.site.register(Cart, CartAdmin)