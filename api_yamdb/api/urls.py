from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (GenreViewSet,
                    TitleViewSet,
                    CategoryViewSet,
                    ReviewViewSet,
                    CommentViewSet,
                    GetTokenUser,
                    UserViewSet,
                    RegisterUser)

router = DefaultRouter()

router.register('genres',
                GenreViewSet,
                basename='genre')
router.register('titles',
                TitleViewSet,
                basename='title')
router.register('categories',
                CategoryViewSet,
                basename='category')
router.register(r'titles/(?P<title_id>\d+)/reviews',
                ReviewViewSet,
                basename='review')
router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comment')
router.register('users', UserViewSet)

urlpatterns = [
    path('v1/', include(router.urls)),
    path('v1/auth/signup/', RegisterUser.as_view()),
    path('v1/auth/token/', GetTokenUser.as_view()),
]
