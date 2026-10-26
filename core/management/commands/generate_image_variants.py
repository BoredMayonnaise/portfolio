from django.core.management.base import BaseCommand

from core.models import Photo, PostImage, Project, ProjectImage


IMAGE_MODELS = (Project, Photo, ProjectImage, PostImage)


class Command(BaseCommand):
    help = "Generate responsive WebP variants for all existing site images."

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Regenerate derivatives even when the current set is complete.",
        )

    def handle(self, *args, **options):
        generated = 0
        skipped = 0
        failed = 0

        for model in IMAGE_MODELS:
            for instance in model.objects.exclude(image="").iterator():
                before = instance.image_variants
                metadata = instance.ensure_image_variants(force=options["force"])
                if not metadata:
                    failed += 1
                    self.stderr.write(
                        f"Could not process {model._meta.label} #{instance.pk}: "
                        f"{instance.image.name}"
                    )
                elif options["force"] or metadata != before:
                    generated += 1
                else:
                    skipped += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Generated {generated}, already current {skipped}, failed {failed}."
            )
        )
