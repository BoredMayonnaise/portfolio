from django.core.management.base import BaseCommand

from core.models import Photo


class Command(BaseCommand):
    """Recompute real SHA-256 hashes for all photos with an image file."""

    help = "Backfill real image hashes for Photo records."

    def handle(self, *args, **options):
        updated = 0
        cleared = 0
        for photo in Photo.objects.all():
            before = photo.image.name
            photo.save()
            if photo.image.name != before:
                updated += 1
            elif photo.hash and not photo.image:
                photo.hash = ""
                photo.save(update_fields=["hash"])
                cleared += 1
        self.stdout.write(
            self.style.SUCCESS(
                f"Updated {updated} photo(s), cleared {cleared} hash(es) without an image."
            )
        )
