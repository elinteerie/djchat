from django.shortcuts import render
from rest_framework import viewsets
from .models import Server
from .serializer import ServerSerializer
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, AuthenticationFailed
from django.db.models import Count
from .schema import server_list_docs

class ServerListViewSet(viewsets.ViewSet):
    """
    ViewSet for listing servers based on various query parameters.

    Parameters:
        request (rest_framework.request.Request): The HTTP request object.

    Returns:
        rest_framework.response.Response: A JSON response containing the serialized server data.

    Raises:
        rest_framework.exceptions.AuthenticationFailed: If the user is not authenticated and tries to use 'by_user' or 'by_serverid' filter.
        rest_framework.exceptions.ValidationError: If 'by_serverid' filter is provided without a valid server ID.

    Example:
        To list all servers:
        ```
        GET /api/servers/
        ```

        To list servers by category:
        ```
        GET /api/servers/?category=example_category
        ```

        To list servers with the number of members:
        ```
        GET /api/servers/?with_num_members=true
        ```

        To limit the number of servers returned:
        ```
        GET /api/servers/?qty=10
        ```

        To list servers filtered by user ID (must be authenticated):
        ```
        GET /api/servers/?by_user=true
        ```

        To list servers by a specific server ID:
        ```
        GET /api/servers/?by_serverid=42
        ```
    """
    queryset = Server.objects.all()
    @server_list_docs
    def list(self, request):
        """
    List servers based on various query parameters.

    Args:
        request (rest_framework.request.Request): The HTTP request object.

    Returns:
        rest_framework.response.Response: A JSON response containing the serialized server data.

    Raises:
        rest_framework.exceptions.AuthenticationFailed: If the user is not authenticated and tries to use 'by_user' or 'by_serverid' filter.
        rest_framework.exceptions.ValidationError: If 'by_serverid' filter is provided without a valid server ID.

    Example:
        To list all servers:
        ```
        GET /api/servers/
        ```

        To list servers by category:
        ```
        GET /api/servers/?category=example_category
        ```

        To list servers with the number of members:
        ```
        GET /api/servers/?with_num_members=true
        ```

        To limit the number of servers returned:
        ```
        GET /api/servers/?qty=10
        ```

        To list servers filtered by user ID (must be authenticated):
        ```
        GET /api/servers/?by_user=true
        ```

        To list servers by a specific server ID:
        ```
        GET /api/servers/?by_serverid=42
        ```
    """ 
        category = request.query_params.get("category")
        qty = request.query_params.get("qty")
        by_user = request.query_params.get("by_user") == "true"
        by_serverid = request.query_params.get("by_serverid")
        with_num_members = request.query_params.get("with_num_members") == "true"

        if by_user or (by_serverid and not request.user.is_authenticated):
            raise AuthenticationFailed(detail='Please login to perform this action.')

        if category:
            self.queryset = self.queryset.filter(category=category)

        if with_num_members:
            self.queryset = self.queryset.annotate(num_members=Count('members'))

        if qty:
            self.queryset = self.queryset[: int(qty)]

        if by_user:
            user_id = request.user.id
            self.queryset = self.queryset.filter(members=user_id)

        if by_serverid:
            try:
                self.queryset = self.queryset.filter(id=by_serverid)
                if not self.queryset.exists():
                    raise ValidationError(detail=f"Server with ID {by_serverid} not found.")
            except ValueError:
                raise ValidationError(detail='Please specify a valid server ID.')

        serializer = ServerSerializer(self.queryset, many=True)
        return Response(serializer.data)