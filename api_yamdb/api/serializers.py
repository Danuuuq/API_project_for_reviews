from datetime import date

from django.conf import settings
from django.contrib.auth.validators import UnicodeUsernameValidator
from rest_framework import serializers

from reviews.models import Title, Genre, Category, Review, Comment
from users.models import User


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ['name', 'slug']
        lookup_field = 'slug'


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['name', 'slug']
        lookup_field = 'slug'


class TitleSerializer(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(
        many=True,
        queryset=Genre.objects.all(),
        slug_field='slug'
    )
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug'
    )
    rating = serializers.IntegerField(source='average_rating', read_only=True)

    def validate_year(self, data):
        if data > date.today().year:
            raise serializers.ValidationError(
                'Нельзя добавить произведение '
                f'из будущего года: {data}')
        return data

    def validate_genre(self, data):
        if len(data) == 0:
            raise serializers.ValidationError('Укажите жанры '
                                              'для произведения')
        return data

    def to_representation(self, instance):
        self.fields['genre'] = GenreSerializer(many=True, read_only=True)
        self.fields['category'] = CategorySerializer(read_only=True)
        return super().to_representation(instance)

    class Meta:
        model = Title
        fields = ['id', 'name', 'year', 'rating',
                  'description', 'genre', 'category']


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(slug_field='username',
                                          read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'text', 'author',
                  'score', 'pub_date']
        read_only_fields = ['author', 'pub_date']

    def validate_score(self, value):
        if not (settings.MIN_RATING <= value <= settings.MAX_RATING):
            raise serializers.ValidationError(
                'Оценка должна быть от 1 до 10.'
            )
        return value


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(slug_field='username',
                                          read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'text', 'author', 'pub_date']
        read_only_fields = ['author', 'pub_date']


class BaseUserSerializer(serializers.BaseSerializer):
    def validate_username(self, data):
        if data == settings.USER_SELF_IDENTIFIER:
            raise serializers.ValidationError(
                f'Нельзя создать пользователя с именем {data}')
        return data


class UserSerializer(serializers.ModelSerializer, BaseUserSerializer):

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name',
                  'last_name', 'bio', 'role')
        lookup_field = 'username'


class SelfUserSerializer(serializers.ModelSerializer, BaseUserSerializer):

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name',
                  'last_name', 'bio', 'role')
        read_only_fields = ('role',)
        lookup_field = 'username'


class RegisterSerializer(serializers.Serializer, BaseUserSerializer):
    email = serializers.EmailField(max_length=settings.MAX_LENGTH_EMAIL,
                                   required=True)
    username = serializers.CharField(
        max_length=settings.MAX_LENGTH_USERNAME,
        required=True,
        validators=(UnicodeUsernameValidator(),)
    )


class TokenSerializer(serializers.Serializer):
    username = serializers.CharField(
        max_length=settings.MAX_LENGTH_USERNAME,
        required=True,
        validators=(UnicodeUsernameValidator(),)
    )
    confirmation_code = serializers.CharField(
        max_length=settings.MAX_LENGTH_CONFIRMATION_CODE,
        required=True,
    )
