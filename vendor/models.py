from django.db import models
from app_accounts.models import *
from app_accounts.utils import *

# Create your models here.
class Vendor(models.Model):
    user=models.OneToOneField(User, related_name='user', on_delete=models.CASCADE)
    user_profile=models.OneToOneField(UserProfile, related_name='user_profile', on_delete=models.CASCADE)
    vendor_name=models.CharField(max_length=100)
    vendor_license=models.ImageField(upload_to='vendor/license')
    is_approved=models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True)
    modified_at=models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.vendor_name
    
    def save(self, *args, **kwargs):
        if self.pk is not None:
            original=Vendor.objects.get(pk=self.pk)
            if original.is_approved!=self.is_approved:
                mail_template='app_accounts/emails/admin_approval_email.html'
                context={
                    'user':self.user,
                    'is_approved':self.is_approved,
                }
                if self.is_approved==True:
                    mail_subject='Congratulations! Your Restaurant has been approved.'
                    send_notification_email(mail_subject, mail_template, context)
                else:
                    mail_subject='We are Sorry! You are not eligible for publishing your food menu on our marketplace.'
                    send_notification_email(mail_subject, mail_template, context)
        return super(Vendor, self).save(*args, **kwargs)