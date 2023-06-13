import re

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer
from rest_framework import exceptions, serializers
from rest_framework.serializers import (CharField, IntegerField,
                                        ModelSerializer, SlugRelatedField)

from reviews.models import Category, Comment, Genre, Review, Title
from api_yamdb.roles import ROLE_ADMIN

User = get_user_model()


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username', read_only=True
    )
    title = serializers.SlugRelatedField(
        slug_field='name', read_only=True
    )

    def validate(self, data):
        request = self.context['request']
        author = request.user
        title = get_object_or_404(
            Title,
            pk=self.context['view'].kwargs.get('title_id')
        )
        if (request.method == 'POST'
                and Review.objects.filter(
                    title=title, author=author
                ).exists()):
            raise serializers.ValidationError(
                'Отзыв возможно оставить только один раз!'
            )
        return data

    class Meta:
        model = Review
        fields = '__all__'


class UserRegistrationSerializer(UserCreateSerializer):
    """Сериализатор для регистрации - проверяет email и username."""
    email = serializers.EmailField(required=True, max_length=254)
    username = serializers.CharField(required=True, max_length=150)

    def validate_username(self, value):
        """Проверяем username на валидность."""
        if value.lower() == 'me':
            raise serializers.ValidationError(
                "The username 'me' is not allowed"
            )

        pattern = r'^[\w.@+-]+$'
        if not re.match(pattern, value):
            raise serializers.ValidationError("Invalid username format")

        return value

    def validate(self, attrs):
        """Проверяем данные на валидность."""
        email = attrs.get('email')
        username = attrs.get('username')

        if User.objects.filter(username=username, email=email).exists():
            return attrs

        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError("Email is already registered")
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError("Username is already taken")

        return attrs

    class Meta(UserCreateSerializer.Meta):
        fields = ('email',
                  'username',
                  'first_name',
                  'last_name',
                  'bio',
                  'role')
        model = User


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    class Meta:
        model = Comment
        fields = '__all__'
        read_only_fields = ('review',)


class TokenSerializer(serializers.Serializer):
    """Сериализатор для выдачи токена - проверяет
    confirmation_code и username."""

    username = serializers.CharField(required=True)
    confirmation_code = serializers.CharField(required=True)

    def validate(self, attrs):
        """Проверяем данные на валидность (особенно код)."""
        username = attrs.get('username')
        confirmation_code = attrs.get('confirmation_code')
        user = get_object_or_404(User, username=username)

        saved_confirmation_code = user.code

        if not User.objects.filter(username=username).exists():
            raise exceptions.NotFound("Username not found")

        if confirmation_code != saved_confirmation_code:
            raise serializers.ValidationError('Invalid confirmation code')

        return attrs


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для пользователя."""

    def get_fields(self):
        """Если пользователь админ или суперпользователь,
        то поле role изменяемое."""
        fields = super().get_fields()
        if self.context['user'].is_superuser:
            fields['role'].read_only = False

        if hasattr(self.context['user'], 'role'):
            if self.context['user'].role == ROLE_ADMIN:
                fields['role'].read_only = False

        return fields

    class Meta:
        model = User
        fields = ('email',
                  'username',
                  'first_name',
                  'last_name',
                  'bio',
                  'role')
        read_only_fields = ('role', 'confirmation_code')


class CategorySerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = ('name', 'slug')


class GenreSerializer(ModelSerializer):
    class Meta:
        model = Genre
        fields = ('name', 'slug')


class TitleSerializer(ModelSerializer):
    category = CategorySerializer()
    genre = GenreSerializer(many=True)
    rating = IntegerField(source='reviews__score__avg', read_only=True)

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'rating', 'description', 'genre', 'category'
        )


class TitleCreateUpdateSerializer(ModelSerializer):
    category = SlugRelatedField(
        queryset=Category.objects.all(), slug_field='slug', required=True
    )
    genre = SlugRelatedField(
        queryset=Genre.objects.all(),
        slug_field='slug',
        many=True,
        required=True,
    )
    description = CharField(required=False)

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'description', 'genre', 'category')
        read_only_fields = ('rating',)
