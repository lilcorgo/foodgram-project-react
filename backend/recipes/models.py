from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
from users.models import User


class Tag(models.Model):
    name = models.CharField(
        verbose_name='Название тега',
        unique=True,
        max_length=150,
    )
    color = models.CharField(
        verbose_name='Цвет в HEX',
        unique=True,
        max_length=7,
        validators=[
            RegexValidator(
                regex='^#(?:[0-9a-fA-F]{3}){1,2}$',
                message='Допустим лишь формат в HEX',
            )
        ]
    )
    slug = models.SlugField(
        verbose_name='Слаг',
        unique=True,
        max_length=150,
    )

    class Meta:
        ordering = ('id',)
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='Ингридиент',
        unique=True,
        max_length=150,
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=20,
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Recipe(models.Model):
    name = models.CharField(
        verbose_name='Название рецепта',
        unique=True,
        max_length=200,
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор рецепта',
        on_delete=models.CASCADE,
        related_name='recipes',
    )
    text = models.TextField(
        verbose_name='Описание рецепта',
    )
    cooking_time = models.IntegerField(
        verbose_name='Время приготовления в минутах',
        validators=[
            MinValueValidator(
                1,
                message='Допустимое время от 1 мин.'
            )
        ]
    )
    image = models.ImageField(
        verbose_name='Изображение',
        upload_to='recipes/',
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингридиенты',
        through='IngredientRecipe',
    )
    created = models.DateTimeField(
        verbose_name='Дата создания',
        auto_now_add=True,
    )

    class Meta:
        ordering = ('-created',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name

    def get_tags(self):
        return '\n'.join([tags.slug for tags in self.tags.all()])

    def get_ingredients(self):
        return '\n'.join(
            [ing.name + ', ' + ing.measurement_unit for ing in
             self.ingredients.all()])


class IngredientRecipe(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
    )
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='Ингредиент',
        on_delete=models.CASCADE,
    )
    amount = models.PositiveIntegerField(
        verbose_name='Количество',
        default=1,
        validators=[
            MinValueValidator(
                1,
                message='Допустимое количество от 1 шт.'
            )
        ],
    )

    def __str__(self):
        return f'Для {self.recipe} нужно {self.amount} {self.ingredient}.'


class FavoriteRecipe(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='Избранный автор',
        on_delete=models.CASCADE,
        related_name='favorite_recipes',
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт из избранного',
        on_delete=models.CASCADE,
        related_name='favorited_by',
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'
        constraints = (
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite',
            ),
        )

    def __str__(self):
        return f'{self.recipe.name} авторства {self.user.name}.'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
        related_name='cart_items',
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Список покупок',
        on_delete=models.CASCADE,
        related_name='added_to_cart',
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_cart',
            ),
        ]
