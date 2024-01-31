from django.contrib import admin
from django.http import HttpResponseRedirect
from .models import *
from django import forms
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from django.urls import reverse
from django.contrib.contenttypes.admin import GenericTabularInline
from django.utils.html import format_html


class BookmarksInline(admin.TabularInline):
    model = Bookmarks
    extra = 1

class ViewsInline(admin.TabularInline):
    model = Views
    extra = 1
    def get_queryset(self, request):
        # Получите текущего пользователя из запроса
        user = request.user

        # Верните queryset, отфильтрованный по текущему пользователю
        return super().get_queryset(request).filter(user=user)


class UserAdmin(admin.ModelAdmin):
    inlines = [ViewsInline, BookmarksInline]


class GeneralSettingsAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Общие настройки', {
            'fields': ['logo', 'logo_light', 'favicon', 'name', 'headerImage', 'content', 'copyright_text', 'registration', 'of_register_message', 'yandex_metrika_link']
        }),
        ('Интеграция интеграция матчей', {
            'fields': ['rapidapi_key_events'],

        }),
        ('Интеграция стримов', {
            'fields': ['rapidapi_key_stream'],

        })
    ]

    def has_add_permission(self, request):
        # Проверяем, есть ли записи в модели GeneralSettings
        if GeneralSettings.objects.exists():
            return False  # Запрещаем создание новых записей
        return True  # Разрешаем создание первой записи

    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        my_urls = [
            path('', self.redirect_to_edit),
        ]
        return my_urls + urls

    def redirect_to_edit(self, request):
        # Перенаправляем на страницу редактирования первой записи,
        # если она существует
        if GeneralSettings.objects.exists():
            url = reverse('admin:mainapp_generalsettings_change', args=[1])
        else:
            # Если записей нет, перенаправляем на страницу создания новой записи
            url = reverse('admin:mainapp_generalsettings_add')
        return HttpResponseRedirect(url)

    class Media:
        js = ('admin/js/custom_admin.js',)
        css = {
            'all': ('admin/css/custom_admin.css',)
        }

class PagesAdminForm(forms.ModelForm):
    description = forms.CharField(label="Описание", widget=CKEditorUploadingWidget())
    class Meta:
        model = Pages
        fields = '__all__'

@admin.register(Pages)
class PagesAdmin(admin.ModelAdmin):
    form = PagesAdminForm
    prepopulated_fields = {"slug": ('name',), }
    fieldsets = [
        ('Ссылка', {
            'fields': ['other_link','picture'],
        }),
        ('Страницы', {
            'fields': ['name', 'description', 'title', 'content', 'slug'],
        })
    ]



@admin.register(Baners)
class BanersAdmin(admin.ModelAdmin):
    list_display = ['slug', 'get_type_display', 'display_baner' ]

    def display_baner(self, obj):
        if obj.baner:
            return format_html('<img src="{}" alt="{}" height="100" />', obj.baner.url, obj.slug)
        return ''
    display_baner.short_description = 'Изображение'

admin.site.register(GeneralSettings, GeneralSettingsAdmin)
admin.site.register(Stopwords)
admin.site.register(User, UserAdmin)
admin.site.register(Messages)

