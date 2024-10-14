from django.contrib import admin

from .models import Genre, Title, Category, Review, Comment, TitleGenre


class TitleGenreInline(admin.TabularInline):
    model = TitleGenre


class TitleInline(admin.TabularInline):
    model = Title


class TitleAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'year')
    list_filter = ('category', )
    search_fields = ('name', 'category', 'year')
    inlines = [TitleGenreInline]


class GenreCategoryBaseAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name', 'slug')


class CategoryAdmin(GenreCategoryBaseAdmin):
    inlines = [TitleInline]


class GenreAdmin(GenreCategoryBaseAdmin):
    inlines = [TitleGenreInline]


class ReviewAdmin(admin.ModelAdmin):
    list_display = ('title', 'score', 'pub_date')
    list_filter = ('author', 'score')
    search_fields = ('title', 'author')


admin.site.register(Genre, GenreAdmin)
admin.site.register(Title, TitleAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Review, ReviewAdmin)
admin.site.register(Comment)
