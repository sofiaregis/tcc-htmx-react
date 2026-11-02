from dataclasses import dataclass
from typing import Any, Callable, Sequence
from collections.abc import Mapping
import csv

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpRequest, HttpResponse, HttpResponseForbidden
from django.db.models import Count, Q
from django.utils import timezone
from django.core.paginator import Paginator
from django.template.loader import render_to_string
from django.template.response import TemplateResponse

from .models import Event, Registration
from .time_utils import get_current_time

OOB_SHELL_TEMPLATE = "c/_oob_shell.html"


@dataclass(frozen=True)
class Oob:
    """Define a fragment and context to be rendered Out-Of-Band for HTMX."""
    template_name: str
    context: dict[str, Any]


def _with_partial(template_name: str | Sequence[str], partial_name: str | None, is_htmx: bool):
    """Append `#partial_name` to candidate template name(s) when servicing HTMX requests."""
    if not is_htmx or not partial_name:
        return template_name
    if isinstance(template_name, (list, tuple)):
        return [f"{t}#{partial_name}" for t in template_name]
    return f"{template_name}#{partial_name}"


def render_htmx(
    request: HttpRequest,
    template_name: str | Sequence[str],
    context: Mapping[str, Any] | None = None,
    content_type: str | None = None,
    status: int | None = None,
    using: str | None = None,
    *,
    partial_name: str | None = "content",
    oob: Sequence[Oob] = (),
    oob_template: str | None = None,
    extra_context: dict[str, Callable] | None = None,
) -> TemplateResponse:
    """
    HTMX-aware replacement for django.shortcuts.render().
    """
    is_htmx = getattr(request, "htmx", False)
    context = dict(context or {})
    context.setdefault("active_partial", partial_name)
    for key, builder in (extra_context or {}).items():
        context[key] = builder(request)

    resolved_template = _with_partial(template_name, partial_name, is_htmx)
    response = TemplateResponse(
        request, resolved_template, context,
        content_type=content_type, status=status, using=using,
    )

    if is_htmx and (oob or oob_template):
        def append_oob(resp):
            if oob_template:
                html = render_to_string(oob_template, context, request=request)
                resp.content += html.encode(resp.charset)
            for frag in oob:
                html = render_to_string(frag.template_name, frag.context, request=request)
                resp.content += html.encode(resp.charset)
            return resp
        response.add_post_render_callback(append_oob)

    return response


def render_page(request: HttpRequest, template_name: str, context: Mapping[str, Any] | None = None, **kwargs) -> TemplateResponse:
    """Wrapper around render_htmx() attaching the default OOB shell for page navigation requests."""
    kwargs.setdefault("oob_template", OOB_SHELL_TEMPLATE)
    return render_htmx(request, template_name, context, **kwargs)


def render_mutation_error(request: HttpRequest, exc_or_message: Any, *, status: int = 400) -> HttpResponse:
    """Error helper for HTMX mutations. Swaps nothing in the main target and pushes error via OOB."""
    messages.error(request, str(exc_or_message))
    messages_html = render_to_string(
        "c/_messages.html",
        {"messages": messages.get_messages(request)},
        request=request,
    )
    response = HttpResponse(
        f'<div id="messages" hx-swap-oob="innerHTML">{messages_html}</div>',
        status=status,
    )
    response["HX-Reswap"] = "none"
    return response

CATEGORIES = dict(Event.CATEGORY_CHOICES)

def get_paginated_context(queryset, page_number, page_size=12):
    paginator = Paginator(queryset, page_size)
    page_obj = paginator.get_page(page_number)
    
    return {
        "events": page_obj.object_list,
        "current_page": page_obj.number,
        "total_pages": paginator.num_pages,
        "has_previous": page_obj.has_previous(),
        "has_next": page_obj.has_next(),
        "previous_page": page_obj.previous_page_number() if page_obj.has_previous() else None,
        "next_page": page_obj.next_page_number() if page_obj.has_next() else None,
        "page_obj": page_obj,
        "is_paginated": page_obj.has_other_pages(),
        "total_count": paginator.count,
    }

def home_view(request):
    now = get_current_time()
    
    # Eventos em destaque do mês corrente que ainda não ocorreram
    start_of_month = now.replace(day=1)
    if start_of_month.month == 12:
        next_month = start_of_month.replace(year=start_of_month.year + 1, month=1)
    else:
        next_month = start_of_month.replace(month=start_of_month.month + 1)

    highlights = (
        Event.objects
        .filter(date__gte=start_of_month, date__lt=next_month)
        .filter(Q(date__gt=now.date()) | (Q(date=now.date()) & Q(time__gte=now.time())))
        .annotate(num_registrations=Count("registrations"))
        .order_by("-num_registrations", "-created_at")[:10]
    )

    # Eventos programados para hoje que ainda não ocorreram
    today_events = (
        Event.objects
        .filter(date=now.date())
        .filter(time__gte=now.time())
        .order_by("time")[:10]
    )

    context = {
        "highlights": highlights,
        "today_events": today_events,
        "categories": CATEGORIES,
    }
    return render_page(request, "home.html", context)

def search_view(request):
    q = request.GET.get("q", "").strip()
    category = request.GET.get("category", "").strip()
    try:
        page = int(request.GET.get("page", 1))
    except ValueError:
        page = 1

    queryset = Event.objects.all().order_by("date", "time")
    
    if q:
        queryset = queryset.filter(Q(title__icontains=q) | Q(description__icontains=q))
    if category:
        queryset = queryset.filter(category=category)

    # Anota a quantidade de inscrições
    queryset = queryset.annotate(registrations_count=Count("registrations"))

    context = get_paginated_context(queryset, page, page_size=12)
    context.update({
        "q": q,
        "category": category,
        "categories": CATEGORIES,
    })

    if getattr(request, "htmx", False) and page > 1:
        return render_htmx(request, "search.html", context, partial_name="events_page")

    return render_page(request, "search.html", context)

def highlighted_events_view(request):
    now = get_current_time()
    page = request.GET.get("page", 1)

    start_of_month = now.replace(day=1)
    if start_of_month.month == 12:
        next_month = start_of_month.replace(year=start_of_month.year + 1, month=1)
    else:
        next_month = start_of_month.replace(month=start_of_month.month + 1)

    queryset = (
        Event.objects
        .filter(date__gte=start_of_month, date__lt=next_month)
        .filter(Q(date__gt=now.date()) | (Q(date=now.date()) & Q(time__gte=now.time())))
        .annotate(registrations_count=Count("registrations"))
        .order_by("-registrations_count", "-created_at")
    )

    context = get_paginated_context(queryset, page, page_size=12)

    return render_page(request, "highlighted_events.html", context)

def today_events_view(request):
    now = get_current_time()
    page = request.GET.get("page", 1)

    queryset = (
        Event.objects
        .filter(date=now.date())
        .filter(time__gte=now.time())
        .annotate(registrations_count=Count("registrations"))
        .order_by("time")
    )

    context = get_paginated_context(queryset, page, page_size=12)

    return render_page(request, "today_events.html", context)

def event_details_view(request, pk):
    event = get_object_or_404(Event.objects.annotate(registrations_count=Count("registrations")), pk=pk)
    
    is_organizer = request.user.is_authenticated and event.organizer == request.user
    is_registered = request.user.is_authenticated and event.registrations.filter(participant=request.user).exists()

    context = {
        "event": event,
        "registrations_count": event.registrations_count,
        "is_organizer": is_organizer,
        "is_registered": is_registered,
    }
    return render_page(request, "event_details.html", context)

def event_register_view(request, pk):
    if not request.user.is_authenticated:
        return HttpResponseForbidden("Você precisa estar autenticado.")

    event = get_object_or_404(Event, pk=pk)
    is_organizer = event.organizer == request.user

    if request.method == "POST":
        if is_organizer:
            return HttpResponseForbidden("O organizador não pode se inscrever no próprio evento.")
        
        # Inscrever se não estiver inscrito
        Registration.objects.get_or_create(event=event, participant=request.user)

    elif request.method == "DELETE":
        # Cancelar inscrição
        Registration.objects.filter(event=event, participant=request.user).delete()

    # Retorna o fragmento do card de participação atualizado
    registrations_count = event.registrations.count()
    is_registered = event.registrations.filter(participant=request.user).exists()

    context = {
        "event": event,
        "registrations_count": registrations_count,
        "is_organizer": is_organizer,
        "is_registered": is_registered,
    }
    return render_htmx(request, "c/registration_card.html", context, partial_name="card")

@login_required
def event_delete_view(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if event.organizer != request.user:
        return HttpResponseForbidden("Você não tem permissão para excluir este evento.")

    if request.method in ["POST", "DELETE"]:
        event.delete()
        if request.headers.get("HX-Request"):
            return HttpResponse("")  # Retorna vazio para o HTMX deletar a linha do DOM
        
        messages.success(request, "Evento excluído com sucesso!")
        return redirect("my-events")

    return redirect("my-events")

@login_required
def my_registrations_view(request):
    registrations = Registration.objects.filter(participant=request.user).select_related("event")
    events = [reg.event for reg in registrations]
    
    # Anota a quantidade de inscrições para cada evento
    for e in events:
        e.registrations_count = e.registrations.count()

    return render_page(request, "my_registrations.html", {"events": events})

@login_required
def my_events_view(request):
    events = Event.objects.filter(organizer=request.user).annotate(registrations_count=Count("registrations")).order_by("-date", "-time")
    
    total_events = events.count()
    total_registrations = Registration.objects.filter(event__organizer=request.user).count()

    context = {
        "events": events,
        "total_events": total_events,
        "total_registrations": total_registrations,
    }
    return render_page(request, "my_events.html", context)

@login_required
def event_registrations_view(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if event.organizer != request.user:
        return HttpResponseForbidden("Você não tem permissão para acessar esta página.")

    registrations = Registration.objects.filter(event=event).select_related("participant").order_by("registered_at")

    if request.GET.get("export") == "csv":
        response = HttpResponse(content_type="text/csv; charset=utf-8")
        filename = f"inscritos_{event.title.lower().replace(' ', '_')}.csv"
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        
        # Adiciona BOM para que o Excel abra corretamente em UTF-8
        response.write('\ufeff'.encode('utf8'))
        
        writer = csv.writer(response)
        writer.writerow(["Nome", "Email", "Data de Inscrição"])
        
        for reg in registrations:
            name = reg.participant.get_full_name() or reg.participant.username
            date_str = reg.registered_at.strftime("%Y-%m-%d %H:%M:%S")
            writer.writerow([name, reg.participant.email, date_str])
            
        return response

    context = {
        "event": event,
        "registrations": registrations,
    }
    return render_page(request, "event_registrations.html", context)

@login_required
def event_create_view(request):
    errors = []
    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        category = request.POST.get("category", "other")
        description = request.POST.get("description", "").strip()
        date = request.POST.get("date")
        time = request.POST.get("time")
        location = request.POST.get("location", "").strip()
        image = request.FILES.get("image")

        if not title or not description or not date or not time or not location:
            errors.append("Todos os campos obrigatórios (*) devem ser preenchidos.")
        else:
            try:
                event = Event.objects.create(
                    title=title,
                    category=category,
                    description=description,
                    date=date,
                    time=time,
                    location=location,
                    image=image,
                    organizer=request.user
                )
                messages.success(request, "Evento criado com sucesso!")
                return redirect("my-events")
            except Exception as e:
                errors.append(f"Erro ao salvar evento: {str(e)}")

    context = {
        "categories": CATEGORIES,
        "errors": errors,
    }
    return render_page(request, "event_form.html", context)

@login_required
def event_edit_view(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if event.organizer != request.user:
        return HttpResponseForbidden("Você não tem permissão para editar este evento.")

    errors = []
    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        category = request.POST.get("category", "other")
        description = request.POST.get("description", "").strip()
        date = request.POST.get("date")
        time = request.POST.get("time")
        location = request.POST.get("location", "").strip()
        image = request.FILES.get("image")

        if not title or not description or not date or not time or not location:
            errors.append("Todos os campos obrigatórios (*) devem ser preenchidos.")
        else:
            try:
                event.title = title
                event.category = category
                event.description = description
                event.date = date
                event.time = time
                event.location = location
                if image:
                    event.image = image
                event.save()
                messages.success(request, "Evento atualizado com sucesso!")
                return redirect("my-events")
            except Exception as e:
                errors.append(f"Erro ao salvar evento: {str(e)}")

    context = {
        "event": event,
        "categories": CATEGORIES,
        "errors": errors,
    }
    return render_page(request, "event_form.html", context)
