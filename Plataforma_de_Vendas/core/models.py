from django.db import models, IntegrityError, transaction
from .helpers import generate_unique_id


class UniqueIDModel(models.Model):
    id = models.CharField(
        max_length=12,
        primary_key=True,
        default=generate_unique_id,
        editable=False,
        unique=True,
    )

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = generate_unique_id()
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
                else:
                    # Handle other IntegrityErrors (like unique constraints on other fields)
                    raise 
                
        raise IntegrityError(f"Could not generate a unique id after {max_attempts} attempts")