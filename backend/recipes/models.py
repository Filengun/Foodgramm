from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
from users.models import User


class Tag(models.Model):
    '''Модель тега'''
    name = models.CharField(
        max_length=200,
        unique=True,
        db_index=True,
        verbose_name='Тег'
    )
    color = models.CharField(
        max_length=7,
        unique=True,
        verbose_name='Цвет тега'
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        validators=[RegexValidator(
            regex=r'[\w.@+-]+$',
            message='Недопустимые символы'
        )],
        verbose_name='Слаг'
    )

    class Meta:
        verbose_name = 'Тег',
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    '''Модель ингридиента'''
    name = models.CharField(
        max_length=200,
        db_index=True,
        verbose_name='Название ингридиента'
    )
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name='Единица измерения'
    )

    class Meta:
        verbose_name = 'Ингридиент',
        verbose_name_plural = 'Ингридиенты'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    '''Модель рецепта'''
    name = models.CharField(
        max_length=200,
        db_index=True,
        verbose_name='Название рецепта'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='recipes',
        verbose_name='Автор'
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Теги'
    )
    text = models.TextField(
        verbose_name='Описание'
    )
    image = models.ImageField(
        upload_to='recipes/',
        verbose_name='Картинка'
    )
    cooking_time = models.PositiveIntegerField(
        verbose_name='Затраченое время на приготовление'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name='Дата создания'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientForRecipe',
        related_name='recipes',
        verbose_name='Ингридиенты'
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ("-pub_date", )

    def __str__(self):
        return self.name


class IngredientForRecipe(models.Model):
    """Класс связи для связи ингредиентов и рецептов"""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name="recipe"
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name="ingredient",
        verbose_name='Ингредиент',
    )
    amount = models.PositiveIntegerField(
        verbose_name='Количество ингредиента',
        default=1,
        validators=[
            MinValueValidator(
                1,
                message="Минимальное количество ингредиента 1"
            )
        ],
    )

    class Meta:
        verbose_name = 'Ингредиенты в рецепте'
        verbose_name_plural = 'Соответствие ингредиентов и рецептов'
        constraints = [
            models.UniqueConstraint(
                fields=['ingredient', 'recipe'],
                name='unique_ingredient'
            )
        ]

    def __str__(self):
        return (f'В рецепте <<{self.recipe.name}>>'
                f'следующий(ие) ингредиент(ы): {self.ingredient.name}'
                f'({self.cnt})')


class Bookmark(models.Model):
    '''Модель закладок/избранных'''
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='bookmark',
        verbose_name='Рецепт'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='bookmark',
        verbose_name='Юзер'
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_bookmark'
            )
        ]

    def __str__(self):
        return (f'Рецепт <<{self.recipe}>> добавлен в избранное'
                f'у пользователя {self.user}')


class Cart(models.Model):
    '''Модель корзины'''
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='cart',
        verbose_name='Рецепт'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='cart',
        verbose_name='Юзер'
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_cart'
            )
        ]

    def __str__(self):
        return (f"{self.user} добавил в корзину: {self.recipe}")
