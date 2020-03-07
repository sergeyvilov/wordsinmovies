from django.db import models
from django.contrib.auth.models import User

# stores users' search history
class HistoryRecords(models.Model):
    query=models.CharField(max_length=30)
    date_added = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.query
