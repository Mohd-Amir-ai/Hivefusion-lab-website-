from django.db import models

class ContectForm(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField(null=False)
    message = models.TextField()
    def __str__(self):
        return f'Contect person : {self.name}'

class EmailAlertForUpcomingProduct(models.Model):
    email = models.EmailField(null=False)
    added_at = models.DateTimeField(auto_now_add=True)