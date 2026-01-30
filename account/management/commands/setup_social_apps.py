from django.core.management.base import BaseCommand
from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site
from decouple import config

class Command(BaseCommand):
    help = 'Set up social authentication apps for Google and GitHub'

    def handle(self, *args, **options):
        # Get the current site
        site = Site.objects.get_current()
        site_domain = config('SITE_DOMAIN', default='localhost')
        site.domain = site_domain
        site.name = site_domain
        site.save()

        # Google App
        google_client_id = config('GOOGLE_CLIENT_ID', default='')
        google_client_secret = config('GOOGLE_CLIENT_SECRET', default='')

        if google_client_id and google_client_secret:
            google_app, created = SocialApp.objects.get_or_create(
                provider='google',
                defaults={
                    'name': 'Google',
                    'client_id': google_client_id,
                    'secret': google_client_secret,
                }
            )
            if created:
                google_app.sites.add(site)
                self.stdout.write(self.style.SUCCESS('Google social app created'))
            else:
                self.stdout.write(self.style.WARNING('Google social app already exists'))
        else:
            self.stdout.write(self.style.WARNING('Google credentials not found in environment'))

        # GitHub App
        github_client_id = config('GITHUB_CLIENT_ID', default='')
        github_client_secret = config('GITHUB_CLIENT_SECRET', default='')

        if github_client_id and github_client_secret:
            github_app, created = SocialApp.objects.get_or_create(
                provider='github',
                defaults={
                    'name': 'GitHub',
                    'client_id': github_client_id,
                    'secret': github_client_secret,
                }
            )
            if created:
                github_app.sites.add(site)
                self.stdout.write(self.style.SUCCESS('GitHub social app created'))
            else:
                self.stdout.write(self.style.WARNING('GitHub social app already exists'))
        else:
            self.stdout.write(self.style.WARNING('GitHub credentials not found in environment'))
