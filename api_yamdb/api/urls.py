from django.urls import include, path
from rest_framework.routers import SimpleRouter

from . import views
from api.views import (CategoriesViewSet, CommentViewSet, GenresViewSet,
                       ReviewViewSet, TitlesViewSet)

app_name = 'api'

v1_router = SimpleRouter()
v1_router.register('categories', CategoriesViewSet, basename='categories')
v1_router.register('genres', GenresViewSet, basename='genres')
v1_router.register('titles', TitlesViewSet, basename='titles')
v1_router.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet, basename='reviews'
)
v1_router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet, basename='comments'
)
v1_router.register(r'users', views.UserViewSet, basename='users')


urlpatterns = [
    path('v1/auth/signup/',
         views.UserRegistrationView.as_view(),
         name='signup'),
    path('v1/auth/token/', views.TokenView.as_view(), name='token'),
    path('v1/', include(v1_router.urls)),
]
