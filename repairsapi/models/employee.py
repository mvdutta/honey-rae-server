from django.db import models
from django.contrib.auth.models import User


class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    specialty = models.CharField(max_length=155)
    
# create a custom property on a database model with the property decorator:
    @property
    #this is the property that we want on an employee to send back to the client
    def full_name(self):
        return f'{self.user.first_name} {self.user.last_name}'
