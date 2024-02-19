from django.core.management.base import BaseCommand, CommandError
from ai_manager.models import GetVendor_AIModel
from account_manager.models import Transaction
import asyncio

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("description", nargs=1, type=str)
        parser.add_argument("name", nargs=1, type=str)

    def handle(self, *args, **options):
        # Do stuff
        model = GetVendor_AIModel.objects.all()[0]
        model.add_item_to_database(options["description"][0], options["name"][0])