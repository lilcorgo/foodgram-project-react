from django.urls import include, path
from djoser import views
from rest_framework.routers import DefaultRouter

from .views import IngredientViewSet, RecipeViewSet, TagViewSet, UserViewSet

router = DefaultRouter()

router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('recipes', RecipeViewSet, basename='recipes')


urlpatterns = [
    path('', include(router.urls)),
    path('users/', views.UserViewSet.as_view(
        {'get': 'list', 'post': 'create'}), name='user-list-create'),
    path('users/<int:id>/', views.UserViewSet.as_view(
        {'get': 'retrieve'}), name='user-detail'),
    path('users/me/', views.UserViewSet.as_view(
        {'get': 'me'}), name='user-me'),
    path('users/set_password/', views.UserViewSet.as_view(
        {'post': 'set_password'}), name='user-set-password'),
    path('users/follows/', UserViewSet.as_view({'get': 'follows'}),
         name='user-follows'),
    path('users/<int:pk>/follow/', UserViewSet.as_view(
        {'post': 'follow', 'delete': 'follow'}), name='user-follow'),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
