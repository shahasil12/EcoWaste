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
    RecyclingCenterListView,
    PickupListCreateView,
    LeaderboardView,
    StorageCleanupView,
)

urlpatterns = [
    # ── Auth ──────────────────────────────────────────────────────────────────
    path('auth/register/',         RegisterView.as_view(),        name='api_register'),
    path('auth/login/',            LoginView.as_view(),           name='api_login'),
    path('auth/company-login/',    CompanyLoginView.as_view(),    name='api_company_login'),
    path('auth/company-register/', CompanyRegisterView.as_view(), name='api_company_register'),
    path('auth/token/refresh/',    TokenRefreshView.as_view(),    name='api_token_refresh'),

    # ── Citizen ───────────────────────────────────────────────────────────────
    path('citizen/profile/',     CitizenProfileView.as_view(), name='api_citizen_profile'),

    # ── Reports ───────────────────────────────────────────────────────────────
    path('reports/',             ReportListCreateView.as_view(), name='api_reports'),
    path('reports/<int:pk>/',    ReportDetailView.as_view(),     name='api_report_detail'),

    # ── Pickups ───────────────────────────────────────────────────────────────
    path('pickups/',             PickupListCreateView.as_view(), name='api_pickups'),

    # ── Public ────────────────────────────────────────────────────────────────
    path('bins/',                BinListView.as_view(),              name='api_bins'),
    path('recycling-centers/',   RecyclingCenterListView.as_view(), name='api_recycling_centers'),
    path('leaderboard/',         LeaderboardView.as_view(),         name='api_leaderboard'),

    # ── Admin / Cron ──────────────────────────────────────────────────────────
    path('admin/cleanup-storage/', StorageCleanupView.as_view(), name='api_cleanup_storage'),
]

