from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import UserProfile, GestureTest
import json
from django.utils import timezone

def home(request):
    return render(request, 'home.html')

@csrf_exempt
def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        # Validation
        if not all([username, email, password, confirm_password]):
            messages.error(request, 'All fields are required.')
            return render(request, 'signup.html')
        
        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'signup.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return render(request, 'signup.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
            return render(request, 'signup.html')
        
        try:
            with transaction.atomic():
                user = User.objects.create_user(username=username, email=email, password=password)
                UserProfile.objects.create(user=user)
                messages.success(request, f'Account created for {username}!')
                # Auto login after signup
                user = authenticate(username=username, password=password)
                if user:
                    login(request, user)
                    return redirect('ai_test')
        except Exception as e:
            messages.error(request, 'Error creating account. Please try again.')
    
    return render(request, 'signup.html')

@csrf_exempt
def signin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if not username or not password:
            messages.error(request, 'Please enter both username and password.')
            return render(request, 'signin.html')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('ai_test')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'signin.html')

def signout(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')

@login_required
def ai_test(request):
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        user_profile = UserProfile.objects.create(user=request.user)
    
    recent_tests = GestureTest.objects.filter(user=request.user).order_by('-tested_at')[:10]
    
    # Calculate user statistics
    total_tests = GestureTest.objects.filter(user=request.user).count()
    avg_confidence = 0
    if total_tests > 0:
        total_confidence = sum([test.confidence for test in GestureTest.objects.filter(user=request.user)])
        avg_confidence = round(total_confidence / total_tests, 1)
    
    gesture_counts = {
        'rock': GestureTest.objects.filter(user=request.user, detected_gesture='rock').count(),
        'paper': GestureTest.objects.filter(user=request.user, detected_gesture='paper').count(),
        'scissors': GestureTest.objects.filter(user=request.user, detected_gesture='scissors').count(),
    }
    
    return render(request, 'ai_test.html', {
        'user_profile': user_profile,
        'recent_tests': recent_tests,
        'total_tests': total_tests,
        'avg_confidence': avg_confidence,
        'gesture_counts': gesture_counts,
    })

@login_required
def profile(request):
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        user_profile = UserProfile.objects.create(user=request.user)
    
    recent_tests = GestureTest.objects.filter(user=request.user).order_by('-tested_at')[:20]
    
    # Enhanced statistics
    total_tests = GestureTest.objects.filter(user=request.user).count()
    avg_confidence = 0
    if total_tests > 0:
        total_confidence = sum([test.confidence for test in GestureTest.objects.filter(user=request.user)])
        avg_confidence = round(total_confidence / total_tests, 1)
    
    gesture_counts = {
        'rock': GestureTest.objects.filter(user=request.user, detected_gesture='rock').count(),
        'paper': GestureTest.objects.filter(user=request.user, detected_gesture='paper').count(),
        'scissors': GestureTest.objects.filter(user=request.user, detected_gesture='scissors').count(),
    }
    
    # Best performance
    best_test = GestureTest.objects.filter(user=request.user).order_by('-confidence').first()
    
    return render(request, 'profile.html', {
        'user_profile': user_profile,
        'recent_tests': recent_tests,
        'total_tests': total_tests,
        'avg_confidence': avg_confidence,
        'gesture_counts': gesture_counts,
        'best_test': best_test,
    })

@csrf_exempt
@login_required
def save_gesture_result(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            gesture = data.get('gesture')
            confidence = data.get('confidence')
            
            if gesture and confidence is not None:
                # Only save high-confidence predictions to avoid spam
                if confidence >= 70:
                    GestureTest.objects.create(
                        user=request.user,
                        detected_gesture=gesture,
                        confidence=confidence
                    )
                    return JsonResponse({'success': True, 'message': 'Gesture saved!'})
                else:
                    return JsonResponse({'success': False, 'error': 'Confidence too low'})
            else:
                return JsonResponse({'success': False, 'error': 'Invalid data'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

# New endpoint for getting live statistics
@csrf_exempt
@login_required
def get_user_stats(request):
    total_tests = GestureTest.objects.filter(user=request.user).count()
    recent_tests = GestureTest.objects.filter(user=request.user).order_by('-tested_at')[:5]
    
    stats = {
        'total_tests': total_tests,
        'recent_tests': [
            {
                'gesture': test.detected_gesture,
                'confidence': test.confidence,
                'time': test.tested_at.strftime('%H:%M:%S')
            } for test in recent_tests
        ]
    }
    
    return JsonResponse(stats)