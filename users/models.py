from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_countries.fields import CountryField
from datetime import date, datetime

class Profile(models.Model):
    occupation_CHOICES = (
        ('s_student','Student'),
        ('u_student','Student (university level)'),
        ('teacher', 'Language teacher'),
        ('u_professor', 'Researcher (linguistics)'),
        ('other','Other'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    #bio = models.TextField(max_length=500, blank=True)
    sex = models.CharField(max_length=1, choices=(('M','M'),('F','F'),), default='M')
    date_of_birth = models.DateField(default=date.today)
    country = CountryField()
    occupation = models.CharField(max_length=30, choices=occupation_CHOICES)
    last_connection = models.DateTimeField(auto_now_add=True)
    n_requests = models.IntegerField(default=100) #number of requests to countdown within 24 hours
    last_query = models.CharField(max_length=100, default='')

class IP(models.Model):
    ip = models.CharField(max_length=100, default='')
    last_connection =  models.DateTimeField(auto_now_add=True)
    n_requests = models.IntegerField(default=50)#number of requests to countdown within 24 hours
    last_query = models.CharField(max_length=100, default='')

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
