from rest_framework import routers, serializers, viewsets, permissions

from lms.models.base import Person
from lms.models.content import Unit
from lms.models.learning import Participant, Presence, Decision


class UnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unit
        fields = ('id', 'code', 'title', 'order', 'task_type')


class UnitViewSet(viewsets.ModelViewSet):
    queryset = Unit.objects.all().order_by('order')
    serializer_class = UnitSerializer
    permission_classes = [permissions.IsAuthenticated]


class ParticipantSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='campus:participant-detail')

    class Meta:
        model = Participant
        fields = ('url', 'id', 'role', 'state', 'code_repository', 'total_score')


class ParticipantViewSet(viewsets.ModelViewSet):
    queryset = Participant.objects.all().order_by('role', 'person')

    filterset_fields = ('role', 'state', 'code_repository')
    serializer_class = ParticipantSerializer
    permission_classes = [permissions.IsAuthenticated]


class PersonSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='campus:person-detail')

    class Meta:
        model = Person
#        fields = ('url', 'id', 'role', 'state', 'code_repository', 'total_score')


class PersonViewSet(viewsets.ModelViewSet):
    queryset = Person.objects.all().order_by('code')

    serializer_class = PersonSerializer
    permission_classes = [permissions.IsAuthenticated]


class CheckMarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Presence
        fields = ('id', 'unit', 'student', 'state', 'score')


class CheckMarkViewSet(viewsets.ModelViewSet):
    queryset = Presence.objects.all()
    serializer_class = CheckMarkSerializer
    permission_classes = [permissions.IsAuthenticated]


class SubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Decision
        fields = ('id', 'state', 'check_mark', 'text', 'student_comment', 'reviewer', 'score', 'reviewer_comment')


class SubmissionViewSet(viewsets.ModelViewSet):
    queryset = Decision.objects.all()
    serializer_class = SubmissionSerializer
    permission_classes = [permissions.IsAuthenticated]


# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'persons', PersonViewSet)
router.register(r'participants', ParticipantViewSet)
router.register(r'units', UnitViewSet)
router.register(r'checkmarks', CheckMarkViewSet)
router.register(r'submissions', SubmissionViewSet)