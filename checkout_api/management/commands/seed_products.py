from django.core.management.base import BaseCommand, CommandError
from checkout_api.services import seedproducts_service

class Command(BaseCommand):
    help = "Creates 10 new products if there aren't any in the database"

    def handle(self, *args, **options):
        seedproducts_service()

        self.stdout.write(
            self.style.SUCCESS('Successfully created 10 example products'))
        
