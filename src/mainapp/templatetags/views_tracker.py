from django import template
from mainapp.models import Views
from ipware import get_client_ip  # Import any necessary modules
from user_agents import parse  # Import the parse function from user_agents

register = template.Library()

@register.simple_tag(takes_context=True)
def record_view(context):
    request = context['request']
    ip_address, _ = get_client_ip(request)
    url = request.path

    # Parse the user agent string from the request headers
    user_agent = request.META.get('HTTP_USER_AGENT')
    parsed_user_agent = parse(user_agent)

    # Extract browser and operating system information
    browser = parsed_user_agent.browser.family
    operationsistem = parsed_user_agent.os.family

    user = request.user if request.user.is_authenticated else None

    # Create a Views object with the user, or with None for anonymous views
    Views.objects.create(
        user=user,
        ip_address=ip_address,
        browser=browser,
        operationsistem=operationsistem,
        region='',  # You can fill this in based on your requirements
        url=url
    )

    return ''
