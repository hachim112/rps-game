from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    last_test_at = models.DateTimeField(null=True, blank=True)  # New field
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    def get_total_tests(self):
        """Get total number of gesture tests"""
        return self.user.gesturetest_set.count()
    
    def get_avg_confidence(self):
        """Get average confidence score"""
        tests = self.user.gesturetest_set.all()
        if tests.exists():
            return sum(test.confidence for test in tests) / tests.count()
        return 0
    
    def update_last_test(self):
        """Update the last test timestamp"""
        self.last_test_at = timezone.now()
        self.save()

class GestureTest(models.Model):
    GESTURE_CHOICES = [
        ('rock', 'Rock'),
        ('paper', 'Paper'),
        ('scissors', 'Scissors'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    detected_gesture = models.CharField(max_length=20, choices=GESTURE_CHOICES)
    confidence = models.FloatField()
    tested_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-tested_at']
        indexes = [
            models.Index(fields=['user', '-tested_at']),
            models.Index(fields=['detected_gesture']),
        ]
    
    def __str__(self):
        return f"{self.user.username}: {self.detected_gesture} ({self.confidence:.2f}%)"
    
    def save(self, *args, **kwargs):
        """Update user's last test timestamp when saving a new test"""
        super().save(*args, **kwargs)
        # Update the user's profile last test time
        try:
            profile = self.user.userprofile
            profile.update_last_test()
        except UserProfile.DoesNotExist:
            # Create profile if it doesn't exist
            UserProfile.objects.create(user=self.user, last_test_at=timezone.now())