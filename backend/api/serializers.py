import webcolors
from django.contrib.auth import get_user_model
from django.db import transaction
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from recipes.models import Cart, Ingredient, IngredientForRecipe, Recipe, Tag
from rest_framework import serializers
from users.models import Subscription

User = get_user_model()


class UserSerializer(UserSerializer):
    '''Сериализатор для User'''
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    def get_is_subscribed(self, obj):
        '''Возвращаем True если юзер подписан на автора'''
        user = self.context.get('request').user
        if not user or user.is_anonymous:
            return False
        return Subscription.objects.filter(
            subscriber=user,
            author=obj).exists()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )


class CreateUserSerializer(UserCreateSerializer):
    '''Сериализатор для создания профиля'''

    def create(self, validated_data):
        user_create = User.objects.create(
            username=validated_data.get("username"),
            email=validated_data.get("email"),
            first_name=validated_data.get("first_name"),
            last_name=validated_data.get("last_name")
        )
        user_create.set_password(validated_data.get("password"))
        user_create.save()
        return user_create

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "password",
            "first_name",
            "last_name"
        )


class HexColorForTag(serializers.Field):

    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        try:
            return webcolors.hex_to_name(data)
        except ValueError:
            raise serializers.ValidationError("Для этого цвета нет имени")


class TagSerializer(serializers.ModelSerializer):
    '''Сериализатор для тегов'''
    color = HexColorForTag

    class Meta:
        model = Tag
        fields = (
            "id",
            "name",
            "color",
            "slug"
        )


class IngredientSerializer(serializers.ModelSerializer):
    '''Сериализатор для ингридиентов'''

    class Meta:
        model = Ingredient
        fields = (
            "id",
            "name",
            "measurement_unit"
        )


class GetIngridientsForRecipeSerializer(serializers.ModelSerializer):
    '''Сериализатор для игридиентов рецепта для get запроса рецептов'''
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientForRecipe
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount'
        )


class PostIngridientsForRecipeSerializer(serializers.ModelSerializer):
    '''Сериализатор для игридиентов рецепта для get запроса рецептов'''
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )

    class Meta:
        model = IngredientForRecipe
        fields = (
            'id',
            'amount'
        )


class RecipeGetSerializer(serializers.ModelSerializer):
    '''Сериализатор для рецептов для get запросов'''
    is_favorited = serializers.BooleanField(read_only=True)
    is_in_shopping_cart = serializers.BooleanField(read_only=True)
    author = UserSerializer(read_only=True)
    image = Base64ImageField()
    ingredients = GetIngridientsForRecipeSerializer(
        many=True,
        source='recipe'
    )
    tags = TagSerializer(many=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
            "pub_date"
        )


class RecipePostSerializer(serializers.ModelSerializer):
    '''Сериализатор для рецептов для get запросов'''
    tags = TagSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
    )
    image = Base64ImageField()
    author = UserSerializer(read_only=True)
    ingredients = PostIngridientsForRecipeSerializer(many=True)

    def _create_ingredients(self, ingredients, recipe):
        create_ingredient = [
            IngredientForRecipe(
                recipe=recipe,
                ingredient=ingredient.get("id"),
                amount=ingredient.get("amount")
            )
            for ingredient in ingredients
        ]
        IngredientForRecipe.objects.bulk_create(create_ingredient)

    @transaction.atomic
    def create(self, validated_data):
        try:
            tags = validated_data.pop('tags')
            ingredient = validated_data.pop('ingredients')
        except Exception:
            raise KeyError(
                'Ингредиент и тег обязательны к заполнению!'
            )
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self._create_ingredients(ingredient, recipe)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        instance.image = validated_data.get('image', instance.image)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )
        instance.tags.clear()
        tags = self.initial_data.get('tags')
        instance.tags.set(tags)
        IngredientForRecipe.objects.filter(recipe=instance).all().delete()
        self.create_ingredients(
            validated_data.get('ingredients'),
            instance
        )
        instance.save()
        return instance

    def to_representation(self, obj):
        return RecipeGetSerializer(obj, context=self.context).data

    class Meta:
        model = Recipe
        fields = (
            'id',
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time',
            'author',
            'pub_date',
        )


class SubscriberSerializer(UserSerializer):
    '''Сериализатор подписок для вывода информции'''
    recipes_count = serializers.SerializerMethodField(read_only=True)
    recipes = serializers.SerializerMethodField(read_only=True)

    def get_recipes_count(self, obj):
        '''Подсчитываем количество рецептов'''
        return obj.recipes.count()

    def get_recipes(self, obj):
        '''Возвращаем рецепты автора'''
        request = self.context.get('request')
        recipes_limit = request.query_params.get('recipes_limit')
        if recipes_limit:
            return SubscriberRecipeSerializer(
                Recipe.objects.filter(author=obj)[:int(recipes_limit)],
                many=True,
                context={'request': request}
            ).data
        return SubscriberRecipeSerializer(
            Recipe.objects.filter(author=obj),
            many=True,
            context={'request': request}
        ).data

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )


class SubscriberListSerializer(serializers.ModelSerializer):
    '''Сериализатор для анализа подписок для POST запроса'''

    class Meta:
        model = Subscription
        fields = (
            "id",
            "subscriber",
            "author"
        )


class SubscriberRecipeSerializer(serializers.ModelSerializer):
    '''Сериализатор который показывает рецепты автора
    на которого подписан юзер.
    Предназначен для сериализатора SubscriberSerializer
    '''
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class ShoppintCartSerializer(serializers.ModelSerializer):
    '''Сериализатор для корзины'''

    class Meta:
        model = Cart
        fields = (
            'id',
            "recipe",
            "user"
        )
