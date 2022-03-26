from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.timezone import now
from rest_framework.authtoken.models import Token


class Batch(models.Model):
    name = models.CharField(max_length=15, unique=True, primary_key=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class UserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        """Creates and save a new user"""
        if not email:
            raise ValueError("Users must have an email address.")

        user = self.model(username=username, email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, username, email, password=None, **extra_field):
        """Creates and saves a new superuser"""
        user = self.create_user(username, email, password)
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=25, unique=True)
    email = models.EmailField(max_length=255, unique=True, verbose_name="email")
    name = models.CharField(max_length=255, default="")
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_student = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "username"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = ["email"]


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


class Student(models.Model):
    user = models.OneToOneField(User, related_name="students", on_delete=models.CASCADE)
    batch = models.ForeignKey(Batch, related_name="students", on_delete=models.CASCADE)
    first_name = models.CharField(max_length=15, blank=True)
    last_name = models.CharField(max_length=15, blank=True)


class Staff(models.Model):
    user = models.OneToOneField(User, related_name="staff", on_delete=models.CASCADE)
    first_name = models.CharField(max_length=15, blank=True)
    last_name = models.CharField(max_length=15, blank=True)


class Coordinator(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="coordinators")
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, related_name="coordinators")

    class Meta:
        unique_together = ["user", "batch"]


# SubmissionType models
class SubmissionType(models.Model):
    class Meta:
        db_table = "submission_types"

    name = models.CharField(max_length=200)
    created_at = models.DateTimeField(default=now, editable=True)
    updated_at = models.DateTimeField(default=now, editable=True)


# Submission models
class Submission(models.Model):
    class Meta:
        db_table = "submissions"

    status = models.CharField(max_length=100)
    comment = models.CharField(max_length=255)
    sub_type = models.ForeignKey(SubmissionType, on_delete=models.CASCADE)
    group_id = models.ForeignKey(Group, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=now, editable=True)
    updated_at = models.DateTimeField(default=now, editable=True)
class SubmissionDeadLine(models.Model):
    name = models.ForeignKey(SubmissionType, on_delete=models.CASCADE, related_name="SubmissionDeadLines")
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, related_name="SubmissionDeadLines")
    class Meta:
        unique_together = ["name", "batch"]




# Evaluation Models
class Evaluation(models.Model):
    class Meta:
        db_table = "evaluations"

    username = models.ForeignKey(User, on_delete=models.CASCADE)
    mark = models.FloatField()
    comment = models.CharField(max_length=255)
    sub_type = models.ForeignKey(SubmissionType, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=now, editable=True)
    updated_at = models.DateTimeField(default=now, editable=True)


class Title(models.Model):
    class Meta:
        db_table = "titles"

    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(default=now, editable=True)
    updated_at = models.DateTimeField(default=now, editable=True)


class TopProject(models.Model):
    class Meta:
        db_table = "top_projects"

    level = models.IntegerField()
    title_name = models.ForeignKey(Title, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=now, editable=True)
    updated_at = models.DateTimeField(default=now, editable=True)

class Group(models.Model):
    group_name = models.CharField(max_length=25)
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, related_name="groups")

    class Meta:
        unique_together = ["group_name", "batch"]


class Member(models.Model):
    group = models.ForeignKey(Group, related_name="members", on_delete=models.CASCADE)
    member = models.ForeignKey(Student, related_name="members", on_delete=models.CASCADE)
    class Meta:
        unique_together = ["group", "member"]

class Advisor(models.Model):
    group = models.ForeignKey(Group,related_name="advisors", on_delete=models.CASCADE)
    advisor = models.ForeignKey(User, related_name="advisors", on_delete=models.CASCADE)
    class Meta:
        unique_together = ["group", "advisor"]

class Examiner(models.Model):
    group = models.ForeignKey(Group, related_name="examiners", on_delete=models.CASCADE)
    examiner = models.ForeignKey(User, related_name="examiners", on_delete=models.CASCADE)
    class Meta:
        unique_together = ["group", "examiner"]
