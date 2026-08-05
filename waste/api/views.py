"""
EcoWaste REST API — Views (api/v1/)

All endpoints return JSON. Authentication uses JWT Bearer tokens.
The Citizen model (not Django auth.User) is the identity source.
"""
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
import os

from waste.models import Citizen, Report, Bin, RecyclingCenter, PickupRequest, Company
from .serializers import (
    CitizenSerializer,
    RegisterSerializer,
    ReportSerializer,
    ReportCreateSerializer,
    BinSerializer,
    RecyclingCenterSerializer,
    PickupRequestSerializer,
    PickupRequestCreateSerializer,
    CompanySerializer,
    CompanyRegisterSerializer,
    AdminCitizenUpdateSerializer,
    AdminCompanyUpdateSerializer,
)


# ─── Helpers ──────────────────────────────────────────────────────────────────

def get_tokens_for_citizen(citizen):
    """
    Generate a JWT refresh + access token pair for a given Citizen instance.
    We embed citizen_id (not Django user_id) into the token payload.
    """
    refresh = RefreshToken()
    refresh['citizen_id'] = citizen.id
    refresh['username'] = citizen.username
    refresh['role'] = 'citizen'
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

def get_tokens_for_company(company):
    """
    Generate a JWT refresh + access token pair for a given Company instance.
    """
    refresh = RefreshToken()
    refresh['company_id'] = company.id
    refresh['name'] = company.name
    refresh['role'] = 'company'
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

def get_tokens_for_admin(user):
    """
    Generate a JWT refresh + access token pair for a Django Admin/Superuser.
    """
    refresh = RefreshToken()
    refresh['user_id'] = user.id
    refresh['username'] = user.username
    refresh['role'] = 'admin'
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


# ─── Auth ─────────────────────────────────────────────────────────────────────

class RegisterView(APIView):
    """
    POST /api/v1/auth/register/
    Body: { username, password, phone, place }
    Returns: citizen profile + JWT tokens
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        citizen = Citizen.objects.create(
            username=data['username'],
            password=make_password(data['password']),
            phone=data['phone'],
            place=data['place'],
        )
        tokens = get_tokens_for_citizen(citizen)
        return Response(
            {
                'message': 'Registration successful.',
                'citizen': CitizenSerializer(citizen).data,
                **tokens,
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    """
    POST /api/v1/auth/login/
    Body: { username, password }
    Returns: { access, refresh, citizen }
    """
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username', '').strip()
        password = request.data.get('password', '')

        if not username or not password:
            return Response(
                {'error': 'username and password are required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            citizen = Citizen.objects.get(username=username)
        except Citizen.DoesNotExist:
            return Response({'error': 'Username not found.'}, status=status.HTTP_404_NOT_FOUND)

        if not check_password(password, citizen.password):
            return Response({'error': 'Incorrect password.'}, status=status.HTTP_401_UNAUTHORIZED)

        tokens = get_tokens_for_citizen(citizen)
        return Response(
            {
                'message': 'Login successful.',
                'citizen': CitizenSerializer(citizen).data,
                'role': 'citizen',
                **tokens,
            },
            status=status.HTTP_200_OK,
        )


class CompanyLoginView(APIView):
    """
    POST /api/v1/auth/company-login/
    Body: { name, password }
    Returns: { access, refresh, company, role: 'company' }
    """
    permission_classes = [AllowAny]

    def post(self, request):
        name = request.data.get('name', '').strip()
        password = request.data.get('password', '')

        if not name or not password:
            return Response(
                {'error': 'name and password are required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            company = Company.objects.get(name=name)
        except Company.DoesNotExist:
            return Response({'error': 'Company name not found.'}, status=status.HTTP_404_NOT_FOUND)

        if not check_password(password, company.password):
            return Response({'error': 'Incorrect password.'}, status=status.HTTP_401_UNAUTHORIZED)

        tokens = get_tokens_for_company(company)
        return Response(
            {
                'message': 'Login successful.',
                'company': CompanySerializer(company).data,
                'role': 'company',
                **tokens,
            },
            status=status.HTTP_200_OK,
        )


class CompanyRegisterView(APIView):
    """
    POST /api/v1/auth/company-register/
    Body: { name, password, address, contact_email }
    Returns: company profile + JWT tokens
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = CompanyRegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        company = Company.objects.create(
            name=data['name'],
            password=make_password(data['password']),
            address=data['address'],
            contact_email=data['contact_email'],
        )
        tokens = get_tokens_for_company(company)
        return Response(
            {
                'message': 'Registration successful.',
                'company': CompanySerializer(company).data,
                'role': 'company',
                **tokens,
            },
            status=status.HTTP_201_CREATED,
        )


class AdminLoginView(APIView):
    """
    POST /api/v1/admin/login/
    Body: { username, password }
    """
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        user = authenticate(username=username, password=password)
        if user is not None and user.is_superuser:
            tokens = get_tokens_for_admin(user)
            return Response({
                'message': 'Admin login successful.',
                'role': 'admin',
                'username': user.username,
                **tokens,
            }, status=status.HTTP_200_OK)
        return Response({'error': 'Invalid admin credentials.'}, status=status.HTTP_401_UNAUTHORIZED)


class TokenRefreshView(APIView):
    """
    POST /api/v1/auth/token/refresh/
    Body: { refresh }
    Returns: { access }
    Allows Flutter app to silently get a new access token without re-login.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response({'error': 'refresh token is required.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            refresh = RefreshToken(refresh_token)
            return Response({'access': str(refresh.access_token)}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_401_UNAUTHORIZED)


# ─── Citizen Profile ──────────────────────────────────────────────────────────

class CitizenProfileView(APIView):
    """
    GET /api/v1/citizen/profile/
    Returns the logged-in citizen's profile and stats.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        citizen = request.user  # Set by CitizenJWTAuthentication
        total_reports = Report.objects.filter(reported_by=citizen).count()
        pending_reports = Report.objects.filter(reported_by=citizen, status='Pending').count()
        resolved_reports = Report.objects.filter(reported_by=citizen, status='Resolved').count()

        data = CitizenSerializer(citizen).data
        data.update({
            'total_reports': total_reports,
            'pending_reports': pending_reports,
            'resolved_reports': resolved_reports,
        })
        return Response(data)


# ─── Reports ──────────────────────────────────────────────────────────────────

class ReportListCreateView(APIView):
    """
    GET  /api/v1/reports/  → list my reports (newest first)
    POST /api/v1/reports/  → submit a new waste report (multipart/form-data with image)
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        citizen = request.user
        reports = Report.objects.filter(reported_by=citizen).order_by('-created_at')
        serializer = ReportSerializer(reports, many=True, context={'request': request})
        return Response(serializer.data)

    def post(self, request):
        citizen = request.user
        serializer = ReportCreateSerializer(data=request.data, context={'request': request})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        report = serializer.save(reported_by=citizen)

        # Award 5 points for submitting a report
        citizen.points += 5
        citizen.save()

        return Response(
            ReportSerializer(report, context={'request': request}).data,
            status=status.HTTP_201_CREATED,
        )


class ReportDetailView(APIView):
    """
    GET /api/v1/reports/<id>/
    Returns a single report. Citizens can only view their own reports.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            report = Report.objects.get(id=pk, reported_by=request.user)
        except Report.DoesNotExist:
            return Response({'error': 'Report not found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = ReportSerializer(report, context={'request': request})
        return Response(serializer.data)


# ─── Bins ─────────────────────────────────────────────────────────────────────

class BinListView(APIView):
    """
    GET /api/v1/bins/
    Public. Returns all bins with location data for the Flutter map screen.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        bins = Bin.objects.all()
        serializer = BinSerializer(bins, many=True)
        return Response(serializer.data)

class PublicCompanyListView(APIView):
    """
    GET /api/v1/companies/
    Public. Returns all companies so citizens/admins can select them.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        companies = Company.objects.all()
        serializer = CompanySerializer(companies, many=True)
        return Response(serializer.data)


# ─── Recycling Centers ────────────────────────────────────────────────────────

class RecyclingCenterListView(APIView):
    """
    GET /api/v1/recycling-centers/
    Public. Returns all recycling centers for the Flutter map/list screen.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        centers = RecyclingCenter.objects.all()
        serializer = RecyclingCenterSerializer(centers, many=True)
        return Response(serializer.data)


# ─── Pickup Requests ──────────────────────────────────────────────────────────

class PickupListCreateView(APIView):
    """
    GET  /api/v1/pickups/  → list my pickup requests
    POST /api/v1/pickups/  → create a new pickup request
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        pickups = PickupRequest.objects.filter(citizen=request.user).order_by('-created_at')
        serializer = PickupRequestSerializer(pickups, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = PickupRequestCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        pickup = serializer.save(citizen=request.user)
        return Response(PickupRequestSerializer(pickup).data, status=status.HTTP_201_CREATED)


# ─── Leaderboard ──────────────────────────────────────────────────────────────

class LeaderboardView(APIView):
    """
    GET /api/v1/leaderboard/
    Public. Returns top 10 citizens by eco points.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        top_citizens = Citizen.objects.order_by('-points')[:10]
        serializer = CitizenSerializer(top_citizens, many=True)
        return Response(serializer.data)


# ─── Storage Cleanup (Cron Endpoint) ────────────────────────────────────────────────

class StorageCleanupView(APIView):
    """
    POST /api/v1/admin/cleanup-storage/
    Protected by a secret key in the Authorization header.
    Called by Vercel Cron daily to auto-delete old images when > 50MB.

    Set CLEANUP_SECRET env var in Vercel. The cron sends:
      Authorization: Bearer <CLEANUP_SECRET>
    """
    permission_classes = [AllowAny]

    def post(self, request):
        # Simple secret-key auth for cron — no JWT needed
        secret = os.environ.get('CLEANUP_SECRET', '')
        auth_header = request.headers.get('Authorization', '')
        provided = auth_header.replace('Bearer ', '').strip()

        if not secret or provided != secret:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            from waste.management.commands.cleanup_storage import run_cleanup
            stats = run_cleanup(dry_run=False, verbose=False)
            return Response(stats, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# ─── Admin Endpoints ──────────────────────────────────────────────────────────

from .permissions import IsAdminRole

class AdminCitizenListView(APIView):
    permission_classes = [IsAuthenticated, IsAdminRole]

    def get(self, request):
        citizens = Citizen.objects.all().order_by('-id')
        return Response(CitizenSerializer(citizens, many=True).data)

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            citizen = Citizen.objects.create(
                username=data['username'],
                password=make_password(data['password']),
                phone=data['phone'],
                place=data['place'],
            )
            return Response(CitizenSerializer(citizen).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AdminCitizenDetailView(APIView):
    permission_classes = [IsAuthenticated, IsAdminRole]

    def delete(self, request, pk):
        try:
            citizen = Citizen.objects.get(pk=pk)
            citizen.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Citizen.DoesNotExist:
            return Response({'error': 'Citizen not found'}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk):
        try:
            citizen = Citizen.objects.get(pk=pk)
        except Citizen.DoesNotExist:
            return Response({'error': 'Citizen not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = AdminCitizenUpdateSerializer(citizen, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AdminCompanyListView(APIView):
    permission_classes = [IsAuthenticated, IsAdminRole]

    def get(self, request):
        companies = Company.objects.all().order_by('-id')
        return Response(CompanySerializer(companies, many=True).data)

    def post(self, request):
        serializer = CompanyRegisterSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            company = Company.objects.create(
                name=data['name'],
                password=make_password(data['password']),
                address=data['address'],
                contact_email=data['contact_email'],
            )
            return Response(CompanySerializer(company).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AdminCompanyDetailView(APIView):
    permission_classes = [IsAuthenticated, IsAdminRole]

    def delete(self, request, pk):
        try:
            company = Company.objects.get(pk=pk)
            company.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Company.DoesNotExist:
            return Response({'error': 'Company not found'}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk):
        try:
            company = Company.objects.get(pk=pk)
        except Company.DoesNotExist:
            return Response({'error': 'Company not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = AdminCompanyUpdateSerializer(company, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AdminReportListView(APIView):
    permission_classes = [IsAuthenticated, IsAdminRole]

    def get(self, request):
        reports = Report.objects.all().order_by('-id')
        return Response(ReportSerializer(reports, many=True).data)

class AdminReportDetailView(APIView):
    permission_classes = [IsAuthenticated, IsAdminRole]

    def delete(self, request, pk):
        try:
            report = Report.objects.get(pk=pk)
            report.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Report.DoesNotExist:
            return Response({'error': 'Report not found'}, status=status.HTTP_404_NOT_FOUND)
            
    def patch(self, request, pk):
        try:
            report = Report.objects.get(pk=pk)
        except Report.DoesNotExist:
            return Response({'error': 'Report not found'}, status=status.HTTP_404_NOT_FOUND)
        
        company_id = request.data.get('assigned_company')
        if company_id:
            try:
                company = Company.objects.get(pk=company_id)
                report.assigned_company = company
            except Company.DoesNotExist:
                return Response({'error': 'Company not found'}, status=status.HTTP_404_NOT_FOUND)
                
        status_val = request.data.get('status')
        if status_val:
            if status_val in dict(Report.STATUS_CHOICES).keys():
                report.status = status_val
            else:
                return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)
                
        report.save()
        return Response(ReportSerializer(report).data)

class AdminBinListView(APIView):
    permission_classes = [IsAuthenticated, IsAdminRole]

    def get(self, request):
        bins = Bin.objects.all().order_by('-id')
        return Response(BinSerializer(bins, many=True).data)

    def post(self, request):
        serializer = BinSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AdminBinDetailView(APIView):
    permission_classes = [IsAuthenticated, IsAdminRole]

    def delete(self, request, pk):
        try:
            bin_obj = Bin.objects.get(pk=pk)
            bin_obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Bin.DoesNotExist:
            return Response({'error': 'Bin not found'}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk):
        try:
            bin_obj = Bin.objects.get(pk=pk)
        except Bin.DoesNotExist:
            return Response({'error': 'Bin not found'}, status=status.HTTP_404_NOT_FOUND)
            
        serializer = BinSerializer(bin_obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ─── Company Portal ───────────────────────────────────────────────────────────

from .permissions import IsCompanyRole

class CompanyAssignedReportsView(APIView):
    permission_classes = [IsAuthenticated, IsCompanyRole]

    def get(self, request):
        company_id = request.auth.get('company_id')
        reports = Report.objects.filter(assigned_company_id=company_id).order_by('-created_at')
        return Response(ReportSerializer(reports, many=True).data)

class CompanyReportDetailView(APIView):
    permission_classes = [IsAuthenticated, IsCompanyRole]

    def patch(self, request, pk):
        company_id = request.auth.get('company_id')
        try:
            report = Report.objects.get(pk=pk, assigned_company_id=company_id)
        except Report.DoesNotExist:
            return Response({'error': 'Report not found or not assigned to you'}, status=status.HTTP_404_NOT_FOUND)
        
        status_val = request.data.get('status')
        if status_val in dict(Report.STATUS_CHOICES).keys():
            report.status = status_val
            report.save()
            return Response(ReportSerializer(report).data)
        return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)

class CompanyPickupRequestListView(APIView):
    permission_classes = [IsAuthenticated, IsCompanyRole]

    def get(self, request):
        company_id = request.auth.get('company_id')
        pickups = PickupRequest.objects.filter(preferred_company_id=company_id).order_by('-created_at')
        return Response(PickupRequestSerializer(pickups, many=True).data)

class CompanyPickupRequestDetailView(APIView):
    permission_classes = [IsAuthenticated, IsCompanyRole]

    def patch(self, request, pk):
        company_id = request.auth.get('company_id')
        try:
            pickup = PickupRequest.objects.get(pk=pk, preferred_company_id=company_id)
        except PickupRequest.DoesNotExist:
            return Response({'error': 'Pickup request not found or not assigned to you'}, status=status.HTTP_404_NOT_FOUND)
        
        status_val = request.data.get('status')
        if status_val in dict(PickupRequest.STATUS_CHOICES).keys():
            pickup.status = status_val
            pickup.save()
            return Response(PickupRequestSerializer(pickup).data)
        return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)
