from django.db import models
from django.utils import timezone

class SoftDeleteQuerySet(models.QuerySet):
    def delete(self):
        # bulk soft delete, will work on filter
        return self.update(deleted_at=timezone.now())

    def hard_delete(self):
        return super().delete()

    def undelete(self):
        return self.update(deleted_at=None)

    def alive(self):
        return self.filter(deleted_at__isnull=True)

    def dead(self):
        return self.filter(deleted_at__isnull=False)


class SoftDeleteManager(models.Manager):
    use_for_related_fields = True  # This makes it apply to reverse relationships
    
    def get_queryset(self):
        # shows only non-deleted rows- Default
        return SoftDeleteQuerySet(self.model, using=self._db).alive()

    def with_deleted(self):
        # include deleted and non–deleted
        return SoftDeleteQuerySet(self.model, using=self._db)

    def deleted(self):
        # only deleted
        return self.with_deleted().dead()