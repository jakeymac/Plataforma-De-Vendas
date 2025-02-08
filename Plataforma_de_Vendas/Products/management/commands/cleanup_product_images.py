from datetime import timedelta

import boto3
from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone
from Products.models import InitialProductImage, ProductImage


class Command(BaseCommand):
    help = "Cleanup orphaned images in the S3 bucket"

    def handle(self, *args, **kwargs):
        self.stdout.write("Beginning Product Images Cleanup...")
        self.stdout.write(f"Current date/time: {timezone.now()}")

        s3 = boto3.resource("s3")
        bucket_name = settings.AWS_STORAGE_BUCKET_NAME
        bucket = s3.Bucket(bucket_name)

        # Get all image paths in S3 bucket
        self.stdout.write("Retreiving all image paths in the S3 bucket...")
        s3_images = [
            obj.key
            for obj in bucket.objects.filter(Prefix="product_images/")
            if obj.key != "product_images/"
        ]

        # Get all image paths in the database
        self.stdout.write("Retreiving all image paths in the database...")
        db_images = list(ProductImage.objects.values_list("s3_key", flat=True))

        # Get all initial image paths in the database that are less than 24 hours
        # old - TODO could possibly remove this with the cleanup initial product
        # states and images script
        self.stdout.write("Retreiving all initial image paths in the database...")
        initial_db_images = InitialProductImage.objects.filter(
            created_at__gte=timezone.now() - timedelta(days=1)
        )
        initial_db_images = list(initial_db_images.values_list("s3_key", flat=True))

        # Find orphaned images - this includes images that still exist as files in the
        # S3 bucket but are not in the database, meaning the user has deleted this
        # product image
        self.stdout.write("Finding orphaned images...")
        orphaned_images = [
            image
            for image in s3_images
            if image not in db_images and image not in initial_db_images
        ]

        # Delete orphaned images
        if orphaned_images:
            self.stdout.write("Deleting orphaned images...")
            for image in orphaned_images:
                bucket.Object(image).delete()
                self.stdout.write(f"Deleted {image}")
            self.stdout.write(self.style.SUCCESS("Orphaned images deleted successfully"))
        else:
            self.stdout.write(self.style.SUCCESS("No orphaned images found"))

        self.stdout.write(self.style.SUCCESS("Product Images Cleanup complete"))
