from .models import Profile
from django.utils.html import format_html
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.contrib import admin
from accounts.models import Profile, PaymentCreditCard
from accounts.forms import CustomUserCreationForm, CustomUserChangeForm

# Register your models here.

User = get_user_model()


class ProfileInline(admin.TabularInline):
    model = Profile
    extra = 0


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2',)
        }),
    )
    model = User
    # inlines = [ProfileInline]

    list_display = ['email', 'username', 'first_name', 'last_name', 'is_staff']


admin.site.register(User, CustomUserAdmin)


class ProfileAdmin(admin.ModelAdmin):
    list_display = ["profile_name", "phone_number",
                    "user_email", "user_type", "email_confirmed", "active"]

    search_fields = ('user__username', 'phone_number', 'user__email',)
    list_filter = ['active', 'email_confirmed', 'user_type']
    list_editable = ['active', 'email_confirmed']
    list_per_page = 20

    def profile_name(self, obj):
        return obj.user.username

    def user_email(self, obj):
        return obj.user.email


admin.site.register(Profile, ProfileAdmin)


class PaymentCreditCardAdmin(admin.ModelAdmin):
    list_display = ["owner", "card_holder", "card_number", "expiration"]
    search_fields = ('owner__username', 'card_holder', 'card_number',)
    list_per_page = 20


admin.site.register(PaymentCreditCard, PaymentCreditCardAdmin)
