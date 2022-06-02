import os
import uuid
from tokenize import group

from django.conf import settings
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.timezone import now
from rest_framework.authtoken.models import Token


# Semister models
class Semister(models.Model):
    class Meta:
        db_table = "semisters"
        unique_together = ["name"]

    name = models.CharField(max_length=200, unique=True)


class Batch(models.Model):
    name = models.CharField(max_length=15, unique=True, primary_key=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


def submission_file_path(instace, filename):
    ext = filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join("uploads/submissions/", filename)


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


class Group(models.Model):
    group_name = models.CharField(max_length=25)
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, related_name="groups")

    class Meta:
        unique_together = ["group_name", "batch"]


class Member(models.Model):
    group = models.ForeignKey(Group, related_name="members", on_delete=models.CASCADE)
    member = models.ForeignKey(User, related_name="members", on_delete=models.CASCADE)

    class Meta:
        unique_together = ["group", "member"]


class Advisor(models.Model):
    group = models.ForeignKey(Group, related_name="advisors", on_delete=models.CASCADE)
    advisor = models.ForeignKey(User, related_name="advisors", on_delete=models.CASCADE)

    class Meta:
        unique_together = ["group", "advisor"]


class Examiner(models.Model):
    group = models.ForeignKey(Group, related_name="examiners", on_delete=models.CASCADE)
    examiner = models.ForeignKey(User, related_name="examiners", on_delete=models.CASCADE)

    class Meta:
        unique_together = ["group", "examiner"]


class SubmissionType(models.Model):
    class Meta:
        db_table = "submission_types"
        unique_together = ["name"]

    name = models.CharField(max_length=200, unique=True, primary_key=True)
    max_mark = models.FloatField(null=True)
    semister = models.ForeignKey(Semister, null=True, related_name="semisters", on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=now, editable=True)
    updated_at = models.DateTimeField(default=now, editable=True)


class SubmissionDeadLine(models.Model):
    name = models.ForeignKey(SubmissionType, on_delete=models.CASCADE, related_name="submission_type_deadline")
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, related_name="submission_deadline_batch")
    dead_line = models.DateTimeField(default=now, editable=True)

    class Meta:
        unique_together = ["name", "batch"]
        db_table = "submission_dead_lines"


class Submission(models.Model):
    group = models.ForeignKey(Group, related_name="submission_group", on_delete=models.CASCADE, null=True)
    submissionType = models.ForeignKey(
        SubmissionType, on_delete=models.CASCADE, related_name="submission_submission_type"
    )
    file = models.FileField(null=True, upload_to=submission_file_path)

    class Meta:
        unique_together = ["group", "submissionType"]


class StudentEvaluation(models.Model):
    class Meta:
        db_table = "student_evalaution"

    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="member_student")
    submission_type = models.ForeignKey(
        SubmissionType, null=True, on_delete=models.CASCADE, related_name="student_evaluation"
    )
    examiner = models.ForeignKey(Examiner, on_delete=models.CASCADE, related_name="student_evaluation")
    comment = models.CharField(null=True, max_length=255)
    mark = models.FloatField(null=True)
    created_at = models.DateTimeField(default=now, editable=True)
    updated_at = models.DateTimeField(default=now, editable=True)


class ProjectTitle(models.Model):
    class STATUS_CHOICES(models.TextChoices):
        APPROVED = "APPROVED"
        PENDING = "PENDING"
        REJECTED = "REJECTED"

    class NO_CHOICES(models.IntegerChoices):
        ONE = 1
        TWO = 2
        THREE = 3

    class Meta:
        db_table = "project_title"
        unique_together = ["group", "no"]

    title_name = models.CharField(max_length=200)
    title_description = models.TextField()
    no = models.IntegerField(choices=NO_CHOICES.choices)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="project_titles")
    rejection_reason = models.CharField(max_length=1000, default=None)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES.choices)


# TopProject model
class TopProject(models.Model):
    title = models.ForeignKey(ProjectTitle, related_name="top_projects_title", on_delete=models.CASCADE, null=True)
    batch = models.ForeignKey(Batch, related_name="top_projects_batch", on_delete=models.CASCADE, null=True)
    group = models.ForeignKey(Group, related_name="top_projects_group", on_delete=models.CASCADE, null=True)
    doc_path = models.CharField(max_length=500, blank=True)
    vote = models.IntegerField(null=True, default=0)
    description = models.CharField(max_length=1000, blank=True)
    is_approved = models.BooleanField(default=False)

    class Meta:
        db_table = "top_projects"
        unique_together = ["batch", "title"]


# Voter models
class Voter(models.Model):
    class Meta:
        db_table = "voters"
        unique_together = [
            "user_id",
        ]

    user_id = models.ForeignKey(User, related_name="voters", on_delete=models.CASCADE)
    project_id = models.ForeignKey(ProjectTitle, related_name="projects", on_delete=models.CASCADE)




class CountModel(models.Model):
    count = models.IntegerField()

class TitleDeadline(models.Model):
    batch = models.ForeignKey(Batch,unique=True ,related_name="title_deadline", on_delete=models.CASCADE)
    deadline = models.DateTimeField(editable=True)
    
###############################Chat################################################
# class Chat(models.Model):
#     name = models.CharField(max_length=100)
#     friends = models.ManyToManyField(User, related_name='friends')
#     created_at = models.DateTimeField(auto_now_add=True)
#     class Meta:
#         db_table = "chats"
#         unique_together = ['name']
         
#     def __str__(self):
#         return self.name

# class Message(models.Model):
#     content = models.CharField(max_length=1000)
#     chat = models.ForeignKey(Chat, related_name='messages', on_delete=models.CASCADE)
#     user = models.ForeignKey(User, related_name='messages', on_delete=models.CASCADE)
#     created_at = models.DateTimeField(auto_now_add=True)
#     class Meta:
#         db_table = "messages"

#     def __str__(self):
#         return self.contact.user.username

class Contact(models.Model):
    user = models.ForeignKey(User, related_name='friends', on_delete=models.CASCADE)
    friends = models.ManyToManyField('self', blank=True)

    def __str__(self):
        return self.user.username


class Message(models.Model):
    contact = models.ForeignKey(Contact, related_name='messages', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.contact.user.username


class Chat(models.Model):
    participants = models.ManyToManyField(Contact, related_name='chats', blank=True)
    messages = models.ManyToManyField(Message, blank=True)

    def __str__(self):
        return "{}".format(self.pk)

