from django.contrib import admin

from .models import Ingredient, Recipe, ShoppingCart, Tag


class IngredientInLine(admin.TabularInline):
    model = Recipe.ingredients.through


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = (IngredientInLine,)
    list_display = (
        'author',
        'name',
        'image',
        'cooking_time',
    )
    list_filter = ('name', 'author', 'tags')
    readonly_fields = ('get_favorite',)

    def get_favorite(self, obj):
        count = obj.favorited_by.count()
        return f'Добавлено в избранное {count} раз.'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'slug',
        'color',
    )
    list_filter = ('name',)
    search_fields = ('name',)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'measurement_unit',
    )
    list_filter = ('name',)
    search_fields = ('name',)


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'recipe',
        'user',
    )
    search_fields = ('recipe',)
    list_filter = ('recipe',)
