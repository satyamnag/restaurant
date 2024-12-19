from django.db import models
from app_accounts.models import *
from app_accounts.utils import *
from datetime import time, date, datetime

# Create your models here.
class Vendor(models.Model):
    user=models.OneToOneField(User, related_name='user', on_delete=models.CASCADE)
    user_profile=models.OneToOneField(UserProfile, related_name='user_profile', on_delete=models.CASCADE)
    vendor_name=models.CharField(max_length=100)
    vendor_slug=models.SlugField(max_length=100, unique=True)
    vendor_license=models.ImageField(upload_to='vendor/license')
    is_approved=models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True)
    modified_at=models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.vendor_name
    
    def is_open(self):
        # today opening hours
        today_date=date.today()
        today=today_date.isoweekday()
        today_opening_hours=OpeningHour.objects.filter(vendor=self, day=today)
        current_time=datetime.now().strftime('%H:%M:%S')
        datetime_current_time=datetime.strptime(current_time, '%H:%M:%S').time()

        for today_opening_hour in today_opening_hours:
            if today_opening_hour.from_hour and today_opening_hour.to_hour:
                if not today_opening_hour.is_closed:
                    start = datetime.strptime(today_opening_hour.from_hour, '%I:%M %p').time()
                    end = datetime.strptime(today_opening_hour.to_hour, '%I:%M %p').time()
                    if datetime_current_time>start and datetime_current_time<end:
                        is_open=True
                    else:
                        is_open=False
            else:
                is_open=False
        return is_open

        
    def save(self, *args, **kwargs):
        if self.pk is not None:
            original=Vendor.objects.get(pk=self.pk)
            if original.is_approved!=self.is_approved:
                mail_template='app_accounts/emails/admin_approval_email.html'
                context={
                    'user':self.user,
                    'is_approved':self.is_approved,
                    'to_email':self.user.email,
                }
                if self.is_approved==True:
                    mail_subject='Congratulations! Your Restaurant has been approved.'
                    send_notification_email(mail_subject, mail_template, context)
                else:
                    mail_subject='We are Sorry! You are not eligible for publishing your food menu on our marketplace.'
                    send_notification_email(mail_subject, mail_template, context)
        return super(Vendor, self).save(*args, **kwargs)
    
DAYS=[
    (1,('Monday')),
    (2,('Tuesday')),
    (3,('Wednesday')),
    (4,('Thursday')),
    (5,('Friday')),
    (6,('Saturday')),
    (7,('Sunday')),
]

HOUR_OF_DAY_24=[(time(h,m).strftime('%I:%M %p'),time(h,m).strftime('%I:%M %p')) for h in range(0,24) for m in (0,30)]
class OpeningHour(models.Model):
    vendor=models.ForeignKey(Vendor, on_delete=models.CASCADE)
    day=models.IntegerField(choices=DAYS)
    from_hour=models.CharField(choices=HOUR_OF_DAY_24, max_length=10, blank=True)
    to_hour=models.CharField(choices=HOUR_OF_DAY_24, max_length=10, blank=True)
    is_closed=models.BooleanField(default=False)

    class Meta:
        ordering=('day', '-from_hour')
        unique_together=('vendor','day', 'from_hour', 'to_hour')

    def __str__(self):
        return self.get_day_display()
