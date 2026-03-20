from django.shortcuts import render, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from .models import User, Node, Edge, Trip, CarpoolRequest, CarpoolOffer
from .serializers import (UserSerializer, NodeSerializer, EdgeSerializer,
                          TripSerializer, CarpoolRequestSerializer, CarpoolOfferSerializer)
from .utils import bfs, get_nodes_within_distance, calculate_fare


# AUTH VIEWS

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({'message': 'User registered successfully'}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(request, username=username, password=password)
    if user:
        login(request, user)
        return Response({'message': 'Login successful', 'role': user.role})
    return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
def logout_view(request):
    logout(request)
    return Response({'message': 'Logged out successfully'})


# NODE AND EDGE VIEWS (Admin only)

@api_view(['GET', 'POST'])
def node_list(request):
    if request.method == 'GET':
        nodes = Node.objects.all()
        serializer = NodeSerializer(nodes, many=True)
        return Response(serializer.data)
    if request.method == 'POST':
        if not request.user.is_staff:
            return Response({'error': 'Admin only'}, status=status.HTTP_403_FORBIDDEN)
        serializer = NodeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
def node_detail(request, pk):
    if not request.user.is_staff:
        return Response({'error': 'Admin only'}, status=status.HTTP_403_FORBIDDEN)
    node = get_object_or_404(Node, pk=pk)
    node.delete()
    return Response({'message': 'Node deleted'})


@api_view(['GET', 'POST'])
def edge_list(request):
    if request.method == 'GET':
        edges = Edge.objects.all()
        serializer = EdgeSerializer(edges, many=True)
        return Response(serializer.data)
    if request.method == 'POST':
        if not request.user.is_staff:
            return Response({'error': 'Admin only'}, status=status.HTTP_403_FORBIDDEN)
        serializer = EdgeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
def edge_detail(request, pk):
    if not request.user.is_staff:
        return Response({'error': 'Admin only'}, status=status.HTTP_403_FORBIDDEN)
    edge = get_object_or_404(Edge, pk=pk)
    edge.delete()
    return Response({'message': 'Edge deleted'})


# TRIP VIEWS

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def trip_list(request):
    if request.method == 'GET':
        trips = Trip.objects.filter(driver=request.user)
        serializer = TripSerializer(trips, many=True)
        return Response(serializer.data)

    if request.method == 'POST':
        if request.user.role != 'driver':
            return Response({'error': 'Only drivers can create trips'}, status=status.HTTP_403_FORBIDDEN)

        start_id = request.data.get('start_node')
        end_id = request.data.get('end_node')
        max_passengers = request.data.get('max_passengers', 3)

        start_node = get_object_or_404(Node, pk=start_id)
        end_node = get_object_or_404(Node, pk=end_id)

        route = bfs(start_node, end_node)
        if not route:
            return Response({'error': 'No route found between these nodes'}, status=status.HTTP_400_BAD_REQUEST)

        route_ids = [node.id for node in route]

        trip = Trip.objects.create(
            driver=request.user,
            start_node=start_node,
            end_node=end_node,
            route=route_ids,
            current_node=start_node,
            max_passengers=max_passengers,
            status='scheduled'
        )
        serializer = TripSerializer(trip)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cancel_trip(request, pk):
    trip = get_object_or_404(Trip, pk=pk, driver=request.user)
    if trip.status != 'scheduled':
        return Response({'error': 'Only scheduled trips can be cancelled'}, status=status.HTTP_400_BAD_REQUEST)
    trip.status = 'cancelled'
    trip.save()
    return Response({'message': 'Trip cancelled'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_current_node(request, pk):
    trip = get_object_or_404(Trip, pk=pk, driver=request.user)
    node_id = request.data.get('node_id')
    node = get_object_or_404(Node, pk=node_id)

    if node_id not in trip.route:
        return Response({'error': 'Node not in route'}, status=status.HTTP_400_BAD_REQUEST)

    if node_id in trip.visited_nodes:
        return Response({'error': 'Node already visited'}, status=status.HTTP_400_BAD_REQUEST)

    trip.visited_nodes.append(node_id)
    trip.current_node = node
    trip.status = 'active'
    trip.save()
    return Response({'message': f'Current node updated to {node.name}'})


# CARPOOL REQUEST VIEWS

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def carpool_request_list(request):
    if request.method == 'GET':
        requests = CarpoolRequest.objects.filter(passenger=request.user)
        serializer = CarpoolRequestSerializer(requests, many=True)
        return Response(serializer.data)

    if request.method == 'POST':
        if request.user.role != 'passenger':
            return Response({'error': 'Only passengers can make carpool requests'}, status=status.HTTP_403_FORBIDDEN)

        pickup_id = request.data.get('pickup_node')
        dropoff_id = request.data.get('dropoff_node')

        pickup_node = get_object_or_404(Node, pk=pickup_id)
        dropoff_node = get_object_or_404(Node, pk=dropoff_id)

        carpool_request = CarpoolRequest.objects.create(
            passenger=request.user,
            pickup_node=pickup_node,
            dropoff_node=dropoff_node,
            status='pending'
        )
        serializer = CarpoolRequestSerializer(carpool_request)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cancel_carpool_request(request, pk):
    carpool_request = get_object_or_404(CarpoolRequest, pk=pk, passenger=request.user)
    if carpool_request.status != 'pending':
        return Response({'error': 'Only pending requests can be cancelled'}, status=status.HTTP_400_BAD_REQUEST)
    carpool_request.status = 'cancelled'
    carpool_request.save()
    return Response({'message': 'Carpool request cancelled'})


# DRIVER SEES INCOMING REQUESTS

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def incoming_requests(request, trip_id):
    if request.user.role != 'driver':
        return Response({'error': 'Drivers only'}, status=status.HTTP_403_FORBIDDEN)

    trip = get_object_or_404(Trip, pk=trip_id, driver=request.user)

    current_index = trip.route.index(trip.current_node.id) if trip.current_node else 0
    remaining_route_ids = trip.route[current_index:]
    remaining_nodes = list(Node.objects.filter(id__in=remaining_route_ids))

    nearby_nodes = get_nodes_within_distance(remaining_nodes, max_distance=2)

    matching_requests = CarpoolRequest.objects.filter(
        pickup_node__in=nearby_nodes,
        dropoff_node__in=nearby_nodes,
        status='pending'
    )

    result = []
    for req in matching_requests:
        new_route = bfs(trip.current_node, req.pickup_node)
        if not new_route:
            continue
        to_dropoff = bfs(req.pickup_node, req.dropoff_node)
        if not to_dropoff:
            continue
        to_end = bfs(req.dropoff_node, trip.end_node)
        if not to_end:
            continue

        original_remaining = len(remaining_route_ids)
        new_remaining = len(new_route) + len(to_dropoff) + len(to_end) - 2
        detour = new_remaining - original_remaining

        pickup_index = len(new_route) - 1
        dropoff_index = pickup_index + len(to_dropoff) - 1
        fare = calculate_fare(new_route + to_dropoff[1:] + to_end[1:],
                              pickup_index, dropoff_index)

        result.append({
            'request_id': req.id,
            'passenger': req.passenger.username,
            'pickup': req.pickup_node.name,
            'dropoff': req.dropoff_node.name,
            'detour': detour,
            'fare': fare
        })

    return Response(result)


# DRIVER MAKES AN OFFER

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def make_offer(request, trip_id, request_id):
    if request.user.role != 'driver':
        return Response({'error': 'Drivers only'}, status=status.HTTP_403_FORBIDDEN)

    trip = get_object_or_404(Trip, pk=trip_id, driver=request.user)
    carpool_request = get_object_or_404(CarpoolRequest, pk=request_id)

    detour = request.data.get('detour', 0)
    fare = request.data.get('fare', 0.0)

    offer = CarpoolOffer.objects.create(
        trip=trip,
        request=carpool_request,
        detour=detour,
        fare=fare,
        status='offered'
    )
    serializer = CarpoolOfferSerializer(offer)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


# PASSENGER CONFIRMS AN OFFER

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def confirm_offer(request, offer_id):
    if request.user.role != 'passenger':
        return Response({'error': 'Passengers only'}, status=status.HTTP_403_FORBIDDEN)

    offer = get_object_or_404(CarpoolOffer, pk=offer_id, request__passenger=request.user)
    offer.status = 'accepted'
    offer.request.status = 'confirmed'
    offer.request.save()
    offer.save()
    return Response({'message': 'Offer confirmed'})
# SSR DASHBOARD VIEWS

from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.shortcuts import redirect

def login_page(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            auth_login(request, user)
            if user.is_staff:
                return redirect('/admin/')
            elif user.role == 'driver':
                return redirect('/dashboard/driver/')
            else:
                return redirect('/dashboard/passenger/')
        return render(request, 'core/login.html', {'error': 'Invalid credentials'})
    return render(request, 'core/login.html')


def register_page(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        role = request.POST.get('role')
        if User.objects.filter(username=username).exists():
            return render(request, 'core/register.html', {'error': 'Username already taken'})
        user = User.objects.create_user(username=username, password=password, role=role)
        auth_login(request, user)
        if role == 'driver':
            return redirect('/dashboard/driver/')
        return redirect('/dashboard/passenger/')
    return render(request, 'core/register.html')


def driver_dashboard(request):
    if not request.user.is_authenticated or request.user.role != 'driver':
        return redirect('/dashboard/login/')
    trips = Trip.objects.filter(driver=request.user).select_related('start_node', 'end_node')
    nodes = Node.objects.all()
    return render(request, 'core/driver_dashboard.html', {'trips': trips, 'nodes': nodes, 'user': request.user})


def create_trip_view(request):
    if not request.user.is_authenticated or request.user.role != 'driver':
        return redirect('/dashboard/login/')
    if request.method == 'POST':
        start_id = int(request.POST.get('start_node'))
        end_id = int(request.POST.get('end_node'))
        max_passengers = int(request.POST.get('max_passengers', 3))
        start_node = get_object_or_404(Node, pk=start_id)
        end_node = get_object_or_404(Node, pk=end_id)
        route = bfs(start_node, end_node)
        if route:
            route_ids = [node.id for node in route]
            Trip.objects.create(
                driver=request.user,
                start_node=start_node,
                end_node=end_node,
                route=route_ids,
                current_node=start_node,
                max_passengers=max_passengers,
                status='scheduled'
            )
    return redirect('/dashboard/driver/')


def cancel_trip_view(request, pk):
    if not request.user.is_authenticated or request.user.role != 'driver':
        return redirect('/dashboard/login/')
    trip = get_object_or_404(Trip, pk=pk, driver=request.user)
    if request.method == 'POST' and trip.status == 'scheduled':
        trip.status = 'cancelled'
        trip.save()
    return redirect('/dashboard/driver/')


def trip_requests_view(request, trip_id):
    if not request.user.is_authenticated or request.user.role != 'driver':
        return redirect('/dashboard/login/')
    trip = get_object_or_404(Trip, pk=trip_id, driver=request.user)
    current_index = trip.route.index(trip.current_node.id) if trip.current_node else 0
    remaining_route_ids = trip.route[current_index:]
    remaining_nodes = list(Node.objects.filter(id__in=remaining_route_ids))
    nearby_nodes = get_nodes_within_distance(remaining_nodes, max_distance=2)
    matching_requests = CarpoolRequest.objects.filter(
        pickup_node__in=nearby_nodes,
        dropoff_node__in=nearby_nodes,
        status='pending'
    )
    result = []
    for req in matching_requests:
        new_route = bfs(trip.current_node, req.pickup_node)
        if not new_route:
            continue
        to_dropoff = bfs(req.pickup_node, req.dropoff_node)
        if not to_dropoff:
            continue
        to_end = bfs(req.dropoff_node, trip.end_node)
        if not to_end:
            continue
        original_remaining = len(remaining_route_ids)
        new_remaining = len(new_route) + len(to_dropoff) + len(to_end) - 2
        detour = new_remaining - original_remaining
        pickup_index = len(new_route) - 1
        dropoff_index = pickup_index + len(to_dropoff) - 1
        fare = calculate_fare(new_route + to_dropoff[1:] + to_end[1:], pickup_index, dropoff_index)
        result.append({
            'request_id': req.id,
            'passenger': req.passenger.username,
            'pickup': req.pickup_node.name,
            'dropoff': req.dropoff_node.name,
            'detour': detour,
            'fare': fare
        })
    route_nodes = Node.objects.filter(id__in=remaining_route_ids)
    return render(request, 'core/trip_requests.html', {
        'trip': trip,
        'requests': result,
        'route_nodes': route_nodes
    })


def update_node_view(request, trip_id):
    if not request.user.is_authenticated or request.user.role != 'driver':
        return redirect('/dashboard/login/')
    trip = get_object_or_404(Trip, pk=trip_id, driver=request.user)
    if request.method == 'POST':
        node_id = int(request.POST.get('node_id'))
        node = get_object_or_404(Node, pk=node_id)
        if node_id in trip.route and node_id not in trip.visited_nodes:
            trip.visited_nodes.append(node_id)
            trip.current_node = node
            trip.status = 'active'
            trip.save()
    return redirect(f'/dashboard/trips/{trip_id}/requests/')


def make_offer_view(request, trip_id, request_id):
    if not request.user.is_authenticated or request.user.role != 'driver':
        return redirect('/dashboard/login/')
    if request.method == 'POST':
        trip = get_object_or_404(Trip, pk=trip_id, driver=request.user)
        carpool_request = get_object_or_404(CarpoolRequest, pk=request_id)
        detour = request.POST.get('detour', 0)
        fare = request.POST.get('fare', 0.0)
        CarpoolOffer.objects.create(
            trip=trip,
            request=carpool_request,
            detour=detour,
            fare=fare,
            status='offered'
        )
    return redirect(f'/dashboard/trips/{trip_id}/requests/')


def passenger_dashboard(request):
    if not request.user.is_authenticated or request.user.role != 'passenger':
        return redirect('/dashboard/login/')
    carpool_requests = CarpoolRequest.objects.filter(
        passenger=request.user
    ).select_related('pickup_node', 'dropoff_node').prefetch_related('offers__trip__driver')
    nodes = Node.objects.all()
    return render(request, 'core/passenger_dashboard.html', {
        'carpool_requests': carpool_requests,
        'nodes': nodes,
        'user': request.user
    })


def create_request_view(request):
    if not request.user.is_authenticated or request.user.role != 'passenger':
        return redirect('/dashboard/login/')
    if request.method == 'POST':
        pickup_id = int(request.POST.get('pickup_node'))
        dropoff_id = int(request.POST.get('dropoff_node'))
        pickup_node = get_object_or_404(Node, pk=pickup_id)
        dropoff_node = get_object_or_404(Node, pk=dropoff_id)
        CarpoolRequest.objects.create(
            passenger=request.user,
            pickup_node=pickup_node,
            dropoff_node=dropoff_node,
            status='pending'
        )
    return redirect('/dashboard/passenger/')


def cancel_request_view(request, pk):
    if not request.user.is_authenticated or request.user.role != 'passenger':
        return redirect('/dashboard/login/')
    carpool_request = get_object_or_404(CarpoolRequest, pk=pk, passenger=request.user)
    if request.method == 'POST' and carpool_request.status == 'pending':
        carpool_request.status = 'cancelled'
        carpool_request.save()
    return redirect('/dashboard/passenger/')


def confirm_offer_view(request, offer_id):
    if not request.user.is_authenticated or request.user.role != 'passenger':
        return redirect('/dashboard/login/')
    if request.method == 'POST':
        offer = get_object_or_404(CarpoolOffer, pk=offer_id, request__passenger=request.user)
        offer.status = 'accepted'
        offer.request.status = 'confirmed'
        offer.request.save()
        offer.save()
    return redirect('/dashboard/passenger/')


def logout_view_page(request):
    auth_logout(request)
    return redirect('/dashboard/login/')
# WALLET VIEWS

from .models import Wallet, Transaction

def get_or_create_wallet(user):
    wallet, created = Wallet.objects.get_or_create(user=user)
    return wallet


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def wallet_balance(request):
    wallet = get_or_create_wallet(request.user)
    return Response({'balance': wallet.balance})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def topup_wallet(request):
    amount = float(request.data.get('amount', 0))
    if amount <= 0:
        return Response({'error': 'Amount must be positive'}, status=status.HTTP_400_BAD_REQUEST)
    wallet = get_or_create_wallet(request.user)
    wallet.balance += amount
    wallet.save()
    Transaction.objects.create(
        user=request.user,
        amount=amount,
        transaction_type='topup',
        description=f'Wallet top up of ${amount}'
    )
    return Response({'message': f'Wallet topped up by ${amount}', 'new_balance': wallet.balance})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def transaction_history(request):
    transactions = Transaction.objects.filter(user=request.user).order_by('-created_at')
    data = [{
        'id': t.id,
        'type': t.transaction_type,
        'amount': t.amount,
        'description': t.description,
        'created_at': t.created_at
    } for t in transactions]
    return Response(data)