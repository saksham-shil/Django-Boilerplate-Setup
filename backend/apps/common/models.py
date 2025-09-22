from django.db import models
from .managers import SoftDeleteManager
from django.utils import timezone


class BaseModel(models.Model):
    """
    An abstract base class that provides self-managed "created_at",
    "updated_at", and "deleted_at" fields.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = SoftDeleteManager()  
    all_objects = models.Manager()     

    class Meta:
        abstract = True


    def delete(self, using=None, keep_parents=False):
        #instance level deletes
        self.deleted_at = timezone.now()
        self.save(update_fields=['deleted_at'])

    def hard_delete(self, using=None, keep_parents=False):
        super().delete(using=using, keep_parents=keep_parents)

    def restore(self):
        self.deleted_at = None
        self.save(update_fields=['deleted_at'])