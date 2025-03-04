from django.db import IntegrityError, models, transaction
from nanoid import generate


def generate_unique_id():
    return generate(size=12)


# Create your models here.
class Store(models.Model):
    id = models.CharField(
        max_length=12,
        primary_key=True,
        default=generate_unique_id,
        editable=False,
        unique=True,
    )
    store_name = models.CharField(max_length=255)
    store_description = models.TextField()
    store_url = models.CharField(max_length=75)
    contact_email = models.EmailField(null=True, blank=True)
    store_logo = models.ImageField(upload_to="store_logos/", null=True, blank=True)

    created_on = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Prevent infinite loops
        attempts = 0
        max_attempts = 5
        while attempts < max_attempts:
            try:
                with transaction.atomic():
                    super().save(*args, **kwargs)
                return

            except IntegrityError as e:
                if "id" in str(e):
                    self.id = generate_unique_id()
                    attempts += 1

        raise IntegrityError(f"Could not generate a unique id after {max_attempts} attempts")

    def __str__(self):
        return self.store_name
