from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender='app_accounts.User')
def post_save_create_profile_receiver(sender, instance, created, **kwargs):
    from .models import UserProfile
    if created:
        UserProfile.objects.create(user=instance)
    else:
        profile, created=UserProfile.objects.get_or_create(user=instance)
        if not created:
            profile.save()
        
post_save.connect(post_save_create_profile_receiver, sender='app_accounts.User')