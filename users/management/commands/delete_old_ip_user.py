# delete all ips that were not active within the last 24 hours and users who didn't activate their
#accounts within 24 hours after registering
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from users.models import Profile, IP
from datetime import datetime, timedelta
from django.utils import timezone

class Command(BaseCommand):
    def handle(self, *args, **options):

        start_time = timezone.make_aware(datetime.now()-timedelta(days=1), timezone.get_default_timezone())

        old_users = User.objects.filter(profile__last_connection__lte = start_time, is_active = False)
        old_ips = IP.objects.filter(last_connection__lte = start_time)

        N_old_Users = len(old_users)
        N_old_IPs = len(old_ips)

        old_users.delete()
        old_ips.delete()
        
        print(str(datetime.now()))
        print('Successfully deleted all {} old users and {} old IPs'.format(N_old_Users, N_old_IPs))
