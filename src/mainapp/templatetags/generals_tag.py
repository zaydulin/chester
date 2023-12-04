from django import template
from mainapp.models import Pages, GeneralSettings

register = template.Library()

def display_registration_form():
    general_settings = GeneralSettings.objects.first()  # Получите объект GeneralSettings из базы данных
    if general_settings and general_settings.registration == 1:
        return "show_form"
    return "show_message"

@register.simple_tag()
def get_current_name():
    return GeneralSettings.objects.first().name

@register.simple_tag()
def get_current_content():
    return GeneralSettings.objects.first().content

@register.simple_tag()
def get_current_favicon():
    return GeneralSettings.objects.first().favicon.url

@register.simple_tag()
def get_current_logo():
    return GeneralSettings.objects.first().logo.url

@register.simple_tag()
def get_current_logo_light():
    return GeneralSettings.objects.first().logo_light.url

@register.simple_tag()
def get_current_copyright_text():
    return GeneralSettings.objects.first().copyright_text


@register.simple_tag()
def get_pages_footer():
    return Pages.objects.all().order_by('id')

@register.simple_tag()
def get_settings():
    return GeneralSettings.objects.all()