from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_page, name='login-page'),
    path('register/', views.register_page, name='register-page'),
    path('logout/', views.logout_view_page, name='logout-page'),
    path('driver/', views.driver_dashboard, name='driver-dashboard'),
    path('passenger/', views.passenger_dashboard, name='passenger-dashboard'),
    path('trips/create/', views.create_trip_view, name='create-trip-view'),
    path('trips/<int:pk>/cancel/', views.cancel_trip_view, name='cancel-trip-view'),
    path('trips/<int:trip_id>/requests/', views.trip_requests_view, name='trip-requests-view'),
    path('trips/<int:trip_id>/update-node/', views.update_node_view, name='update-node-view'),
    path('trips/<int:trip_id>/offer/<int:request_id>/', views.make_offer_view, name='make-offer-view'),
    path('requests/create/', views.create_request_view, name='create-request-view'),
    path('requests/<int:pk>/cancel/', views.cancel_request_view, name='cancel-request-view'),
    path('offers/<int:offer_id>/confirm/', views.confirm_offer_view, name='confirm-offer-view'),
]