from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.utils import timezone
from .models import SubscriptionPlan, UserSubscription
from .serializers import SubscriptionPlanSerializer, UserSubscriptionSerializer
from django.db.models import Q

@swagger_auto_schema(
    method='post',
    request_body=SubscriptionPlanSerializer,
    responses={201: SubscriptionPlanSerializer, 400: 'Bad Request'},
    operation_description="Create a new subscription plan (admin use case)."
)
@swagger_auto_schema(
    method='get',
    responses={200: SubscriptionPlanSerializer(many=True)},
    operation_description="List all active subscription plans."
)
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticatedOrReadOnly])
def subscription_plans(request):
    """
    GET: List all active subscription plans
    POST: Create a new subscription plan (admin use case)
    """
    if request.method == 'GET':
        plans = SubscriptionPlan.objects.filter(is_active=True).order_by('price')
        serializer = SubscriptionPlanSerializer(plans, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = SubscriptionPlanSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='post',
    manual_parameters=[
        openapi.Parameter('plan_id', openapi.IN_PATH, description="ID of the subscription plan", type=openapi.TYPE_INTEGER)
    ],
    responses={201: UserSubscriptionSerializer, 404: 'Plan not found'},
    operation_description="Subscribe the user to the selected plan. Cancels any existing active subscription."
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def subscribe_user(request, plan_id):
    """
    Subscribes the user to a selected plan.
    - Prevents subscribing if the user already has an active subscription (same or different plan).
    """
    try:
        plan = SubscriptionPlan.objects.get(id=plan_id, is_active=True)
    except SubscriptionPlan.DoesNotExist:
        return Response({"error": "Plan does not exist."}, status=status.HTTP_404_NOT_FOUND)

    # Check for any active subscription
    active_subscription = UserSubscription.objects.filter(user=request.user, is_active=True).first()
    if active_subscription:
        return Response(
            {"message": "You already have an active subscription. Please cancel it before subscribing to a new plan."},
            status=status.HTTP_400_BAD_REQUEST
        )

    now = timezone.now()
    end_date = now + timezone.timedelta(days=plan.duration_days)

    subscription = UserSubscription.objects.create(
        user=request.user,
        plan=plan,
        start_date=now,
        end_date=end_date,
        is_active=True
    )

    serializer = UserSubscriptionSerializer(subscription)
    return Response(serializer.data, status=status.HTTP_201_CREATED)

@swagger_auto_schema(
    method='get',
    responses={200: UserSubscriptionSerializer},
    operation_description="Retrieve the user's currently active subscription."
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_active_subscription(request):
    """
    Retrieves the current active subscription of a user.
    """
    subscription = UserSubscription.objects.select_related('plan').filter(
        user=request.user,
        is_active=True
    ).first()

    if not subscription:
        return Response({"message": "No active subscription."}, status=status.HTTP_200_OK)

    serializer = UserSubscriptionSerializer(subscription)
    return Response(serializer.data)


@swagger_auto_schema(
    method='get',
    responses={200: UserSubscriptionSerializer(many=True)},
    operation_description="Get the full subscription history for the authenticated user."
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def subscription_history(request):
    """
    Returns the full subscription history of the authenticated user.
    """
    history = UserSubscription.objects.select_related('plan').filter(user=request.user)
    serializer = UserSubscriptionSerializer(history, many=True)
    return Response(serializer.data)



@swagger_auto_schema(
    method='post',
    manual_parameters=[
        openapi.Parameter(
            'new_plan_id',
            openapi.IN_PATH,
            description="ID of the new subscription plan to upgrade to",
            type=openapi.TYPE_INTEGER,
            required=True
        )
    ],
    responses={
        201: UserSubscriptionSerializer,
        400: 'New plan must be higher than the current one.',
        404: 'New plan does not exist.'
    },
    operation_description="Upgrade the user's subscription to a higher-tier plan. Deactivates the current plan and activates the new one."
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upgrade_subscription(request, new_plan_id):
    """
    Upgrade the user's subscription to a higher plan.
    This deactivates the current subscription and creates a new one.
    """
    try:
        new_plan = SubscriptionPlan.objects.get(id=new_plan_id, is_active=True)
    except SubscriptionPlan.DoesNotExist:
        return Response({"error": "New plan does not exist."}, status=status.HTTP_404_NOT_FOUND)

    current_subscription = UserSubscription.objects.filter(
        user=request.user,
        is_active=True
    ).first()

    if current_subscription and new_plan.price <= current_subscription.plan.price:
        return Response({"error": "New plan must be higher than the current one."}, status=status.HTTP_400_BAD_REQUEST)

    # Cancel current subscription
    if current_subscription:
        current_subscription.is_active = False
        current_subscription.end_date = timezone.now()
        current_subscription.save()

    # Create new upgraded subscription
    now = timezone.now()
    end_date = now + timezone.timedelta(days=new_plan.duration_days)

    new_subscription = UserSubscription.objects.create(
        user=request.user,
        plan=new_plan,
        start_date=now,
        end_date=end_date,
        is_active=True
    )

    serializer = UserSubscriptionSerializer(new_subscription)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@swagger_auto_schema(
    method='post',
    responses={
        200: openapi.Response(description="Subscription cancelled successfully."),
        400: openapi.Response(description="No active subscription to cancel.")
    },
    operation_description="Cancel the currently active subscription for the authenticated user."
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cancel_subscription(request):
    """
    Cancel the currently active subscription.
    """
    subscription = UserSubscription.objects.filter(
        user=request.user,
        is_active=True
    ).first()

    if not subscription:
        return Response({"message": "No active subscription to cancel."}, status=status.HTTP_400_BAD_REQUEST)

    subscription.is_active = False
    subscription.end_date = timezone.now()
    subscription.save()

    return Response({"message": "Subscription cancelled successfully."}, status=status.HTTP_200_OK)