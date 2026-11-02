from django.shortcuts import render
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Count, Q
from django.views import View
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator
from django.core.paginator import Paginator, EmptyPage
from .models import Event, Registration
from .time_utils import get_current_time
import json

# Helper para serializar um objeto Event nos mesmos campos do DRF
def serialize_event(event, request):
    return {
        "id": event.id,
        "title": event.title,
        "description": event.description,
        "location": event.location,
        "date": event.date.isoformat() if event.date else None,
        "time": event.time.strftime("%H:%M:%S") if event.time else None,
        "category": event.category,
        "organizer": event.organizer.id,
        "organizer_username": event.organizer.username,
        "image": event.image.url if event.image else None,
        "is_past": event.is_past,
        "created_at": event.created_at.isoformat() if event.created_at else None,
        "registrations_count": getattr(event, 'registrations_count', getattr(event, 'num_registrations', event.registrations.count())),
        "is_registered": event.registrations.filter(participant=request.user).exists() if request.user.is_authenticated else False
    }

# Helper comum para paginação JSON
def get_paginated_response(queryset, request, serialize_func, default_page_size=12):
    page_number = request.GET.get('page', 1)
    page_size = request.GET.get('page_size', default_page_size)
    
    try:
        page_size = int(page_size)
    except ValueError:
        page_size = default_page_size
        
    paginator = Paginator(queryset, page_size)
    
    try:
        page = paginator.page(page_number)
    except EmptyPage:
        return JsonResponse({
            'count': paginator.count,
            'total_pages': paginator.num_pages,
            'current_page': int(page_number),
            'next': None,
            'previous': None,
            'results': []
        })
    except Exception:
        page = paginator.page(1)
        
    serialized_results = [serialize_func(obj, request) for obj in page.object_list]
    
    return JsonResponse({
        'count': paginator.count,
        'total_pages': paginator.num_pages,
        'current_page': page.number,
        'next': page.next_page_number() if page.has_next() else None,
        'previous': page.previous_page_number() if page.has_previous() else None,
        'results': serialized_results
    })

# View de tempo do servidor
@ensure_csrf_cookie
def time(request):
    return JsonResponse({"server_time": get_current_time().isoformat()})

# Eventos em Destaque do Mês
@ensure_csrf_cookie
def highlighted_events(request):
    now = get_current_time()
    start_of_month = now.replace(day=1)
    if start_of_month.month == 12:
        next_month = start_of_month.replace(year=start_of_month.year + 1, month=1)
    else:
        next_month = start_of_month.replace(month=start_of_month.month + 1)

    events = (
        Event.objects
        .filter(date__gte=start_of_month, date__lt=next_month)
        .filter(Q(date__gt=now.date()) | (Q(date=now.date()) & Q(time__gte=now.time())))
        .annotate(num_registrations=Count("registrations"))
        .order_by("-num_registrations", "-created_at")
    )

    limit = request.GET.get("limit")
    if limit:
        try:
            events = events[:int(limit)]
        except ValueError:
            pass
        serialized_events = [serialize_event(ev, request) for ev in events]
        return JsonResponse(serialized_events, safe=False)

    return get_paginated_response(events, request, serialize_event)

# Eventos Acontecendo Hoje
@ensure_csrf_cookie
def today_events(request):
    now = get_current_time()
    today_events = (
        Event.objects
        .filter(date=now.date())
        .filter(time__gte=now.time())
        .order_by("time")
    )

    limit = request.GET.get("limit")
    if limit:
        try:
            today_events = today_events[:int(limit)]
        except ValueError:
            pass
        serialized_events = [serialize_event(ev, request) for ev in today_events]
        return JsonResponse(serialized_events, safe=False)

    return get_paginated_response(today_events, request, serialize_event)

# Listagem geral e filtros de Eventos
@method_decorator(ensure_csrf_cookie, name='dispatch')
class EventListView(View):
    def get(self, request):
        queryset = Event.objects.all().order_by("date")
        category = request.GET.get('category', None)
        if category:
            queryset = queryset.filter(category=category)
        
        search = request.GET.get('search', None)
        if search:
            queryset = queryset.filter(Q(title__icontains=search) | Q(description__icontains=search))
            
        return get_paginated_response(queryset, request, serialize_event)

# Criação de Evento
class EventCreateView(View):
    def post(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({"error": "Não autenticado"}, status=401)
            
        title = request.POST.get("title")
        description = request.POST.get("description", "")
        location = request.POST.get("location", "")
        date_str = request.POST.get("date")
        time_str = request.POST.get("time")
        category = request.POST.get("category")
        image = request.FILES.get("image")
        
        if not title or not date_str or not time_str or not category:
            return JsonResponse({"error": "Campos obrigatórios ausentes"}, status=400)
            
        try:
            event = Event.objects.create(
                title=title,
                description=description,
                location=location,
                date=date_str,
                time=time_str,
                category=category,
                image=image,
                organizer=request.user
            )
        except Exception as e:
            return JsonResponse({"error": f"Erro ao criar evento: {e}"}, status=400)
            
        return JsonResponse(
            {"message": "Evento criado com sucesso!", "data": serialize_event(event, request)},
            status=201
        )

# Detalhe, Atualização e Exclusão de Evento
@method_decorator(ensure_csrf_cookie, name='dispatch')
class EventDetailView(View):
    def get(self, request, pk):
        try:
            event = Event.objects.get(pk=pk)
        except Event.DoesNotExist:
            return JsonResponse({"error": "Evento não encontrado."}, status=404)
        return JsonResponse(serialize_event(event, request))
        
    def patch(self, request, pk):
        try:
            event = Event.objects.get(pk=pk)
        except Event.DoesNotExist:
            return JsonResponse({"error": "Evento não encontrado."}, status=404)
            
        if not request.user.is_authenticated or event.organizer != request.user:
            return JsonResponse({"error": "Sem permissão"}, status=403)
            
        # Carregar POST e FILES para requisição PATCH
        initial_method = request.method
        request.method = 'POST'
        request._load_post_and_files()
        request.method = initial_method
        
        title = request.POST.get("title")
        description = request.POST.get("description")
        location = request.POST.get("location")
        date_str = request.POST.get("date")
        time_str = request.POST.get("time")
        category = request.POST.get("category")
        image = request.FILES.get("image")
        
        if title: event.title = title
        if description is not None: event.description = description
        if location is not None: event.location = location
        if date_str: event.date = date_str
        if time_str: event.time = time_str
        if category: event.category = category
        if image: event.image = image
        
        event.save()
        return JsonResponse(serialize_event(event, request))
        
    def delete(self, request, pk):
        try:
            event = Event.objects.get(pk=pk)
        except Event.DoesNotExist:
            return JsonResponse({"error": "Evento não encontrado."}, status=404)
            
        if not request.user.is_authenticated or event.organizer != request.user:
            return JsonResponse({"error": "Sem permissão"}, status=403)
            
        event.delete()
        return JsonResponse({"message": "Evento excluído com sucesso!"})

# Registro/Inscrição em Evento
class RegistrationView(View):
    def post(self, request, pk):
        if not request.user.is_authenticated:
            return JsonResponse({"error": "Não autenticado"}, status=401)
            
        try:
            event = Event.objects.get(pk=pk)
        except Event.DoesNotExist:
            return JsonResponse({"error": "Evento não encontrado."}, status=404)
            
        if Registration.objects.filter(event=event, participant=request.user).exists():
            return JsonResponse({"error": "Você já está inscrito neste evento."}, status=400)
            
        reg = Registration.objects.create(event=event, participant=request.user)
        return JsonResponse({
            "message": "Inscrição realizada com sucesso!",
            "data": {
                "id": reg.id,
                "event": reg.event.id,
                "participant": reg.participant.id,
                "registered_at": reg.registered_at.isoformat() if reg.registered_at else None
            }
        }, status=201)
        
    def delete(self, request, pk):
        if not request.user.is_authenticated:
            return JsonResponse({"error": "Não autenticado"}, status=401)
            
        try:
            event = Event.objects.get(pk=pk)
        except Event.DoesNotExist:
            return JsonResponse({"error": "Evento não encontrado."}, status=404)
            
        registrations = Registration.objects.filter(event=event, participant=request.user)
        if not registrations.exists():
            return JsonResponse({"error": "Você não está inscrito neste evento."}, status=400)
            
        registrations.delete()
        return JsonResponse({"message": "Inscrição cancelada com sucesso!"})

# Lista de inscritos para o Organizador
class EventRegistrationsView(View):
    def get(self, request, pk):
        if not request.user.is_authenticated:
            return JsonResponse({"error": "Não autenticado"}, status=401)
            
        try:
            event = Event.objects.get(pk=pk)
        except Event.DoesNotExist:
            return JsonResponse({"error": "Evento não encontrado."}, status=404)
            
        if event.organizer != request.user:
            return JsonResponse({"error": "Você não tem permissão para visualizar esses dados."}, status=403)
            
        registrations = (
            Registration.objects
            .filter(event=event)
            .select_related("participant")
            .order_by("registered_at")
        )
        
        data = {
            "event_title": event.title,
            "registrations": [
                {
                    "name": reg.participant.get_full_name() or reg.participant.username,
                    "email": reg.participant.email,
                    "registered_at": reg.registered_at.isoformat() if reg.registered_at else None,
                }
                for reg in registrations
            ],
        }
        return JsonResponse(data)

# Inscrições do participante logado
class MyRegistrationsView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({"error": "Não autenticado"}, status=401)
            
        registrations = Registration.objects.filter(
            participant=request.user
        ).select_related("event")
        
        events = [reg.event for reg in registrations]
        serialized_events = [serialize_event(ev, request) for ev in events]
        return JsonResponse(serialized_events, safe=False)

# Eventos criados pelo organizador logado
class MyEventsView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({"error": "Não autenticado"}, status=401)
            
        events = Event.objects.filter(organizer=request.user).order_by("-date")
        serialized_events = [serialize_event(ev, request) for ev in events]
        return JsonResponse(serialized_events, safe=False)

# Estatísticas agregadas do organizador
class OrganizerDashboardStatsView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({"error": "Não autenticado"}, status=401)
            
        organized_events = Event.objects.filter(organizer=request.user)
        total_events = organized_events.count()
        total_registrations = Registration.objects.filter(event__organizer=request.user).count()
        
        return JsonResponse({
            "total_events": total_events,
            "total_registrations": total_registrations
        })
