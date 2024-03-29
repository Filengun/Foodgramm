from django.contrib.auth import get_user_model
from django_filters.rest_framework import FilterSet, filters
from recipes.models import Ingredient, Recipe, Tag

User = get_user_model()


class IngredientsFilter(FilterSet):
    '''Фильтр ингредиентов'''
    name = filters.CharFilter(lookup_expr="istartswith")

    class Meta:
        model = Ingredient
        fields = ("name",)


class RecipesFilter(FilterSet):
    '''Фильтр рецептов'''
    tags = filters.ModelMultipleChoiceFilter(
        field_name="tags__slug",
        to_field_name='slug',
        queryset=Tag.objects.all()
    )
    author = filters.ModelChoiceFilter(queryset=User.objects.all())
    is_favorited = filters.BooleanFilter(method="filter_for_is_favorited")
    is_in_shopping_cart = filters.BooleanFilter(
        method="filter_for_is_in_shopping_cart"
    )

    class Meta:
        model = Recipe
        fields = ("tags", "author", )

    def filter_for_is_favorited(self, queryset, name, value):
        '''Фильтруем подписки'''
        request = self.request.user
        if value and not request.is_anonymous:
            return queryset.filter(bookmark__user=request)
        return queryset

    def filter_for_is_in_shopping_cart(self, queryset, name, value):
        '''Фильтруем рецепты в корзине'''
        request = self.request.user
        if value and not request.is_anonymous:
            return queryset.filter(cart__user=request)
        return queryset
