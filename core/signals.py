from allauth.socialaccount.signals import social_account_added, pre_social_login
from allauth.account.signals import user_signed_up
from django.dispatch import receiver
from .models import User


@receiver(user_signed_up)
def set_empty_role_on_signup(request, user, **kwargs):
    """
    When a new user signs up (via Google OAuth or regular registration),
    if they have no role set, clear it so they get redirected to set-role page.
    """
    if not user.role:
        user.role = ''
        user.save()