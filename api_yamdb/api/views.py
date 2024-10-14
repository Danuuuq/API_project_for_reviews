import uuid

from django.conf import settings
from django.db import IntegrityError
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, permissions, filters, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import (ValidationError, NotFound,
                                       MethodNotAllowed)

from reviews.models import Genre, Title, Category, Review
from users.models import User
from .serializers import (GenreSerializer, TitleSerializer, CategorySerializer,
                          ReviewSerializer, CommentSerializer, UserSerializer,
                          RegisterSerializer, TokenSerializer,
                          SelfUserSerializer)
from .utils import send_code, get_tokens_for_user
from .paginations import DefaultPagination
from .permissions import AdminOnly, SelfUserOnly, AdminModeratorAuthorOnly
from .filters import TitleFilter


class RedocView(TemplateView):
    template_name = 'redoc.html'


class BaseViewSet(viewsets.ModelViewSet):
    pagination_class = DefaultPagination

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [AdminOnly()]


class BaseGenreCategoryVieSet(BaseViewSet):
    lookup_field = 'slug'
    http_method_names = ['get', 'post', 'delete']
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

    def get_permissions(self):
        if self.action == 'retrieve' and self.kwargs['slug'] is not None:
            raise MethodNotAllowed('GET')
        return super().get_permissions()


class GenreViewSet(BaseGenreCategoryVieSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class CategoryViewSet(BaseGenreCategoryVieSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class TitleViewSet(BaseViewSet):
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter
    http_method_names = ['get', 'post', 'patch', 'delete']
    order_by = ('id', 'name')

    def get_queryset(self):
        return (self.queryset.annotate(average_rating=Avg('reviews__score'))
                .order_by('id', 'name'))


class CommentReviewBaseViewSet(viewsets.ModelViewSet):
    permission_classes = (AdminModeratorAuthorOnly,)
    http_method_names = ['get', 'post', 'patch', 'delete']


class ReviewViewSet(CommentReviewBaseViewSet):
    serializer_class = ReviewSerializer

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        return Review.objects.filter(title_id=title_id)

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)
        if Review.objects.filter(title=title,
                                 author=self.request.user).exists():
            raise ValidationError(
                'Вы уже оставляли отзыв на данное произведение.')
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(CommentReviewBaseViewSet):
    serializer_class = CommentSerializer

    def get_review(self):
        """Проверка и возвращение отзыва при его наличии."""
        review_id = self.kwargs.get('review_id')
        title_id = self.kwargs.get('title_id')
        review = get_object_or_404(Review, id=review_id)
        title = get_object_or_404(Title, id=title_id)
        if review.title != title:
            raise NotFound('Данного ревью не существует.')
        return review

    def get_queryset(self):
        review = self.get_review()
        return review.comments.all()

    def perform_create(self, serializer):
        review = self.get_review()
        serializer.save(author=self.request.user,
                        review=review)


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username', )
    permission_classes = (AdminOnly,)
    queryset = User.objects.all()
    lookup_field = 'username'
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_permissions(self):
        if self.request.user.is_anonymous:
            return (permissions.IsAuthenticated(),)
        elif (self.action == 'destroy'
              and self.kwargs['username'] == settings.USER_SELF_IDENTIFIER):
            raise MethodNotAllowed('DELETE')
        elif (self.action in ['retrieve', 'partial_update']
              and self.kwargs['username'] == settings.USER_SELF_IDENTIFIER):
            return (SelfUserOnly(),)
        return super().get_permissions()

    def get_user(self):
        if self.kwargs['username'] == settings.USER_SELF_IDENTIFIER:
            return User.objects.get(username=self.request.user.username)
        return self.get_object()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_user()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_user()
        serializer = self.get_serializer(instance,
                                         data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def get_serializer_class(self):
        if not (self.request.user.is_superuser
                or self.request.user.is_admin):
            return SelfUserSerializer
        return super().get_serializer_class()


class RegisterUser(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user, create = User.objects.get_or_create(
                **serializer.validated_data)
        except IntegrityError:
            UserSerializer(data=request.data).is_valid(
                raise_exception=True)
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
        user.confirmation_code = uuid.uuid4().hex[-16:]
        user.save()
        send_code(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class GetTokenUser(APIView):

    def post(self, request):
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = get_object_or_404(User, username=request.data['username'])
        if request.data['confirmation_code'] == user.confirmation_code:
            token = get_tokens_for_user(user)
            return Response(token, status=status.HTTP_200_OK)
        return Response(
            {'confirmation_code': 'Неправильный код доступа'},
            status=status.HTTP_400_BAD_REQUEST)
