import requests
import json
from django.http import HttpResponse
from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.db import IntegrityError
from django.http import JsonResponse
from datetime import datetime,date
import traceback

# Create your views here.
def index(request):
    return render(request, 'index.html')

import requests
from datetime import date, datetime
from django.http import JsonResponse
import traceback

def holidays_api(request):
    urls_to_try = [
        "https://date.nager.at/api/v3/PublicHolidays/2025/IN",
        "https://date.nager.at/Api/v2/PublicHolidays/2025/IN",
        "https://date.nager.at/Api/v3/PublicHolidays/2025/AT",
    ]
    try:
        resp = None
        for url in urls_to_try:
            try:
                resp = requests.get(url, timeout=10)
                print(f"[holidays_api] GET {url} -> {resp.status_code}")
                resp.raise_for_status()

                try:
                    data = resp.json()
                except ValueError:
                    print(f"[holidays_api] JSON decode failed from {url}: {resp.text[:300]}")
                    continue

                if isinstance(data, list) and data:
                    today = date.today()

                    def parse_date(item):
                        try:
                            return datetime.strptime(item.get('date', ''), '%Y-%m-%d').date()
                        except Exception:
                            return None

                    upcoming = [h for h in data if (d := parse_date(h)) is None or d >= today]
                    upcoming.sort(key=lambda it: parse_date(it) or date.max)
                    return JsonResponse(upcoming, safe=False)

                print(f"[holidays_api] No list data returned from {url}")

            except requests.RequestException as e:
                snippet = ''
                try:
                    snippet = (resp.text or '')[:300] if resp is not None else ''
                except Exception:
                    pass
                print(f"[holidays_api] RequestException for {url}: {e}; snippet: {snippet}")
                continue

        # static fallback
        fallback = [
            {"date": "2025-01-26", "localName": "Republic Day", "name": "Republic Day", "countryCode": "IN"},
            {"date": "2025-03-29", "localName": "Holi", "name": "Holi", "countryCode": "IN"},
            {"date": "2025-08-15", "localName": "Independence Day", "name": "Independence Day", "countryCode": "IN"},
            {"date": "2025-10-02", "localName": "Gandhi Jayanti", "name": "Gandhi Jayanti", "countryCode": "IN"},
            {"date": "2025-12-25", "localName": "Christmas Day", "name": "Christmas Day", "countryCode": "IN"},
        ]
        print("[holidays_api] Returning static fallback after upstream failures.")
        return JsonResponse(fallback, safe=False)

    except Exception as e:
        print(f"[holidays_api] Unexpected error: {e}")
        traceback.print_exc()
        return JsonResponse({'error': 'Internal server error', 'detail': str(e)}, status=502)

def loginp(request):
    if request.method=="POST":
        # handle POST submission here (validate form, authenticate user, etc.)
        username=request.POST['username']
        password=request.POST['password']
        user=authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            if not User.objects.filter(username=username).exists():
                messages.error(request, "Username does not exist. Please register first.")
            else:
                messages.error(request, "Invalid credentials. Please try again.")   
            return redirect('loginp')
    return render(request, 'login.html')
def register(request):
    if request.method=="POST":
        # handle POST submission here (validate form, create user, etc.)
        username=request.POST['username']
        password=request.POST['password']
        repeatpassword=request.POST['repeatpassword']
        email=request.POST['email']
        dob=request.POST['dob']
        if password!=repeatpassword:
            messages.error(request, "Passwords do not match.")
            return redirect('register')
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
            return redirect('register')
        user=User.objects.create_user(username,email,password)
        user.save() 
        messages.success(request, "Account created successfully. Please log in.")
        #send welcome email
        subject = "Welcome to My Website"
        message = f"Hi {user.username}, thank you for registering at our website.\n\nRegards,\nMy Website Team"
        from_email = settings.EMAIL_HOST_USER or settings.DEFAULT_FROM_EMAIL or 'nidhidaniel1993@gmail.com'
        try:
            result = send_mail(subject, message, from_email, [user.email], fail_silently=False)
            if result:
                messages.success(request, "Account created and welcome email sent.")
            else:
                messages.warning(request, "Account created but email was not sent.")
        except Exception as e:
            print(f"Error sending email: {e}")
        return redirect('loginp')

    return render(request, 'signup.html')

def logout_view(request):
    from django.contrib.auth import logout
    username = request.user.username if request.user.is_authenticated else ''
    logout(request)
    return render(request, 'logout.html', {'username': username})
def some_post_view(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)
    try:
        body=request.body.decode('utf-8')
        data=json.loads(body) if body else {}
    except Exception:
        data={'raw_body':body}
    return JsonResponse({'status':'ok','received_data': data})