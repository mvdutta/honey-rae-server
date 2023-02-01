"""View module for handling requests for customer data"""
from django.http import HttpResponseServerError
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers, status
from repairsapi.models import ServiceTicket, Customer, Employee


class ServiceTicketView(ViewSet):
    """Honey Rae API service_ticket view"""

    def list(self, request):
        """Handle GET requests to get all service_tickets

        Returns:
            Response -- JSON serialized list of tickets
        """
        service_tickets = []


        if request.auth.user.is_staff:
            service_tickets = ServiceTicket.objects.all()

            if "status" in request.query_params:
                if request.query_params['status'] == "done":
                    service_tickets = service_tickets.filter(date_completed__isnull=False)

                if request.query_params['status'] == "all":
                    pass

        else:
            service_tickets = ServiceTicket.objects.filter(customer__user=request.auth.user)

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

    def create(self, request):
        """Handle POST requests for service tickets

        Returns:
            Response: JSON serialized representation of newly created service ticket
        """
        new_ticket = ServiceTicket()
        new_ticket.customer = Customer.objects.get(user=request.auth.user)
        new_ticket.description = request.data['description']
        new_ticket.emergency = request.data['emergency']
        new_ticket.save()

        serialized = ServiceTicketSerializer(new_ticket, many=False)

        return Response(serialized.data, status=status.HTTP_201_CREATED)
    
    def update(self, request, pk=None):
        """Handle PUT requests for a single customer. 
        Returns: Response--no response body. Just 204 status code."""

        #Select the targeted ticket using pk
        ticket = ServiceTicket.objects.get(pk=pk)

        #Get the employee id form the client request
        employee_id = request.data['employee']

        #Select the employee from the database using that id
        assigned_employee = Employee.objects.get(pk=employee_id)

        #Assign that employee instance to the employee property of the ticket
        ticket.employee = assigned_employee

        #Save the updated ticket
        ticket.save()

        return Response(None, status=status.HTTP_204_NO_CONTENT)
    
    def destroy(self, request, pk=None):
        """Handle DELETE requests for service tickets

        Returns:
            Response: None with 204 status code
        """
        #get the ticket that the client wants to delete:
        service_ticket = ServiceTicket.objects.get(pk=pk)
        #Invoke the ORM method of delete:
        service_ticket.delete()
        #Don't need to serialize anything b/c 204 status code means "no body", but we do need to return a response:
        return Response(None, status=status.HTTP_204_NO_CONTENT)




#Need to create a specific serializer just for employee on the service ticket:
class TicketEmployeeSerializer(serializers.ModelSerializer):
    """JSON serializer for employee on service_tickets"""
    class Meta:
        model = Employee
        fields = ('id', 'specialty', 'full_name',)


class ServiceTicketSerializer(serializers.ModelSerializer):
    """JSON serializer for service_tickets"""
    #Need to specify how the employee should be serialized:
    employee = TicketEmployeeSerializer(many=False)
    class Meta:
        model = ServiceTicket
        fields = ('id', 'customer', 'employee', 'description', 'emergency', 'date_completed',) 
        depth = 1