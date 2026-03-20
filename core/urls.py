from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path('auth/register/', views.register, name='register'),
    path('auth/login/', views.login_view, name='login'),
    path('auth/logout/', views.logout_view, name='logout'),

    # Nodes and Edges (Admin)
    path('nodes/', views.node_list, name='node-list'),
    path('nodes/<int:pk>/', views.node_detail, name='node-detail'),
    path('edges/', views.edge_list, name='edge-list'),
    path('edges/<int:pk>/', views.edge_detail, name='edge-detail'),

    # Trips (Driver)
    path('trips/', views.trip_list, name='trip-list'),
    path('trips/available/', views.available_trips, name='available-trips'),
    path('trips/<int:pk>/cancel/', views.cancel_trip, name='cancel-trip'),
    path('trips/<int:pk>/update-node/', views.update_current_node, name='update-node'),
    path('trips/<int:trip_id>/requests/', views.incoming_requests, name='incoming-requests'),
    path('trips/<int:trip_id>/offer/<int:request_id>/', views.make_offer, name='make-offer'),

    # Carpool Requests (Passenger)
    path('requests/', views.carpool_request_list, name='request-list'),
    path('requests/<int:pk>/cancel/', views.cancel_carpool_request, name='cancel-request'),

    # Offers (Passenger confirms)
    path('offers/<int:offer_id>/confirm/', views.confirm_offer, name='confirm-offer'),

    # Wallet
    path('wallet/', views.wallet_balance, name='wallet-balance'),
    path('wallet/topup/', views.topup_wallet, name='wallet-topup'),
    path('wallet/transactions/', views.transaction_history, name='transaction-history'),
]