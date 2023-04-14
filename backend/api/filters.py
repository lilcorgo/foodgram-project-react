from django_filters import AllValuesMultipleFilter, FilterSet, NumberFilter

from recipes.models import Recipe


class RecipeFilter(FilterSet):
    is_favorited = NumberFilter(method='in_favorited')
    is_in_shopping_cart = NumberFilter(method='in_shopping_cart')
    author = NumberFilter(field_name='author_id')
    tags = AllValuesMultipleFilter(field_name='tags__slug')

    class Meta:
        model = Recipe
        fields = (
            'author',
            'tags',
            'is_favorited',
            'is_in_shopping_cart',
        )

    def in_favorited(self, queryset, name, value):
        if value not in (1, 0):
            return queryset.none()
        if value:
            queryset = queryset.filter(favorited_by__user=self.request.user)
        else:
            queryset = queryset.exclude(favorited_by__user=self.request.user)
        return queryset

    def in_shopping_cart(self, queryset, name, value):
        if value not in (1, 0):
            return queryset.none()
        if value:
            queryset = queryset.filter(added_to_cart__user=self.request.user)
        else:
            queryset = queryset.exclude(added_to_cart__user=self.request.user)
        return queryset
