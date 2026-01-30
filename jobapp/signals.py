from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.apps import apps
import logging

logger = logging.getLogger(__name__)

# List of apps to synchronize
SYNC_APPS = ['custom_account', 'jobapp']

def get_model_instances(instance):
    """Helper to get the model class and primary key."""
    return instance.__class__, instance.pk

@receiver(post_save)
def sync_save_to_both(sender, instance, created, **kwargs):
    # Only sync if we are in the primary database (default/mysql)
    # and if the app is in our sync list
    if kwargs.get('raw'):
        return
    
    app_label = sender._meta.app_label
    if app_label not in SYNC_APPS:
        return

    using_db = kwargs.get('using', 'default')
    
    # If saved to default, replicate to sqlite
    if using_db == 'default':
        try:
            # We use save(using='sqlite') to replicate
            # Note: This will trigger the signal again with using='sqlite', 
            # which is why we check using_db == 'default' to avoid recursion.
            instance.save(using='sqlite')
            # logger.info(f"Synchronized SAVE for {sender.__name__} (PK: {instance.pk}) to sqlite")
        except Exception as e:
            # Silent failure to avoid console flooding and server stress
            # logger.error(f"Failed to sync SAVE for {sender.__name__} to sqlite: {e}")
            pass

@receiver(post_delete)
def sync_delete_to_both(sender, instance, **kwargs):
    app_label = sender._meta.app_label
    if app_label not in SYNC_APPS:
        return

    using_db = kwargs.get('using', 'default')
    
    if using_db == 'default':
        try:
            # Try to delete from sqlite as well
            model_class = instance.__class__
            model_class.objects.using('sqlite').filter(pk=instance.pk).delete()
            # logger.info(f"Synchronized DELETE for {sender.__name__} (PK: {instance.pk}) from sqlite")
        except Exception as e:
            # Silent failure
            # logger.error(f"Failed to sync DELETE for {sender.__name__} from sqlite: {e}")
            pass
