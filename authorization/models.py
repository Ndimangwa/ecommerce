from django.db import models
from django.contrib.auth.models import AbstractUser
import datetime
from django.db.models.signals import pre_save
from django.dispatch import receiver

# ContextManager
class ContextManager(models.Model):
    defaultXValue = models.BooleanField(unique=True, default=True)
    defaultIfNoRule = models.BooleanField(unique=True, default=True)

# ContextLookup
class ContextLookup(models.Model):
    symbol = models.CharField(max_length=1,null=False, blank=False)
    cvalue = models.CharField(max_length=4, null=False, blank=False, unique=True)
    #A - 0000
    #B - 0001
    #C - 0002
    #D - 0010
    # ....
    #; - 2222

#ContextPosition
class ContextPosition(models.Model):
    cName = models.CharField(max_length=32, null=False, blank=False, unique=True)
    cPosition = models.IntegerField(unique=True)
    caption = models.CharField(max_length=96)
    #(cName, cPosition, caption) = ('delete_product', 17, 'Delete Products')

    def __str__(self):
        return f"{self.cName}"
#=======================================================
#Now Roles
class Roles(models.Model):
    role_name = models.CharField(max_length=64, blank=False, null=False, unique=True)
    context = models.CharField(max_length=255, null=False, blank=False, default=';;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;')
    time_created = models.DateTimeField(auto_now_add=True)
    time_updated = models.DateTimeField(blank=True, null=True)
    # role_name = Admin Roles
    # A collection of policies

    def __str__(self):
        return f"{self.role_name}"
    
    class Meta:
        verbose_name_plural='Roles'

class JobTitle(models.Model):
    job_name = models.CharField(max_length=64, blank=False, null=False, unique=True)
    role = models.ForeignKey(Roles, on_delete=models.CASCADE)
    time_created = models.DateTimeField(auto_now_add=True)
    time_updated = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.job_name}"

class Group(models.Model):
    group_name = models.CharField(max_length=64, blank=False, null=False, unique=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subgroups')
    role = models.ForeignKey(Roles, on_delete=models.CASCADE)
    time_created = models.DateTimeField(auto_now_add=True)
    time_updated = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.group_name}"

#Handling Custom User
class User(AbstractUser):
    """
    I need this class to be a replacement for User
    """
    job_title = models.ForeignKey(JobTitle, on_delete=models.DO_NOTHING, null=True)
    group = models.ForeignKey(Group, on_delete=models.DO_NOTHING, null=True)
    role = models.ForeignKey(Roles, on_delete=models.DO_NOTHING, null=True)
    time_created = models.DateTimeField(auto_now_add=True)
    time_updated = models.DateTimeField(blank=True, null=True)

    class Meta(AbstractUser.Meta):
        swappable = "AUTH_USER_MODEL"


#Working with signals
@receiver(pre_save, sender=Roles)
def roles_set_time_updated(sender, instance, **kwargs):
    if instance.pk:
        # This is an update operation
        now = datetime.datetime.now()
        instance.time_updated = now

@receiver(pre_save, sender=JobTitle)
def jobtitle_set_time_updated(sender, instance, **kwargs):
    if instance.pk:
        #This is an update operation
        now = datetime.datetime.now()
        instance.time_updated = now

@receiver(pre_save, sender=Group)
def group_set_time_updated(sender, instance, **kwargs):
    if instance.pk:
        #This is an update operation
        now = datetime.datetime.now()
        instance.time_updated = now

@receiver(pre_save, sender=User)
def user_set_time_updated(sender, instance, **kwargs):
    if instance.pk:
        #This is an update operation
        now = datetime.datetime.now()
        instance.time_updated = now