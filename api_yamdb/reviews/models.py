from django.conf import settings
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class BaseModel(models.Model):
    class Meta:
        abstract = True
        app_label = 'api_yamdb'


class GenreCategoryBaseModel(BaseModel):
    name = models.CharField('Название', max_length=settings.MAX_LENGHT_NAME)
    slug = models.SlugField(max_length=settings.MAX_LENGHT_SLUG,
                            unique=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


class Genre(GenreCategoryBaseModel):
    class Meta:
        ordering = ('name', 'id')
        verbose_name = 'жанр'
        verbose_name_plural = 'Жанры'


class Category(GenreCategoryBaseModel):

    class Meta:
        ordering = ('name', 'id')
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'


class Title(BaseModel):
    name = models.CharField('Название', max_length=settings.MAX_LENGHT_NAME)
    year = models.IntegerField('Год')
    description = models.TextField('Описание',
                                   blank=True,
                                   null=False)
    category = models.ForeignKey(Category,
                                 on_delete=models.SET_NULL,
                                 null=True,
                                 verbose_name='Категория')
    genre = models.ManyToManyField(Genre, through='TitleGenre',
                                   verbose_name='Жанр')

    class Meta:
        default_related_name = 'titles'
        ordering = ('id', 'name')
        verbose_name = 'произведение'
        verbose_name_plural = 'Произведения'

    def __str__(self):
        return self.name


class TitleGenre(models.Model):
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE,
                              verbose_name='Жанр')
    title = models.ForeignKey(Title, on_delete=models.CASCADE,
                              verbose_name='Произведение')

    def __str__(self):
        return f'{self.title} {self.genre}'


class Review(BaseModel):
    title = models.ForeignKey(Title, on_delete=models.CASCADE,
                              verbose_name='Произведение')
    text = models.TextField('Текст')
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               verbose_name='Автор')
    score = models.IntegerField('Оценка')
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)

    class Meta:
        default_related_name = 'reviews'
        constraints = [
            models.UniqueConstraint(fields=['title', 'author'],
                                    name='unique_review')
        ]
        ordering = ('id', 'pub_date')
        verbose_name = 'отзыв'
        verbose_name_plural = 'Отзывы'

    def __str__(self):
        return f'Review by {self.author} on {self.title}'


class Comment(BaseModel):
    review = models.ForeignKey(Review, on_delete=models.CASCADE,
                               verbose_name='Отзыв')
    text = models.TextField('Текст')
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               verbose_name='Автор')
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)

    class Meta:
        default_related_name = 'comments'
        ordering = ('id', 'pub_date')
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return f'Comment by {self.author} on review {self.review.id}'
