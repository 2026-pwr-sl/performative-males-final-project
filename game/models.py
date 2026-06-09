from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Movie(models.Model):
    title = models.CharField(max_length=255)
    poster_url = models.URLField(max_length=500)

    review_5 = models.TextField()
    review_3 = models.TextField()
    # rn im assuming well hold reviews as texts
    review_1 = models.TextField()

    def __str__(self):
        return self.title


class Profile(models.Model):
    # im using the djangos built in authentication User
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    avatar = models.ImageField(
        default="default_pfp.png",
        upload_to="profile_avatrs"
    )

    high_score = models.BigIntegerField(default=0)
    games_played = models.IntegerField(default=0)

    # for endless mode could be deleted if we decide not to use this
    longest_streak = models.IntegerField(default=0)
    current_streak = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.username}'s Profile"


# the below signals ensure a Profile is created automatically
# whenever a User registers
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
