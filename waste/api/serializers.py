from rest_framework import serializers
from waste.models import Citizen, Report, Bin, RecyclingCenter, PickupRequest, Company


# ─── Citizen ──────────────────────────────────────────────────────────────────

class CitizenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Citizen
        fields = ['id', 'username', 'phone', 'place', 'points']
        read_only_fields = ['id', 'points']


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=20)
    password = serializers.CharField(max_length=128, write_only=True)
    phone = serializers.CharField(max_length=30)
    place = serializers.CharField(max_length=20)

    def validate_username(self, value):
        if Citizen.objects.filter(username=value).exists():
            raise serializers.ValidationError('Username already exists.')
        return value

    def validate_phone(self, value):
        if not value.isdigit() or len(value) != 10:
            raise serializers.ValidationError('Enter a valid 10-digit phone number.')
        return value


# ─── Report ───────────────────────────────────────────────────────────────────

class ReportedByCitizenSerializer(serializers.ModelSerializer):
    """Lightweight citizen info embedded in a report response."""
    class Meta:
        model = Citizen
        fields = ['id', 'username']


class ReportSerializer(serializers.ModelSerializer):
    """Read serializer — returns full report detail."""
    reported_by = ReportedByCitizenSerializer(read_only=True)
    assigned_company_name = serializers.SerializerMethodField()

    class Meta:
        model = Report
        fields = [
            'id',
            'reported_by',
            'created_at',
            'place',
            'latitude',
            'longitude',
            'waste_type',
            'fee',
            'image',
            'status',
            'assigned_company',
            'assigned_company_name',
        ]
        read_only_fields = ['id', 'created_at', 'status', 'reported_by']

    def get_assigned_company_name(self, obj):
        return obj.assigned_company.name if obj.assigned_company else None


class ReportCreateSerializer(serializers.ModelSerializer):
    """Write serializer — used when submitting a new report (multipart/form-data)."""

    class Meta:
        model = Report
        fields = [
            'place',
            'latitude',
            'longitude',
            'waste_type',
            'fee',
            'image',
            'assigned_company',
        ]


# ─── Bin ──────────────────────────────────────────────────────────────────────

class BinSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bin
        fields = ['id', 'name', 'latitude', 'longitude', 'address', 'status', 'types']


# ─── Recycling Center ─────────────────────────────────────────────────────────

class RecyclingCenterSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecyclingCenter
        fields = ['id', 'name', 'address', 'accepted_waste_types', 'contact', 'latitude', 'longitude']


# ─── Pickup Request ───────────────────────────────────────────────────────────

class PickupRequestSerializer(serializers.ModelSerializer):
    citizen_username = serializers.SerializerMethodField()
    assigned_worker_username = serializers.SerializerMethodField()

    class Meta:
        model = PickupRequest
        fields = [
            'id',
            'citizen_username',
            'waste_type',
            'address',
            'latitude',
            'longitude',
            'pickup_date',
            'created_at',
            'status',
            'assigned_worker_username',
            'preferred_company',
        ]
        read_only_fields = ['id', 'created_at', 'status', 'citizen_username', 'assigned_worker_username']

    def get_citizen_username(self, obj):
        return obj.citizen.username if obj.citizen else None

    def get_assigned_worker_username(self, obj):
        return obj.assigned_worker.username if obj.assigned_worker else None


class PickupRequestCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PickupRequest
        fields = ['waste_type', 'address', 'latitude', 'longitude', 'pickup_date', 'preferred_company']


# ─── Company ──────────────────────────────────────────────────────────────────

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['id', 'name', 'address', 'contact_email']
        read_only_fields = ['id']


class CompanyRegisterSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    password = serializers.CharField(max_length=100, write_only=True)
    address = serializers.CharField(max_length=200)
    contact_email = serializers.EmailField()

    def validate_name(self, value):
        if Company.objects.filter(name=value).exists():
            raise serializers.ValidationError('Company name already exists.')
        return value

# ─── Admin Update Serializers ───────────────────────────────────────────────────

class AdminCitizenUpdateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=128, write_only=True, required=False)

    class Meta:
        model = Citizen
        fields = ['id', 'username', 'phone', 'place', 'points', 'password']
        read_only_fields = ['id']

    def update(self, instance, validated_data):
        from django.contrib.auth.hashers import make_password
        if 'password' in validated_data and validated_data['password']:
            validated_data['password'] = make_password(validated_data['password'])
        else:
            validated_data.pop('password', None)
        return super().update(instance, validated_data)

class AdminCompanyUpdateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=128, write_only=True, required=False)

    class Meta:
        model = Company
        fields = ['id', 'name', 'address', 'contact_email', 'password']
        read_only_fields = ['id']

    def update(self, instance, validated_data):
        from django.contrib.auth.hashers import make_password
        if 'password' in validated_data and validated_data['password']:
            validated_data['password'] = make_password(validated_data['password'])
        else:
            validated_data.pop('password', None)
        return super().update(instance, validated_data)


