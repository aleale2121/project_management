from tokenize import group

from core.models import Batch, Group, Member, Student, User
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from users.serializers import StudentSerializer, StudentSerializerTwo


class MemberSerializer(serializers.ModelSerializer):
    """Serializer for the batch object"""

    member = StudentSerializerTwo()

    class Meta:
        model = Member
        # fields = ["member"]
        # read_only_fields = ["is_active"]
        fields = "__all__"


class GroupSerializer(serializers.ModelSerializer):
    group_name = serializers.CharField(
        max_length=25,
    )
    group_members = serializers.ListField(child=serializers.CharField(), write_only=True)
    # members = serializers.PrimaryKeyRelatedField(many=True, queryset=Member.objects.all(), default=None)
    members = MemberSerializer(many=True, read_only=True)
    batch = serializers.SlugRelatedField(slug_field="name", queryset=Batch.objects.all())

    class Meta:
        model = Group
        fields = ("group_name", "batch", "members", "group_members")
        read_only_fields = ("batch", "members")
        extra_kwargs = {
            "group_members": {"write_only": True},
        }

    def validate(self, data):
        g_members = data.get("group_members")
        active_batch = None
        try:
            active_batch = Batch.objects.get(is_active=True)
        except Batch.DoesNotExist:
            raise serializers.ValidationError({"error": "currently there is no active batch"})

        current_batch_groups = Group.objects.filter(batch=active_batch)
        print(current_batch_groups)
        print(active_batch)
        for current_batch_group in current_batch_groups:
            group_members_list = Member.objects.filter(group=current_batch_group)
            for group_member in group_members_list:
                for g_member in g_members:
                    if MemberSerializer(group_member).data['member']['username'] == g_member:
                        response = "student with username " + g_member + " cannot join 2 groups"
                        raise serializers.ValidationError(
                            {
                                "error": response,
                            },
                        )

        return super().validate(data)

    def create(self, validated_data):
        members_data = validated_data.pop("group_members")
        active_batch = None
        try:
            active_batch = Batch.objects.get(is_active=True)
        except Batch.DoesNotExist:
            raise serializers.ValidationError({"error": "currently there is no active batch"})
        student_list = []
        for member_data in members_data:
            user = None
            try:
                user = User.objects.get(username=member_data)
                try:
                    student = Student.objects.get(user=user, batch=active_batch)
                    student_list.append(student)
                except Student.DoesNotExist:
                    response = (
                        "student with username " + member_data + " is not registered for the current acadamic year"
                    )
                    raise serializers.ValidationError({"error": response})

            except User.DoesNotExist:
                response = "student with username " + member_data + " not found"
                raise serializers.ValidationError({"error": response})

        group = Group.objects.create(group_name=self.validated_data["group_name"], batch=active_batch)

        for student in student_list:
            Member.objects.create(group=group, member=student)
        return group
