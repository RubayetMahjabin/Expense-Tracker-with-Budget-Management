from django.core.management.base import BaseCommand
from tracker.models import Category

class Command(BaseCommand):
    help = 'Populates initial categories in the database'

    def handle(self, *args, **kwargs):
        categories = [
            'Food',
            'Utilities',
            'Entertainment',
            'Transportation',
            'Shopping',
            'Healthcare',
            'Education',
            'Other',
        ]
        for category_name in categories:
            Category.objects.create(name=category_name)
        self.stdout.write(self.style.SUCCESS('Successfully populated categories'))
