import hashlib

from django.core.management.base import BaseCommand

from wagtail.images import get_image_model


class Command(BaseCommand):
    def handle(self, *args, **options):
        Image = get_image_model()

        for image in Image.objects.filter(file_hash='').iterator():
            self.stdout.write("Hashing image '{}' (id: {})".format(image.title, image.id))

            with image.open_file() as image_file:
                contents = image_file.read()
                image.file_hash = hashlib.sha1(contents).hexdigest()

                # Set file size as well
                image.file_size = len(contents)

            image.save(update_fields=['file_hash', 'file_size'])
