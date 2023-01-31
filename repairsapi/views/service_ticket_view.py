"""View module for handling requests for customer data"""
from django.http import HttpResponseServerError
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers, status
from repairsapi.models import ServiceTicket


class TicketView(ViewSet):
    """Honey Rae API service_ticket view"""

    def list(self, request):
        """Handle GET requests to get all service_tickets

        Returns:
            Response -- JSON serialized list of tickets
        """
        if request.auth.user.is_staff:
            service_tickets = ServiceTicket.objects.all()
        else:
            service_tickets = ServiceTicket.objects.filter(
                customer__user=request.auth.user)
        serialized = ServiceTicketSerializer(service_tickets, many=True)
        return Response(serialized.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        """Handle GET requests for single ticket

        Returns:
            Response -- JSON serialized ticket record
        """

        service_ticket = ServiceTicket.objects.get(pk=pk)
        serialized = ServiceTicketSerializer(service_ticket, context={'request': request})
        return Response(serialized.data, status=status.HTTP_200_OK)


class ServiceTicketSerializer(serializers.ModelSerializer):
    """JSON serializer for service_tickets"""
    class Meta:
        model = ServiceTicket
        fields = ('id', 'customer', 'employee', 'description', 'emergency', 'date_completed',) 
        depth = 1