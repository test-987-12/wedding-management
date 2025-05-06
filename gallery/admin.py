from django.contrib import admin
from .models import MediaCategory, Media, MediaComment, MediaLike

class MediaCommentInline(admin.TabularInline):
    model = MediaComment
    extra = 0

class MediaLikeInline(admin.TabularInline):
    model = MediaLike
    extra = 0

@admin.register(MediaCategory)
class MediaCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'wedding', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'description', 'wedding__title')

@admin.register(Media)
class MediaAdmin(admin.ModelAdmin):
    list_display = ('title', 'wedding', 'category', 'media_type', 'uploaded_by', 'is_featured', 'is_private', 'upload_date')
    list_filter = ('media_type', 'is_featured', 'is_private', 'upload_date')
    search_fields = ('title', 'description', 'wedding__title')
    date_hierarchy = 'upload_date'
    inlines = [MediaCommentInline, MediaLikeInline]

@admin.register(MediaComment)
class MediaCommentAdmin(admin.ModelAdmin):
    list_display = ('media', 'user', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('media__title', 'user__username', 'comment')

@admin.register(MediaLike)
class MediaLikeAdmin(admin.ModelAdmin):
    list_display = ('media', 'user', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('media__title', 'user__username')
