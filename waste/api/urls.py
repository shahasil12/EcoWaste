from django.urls import path
from .views import (
    RegisterView,
    LoginView,
    CompanyLoginView,
    CompanyRegisterView,
    TokenRefreshView,
    CitizenProfileView,
    ReportListCreateView,
    ReportDetailView,
    BinListView,
    PublicCompanyListView,
    RecyclingCenterListView,
    PickupListCreateView,
    CompanyPickupRequestListView,
    LeaderboardView,
    StorageCleanupView,
    AdminLoginView,
    AdminCitizenListView,
    AdminCitizenDetailView,
    AdminCompanyListView,
    AdminCompanyDetailView,
    AdminReportListView,
    AdminReportDetailView,
    CompanyAssignedReportsView,
    CompanyReportDetailView,
    CompanyPickupRequestDetailView,
)

urlpatterns = [
    # ── Auth ──────────────────────────────────────────────────────────────────
    path('auth/register/',         RegisterView.as_view(),        name='api_register'),
    path('auth/login/',            LoginView.as_view(),           name='api_login'),
    path('auth/company-login/',    CompanyLoginView.as_view(),    name='api_company_login'),
    path('auth/company-register/', CompanyRegisterView.as_view(), name='api_company_register'),
    path('auth/token/refresh/',    TokenRefreshView.as_view(),    name='api_token_refresh'),

    # ── Company Portal ────────────────────────────────────────────────────────
    path('companies/reports/', CompanyAssignedReportsView.as_view(), name='api_company_reports'),
    path('companies/reports/<int:pk>/', CompanyReportDetailView.as_view(), name='api_company_report_detail'),
    path('companies/pickups/', CompanyPickupRequestListView.as_view(), name='api_company_pickups'),
    path('companies/pickups/<int:pk>/', CompanyPickupRequestDetailView.as_view(), name='api_company_pickup_detail'),

    # ── Admin App ─────────────────────────────────────────────────────────────
    path('admin/login/', AdminLoginView.as_view(), name='api_admin_login'),
    path('admin/citizens/', AdminCitizenListView.as_view(), name='api_admin_citizens'),
    path('admin/citizens/<int:pk>/', AdminCitizenDetailView.as_view(), name='api_admin_citizen_detail'),
    path('admin/companies/', AdminCompanyListView.as_view(), name='api_admin_companies'),
    path('admin/companies/<int:pk>/', AdminCompanyDetailView.as_view(), name='api_admin_company_detail'),
    path('admin/reports/', AdminReportListView.as_view(), name='api_admin_reports'),
    path('admin/reports/<int:pk>/', AdminReportDetailView.as_view(), name='api_admin_report_detail'),

    # ── Citizen ───────────────────────────────────────────────────────────────
    path('citizen/profile/',     CitizenProfileView.as_view(), name='api_citizen_profile'),

    # ── Reports ───────────────────────────────────────────────────────────────
    path('reports/',             ReportListCreateView.as_view(), name='api_reports'),
    path('reports/<int:pk>/',    ReportDetailView.as_view(),     name='api_report_detail'),

    # ── Pickups ───────────────────────────────────────────────────────────────
    path('pickups/',             PickupListCreateView.as_view(), name='api_pickups'),

    # ── Public ────────────────────────────────────────────────────────────────
    path('bins/',                BinListView.as_view(),              name='api_bins'),
    path('companies/',           PublicCompanyListView.as_view(),    name='api_public_companies'),
    path('recycling-centers/',   RecyclingCenterListView.as_view(), name='api_recycling_centers'),
    path('leaderboard/',         LeaderboardView.as_view(),         name='api_leaderboard'),

    # ── Admin / Cron ──────────────────────────────────────────────────────────
    path('admin/cleanup-storage/', StorageCleanupView.as_view(), name='api_cleanup_storage'),
]

