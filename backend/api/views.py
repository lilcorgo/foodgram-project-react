from django.db.models import Sum
from django_filters.rest_framework import DjangoFilterBackend
from django.http import HttpResponse
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from recipes.models import (FavoriteRecipe, Ingredient, IngredientRecipe,
                            Recipe, ShoppingCart, Tag)
from users.models import Follow, User
from .filters import RecipeFilter
from .mixins import RetrieveListViewSet
from .paginators import CustomPagination
from .permissions import IsAdminOrAuthorOrReadOnly
from .serializers import (CreateUpdateRecipeSerializer, ShoppingCartSerializer,
                          IngredientSerializer, RecipeSerializer,
                          ShortRecipeSerializer, FollowSerializer,
                          TagSerializer, UserSerializer,
                          ValidateFollowSerializer)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(methods=['POST', 'DELETE'],
            permission_classes=(IsAuthenticated,),
            detail=True)
    def subscribe(self, request, pk):
        follow = self.get_object()
        context = {'follow': follow,
                   'request': request}
        serializer_to_validate = ValidateFollowSerializer(
            data=request.data, context=context)
        serializer_to_validate.is_valid(raise_exception=True)
        serializer_to_create = FollowSerializer(
            follow, context={'request': request})

        if request.method == 'POST':
            Follow.objects.create(follower=request.user,
                                  to_follow=follow)
            return Response(data=serializer_to_create.data,
                            status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            Follow.objects.get(follower=request.user,
                               to_follow_id=pk).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['GET'],
            permission_classes=(IsAuthenticated,),
            detail=False, )
    def subscriptions(self, request):
        queryset = User.objects.filter(
            subscribing__follower=self.request.user)
        paginator = CustomPagination()
        subscriptions = paginator.paginate_queryset(queryset, request)
        serializer = FollowSerializer(subscriptions, many=True,
                                      context={'request': request})
        return paginator.get_paginated_response(serializer.data)


class TagViewSet(RetrieveListViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(RetrieveListViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (SearchFilter,)
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    filterset_fields = ('author', 'tags')
    permission_classes = (IsAuthenticatedOrReadOnly, IsAdminOrAuthorOrReadOnly)

    def get_serializer_class(self):
        if self.action in ('create', 'partial_update'):
            return CreateUpdateRecipeSerializer
        return RecipeSerializer

    @action(methods=['POST', 'DELETE'],
            detail=True,
            permission_classes=(IsAuthenticated,))
    def favorite(self, request, pk):
        recipe = self.get_object()
        context = {'action': 'favorite', 'user': request.user,
                   'recipe': recipe, 'method': request.method}
        to_validate = ShoppingCartSerializer(data=request.data,
                                             context=context)
        to_validate.is_valid(raise_exception=True)
        serializer = ShortRecipeSerializer(recipe)

        if request.method == 'POST':
            FavoriteRecipe.objects.get_or_create(
                recipe=recipe, user=request.user)
            return Response(
                data=serializer.data, status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            FavoriteRecipe.objects.get(recipe=recipe,
                                       user=request.user).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['POST', 'DELETE'],
            detail=True,
            permission_classes=(IsAuthenticated,))
    def shopping_cart(self, request, pk):
        recipe = self.get_object()
        context = {'action': 'shopping_cart', 'user': request.user,
                   'recipe': recipe, 'method': request.method}
        to_validate = ShoppingCartSerializer(data=request.data,
                                             context=context)
        to_validate.is_valid(raise_exception=True)
        to_create = ShortRecipeSerializer(recipe)

        if request.method == 'POST':
            ShoppingCart.objects.create(recipe=recipe, user=request.user)
            return Response(
                data=to_create.data, status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            ShoppingCart.objects.get(recipe=recipe, user=request.user).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['GET'],
            detail=False,
            permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request):
        if not request.user.cart.exists():
            return Response(
                'Корзина пуста', status=status.HTTP_400_BAD_REQUEST)
        ingredients = (
            IngredientRecipe.objects
            .filter(recipe__cart__user=request.user)
            .values('ingredient')
            .annotate(total_amount=Sum('amount'))
            .values_list(
                'ingredient__name',
                'total_amount',
                'ingredient__measurement_unit'
            )
        )

        text = ''
        for ingredient in ingredients:
            text += '{} - {} {}. \n'.format(*ingredient)

        file = HttpResponse(
            f'Корзина:\n {text}', content_type='text/plain'
        )

        file['Content-Disposition'] = ('attachment; filename=cart.txt')
        return file
