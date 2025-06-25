from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import UserProfile, GestureTest

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'created_at', 'get_total_tests', 'get_avg_confidence', 'get_last_test']
    list_filter = ['created_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at', 'get_total_tests', 'get_avg_confidence', 'get_last_test']
    
    def get_total_tests(self, obj):
        """Get total number of gesture tests for this user"""
        return GestureTest.objects.filter(user=obj.user).count()
    get_total_tests.short_description = 'Total Tests'
    get_total_tests.admin_order_field = 'user'
    
    def get_avg_confidence(self, obj):
        """Get average confidence score for this user"""
        tests = GestureTest.objects.filter(user=obj.user)
        if tests.exists():
            avg = sum(test.confidence for test in tests) / tests.count()
            return f"{avg:.1f}%"
        return "No tests"
    get_avg_confidence.short_description = 'Avg Confidence'
    
    def get_last_test(self, obj):
        """Get the last test performed by this user"""
        last_test = GestureTest.objects.filter(user=obj.user).order_by('-tested_at').first()
        if last_test:
            return f"{last_test.detected_gesture.title()} ({last_test.tested_at.strftime('%Y-%m-%d %H:%M')})"
        return "No tests"
    get_last_test.short_description = 'Last Test'

@admin.register(GestureTest)
class GestureTestAdmin(admin.ModelAdmin):
    list_display = ['user', 'detected_gesture', 'confidence', 'tested_at', 'get_gesture_emoji']
    list_filter = ['detected_gesture', 'tested_at', 'confidence']
    search_fields = ['user__username', 'detected_gesture']
    readonly_fields = ['tested_at']
    date_hierarchy = 'tested_at'
    ordering = ['-tested_at']
    
    def get_gesture_emoji(self, obj):
        """Display emoji for the gesture"""
        emojis = {
            'rock': '🪨',
            'paper': '📄',
            'scissors': '✂️'
        }
        return emojis.get(obj.detected_gesture, '❓')
    get_gesture_emoji.short_description = 'Gesture'
    
    def get_queryset(self, request):
        """Optimize queryset with select_related"""
        return super().get_queryset(request).select_related('user')

# Optional: Custom admin site configuration
admin.site.site_header = "GestureBattle AI Admin"
admin.site.site_title = "GestureBattle AI"
admin.site.index_title = "Welcome to GestureBattle AI Administration"