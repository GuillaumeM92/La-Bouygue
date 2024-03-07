from django.core.management.base import BaseCommand
from django.core.mail import send_mail

from apps.users.models import MyUser


class Command(BaseCommand):
    help = 'Send an email to all registered users.'

    def handle(self, *args, **options):
        users = MyUser.objects.all()
        user_emails = [user.email for user in users]
        self.stdout.write(self.style.SUCCESS(f'Sending email to {user_emails}'))
        send_mail(
            subject="La Bouygue - Changement d'adresse pour le site web",
            message=(
                "Le site change d'adresse !\n\n"
                "Pour réduire les coûts, le site a été déplacé de labouygue.com vers labouygue.fr\n"
                "Le domaine en '.com' cessera d'être accessible à compter du 12 Avril prochain."
            ),
            from_email=None,
            recipient_list=user_emails,
            fail_silently=True
        )
        self.stdout.write(self.style.SUCCESS('Successfully ran custom command'))
