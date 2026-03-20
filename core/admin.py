from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Node, Edge, Trip, CarpoolRequest, CarpoolOffer, Wallet, Transaction

admin.site.register(User, UserAdmin)
admin.site.register(Node)
admin.site.register(Edge)
admin.site.register(Trip)
admin.site.register(CarpoolRequest)
admin.site.register(CarpoolOffer)
admin.site.register(Wallet)
admin.site.register(Transaction)