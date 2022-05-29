from crypt import methods

from rest_framework.permissions import SAFE_METHODS, BasePermission
from rest_framework.response import Response

from core.models import Batch, Coordinator, Group, Member, Submission


class IsReadOnly(BasePermission):
    def has_permission(self, request, view):
        return bool(request.method in SAFE_METHODS)


class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.method in SAFE_METHODS
            or request.user
            and request.user.is_authenticated
            and request.user.is_superuser
        )


class IsStudentOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.method in SAFE_METHODS
            or request.user
            and request.user.is_authenticated
            and request.user.is_student
        )


class IsStudentOrReadOnlyAndGroupMember(BasePermission):
    def has_permission(self, request, view):
        is_student_or_safe = bool(
            request.method in SAFE_METHODS
            or request.user
            and request.user.is_authenticated
            and request.user.is_student
        )
        if not is_student_or_safe:
            return False

        if not request.method in SAFE_METHODS:
            print("********* ", request.method)
            if request.method == "POST":
                group = None
                try:
                    group = Group.objects.get(id=request.data["group"])
                except KeyError:
                    return False
                except Group.DoesNotExist:
                    return False
                try:
                    Member.objects.get(group=group, member=request.user)
                except Member.DoesNotExist:
                    return False
            if request.method == "DELETE" or request.method == "PUT" or request.method == "PATCH":
                group = None
                try:
                    print(view.kwargs["pk"])
                    submission = Submission.objects.get(id=view.kwargs["pk"])
                    group = submission.group
                except Submission.DoesNotExist:
                    return False
                try:
                    Member.objects.get(group=group, member=request.user)
                except Member.DoesNotExist:
                    return False
        return True


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_superuser)


# class IsStudent(BasePermission):
#     def has_permission(self, request, view):
#         return bool(request.user and request.user.is_authenticated and request.user.is_student)


class IsStudent(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_student)


class HasGroup(BasePermission):
    def has_permission(self, request, view):
        member_student = None
        try:
            member_student = Member.objects.get(member=request.user.username)
        except Member.DoesNotExist:
            return False
        return True


class IsStaff(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)


class IsStaffOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.method in SAFE_METHODS or request.user and request.user.is_authenticated and request.user.is_staff
        )


class IsCoordinatorOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        active_batch = None
        try:
            active_batch = Batch.objects.get(is_active=True)
        except Batch.DoesNotExist:
            pass
        coordinator_history = None
        is_coordinator = False

        if active_batch != None:
            try:
                coordinator_history = Coordinator.objects.get(user=user, batch=active_batch)
            except Coordinator.DoesNotExist:
                pass
        if coordinator_history != None:
            is_coordinator = True
        return bool(
            request.method in SAFE_METHODS
            or request.user
            and request.user.is_authenticated
            and request.user.is_staff
            and is_coordinator
        )


class IsCoordinatorOrStudentReadOnly(BasePermission):
    def has_permission(self, request, view):
        is_student = bool(
            request.method in SAFE_METHODS
            or request.user
            and request.user.is_authenticated
            and request.user.is_student
        )
        if is_student:
            return True

        user = request.user
        active_batch = None
        try:
            active_batch = Batch.objects.get(is_active=True)
        except Batch.DoesNotExist:
            pass

        coordinator_history = None
        is_coordinator = False

        if active_batch != None:
            try:
                coordinator_history = Coordinator.objects.get(user=user, batch=active_batch)
            except Coordinator.DoesNotExist:
                pass
        if coordinator_history != None:
            is_coordinator = True

        return bool(
            request.method in SAFE_METHODS
            or request.user
            and request.user.is_authenticated
            and request.user.is_staff
            and is_coordinator
        )


class PermissionPolicyMixin:
    def check_permissions(self, request):
        try:
            handler = getattr(self, request.method.lower())
        except AttributeError:
            handler = None

        if handler and self.permission_classes_per_method and self.permission_classes_per_method.get(handler.__name__):
            self.permission_classes = self.permission_classes_per_method.get(handler.__name__)

        super().check_permissions(request)
