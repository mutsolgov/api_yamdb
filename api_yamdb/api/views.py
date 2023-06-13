from django.contrib.auth import get_user_model
from django.db.models import Avg
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from reviews.models import Category, Genre, Review, Title
from .filters import TitlesFilter
from .mixins import ListCreateDestroyViewSet
from .permissions import AuthorAdminModerator, IsAdmin, IsAdminOrReadOnly
from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, ReviewSerializer,
                          TitleCreateUpdateSerializer, TitleSerializer,
                          TokenSerializer, UserRegistrationSerializer,
                          UserSerializer)
from .utils import generate_confirmation_code, send_confirmation_email

User = get_user_model()


class ReviewViewSet(viewsets.ModelViewSet):
    permission_classes = [AuthorAdminModerator]
    serializer_class = ReviewSerializer

    def perform_create(self, serializer):
        title = get_object_or_404(Title,
                                  id=self.kwargs.get('title_id')
                                  )
        serializer.save(author=self.request.user, title=title)

    def get_queryset(self):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        return title.reviews.all()


class CommentViewSet(viewsets.ModelViewSet):
    permission_classes = [AuthorAdminModerator]
    serializer_class = CommentSerializer

    def perform_create(self, serializer):
        review = get_object_or_404(Review,
                                   id=self.kwargs.get('review_id'),
                                   title=self.kwargs.get('title_id'))
        serializer.save(author=self.request.user, review=review)

    def get_queryset(self):
        review = get_object_or_404(Review,
                                   id=self.kwargs.get('review_id'),
                                   title=self.kwargs.get('title_id'))
        return review.comments.all()


class UserRegistrationView(APIView):
    """Вью-функция с регистрацией пользователя."""
    def post(self, request):
        """Post-запрос отправляет код, если все валидно."""
        serializer = UserRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data['username']
        if not User.objects.filter(username=username).exists():
            serializer.save()

        user = get_object_or_404(User, username=username)
        confirmation_code = generate_confirmation_code()
        user.code = confirmation_code
        user.save()

        send_confirmation_email(user.email, confirmation_code)

        return Response(data=request.data, status=200)


class TokenView(APIView):
    """Вью-функция с отправкой токена пользователю."""
    def post(self, request):
        """Post-запрос возвращает токен, если все валидно."""
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data['username']
        user = User.objects.get(username=username)
        token = RefreshToken.for_user(user)
        return Response({'token': str(token.access_token)},
                        status=status.HTTP_200_OK)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdmin,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    http_method_names = ('get', 'post', 'patch', 'delete')
    lookup_field = 'username'

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['user'] = self.request.user
        return context

    @action(detail=False,
            methods=['GET', 'PATCH'],
            permission_classes=[IsAuthenticated])
    def me(self, request):
        if request.method == 'GET':
            user = request.user
            serializer = UserSerializer(user, context={'user': request.user})
            return Response(serializer.data)
        user = request.user
        serializer = UserSerializer(user,
                                    data=request.data,
                                    partial=True,
                                    context={'user': request.user})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class CategoriesViewSet(ListCreateDestroyViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenresViewSet(ListCreateDestroyViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TitlesViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.annotate(Avg('reviews__score'))
    serializer_class = TitleSerializer
    permission_classes = [IsAdminOrReadOnly, ]
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filterset_class = TitlesFilter
    ordering = ('id',)

    def get_serializer_class(self):
        if self.action in ['create', 'partial_update']:
            return TitleCreateUpdateSerializer
        return TitleSerializer
