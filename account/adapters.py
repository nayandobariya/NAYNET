from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.models import SocialAccount, SocialApp
from allauth.core.exceptions import ImmediateHttpResponse
from django.contrib.auth import get_user_model
from django.shortcuts import redirect
from django.urls import reverse
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

class CustomAccountAdapter(DefaultAccountAdapter):
    def get_login_redirect_url(self, request):
        return reverse('jobapp:home')

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def get_app(self, request, provider, client_id=None):
        # Prefer database apps over settings apps
        try:
            apps = SocialApp.objects.on_site(request).filter(provider=provider)
            if client_id:
                apps = apps.filter(client_id=client_id)
            if apps.exists():
                app = apps.first()
                if app.client_id and app.secret:
                    return app
        except Exception as e:
            logger.error(f"Error fetching SocialApp from DB: {e}")

        # Fall back to settings
        try:
            fallback_app = super().get_app(request, provider, client_id)
            if fallback_app and fallback_app.client_id and fallback_app.secret:
                return fallback_app
        except Exception:
            pass
        return None

    def on_authentication_error(self, request, provider, error=None, exception=None, extra_context=None):
        logger.error(f"Authentication error with {provider.name if provider else 'unknown'}: {error}, exception: {exception}")
        from django.contrib import messages
        messages.error(request, f"Social authentication failed. Please try again or use another method.")
        raise ImmediateHttpResponse(redirect(reverse('account:login')))

    def pre_social_login(self, request, sociallogin):
        # Auto-connect to existing user with same email
        if sociallogin.is_existing:
            return

        # Try to get email from user object or extra data
        email = sociallogin.user.email
        if not email and 'email' in sociallogin.account.extra_data:
            email = sociallogin.account.extra_data.get('email')
            sociallogin.user.email = email
            
        if email:
            try:
                # Use a case-insensitive lookup
                existing_user = User.objects.get(email__iexact=email)
                sociallogin.connect(request, existing_user)
                logger.info(f"Auto-connected social account for {email}")
            except User.DoesNotExist:
                # For new users, ensure email is stored for auto-signup
                pass
        else:
            # If still no email from social provider, we might need to prompt for it
            # but we've requested it in SCOPE.
            logger.warning(f"No email provided by social provider: {sociallogin.account.provider}")

    def populate_user(self, request, sociallogin, data):
        logger.info(f"Populating user from {sociallogin.account.provider} with data: {data}")
        user = super().populate_user(request, sociallogin, data)
        
        # GitHub specific name handling
        if sociallogin.account.provider == 'github':
            if not user.first_name and data.get('name'):
                name_parts = data['name'].split(' ', 1)
                user.first_name = name_parts[0]
                if len(name_parts) > 1:
                    user.last_name = name_parts[1]
            if not user.email and data.get('email'):
                user.email = data.get('email')

        # Populate name fields from social data for other providers
        if data.get('first_name'):
            user.first_name = data.get('first_name')
        if data.get('last_name'):
            user.last_name = data.get('last_name')
        
        # Ensure role and gender defaults for social signup
        if not user.role:
            user.role = 'employee'
        if not user.gender:
            user.gender = 'M'
            
        return user

    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form=form)
        if not user.role:
            user.role = 'employee'
        if not user.gender:
            user.gender = 'M'
        user.save()
        return user
