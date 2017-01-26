from django.core.cache import cache

from zweb_utils.views import generate_menu_user


def user_menu(request):
    # warning: si se cambia la key, actualizar el invalidador en logout
    key = "user_menu_{}".format(request.user.pk)
    if cache.get(key):
        return cache.get(key)
    else:
        menu = {'user_menu': generate_menu_user(request.user)}
        cache.set(key, menu, 60 * 60 * 24)  # cached for 24 hours
        return menu
