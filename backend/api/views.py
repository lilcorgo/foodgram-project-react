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
from users.models import Following, User
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
        follow_to = self.get_object()
        context = {'follow_to': follow_to,
                   'request': request}
        validate_serializer = ValidateFollowSerializer(
            data=request.data, context=context)
        validate_serializer.is_valid(raise_exception=True)
        create_serializer = FollowSerializer(
            follow_to, context={'request': request})

        if request.method == 'POST':
            Following.objects.create(follower=request.user,
                                     to_follow=follow_to)
            return Response(data=create_serializer.data,
                            status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            Following.objects.get(follower=request.user,
                                  to_follow_id=pk).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['GET'],
            permission_classes=(IsAuthenticated,),
            detail=False, )
    def subscriptions(self, request):
        queryset = User.objects.filter(
            following__follower=self.request.user)
        paginator = CustomPagination()
        follows = paginator.paginate_queryset(queryset, request)
        serializer = FollowSerializer(follows, many=True,
                                      context={'request': request})
        return paginator.get_paginated_response(serializer.data)


class TagViewSet(RetrieveListViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(RetrieveListViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (SearchFilter,)
    search_fields = ('^name',)
    pagination_class = None


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
        if not request.user.cart_items.exists():
            return Response(
                'Корзина пуста',
                status=status.HTTP_400_BAD_REQUEST)
        recipes = Recipe.objects.filter(added_to_cart__user=request.user)
        ingredients = (
            IngredientRecipe.objects
            .filter(recipe__in=recipes)
            .values('ingredient__name', 'ingredient__measurement_unit')
            .annotate(total_amount=Sum('amount'))
        )

        text = ''
        for ingredient in ingredients:
            text += (f'{ingredient["ingredient__name"]} - {ingredient["amount"]}'
                     f' {ingredient["ingredient__measurement_unit"]}. \n')

        file = HttpResponse(
            f'Корзина:\n {text}', content_type='text/plain'
        )

        file['Content-Disposition'] = ('attachment; filename=cart.txt')
        return file
