from django.contrib.auth import get_user_model
from django.db.models import Exists, OuterRef, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from recipes.models import (Bookmark, Cart, Ingredient, IngredientForRecipe,
                            Recipe, Tag)
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from users.models import Subscription

from .filters import IngredientsFilter, RecipesFilter
from .pagination import UserPagination
from .permissions import IsAuthorOrReadOnly
from .serializers import (IngredientSerializer, RecipeGetSerializer,
                          RecipePostSerializer, ShoppintCartSerializer,
                          SubscriberListSerializer, SubscriberRecipeSerializer,
                          SubscriberSerializer, TagSerializer, UserSerializer)

User = get_user_model()


class UserViewSet(UserViewSet):
    '''Вьюсет для юзера'''
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = UserPagination
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    @action(
        detail=False,
        methods=['GET'],
        permission_classes=(permissions.IsAuthenticated,)
    )
    def subscriptions(self, request):
        '''Авторы на которых подписан Юзер'''
        subscribers = User.objects.filter(author__subscriber=request.user)
        page = self.paginate_queryset(subscribers)
        serializer = SubscriberSerializer(
            page,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        permission_classes=(permissions.IsAuthenticated,)
    )
    def subscribe(self, request, id):
        '''Подписка и отписка от других авторов'''
        author = get_object_or_404(User, id=id)
        subscribed = request.user
        if request.method == 'POST':
            data = {
                'subscriber': subscribed.id,
                'author': author.id
            }
            serializer = SubscriberListSerializer(
                data=data,
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            information_output_serializer = SubscriberSerializer(
                author,
                context={'request': request}
            )
            return Response(
                information_output_serializer.data,
                status=status.HTTP_201_CREATED
            )
        if request.method == 'DELETE':
            subscription = get_object_or_404(
                Subscription,
                subscriber=subscribed,
                author=author
            )
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        # return Response(status=status.HTTP_204_NO_CONTENT)


class IngredientViewSet(viewsets.ModelViewSet):
    '''Вьюсет для ингридиентов'''
    queryset = Ingredient.objects.all()
    pagination_class = None
    serializer_class = IngredientSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = IngredientsFilter
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


class TagViewSet(viewsets.ModelViewSet):
    '''Вьюсет для тегов'''
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


class RecipeViewSet(viewsets.ModelViewSet):
    '''Вьюсет для рецептов'''
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend, )
    filterset_class = RecipesFilter
    serializer_class = RecipeGetSerializer

    def get_serializer_class(self):
        '''Метод возвращает сериализатор в зависимости от запроса'''
        if self.request.method == "GET":
            return RecipeGetSerializer
        return RecipePostSerializer

    def get_queryset(self):
        '''Метод возвращает набор необходимых данных'''
        queryset = Recipe.objects.select_related(
            "author"
        ).prefetch_related(
            "ingredients",
            "tags"
        )
        user = self.request.user
        if user.is_authenticated:
            queryset = queryset.annotate(
                is_favorited=Exists(
                    Bookmark.objects.filter(
                        user=user,
                        recipe=OuterRef("id")
                    )
                ),
                is_in_shopping_cart=Exists(
                    Cart.objects.filter(
                        user=user,
                        recipe=OuterRef("id")
                    )
                )
            )
        return queryset

    def perform_create(self, serializer):
        """"Передает в поле author данные о пользователе"""
        serializer.save(author=self.request.user)

    def perform_destroy(self, instance):
        """Удаляет объект класса рецепт"""
        instance.delete()

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=(permissions.IsAuthenticated,)
    )
    def favorite(self, request, id):
        '''Добавление и удаление в избранное'''
        recipe = get_object_or_404(Recipe, id=id)
        if request.method == 'POST':
            Bookmark.objects.create(
                user=request.user,
                recipe=recipe
            )
            serializer = SubscriberRecipeSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if Bookmark.objects.filter(
            user=request.user,
            recipe__id=id
        ).exists():
            Bookmark.objects.filter(
                user=request.user,
                recipe__id=id
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=(permissions.IsAuthenticated,)
    )
    def shopping_cart(self, request, id):
        '''Корзина'''
        recipe = get_object_or_404(Recipe, id=id)
        if request.method == 'POST':
            serializer = ShoppintCartSerializer(
                data={
                    'user': request.user.id,
                    'recipe': recipe.id
                }
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            information_output_serializer = SubscriberRecipeSerializer(recipe)
            return Response(
                information_output_serializer.data,
                status=status.HTTP_201_CREATED
            )
        if Cart.objects.filter(
            user=request.user,
            recipe__id=id
        ).exists():
            Cart.objects.filter(
                user=request.user,
                recipe__id=id
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(
        methods=["GET"],
        detail=False,
        permission_classes=(permissions.IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        '''Скачать информацию об рецептах в корзине'''
        ingredients = IngredientForRecipe.objects.select_related(
            "recipe", "ingredient"
        )
        ingredients = IngredientForRecipe.objects.filter(
            recipe__cart__user=request.user
        ).values(
            "ingredient__name",
            "ingredient__measurement_unit"
        ).annotate(amount=Sum("amount"))
        data_cart = "Продукты которые нужно купить:\n\n"
        for ingredient in ingredients:
            data_cart += "- {}({}) - {}\n".format(
                ingredient['ingredient__name'],
                ingredient['ingredient__measurement_unit'],
                ingredient['amount']
            )
        data_cart += "\n\n\n\nПроект создан Filengun"
        filename = "foodgram_shopping_cart.txt"
        response = HttpResponse(data_cart, content_type="text/plain")
        response["Content-Disposition"] = f"attachment; {filename}"
        return response
