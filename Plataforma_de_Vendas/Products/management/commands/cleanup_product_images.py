from datetime import timedelta

import boto3
from django.conf import settings
from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from django.utils import timezone
from Products.models import InitialProductImage, ProductImage


class Command(BaseCommand):
    help = "Cleanup orphaned images in the S3 bucket"

    def handle(self, *args, **kwargs):
        self.stdout.write("\nBeginning Product Images Cleanup...")
        self.stdout.write(f"Current date/time: {timezone.now()}")

        try:
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
            self.stdout.write(f"Found {len(s3_images)} images in the S3 bucket")
            self.stdout.write("Images in S3 bucket:")
            for image in s3_images:
                self.stdout.write(f"- {image}")
            self.stdout.write("\n")

            # Get all image paths in the database
            self.stdout.write("Retreiving all image paths in the database...")
            db_images = list(ProductImage.objects.values_list("s3_key", flat=True))
            self.stdout.write(f"Found {len(db_images)} images in the database")
            self.stdout.write("Images in database:")
            for image in db_images:
                self.stdout.write(f"- {image}")
            self.stdout.write("\n")

            # Get all initial image paths in the database that are less than 24 hours
            # old - TODO could possibly remove this with the cleanup initial product
            # states and images script
            self.stdout.write("Retreiving all initial image paths in the database...")
            initial_db_images = InitialProductImage.objects.filter(
                created_at__gte=timezone.now() - timedelta(days=1)
            )
            initial_db_images = list(initial_db_images.values_list("s3_key", flat=True))
            self.stdout.write(f"Found {len(initial_db_images)} initial images in the database")
            self.stdout.write("Initial images in database:")
            for image in initial_db_images:
                self.stdout.write(f"- {image}")
            self.stdout.write("\n")

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
                self.stdout.write(
                    f"Found {len(orphaned_images)} orphaned image(s) in the S3 bucket"
                )
                self.stdout.write("Deleting orphaned images...")
                for image in orphaned_images:
                    bucket.Object(image).delete()
                    self.stdout.write(f"Deleted {image}")
                self.stdout.write(self.style.SUCCESS("Orphaned images deleted successfully"))
            else:
                self.stdout.write(self.style.SUCCESS("No orphaned images found"))

            self.stdout.write(self.style.SUCCESS("Product Images Cleanup complete"))

            # Send email summary
            subject = "S3 Product Image Cleanup Completed"

            s3_images_str = "\n".join(s3_images)
            db_images_str = "\n".join(db_images)
            initial_db_images_str = "\n".join(initial_db_images)
            orphaned_images_str = "\n".join(orphaned_images[:50])

            if orphaned_images:
                message = (
                    f"Cleanup completed at {timezone.now()}.\n"
                    f"Found images in the S3 bucket:\n{s3_images_str}\n"
                    f"Found images in the database:\n{db_images_str}\n"
                    f"Found initial images in the database:\n{initial_db_images_str}\n"
                    f"Deleted {len(orphaned_images)} orphaned image(s).\n\n"
                    f"{orphaned_images_str}"
                )
            else:
                message = (
                    f"Cleanup completed at {timezone.now()}.\n" "No orphaned images were found."
                )
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                settings.IMAGE_CLEANUP_SCRIPT_EMAIL_LIST,
            )

        except Exception as e:
            error_message = f"Cleanup failed at {timezone.now()}.\n\n{str(e)}"
            send_mail(
                "S3 Product Image Cleanup FAILED",
                error_message,
                settings.DEFAULT_FROM_EMAIL,
                settings.IMAGE_CLEANUP_SCRIPT_EMAIL_LIST,
            )
            self.stderr.write(self.style.ERROR("An error occurred during cleanup."))
            raise  # Ensure the exception still bubbles up
