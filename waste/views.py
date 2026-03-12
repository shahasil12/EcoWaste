from django.contrib import messages 
from django.shortcuts import redirect, render
from .forms import Citizen_login, ReportForm, UserForm
from .models import Citizen, Report
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password
from .models import Company
from .models import Company
from .forms import CompanyLoginForm
from django.shortcuts import  get_object_or_404
import random
from django.core.mail import send_mail
from django.http import JsonResponse
from .models import Bin, BinReport

def home(request):
    top_citizens = Citizen.objects.order_by('-points')[:5]
    total_bins = Bin.objects.count()
    full_bins = Bin.objects.filter(status='Full').count()
    available_bins = Bin.objects.filter(status='Available').count()
    total_resolved = Report.objects.filter(status='Resolved').count()
    # Mock conversions: Let's assume on average each resolved report handles 5kg of waste
    # and 50kg corresponds to roughly 1 tree saved (just for gamification stats)
    waste_collected_kg = total_resolved * 5
    trees_saved = waste_collected_kg // 50

    return render(request, 'index.html', {
        'top_citizens': top_citizens,
        'total_bins': total_bins,
        'full_bins': full_bins,
        'available_bins': available_bins,
        'total_resolved': total_resolved,
        'waste_collected_kg': waste_collected_kg,
        'trees_saved': trees_saved
    })

def citizen(request):
    login_form = Citizen_login()
    register_form = UserForm()
    return render(request, 'citizen/citizen.html', {
        'login_form': login_form,
        'form': register_form
    })

def register_user(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            phone = form.cleaned_data['phone']
            place = form.cleaned_data['place']

            if Citizen.objects.filter(username=username).exists():
                messages.error(request,"Username already exists")
                return render(request, 'citizen/citizen.html', {'form': form, 'login_form': Citizen_login(), 'active_tab': 'register'})
            
            citizen = Citizen(
                username=username,
                password=make_password(password),
                phone=phone,
                place=place
            )
            citizen.save()
            messages.success(request,"Registration Success")
            return redirect('citizen_login')
        else:
            messages.error(request, "Registration invalid")
            return render(request, 'citizen/citizen.html', {'form': form, 'login_form': Citizen_login(), 'active_tab': 'register'})
    else:
        form = UserForm()
    return render(request, 'citizen/citizen.html', {'form': form, 'login_form': Citizen_login(), 'active_tab': 'register'})

def citizen_logout(request):
    try:
        del request.session['citizen_id']
    except KeyError:
        pass  
    return redirect('citizen_login')  

from .decorators import citizen_required, company_required

@citizen_required
def citizen_profile(request):
    citizen_id = request.session.get('citizen_id')
    try:
        citizen = Citizen.objects.get(id=citizen_id)
    except Citizen.DoesNotExist:
        return redirect('citizen_login')
    
    total_reports = Report.objects.filter(reported_by=citizen).count()
    pending_reports = Report.objects.filter(reported_by=citizen, status='Pending').count()
    resolved_reports = Report.objects.filter(reported_by=citizen, status='Resolved').count()

    context = {
        'citizen': citizen,
        'total_reports': total_reports,
        'pending_reports': pending_reports,
        'resolved_reports': resolved_reports,
    }
    return render(request, 'citizen/profile.html', context)


@citizen_required
def citizen_home(request):
    citizen_id = request.session.get('citizen_id')
    try:
        citizen = Citizen.objects.get(id=citizen_id)
    except Citizen.DoesNotExist:
        return redirect('citizen_login')

    from .models import PickupRequest
    total_reports = Report.objects.filter(reported_by=citizen).count()
    pending_reports = Report.objects.filter(reported_by=citizen, status='Pending').count()
    resolved_reports = Report.objects.filter(reported_by=citizen, status='Resolved').count()
    recent_reports = Report.objects.filter(reported_by=citizen).order_by('-created_at')[:5]
    total_pickups = PickupRequest.objects.filter(citizen=citizen).count()
    eco_points = citizen.points

    context = {
        'citizen': citizen,
        'total_reports': total_reports,
        'pending_reports': pending_reports,
        'resolved_reports': resolved_reports,
        'recent_reports': recent_reports,
        'total_pickups': total_pickups,
        'eco_points': eco_points,
    }
    return render(request, 'citizen/citizen_home.html', context)



def citizen_login(request):
    if request.session.get('citizen_id'):
        return redirect('citizen_home')
    login_form = Citizen_login()
    if request.method == 'POST':
        login_form = Citizen_login(request.POST)
        if login_form.is_valid():
            username = login_form.cleaned_data['username']
            password = login_form.cleaned_data['password']
            try:
                citizen = Citizen.objects.get(username=username)
                if check_password(password, citizen.password):
                    request.session['citizen_id'] = citizen.id
                    return redirect('citizen_home')
                else:
                    messages.error(request, "Incorrect password")
            except Citizen.DoesNotExist:
                messages.error(request, "Username not found")

    return render(request, 'citizen/citizen.html', {
        'login_form': login_form,
        'form': UserForm()
    })


@citizen_required
def citizen_map(request):
    citizen_id = request.session.get('citizen_id')
    citizen = get_object_or_404(Citizen, id=citizen_id)
    return render(request, 'citizen/map.html', {'citizen': citizen})

WASTE_GUIDES = {
    'pizza box': {'category': 'General', 'description': 'Greasy pizza boxes cannot be recycled and should go to general waste.'},
    'battery': {'category': 'E-waste', 'description': 'Batteries contain hazardous materials. Drop them off at specific E-waste recycling centers.'},
    'plastic bottle': {'category': 'Plastic', 'description': 'Empty and rinse plastic bottles before putting them in the plastic recycling bin.'},
    'glass bottle': {'category': 'Glass', 'description': 'Rinse glass bottles. Labels do not need to be removed.'},
    'apple core': {'category': 'Organic', 'description': 'Perfect for composting or the organic waste bin.'},
    'cardboard': {'category': 'General', 'description': 'Clean, dry cardboard can be recycled. Break down boxes before disposal.'},
    'smartphone': {'category': 'E-waste', 'description': 'Smartphones need specialized E-waste recycling to recover precious metals safely.'},
    'aluminum can': {'category': 'Metal', 'description': 'Rinse lightly and crush to save space in the Metal bin.'},
}

def waste_sorting_api(request):
    query = request.GET.get('q', '').lower()
    results = []
    if query:
        for item, details in WASTE_GUIDES.items():
            if query in item:
                results.append({
                    'item': item.title(),
                    'category': details['category'],
                    'description': details['description']
                })
    return JsonResponse({'results': results})

@citizen_required
def citizen_rewards(request):
    citizen_id = request.session.get('citizen_id')
    citizen = get_object_or_404(Citizen, id=citizen_id)
    top_citizens = Citizen.objects.order_by('-points')[:10]
    return render(request, 'citizen/rewards.html', {'citizen': citizen, 'top_citizens': top_citizens})


from django.contrib import messages
from django.shortcuts import render, redirect
from .forms import ReportForm
from .models import Citizen

def report_waste(request):
    if request.method == 'POST':
        waste = ReportForm(request.POST, request.FILES)
        if waste.is_valid():
            new_report = waste.save(commit=False)
            citizen_id = request.session.get('citizen_id')
            if citizen_id is not None:
                try:
                    citizen = Citizen.objects.get(id=citizen_id)
                    new_report.reported_by = citizen
                    new_report.save()
                    messages.success(request, "Report submitted successfully!")
                    return redirect('citizen_home')  # or your desired report/list view name
                except Citizen.DoesNotExist:
                    messages.error(request, "Citizen not found.")
            else:
                messages.error(request, "No citizen in session.")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        waste = ReportForm()
    return render(request, 'citizen/report_waste.html', {'waste': waste})


@citizen_required
def citizen_report(request):
    citizen_id = request.session.get('citizen_id')
    citizen = Citizen.objects.filter(id=citizen_id).first()
    reports = Report.objects.filter(reported_by=citizen) if citizen else []
    return render(request, 'citizen/citizen_reports.html', {'reports': reports, 'citizen': citizen})




def company_login(request):
    error_message = ''
    if request.method == 'POST':
        anu = CompanyLoginForm(request.POST)
        if anu.is_valid():
            name = anu.cleaned_data['name']
            password = anu.cleaned_data['password']
            try:
                company = Company.objects.filter(name=name).first()
                if not company:
                    company = None
            except Exception:
                company = None

            if company and check_password(password, company.password):  
                request.session['company_id'] = company.id
                return redirect('company_dashboard', company_id=company.id)
    
            else:
                error_message = "Invalid company name or password."
    else:
        anu = CompanyLoginForm()

    return render(request, 'company/company_login.html', {'anu': anu, 'error_message': error_message})



def company_logout(request):
    try:
        del request.session['company_id']
    except KeyError:
        pass  
    return redirect('company_login') 



def company_forgot_password(request):
    message = ''
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            company = Company.objects.get(contact_email=email)
            otp = str(random.randint(100000, 999999))
            request.session['reset_email'] = email
            request.session['reset_otp'] = otp
            send_mail(
                subject='Your Ecogreen OTP',
                message=f'Your OTP is: {otp}',
                from_email=None,  
                recipient_list=[email],
            )
            return redirect('company_reset_password')
        except Company.DoesNotExist:
            message = "Email not found."
    return render(request, 'company/company_forgot_password.html', {'message': message})


def company_reset_password(request):
    message = ''
    email = request.session.get('reset_email')
    otp_sent = request.session.get('reset_otp')
    if not (email and otp_sent):
        return redirect('company_forgot_password')
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        new_password = request.POST.get('new_password')
        if entered_otp == otp_sent:
            company = Company.objects.get(contact_email=email)
            company.password = make_password(new_password) 
            company.save()
            
            del request.session['reset_email']
            del request.session['reset_otp']
            message = "Your password was reset. You can now log in."
            return render(request, 'company/company_reset_password.html', {'success': True, 'message': message})
        else:
            message = "Invalid OTP."
    return render(request, 'company/company_reset_password.html', {'message': message})


@company_required
def company_dashboard(request, company_id):
    company = Company.objects.get(id=company_id)
    assigned_reports = Report.objects.filter(assigned_company=company)
    pending_count = assigned_reports.filter(status='Pending').count()
    resolved_count = assigned_reports.filter(status='Resolved').count()
    company_score = resolved_count * 10

    from .models import PickupRequest
    pickup_requests = PickupRequest.objects.filter(preferred_company=company).order_by('-created_at')
    pickup_pending = pickup_requests.filter(status='Pending').count()
    pickup_assigned = pickup_requests.filter(status='Assigned').count()
    pickup_completed = pickup_requests.filter(status='Completed').count()

    context = {
        'company': company,
        'assigned_reports': assigned_reports,
        'pending_count': pending_count,
        'resolved_count': resolved_count,
        'company_score': company_score,
        'pickup_requests': pickup_requests,
        'pickup_pending': pickup_pending,
        'pickup_assigned': pickup_assigned,
        'pickup_completed': pickup_completed,
    }
    return render(request, 'company/dashboard.html', context)



@company_required
def company_resolve_report(request, report_id):
    company_id = request.session.get('company_id')
    report = get_object_or_404(Report, id=report_id, assigned_company_id=company_id)

    if request.method == "POST":
        report.status = 'Resolved'
        report.save()
        
        # Award points to citizen
        if report.reported_by:
            report.reported_by.points += 10
            report.reported_by.save()
            
        # Pass company_id to redirect!
        return redirect('company_dashboard', company_id=company_id)

    return render(request, 'company/confirm_resolve.html', {
        'report': report,
        'company_id': company_id,
    })


@company_required
def company_complete_pickup(request, pickup_id):
    company_id = request.session.get('company_id')
    pickup = get_object_or_404(PickupRequest, id=pickup_id, preferred_company_id=company_id)

    if request.method == "POST":
        pickup.status = 'Completed'
        pickup.save()

        # Award points to citizen (20 points for pickup)
        pickup.citizen.points += 20
        pickup.citizen.save()

        return redirect('company_dashboard', company_id=company_id)

    return render(request, 'company/confirm_complete_pickup.html', {
        'pickup': pickup,
        'company_id': company_id,
    })





def bins_json(request):
    bins = list(Bin.objects.values('name', 'latitude', 'longitude', 'address', 'status', 'types'))
    return JsonResponse(bins, safe=False)

@citizen_required
def report_bin_full(request, bin_id):
    if request.method == 'POST':
        bin_obj = get_object_or_404(Bin, id=bin_id)
        citizen_id = request.session.get('citizen_id')
        citizen = get_object_or_404(Citizen, id=citizen_id)

        # Check if already reported
        if BinReport.objects.filter(bin=bin_obj, reported_by=citizen).exists():
            return JsonResponse({'status': 'error', 'message': 'You have already reported this bin.'}, status=400)

        # Create report
        BinReport.objects.create(bin=bin_obj, reported_by=citizen)
        
        # Update bin count
        bin_obj.full_reports_count += 1
        
        # Automatic status update threshold (3 reports)
        if bin_obj.full_reports_count >= 3:
            bin_obj.status = 'Full'
        
        bin_obj.save()
        
        return JsonResponse({
            'status': 'success', 
            'message': 'Report submitted! Thank you for helping.',
            'reports_count': bin_obj.full_reports_count,
            'bin_status': bin_obj.status
        })
    return JsonResponse({'status': 'error', 'message': 'Invalid request.'}, status=400)



from .forms import PickupRequestForm
from .models import PickupRequest

@citizen_required
def request_pickup(request):
    citizen = Citizen.objects.get(id=request.session.get('citizen_id'))
    if request.method == 'POST':
        form = PickupRequestForm(request.POST)
        if form.is_valid():
            pickup = form.save(commit=False)
            pickup.citizen = citizen
            pickup.save()
            messages.success(request, "Pickup request submitted successfully!")
            return redirect('citizen_pickups')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = PickupRequestForm()
    return render(request, 'citizen/request_pickup.html', {'form': form})

@citizen_required
def citizen_pickups(request):
    citizen = Citizen.objects.get(id=request.session.get('citizen_id'))
    pickups = PickupRequest.objects.filter(citizen=citizen).order_by('-created_at')
    return render(request, 'citizen/pickup_list.html', {'pickups': pickups})

from .forms import WorkerLoginForm
from .models import Worker
from .decorators import worker_required

def worker_login(request):
    error_message = ''
    if request.method == 'POST':
        form = WorkerLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            try:
                worker = Worker.objects.get(username=username)
                if check_password(password, worker.password):
                    request.session['worker_id'] = worker.id
                    return redirect('worker_dashboard')
                else:
                    error_message = "Invalid password."
            except Worker.DoesNotExist:
                error_message = "Worker username not found."
    else:
        form = WorkerLoginForm()
    return render(request, 'worker/worker_login.html', {'form': form, 'error_message': error_message})

def worker_logout(request):
    try:
        del request.session['worker_id']
    except KeyError:
        pass
    return redirect('worker_login')

@worker_required
def worker_dashboard(request):
    worker = Worker.objects.get(id=request.session.get('worker_id'))
    pending_pickups = PickupRequest.objects.filter(status='Pending').order_by('pickup_date')
    
    # Simple Route Optimization: Sort assigned pickups by latitude (North to South) as a heuristic
    assigned_pickups_qs = PickupRequest.objects.filter(assigned_worker=worker, status='Assigned').order_by('pickup_date')
    
    # Attempt to sort them spatially if they have coordinates
    assigned_pickups_list = list(assigned_pickups_qs)
    # Give items without lat/lng a default high value to put them at the end
    assigned_pickups_list.sort(key=lambda p: float(p.latitude) if p.latitude else 999.0)
    
    completed_pickups = PickupRequest.objects.filter(assigned_worker=worker, status='Completed').order_by('-created_at')[:10]
    
    return render(request, 'worker/dashboard.html', {
        'worker': worker,
        'pending_pickups': pending_pickups,
        'assigned_pickups': assigned_pickups_list,
        'completed_pickups': completed_pickups
    })

@worker_required
def claim_pickup(request, pickup_id):
    worker = Worker.objects.get(id=request.session.get('worker_id'))
    pickup = get_object_or_404(PickupRequest, id=pickup_id, status='Pending')
    pickup.status = 'Assigned'
    pickup.assigned_worker = worker
    pickup.save()
    messages.success(request, "Pickup successfully claimed!")
    return redirect('worker_dashboard')

@worker_required
def complete_pickup(request, pickup_id):
    worker = Worker.objects.get(id=request.session.get('worker_id'))
    pickup = get_object_or_404(PickupRequest, id=pickup_id, assigned_worker=worker, status='Assigned')
    pickup.status = 'Completed'
    pickup.save()
    messages.success(request, "Pickup marked as completed!")
    return redirect('worker_dashboard')

from .models import RecyclingCenter

@citizen_required
def recycling_centers(request):
    return render(request, 'citizen/recycling_centers.html')

def recycling_centers_json(request):
    centers = list(RecyclingCenter.objects.values('name', 'address', 'accepted_waste_types', 'contact', 'latitude', 'longitude'))
    return JsonResponse(centers, safe=False)

from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count
from .models import Company, Report

@staff_member_required
def admin_analytics(request):
    total_citizens = Citizen.objects.count()
    total_companies = Company.objects.count()
    total_workers = Worker.objects.count()
    
    # Reports by status
    reports_status = list(Report.objects.values('status').annotate(count=Count('id')))
    
    # Pickups by status
    pickups_status = list(PickupRequest.objects.values('status').annotate(count=Count('id')))
    
    context = {
        'total_citizens': total_citizens,
        'total_companies': total_companies,
        'total_workers': total_workers,
        'reports_status': reports_status,
        'pickups_status': pickups_status
    }
    return render(request, 'admin/analytics_dashboard.html', context)

