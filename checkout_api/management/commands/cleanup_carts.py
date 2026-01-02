from django.core.management.base import BaseCommand, CommandError
from checkout_api.services import cleanupcarts_service

class Command(BaseCommand):
    help = "Cleans up carts that are abandoned"

    def handle(self, *args, **options):
        count = cleanupcarts_service()

        self.stdout.write(
            self.style.SUCCESS('Successfully deleted "%s" abandoned carts' % count))
        
