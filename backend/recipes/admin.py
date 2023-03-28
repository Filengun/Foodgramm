from django.contrib import admin

from .models import (Bookmark, Cart, Ingredient, IngredientForRecipe, Recipe,
                     Tag)


class TagAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'color',
        'slug',
    )


class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'measurement_unit'
    )


class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'author',
        'text',
        'image',
        'cooking_time',
        'pub_date',
    )
    list_filter = ('name',)
    empty_value_display = 'нет информации'


class BookmarkAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'recipe',
        'user'
    )


class CartAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'recipe',
        'user'
    )


class IngredientForRecipeAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'recipe',
        'amount'
    )


admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Bookmark, BookmarkAdmin)
admin.site.register(Cart, CartAdmin)
admin.site.register(IngredientForRecipe, IngredientForRecipeAdmin)
