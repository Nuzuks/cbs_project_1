from django.db import models
from django.conf import settings

# The fix uses djangos own Users model and dicards this custom model completely
class CustomUser(models.Model): 
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=50) # PLAINTEXT PASSWORD!
    is_admin = models.BooleanField(default=False)

    def __str__(self):
        return self.username

class Note(models.Model):
    # THis code works with djangos own user model
    # author = models.ForeignKey(
    #     settings.AUTH_USER_MODEL,
    #     on_delete=models.CASCADE,
    #     null=True,
    #     blank=True
    # )
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=100)
    content = models.TextField() 
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title