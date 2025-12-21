
import logging
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from .models import Ticket, Message
from .serializers import TicketSerializer, MessageSerializer
from .permissions import IsAdminOrReadOnly
from apps.admin.models import Admin, AdminCategory


logger = logging.getLogger(__name__)


class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        """Admin faqat o'z ticketlarini ko'radi"""
        queryset = super().get_queryset()
        admin_id = self.request.query_params.get('admin_id')
        if admin_id:
            try:
                return queryset.filter(assigned_admin_id=int(admin_id))
            except (ValueError, TypeError):
                pass
        return queryset

    def perform_create(self, serializer):
        """Ticket yaratilganda avtomatik admin biriktirish"""
        ticket = serializer.save()
        self.assign_admin_to_ticket(ticket)
        return ticket

    def assign_admin_to_ticket(self, ticket):
        """Kategoriya bo'yicha admin biriktirish (optimizatsiya qilingan)"""
        # Kategoriya bo'yicha adminlarni topish (optimizatsiya)
        admin_categories = AdminCategory.objects.filter(
            category=ticket.category,
            admin__is_blocked=False  # Faqat faol adminlar
        ).select_related('admin', 'admin__user')

        if not admin_categories.exists():
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Kategoriya {ticket.category.name_uz}"
                           " uchun admin topilmadi")
            return None

        # Faol adminlarni olish
        available_admins = [ac.admin for ac in admin_categories]

        if not available_admins:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Kategoriya {ticket.category.name_uz}"
                           " uchun faol admin yo'q")
            return None

        # Eng kam yuklangan adminni tanlash (optimizatsiya - bitta query)
        from django.db.models import Count
        admin_workloads = Ticket.objects.filter(
            assigned_admin__in=available_admins,
            status__in=['open', 'waiting_admin', 'in_progress']
        ).values('assigned_admin').annotate(
            workload=Count('id')
        )

        # Admin ID -> workload mapping
        workload_dict = {
            item['assigned_admin']: item['workload']
            for item in admin_workloads}

        # Eng kam yuklangan adminni tanlash
        from django.utils import timezone
        from datetime import datetime

        # Eng kam yuklangan adminni tanlash (workload birinchi, keyin esa last_assigned_at)
        selected_admin = min(
            available_admins,
            key=lambda admin: (
                workload_dict.get(admin.id, 0),
                admin.last_assigned_at or timezone.make_aware(datetime.min)
            )
        )

        # Adminni biriktirib, statusni va vaqtni yangilash
        ticket.assigned_admin = selected_admin
        ticket.status = 'waiting_admin'
        ticket.save()

        # Adminning oxirgi biriktirilgan vaqtini yangilash
        selected_admin.last_assigned_at = timezone.now()
        selected_admin.save(update_fields=['last_assigned_at'])

        # Admin faoliyatini yozish
        from .models import AdminActivityLog
        AdminActivityLog.objects.create(
            admin=selected_admin,
            ticket=ticket,
            action='assigned'
        )

        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Ticket {ticket.ticket_number} admin {selected_admin.id} "
                    "ga biriktirildi")

        return selected_admin

    @action(detail=True, methods=['post'])
    def assign_admin(self, request, pk=None):
        """Manual admin biriktirish"""
        ticket = self.get_object()
        admin_id = request.data.get('admin_id')

        if not admin_id:
            return Response(
                {'error': 'admin_id required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            admin = Admin.objects.get(id=admin_id, is_blocked=False)
            ticket.assigned_admin = admin
            ticket.status = 'waiting_admin'
            ticket.save()

            serializer = self.get_serializer(ticket)
            return Response(serializer.data)

        except Admin.DoesNotExist:
            return Response(
                {'error': 'Admin not found or blocked'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'])
    def close_ticket(self, request, pk=None):
        """Ticketni yopish"""
        ticket = self.get_object()
        close_reason = request.data.get('close_reason', '')
        admin_id = request.data.get('admin_id')

        if admin_id:
            try:
                admin = Admin.objects.get(id=admin_id)
                ticket.closed_by = admin
            except Admin.DoesNotExist:
                pass

        ticket.status = 'closed'
        ticket.close_reason = close_reason
        ticket.save()

        serializer = self.get_serializer(ticket)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def close_expired(self, request):
        """10 minutdan o'shgan va javob berilmagan ticketlarni yopish"""
        from django.utils import timezone
        from datetime import timedelta
        
        ten_minutes_ago = timezone.now() - timedelta(minutes=10)
        
        # Ochiq va 10 minutdan oldin yaratilgan/yangilangan ticketlar
        expired_tickets = Ticket.objects.filter(
            status__in=['open', 'waiting_admin', 'in_progress'],
            updated_at__lte=ten_minutes_ago
        )
        
        count = 0
        for ticket in expired_tickets:
            # Ticket xabarlarini tekshiramiz (admin javobi bormi?)
            has_admin_reply = Message.objects.filter(
                ticket=ticket,
                sender_admin__isnull=False
            ).exists()
            
            if not has_admin_reply:
                ticket.status = 'closed'
                ticket.close_reason = "10 minutdan o'tib ketilgan"
                ticket.save()
                count += 1
                
                # Log yozish
                from .models import AdminActivityLog
                AdminActivityLog.objects.create(
                    ticket=ticket,
                    action='closed',
                    admin=None 
                )
        
        return Response({'message': f'{count} tickets auto-closed'}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def my_tickets(self, request):
        """Adminning o'z ticketlari (sana bo'yicha filtr bilan)"""
        admin_id = request.query_params.get('admin_id')
        date_filter = request.query_params.get('date_filter', 'today')
        
        if not admin_id:
            return Response(
                {'error': 'admin_id required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        queryset = self.queryset.filter(assigned_admin_id=admin_id)
        
        from django.utils import timezone
        from datetime import timedelta
        
        now = timezone.now()
        today = now.date()
        
        if date_filter == 'today':
            queryset = queryset.filter(created_at__date=today)
        elif date_filter == 'yesterday':
            yesterday = today - timedelta(days=1)
            queryset = queryset.filter(created_at__date=yesterday)
        elif date_filter == 'old':
            yesterday = today - timedelta(days=1)
            queryset = queryset.filter(created_at__date__lt=yesterday)
        elif '-' in date_filter:  # YYYY-MM-DD format
            try:
                from datetime import datetime
                target_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
                queryset = queryset.filter(created_at__date=target_date)
            except ValueError:
                pass
        # else 'all' - no date filtering
            
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def user_tickets(self, request):
        """Userning ticketlari"""
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response(
                {'error': 'user_id required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        tickets = self.queryset.filter(user_id=user_id)
        serializer = self.get_serializer(tickets, many=True)
        return Response(serializer.data)


class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        queryset = super().get_queryset()
        ticket_id = self.request.query_params.get('ticket')
        if ticket_id:
            queryset = queryset.filter(ticket_id=ticket_id)
        return queryset
