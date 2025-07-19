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
from .models import Bin

def home(request):
    return render(request,'index.html')

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
                messages.error(request,"Username already exits")
                return redirect('Citizen')
            citizen = Citizen(
                username = username,
                password = make_password(password),
                phone = phone,
                place = place
            )
            citizen.save()
            messages.success(request,"Registration Success")
            return redirect('citizen')
    else:
        form = UserForm()
        print('failed')
    return render(request,'citizen/citizen.html',{'form':form})

def citizen_logout(request):
    try:
        del request.session['citizen_id']
    except KeyError:
        pass  
    return redirect('citizen_login')  

def citizen_profile(request):
    #
    citizen_id = request.session.get('citizen_id')
    if not citizen_id:
        return redirect('citizen_login')  


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


def citizen_home(request):
    
    citizen_id = request.session.get('citizen_id')
    if not citizen_id:
        return redirect('citizen_login')  

    
    try:
        citizen = Citizen.objects.get(id=citizen_id)
    except Citizen.DoesNotExist:
        return redirect('citizen_login')

    
    total_reports = Report.objects.filter(reported_by=citizen).count()
    pending_reports = Report.objects.filter(reported_by=citizen, status='Pending').count()
    resolved_reports = Report.objects.filter(reported_by=citizen, status='Resolved').count()
    #
    recent_reports = Report.objects.filter(reported_by=citizen).order_by('-created_at')[:5]

    context = {
        'citizen': citizen,
        'total_reports': total_reports,
        'pending_reports': pending_reports,
        'resolved_reports': resolved_reports,
        'recent_reports': recent_reports,
    }
    return render(request, 'citizen/citizen_home.html', context)


def citizen_login(request):
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
        'login_form': Citizen_login(),
        'form': UserForm()
    })


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


def citizen_report(request):
    citizen = Citizen.objects.filter(id=request.user.id).first()
    reports = Report.objects.filter(reported_by=citizen.id) if citizen else []
    return render(request, 'citizen/citizen_reports.html', {'reports': reports, 'citizen': citizen})




def company_login(request):
    error_message = ''
    if request.method == 'POST':
        anu = CompanyLoginForm(request.POST)
        if anu.is_valid():
            name = anu.cleaned_data['name']
            password = anu.cleaned_data['password']
            try:
                company = Company.objects.get(name=name)
            except Company.DoesNotExist:
                company = None

            if company and company.password == password:  
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
            company.password = new_password 
            company.save()
            
            del request.session['reset_email']
            del request.session['reset_otp']
            message = "Your password was reset. You can now log in."
            return render(request, 'company/company_reset_password.html', {'success': True, 'message': message})
        else:
            message = "Invalid OTP."
    return render(request, 'company/company_reset_password.html', {'message': message})


def company_dashboard(request, company_id):
    company = Company.objects.get(id=company_id)
    assigned_reports = Report.objects.filter(assigned_company=company)
    pending_count = assigned_reports.filter(status='Pending').count()
    resolved_count = assigned_reports.filter(status='Resolved').count()
    company_score = resolved_count * 10
    
    context = {
        'company': company,
        'assigned_reports': assigned_reports,
        'pending_count': pending_count,
        'resolved_count': resolved_count,
        'company_score': company_score,  
    }
    return render(request, 'company/dashboard.html', context)



def company_resolve_report(request, report_id):
    company_id = request.session.get('company_id')
    if not company_id:
        return redirect('company_login')

    report = get_object_or_404(Report, id=report_id, assigned_company_id=company_id)

    if request.method == "POST":
        report.status = 'Resolved'
        report.save()
        # Pass company_id to redirect!
        return redirect('company_dashboard', company_id=company_id)

    return render(request, 'company/confirm_resolve.html', {
        'report': report,
        'company_id': company_id,
    })




def bins_json(request):
    bins = list(Bin.objects.values('name', 'latitude', 'longitude', 'address', 'status', 'types'))
    return JsonResponse(bins, safe=False)
