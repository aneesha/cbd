from django.db import models
from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):

    VIEWER = 'Viewer'
    MODERATOR = 'Moderatior'
    USERTYPE_OPTIONS = (
        (VIEWER, VIEWER),
        (MODERATOR, MODERATOR),
    )
    user_type = models.CharField(max_length=50, choices=USERTYPE_OPTIONS, default=VIEWER)


    # Override the __unicode__() method to return out something meaningful!
    def __unicode__(self):
        return self.user.username

class ProcessedSocialMediaMessage(models.Model):
    postid = models.TextField(blank=True)
    body = models.TextField(blank=True)
    date = models.DateTimeField()
    username = models.TextField(blank=True)
    location = models.TextField(blank=True)

    YES = 'Yes'
    NO = 'No'
    BULLY_OPTIONS = (
		(YES, YES),
		(NO, NO)
		)

    has_bullying = models.CharField(max_length=200, choices=BULLY_OPTIONS, default=YES)

    def __unicode__(self):
        return str(self.postid)

class IncorrectClassification(models.Model):
    user = models.OneToOneField(User)
    post = models.OneToOneField(ProcessedSocialMediaMessage)
    comment = models.TextField(blank=True)

    def __unicode__(self):
        return str(self.id)

class MLCache(models.Model):
    topic_model_json = models.TextField(blank=True)
    topic_model_cyberbullying_json = models.TextField(blank=True)
    affective_counts_json = models.TextField(blank=True)
    affective_counts_cyberbullying_json = models.TextField(blank=True)

    def __unicode__(self):
        return str(self.id)
