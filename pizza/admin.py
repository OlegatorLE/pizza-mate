from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from pizza.models import CustomUser, Pizza, PizzaSize


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = UserAdmin.list_display + ("phone", "address",)
    fieldsets = UserAdmin.fieldsets + (
        (("Additional Info", {"fields": ("phone", "address",)}),)
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            "Additional Info",
            {
                "fields": ("first_name", "last_name", "phone", "address",)
            }
        )
    )


@admin.register(Pizza)
class PizzaAdmin(admin.ModelAdmin):
    list_display = ("name", "base_price", "size", "user")


@admin.register(PizzaSize)
class PizzaSizeAdmin(admin.ModelAdmin):
    list_display = ("name", "multiplier",)