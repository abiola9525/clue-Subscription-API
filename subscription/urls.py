from django.urls import path
from . import views

urlpatterns = [
    path('subscription/plans/', views.subscription_plans, name='plans'),
    path('subscription/subscribe/<int:plan_id>/', views.subscribe_user, name='subscribe'),
    path('subscription/upgrade/<int:new_plan_id>/', views.upgrade_subscription, name='upgrade-subscription'),
    path('subscription/cancel/', views.cancel_subscription, name='cancel-subscription'),
    path('subscription/active/', views.get_active_subscription, name='active-subscription'),
    path('subscription/history/', views.subscription_history, name='subscription-history'),
]