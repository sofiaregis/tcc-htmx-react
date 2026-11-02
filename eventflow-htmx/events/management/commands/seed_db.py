import os
import random
import requests
import shutil
from datetime import timedelta
from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import connections
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from events.models import Event, Registration
from faker import Faker

TITLE_TEMPLATES = {
    "tech": {
        "prefixes": [
            "Workshop de", "Curso Avançado de", "Apresentação sobre", "Simpósio de", 
            "Encontro de", "Fórum de", "Imersão em", "Hackathon de", "Bootcamp de", 
            "Palestra sobre", "Jornada de", "Mesa Redonda de", "Congresso de", "Conferência de"
        ],
        "suffixes": [
            "Python para Iniciantes", "React e Hooks Avançados", "Machine Learning & IA", 
            "Segurança da Informação", "Desenvolvimento Web Moderno", "Banco de Dados NoSQL", 
            "Arquitetura Cloud & AWS", "DevOps & Docker", "Desenvolvimento Go", 
            "Sistemas Distribuídos", "Desenvolvimento de APIs REST", "TypeScript no Backend"
        ]
    },
    "business": {
        "prefixes": [
            "Palestra de", "Seminário de", "Mesa Redonda sobre", "Workshop de", 
            "Conferência de", "Fórum de", "Painel sobre", "Masterclass de", "Simpósio de"
        ],
        "suffixes": [
            "Liderança e Gestão de Pessoas", "Growth Hacking & Vendas", "Startups e Captação de Recursos", 
            "Marketing Digital Estratégico", "Planejamento Financeiro", "Oratória e Negociação", 
            "Design Thinking no Negócio", "Gestão de Projetos Ágeis", "Estratégia Corporativa"
        ]
    },
    "art": {
        "prefixes": [
            "Exposição de", "Oficina de", "Mostra de", "Galeria de", "Festival de",
            "Workshop de", "Curso de", "Encontro de"
        ],
        "suffixes": [
            "Escultura Contemporânea", "Pintura em Aquarela", "Design e Ilustração", 
            "Teatro e Expressão Corporal", "Cinema Independente", "História da Arte",
            "Cerâmica Artesanal", "Xilogravura e Gravura", "Dança Moderna"
        ]
    },
    "sports": {
        "prefixes": [
            "Torneio de", "Campeonato de", "Maratona de", "Copa de", "Treinamento de",
            "Circuito de", "Desafio de", "Jornada de"
        ],
        "suffixes": [
            "Crossfit Amador", "Corrida de Rua 10k", "Futebol Society", 
            "Basquete de Rua 3x3", "Vôlei de Praia", "Ciclismo de Estrada",
            "Natação em Águas Abertas", "Corrida de Obstáculos", "Tênis de Mesa"
        ]
    },
    "music": {
        "prefixes": [
            "Show de", "Festival de", "Apresentação de", "Concerto de", "Noite de",
            "Jam Session de", "Tributo a", "Recital de"
        ],
        "suffixes": [
            "Jazz & Blues", "Música Popular Brasileira", "Rock Clássico", 
            "Música Eletrônica", "Piano Clássico", "Hip Hop & Rap",
            "Heavy Metal Nacional", "Samba e Pagode de Mesa", "Indie Rock"
        ]
    },
    "education": {
        "prefixes": [
            "Seminário de", "Palestra sobre", "Fórum de", "Congresso de", "Jornada de",
            "Painel de", "Colóquio de", "Simpósio de"
        ],
        "suffixes": [
            "Metodologias Ativas de Ensino", "Educação Financeira Infantil", 
            "Tecnologia na Sala de Aula", "Políticas Públicas de Educação", "Escrita Criativa", 
            "Inclusão Escolar e Acessibilidade", "Alfabetização Científica", "Inovação Pedagógica"
        ]
    },
    "health": {
        "prefixes": [
            "Retiro de", "Aulão de", "Palestra sobre", "Jornada de", "Simpósio de",
            "Oficina de", "Encontro de", "Circuito de"
        ],
        "suffixes": [
            "Yoga e Meditação", "Nutrição Funcional", "Saúde Mental no Trabalho", 
            "Pilates Clínico", "Hábitos Saudáveis no Cotidiano", "Treino Funcional",
            "Detox e Mindfulness", "Prevenção do Estresse", "Longevidade Saudável"
        ]
    },
    "food": {
        "prefixes": [
            "Oficina de", "Degustação de", "Masterclass de", "Curso de", "Festival de",
            "Feira de", "Circuito de", "Encontro de"
        ],
        "suffixes": [
            "Culinária Italiana", "Cervejas Artesanais", "Panificação Artesanal", 
            "Doces Gourmet", "Cozinha Vegana", "Vinhos Importados",
            "Gastronomia Japonesa", "Chocolates Finos", "Cozinha Brasileira de Raiz"
        ]
    },
    "environment": {
        "prefixes": [
            "Mutirão de", "Workshop sobre", "Palestra de", "Encontro de", "Fórum de",
            "Painel sobre", "Jornada de"
        ],
        "suffixes": [
            "Reciclagem e Lixo Zero", "Preservação da Fauna Local", "Energia Solar Residencial", 
            "Hortas Urbanas Coletivas", "Sustentabilidade no Cotidiano", "Consumo Consciente",
            "Arquitetura Ecológica", "Reflorestamento Urbano"
        ]
    },
    "photography": {
        "prefixes": [
            "Oficina de", "Workshop de", "Saída Fotográfica de", "Exposição de",
            "Curso de", "Apresentação de"
        ],
        "suffixes": [
            "Retrato em Luz Natural", "Fotografia de Paisagem", "Técnicas de Iluminação de Estúdio", 
            "Fotografia de Eventos", "Edição no Lightroom e Photoshop", "Street Photography",
            "Fotografia com Smartphones", "Composição Visual"
        ]
    },
    "other": {
        "prefixes": [
            "Encontro de", "Feira de", "Palestra sobre", "Workshop de", "Celebração de",
            "Festival de", "Oficina de"
        ],
        "suffixes": [
            "Jogos de Tabuleiro", "Artesanato e Patchwork", "Filosofia Moderna", 
            "Astronomia Amadora", "Organização Doméstica", "Criatividade e Inovação",
            "RPG de Mesa", "Antiguidades e Colecionismo"
        ]
    }
}

SUFFIX_KEYWORDS = {
    # Tech
    "Python para Iniciantes": "python,code",
    "React e Hooks Avançados": "reactjs,code",
    "Machine Learning & IA": "artificialintelligence,machinelearning",
    "Segurança da Informação": "cybersecurity,hacker",
    "Desenvolvimento Web Moderno": "webdevelopment,website",
    "Banco de Dados NoSQL": "database,server",
    "Arquitetura Cloud & AWS": "cloud,server",
    "DevOps & Docker": "devops,docker",
    "Desenvolvimento Go": "golang,code",
    "Sistemas Distribuídos": "network,server",
    "Desenvolvimento de APIs REST": "api,code",
    "TypeScript no Backend": "typescript,code",
    # Business
    "Liderança e Gestão de Pessoas": "leadership,business",
    "Growth Hacking & Vendas": "sales,growth",
    "Startups e Captação de Recursos": "startup,money",
    "Marketing Digital Estratégico": "marketing,digital",
    "Planejamento Financeiro": "finance,money",
    "Oratória e Negociação": "speech,meeting",
    "Design Thinking no Negócio": "designthinking,business",
    "Gestão de Projetos Ágeis": "agile,scrum",
    "Estratégia Corporativa": "strategy,business",
    # Art
    "Escultura Contemporânea": "sculpture,museum",
    "Pintura em Aquarela": "watercolor,painting",
    "Design e Ilustração": "illustration,design",
    "Teatro e Expressão Corporal": "theater,acting",
    "Cinema Independente": "cinema,movie",
    "História da Arte": "art,history",
    "Cerâmica Artesanal": "pottery,ceramic",
    "Xilogravura e Gravura": "woodcut,engraving",
    "Dança Moderna": "dance,performance",
    # Sports
    "Crossfit Amador": "crossfit,fitness",
    "Corrida de Rua 10k": "running,marathon",
    "Futebol Society": "soccer,football",
    "Basquete de Rua 3x3": "basketball,hoop",
    "Vôlei de Praia": "beach,volleyball",
    "Ciclismo de Estrada": "cycling,bike",
    "Natação em Águas Abertas": "swimming,lake",
    "Corrida de Obstáculos": "obstacle,race",
    "Tênis de Mesa": "pingpong",
    # Music
    "Jazz & Blues": "jazz,blues",
    "Música Popular Brasileira": "guitar,acoustic",
    "Rock Clássico": "rockband,guitar",
    "Música Eletrônica": "dj,electronicmusic",
    "Piano Clássico": "piano,classical",
    "Hip Hop & Rap": "hiphop,rap",
    "Heavy Metal Nacional": "heavymetal,concert",
    "Samba e Pagode de Mesa": "samba,instruments",
    "Indie Rock": "indierock,concert",
    # Education
    "Metodologias Ativas de Ensino": "teaching,classroom",
    "Educação Financeira Infantil": "kids,money",
    "Tecnologia na Sala de Aula": "classroom,laptop",
    "Políticas Públicas de Educação": "education,lecture",
    "Escrita Criativa": "writing,creative",
    "Inclusão Escolar e Acessibilidade": "accessibility,inclusion",
    "Alfabetização Científica": "science,education",
    "Inovação Pedagógica": "classroom,innovation",
    # Health
    "Yoga e Meditação": "yoga,meditation",
    "Nutrição Funcional": "nutrition,healthyfood",
    "Saúde Mental no Trabalho": "mentalhealth,office",
    "Pilates Clínico": "pilates,fitness",
    "Hábitos Saudáveis no Cotidiano": "healthy,habits",
    "Treino Funcional": "workout,gym",
    "Detox e Mindfulness": "detox,mindfulness",
    "Prevenção do Estresse": "stressrelief,calm",
    "Longevidade Saudável": "elderly,active",
    # Food
    "Culinária Italiana": "italian,food",
    "Cervejas Artesanais": "craftbeer,mug",
    "Panificação Artesanal": "bread,baking",
    "Doces Gourmet": "dessert,chocolate",
    "Cozinha Vegana": "vegan,food",
    "Vinhos Importados": "wine,bottle",
    "Gastronomia Japonesa": "japanese,sushi",
    "Chocolates Finos": "chocolate,sweets",
    "Cozinha Brasileira de Raiz": "brazilian,food",
    # Environment
    "Reciclagem e Lixo Zero": "recycling,zerowaste",
    "Preservação da Fauna Local": "wildlife,animals",
    "Energia Solar Residencial": "solarpanel,roof",
    "Hortas Urbanas Coletivas": "urban,garden",
    "Sustentabilidade no Cotidiano": "sustainability,green",
    "Consumo Consciente": "shopping,organic",
    "Arquitetura Ecológica": "greenbuilding,house",
    "Reflorestamento Urbano": "planting,trees",
    # Photography
    "Retrato em Luz Natural": "portrait,photography",
    "Fotografia de Paisagem": "landscape,photography",
    "Técnicas de Iluminação de Estúdio": "studio,lighting",
    "Fotografia de Eventos": "event,photography",
    "Edição no Lightroom e Photoshop": "photoediting,software",
    "Street Photography": "street,photography",
    "Fotografia com Smartphones": "mobile,photography",
    "Composição Visual": "photography,composition",
    # Other
    "Jogos de Tabuleiro": "boardgames",
    "Artesanato e Patchwork": "craft,sewing",
    "Filosofia Moderna": "philosophy,books",
    "Astronomia Amadora": "astronomy,telescope",
    "Organização Doméstica": "closet,organized",
    "Criatividade e Inovação": "brainstorming,creative",
    "RPG de Mesa": "rpg,dice",
    "Antiguidades e Colecionismo": "antique,collecting"
}

CATEGORY_IMAGES = {
    "tech": "https://images.unsplash.com/photo-1517694712202-14dd9538aa97?w=800",
    "business": "https://images.unsplash.com/photo-1552664730-d307ca884978?w=800",
    "art": "https://images.unsplash.com/photo-1561070791-2526d30994b5?w=800",
    "sports": "https://images.unsplash.com/photo-1506126613408-eca07ce68773?w=800",
    "music": "https://images.unsplash.com/photo-1470225620780-dba8ba36b745?w=800",
    "education": "https://images.unsplash.com/photo-1524178232363-1fb2b075b655?w=800",
    "health": "https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?w=800",
    "food": "https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=800",
    "environment": "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=800",
    "photography": "https://images.unsplash.com/photo-1516035069371-29a1b244cc32?w=800",
    "other": "https://images.unsplash.com/photo-1513151233558-d860c5398176?w=800",
}

class Command(BaseCommand):
    help = "Seeds database from scratch with organizers, participants, events, and registrations."

    def add_arguments(self, parser):
        parser.add_argument(
            "--events",
            type=int,
            default=700,
            help="Number of future events to generate",
        )
        parser.add_argument(
            "--past-events",
            type=int,
            default=200,
            help="Number of past events to generate",
        )
        parser.add_argument(
            "--today-events",
            type=int,
            default=100,
            help="Number of today events to generate",
        )
        parser.add_argument(
            "--organizers",
            type=int,
            default=500,
            help="Number of organizers to generate",
        )
        parser.add_argument(
            "--participants",
            type=int,
            default=10000,
            help="Number of participants to generate",
        )

    def handle(self, *args, **options):
        fake = Faker("pt_BR")
        hashed_password = make_password("password123")

        # 1. Close active connections and remove database & images directories
        self.stdout.write("Fechando conexões ativas com o banco de dados...")
        connections.close_all()

        db_path = settings.DATABASES['default']['NAME']
        if os.path.exists(db_path):
            self.stdout.write(f"Limpando banco de dados: {db_path}...")
            try:
                with open(db_path, "wb") as f:
                    f.truncate(0)
                self.stdout.write(self.style.SUCCESS("Banco de dados truncado e limpo com sucesso."))
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"Não foi possível truncar ({e}). Limpando tabelas existentes via ORM..."))
                try:
                    Registration.objects.all().delete()
                    Event.objects.all().delete()
                    User.objects.filter(is_superuser=False).delete()
                    self.stdout.write(self.style.SUCCESS("Tabelas limpas com sucesso."))
                except Exception as del_err:
                    self.stdout.write(self.style.WARNING(f"Erro na limpeza de tabelas: {del_err}"))

        images_dir = os.path.join(settings.MEDIA_ROOT, "event_images")
        if os.path.exists(images_dir):
            self.stdout.write(f"Removendo diretório de imagens antigo: {images_dir}...")
            try:
                shutil.rmtree(images_dir)
                self.stdout.write(self.style.SUCCESS("Imagens antigas removidas com sucesso."))
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"Não foi possível remover o diretório de imagens: {e}"))

        os.makedirs(images_dir, exist_ok=True)

        # 2. Run migrations
        self.stdout.write("Executando migrações do banco de dados (novas tabelas)...")
        call_command("migrate", interactive=False)
        self.stdout.write(self.style.SUCCESS("Migrações concluídas."))

        # 3. Download category base fallback images
        self.stdout.write("Preparando imagens base de categorias (fallbacks)...")
        for cat, url in CATEGORY_IMAGES.items():
            file_path = os.path.join(images_dir, f"seed_{cat}.jpg")
            if not os.path.exists(file_path):
                self.stdout.write(f"Baixando imagem base para '{cat}'...")
                try:
                    res = requests.get(url, timeout=10)
                    if res.status_code == 200:
                        with open(file_path, "wb") as f:
                            f.write(res.content)
                    else:
                        self.stdout.write(self.style.WARNING(f"Falha ao baixar imagem para '{cat}', status {res.status_code}"))
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f"Erro ao baixar imagem para '{cat}': {e}"))

        # 4. Generate clean organizers without org_ prefix
        self.stdout.write(f"Gerando {options['organizers']} organizadores...")
        orgs_to_create = []
        for _ in range(options["organizers"]):
            username = fake.user_name()
            while User.objects.filter(username=username).exists() or any(u.username == username for u in orgs_to_create):
                username = f"{fake.user_name()}_{random.randint(100, 999)}"
            
            orgs_to_create.append(User(
                username=username,
                email=fake.email(),
                password=hashed_password,
                first_name=fake.first_name(),
                last_name=fake.last_name()
            ))
        User.objects.bulk_create(orgs_to_create)
        organizers = list(User.objects.filter(is_superuser=False))

        # 5. Generate clean participants without part_ prefix
        self.stdout.write(f"Gerando {options['participants']} participantes...")
        parts_to_create = []
        for _ in range(options["participants"]):
            username = fake.user_name()
            while User.objects.filter(username=username).exists() or any(u.username == username for u in parts_to_create):
                username = f"{fake.user_name()}_{random.randint(100, 999)}"
            
            parts_to_create.append(User(
                username=username,
                email=fake.email(),
                password=hashed_password,
                first_name=fake.first_name(),
                last_name=fake.last_name()
            ))
        User.objects.bulk_create(parts_to_create)
        
        all_users = list(User.objects.filter(is_superuser=False))
        organizer_ids = set(u.id for u in organizers)
        participants = [u for u in all_users if u.id not in organizer_ids]

        # 6. Generate events
        past_count = options["past_events"]
        today_count = options["today_events"]
        future_count = options["events"]
        total_events = past_count + today_count + future_count

        self.stdout.write(f"Gerando {total_events} eventos ({past_count} passados, {today_count} de hoje, {future_count} futuros)...")
        events_to_create = []
        categories_keys = list(TITLE_TEMPLATES.keys())

        now = timezone.localtime()
        event_dates = []
        for _ in range(past_count):
            event_dates.append((now - timedelta(days=random.randint(1, 180)), True, False))
        for _ in range(today_count):
            event_dates.append((now, False, True))
        for _ in range(future_count):
            event_dates.append((now + timedelta(days=random.randint(1, 120)), False, False))

        random.shuffle(event_dates)

        created_titles = set()
        for i, (dt, is_past, is_today) in enumerate(event_dates):
            category = random.choice(categories_keys)
            template = TITLE_TEMPLATES[category]
            prefix = random.choice(template["prefixes"])
            suffix = random.choice(template["suffixes"])
            title = f"{prefix} {suffix}"

            while title in created_titles or Event.objects.filter(title=title).exists():
                title = f"{prefix} {suffix} - {fake.word().capitalize()}"
            created_titles.add(title)

            description = fake.paragraph(nb_sentences=random.randint(4, 7))
            location = f"{fake.street_name()}, {fake.building_number()} - {fake.city()}, {fake.state_abbr()}"
            organizer = random.choice(organizers)

            # Random time: rounded to 15 mins
            hour = random.choice([8, 9, 10, 11, 14, 15, 16, 17, 18, 19, 20])
            minute = random.choice([0, 15, 30, 45])
            time_obj = timezone.datetime.strptime(f"{hour:02d}:{minute:02d}", "%H:%M").time()

            # Resolve image (using unique cached image based on suffix)
            suffix_slug = suffix.lower().replace(" ", "_").replace("&", "and")
            image_name = f"seed_suffix_{suffix_slug}.jpg"
            image_path = os.path.join(images_dir, image_name)
            relative_image_path = f"event_images/{image_name}"

            if not os.path.exists(image_path):
                # Download suffix image
                keywords = SUFFIX_KEYWORDS.get(suffix, category)
                self.stdout.write(f"Baixando imagem customizada para '{suffix}' ({keywords})...")
                try:
                    res = requests.get(f"https://loremflickr.com/800/600/{keywords}", timeout=10)
                    if res.status_code == 200:
                        with open(image_path, "wb") as f:
                            f.write(res.content)
                    else:
                        relative_image_path = f"event_images/seed_{category}.jpg"
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f"Erro ao baixar imagem para '{suffix}': {e}"))
                    relative_image_path = f"event_images/seed_{category}.jpg"

            # Check if file exists, if not fallback
            if not os.path.exists(os.path.join(settings.MEDIA_ROOT, relative_image_path)):
                relative_image_path = f"event_images/seed_{category}.jpg"

            events_to_create.append(Event(
                title=title,
                description=description,
                location=location,
                date=dt.date(),
                time=time_obj,
                category=category,
                organizer=organizer,
                image=relative_image_path
            ))

        Event.objects.bulk_create(events_to_create)
        all_events = list(Event.objects.all())
        self.stdout.write(self.style.SUCCESS(f"{len(events_to_create)} eventos criados!"))

        # 7. Generate random registrations
        self.stdout.write("Gerando inscrições aleatórias...")
        registrations_to_create = []
        for part in participants:
            k = random.randint(2, 6)
            selected_events = random.sample(all_events, min(k, len(all_events)))
            for ev in selected_events:
                if ev.organizer == part:
                    continue
                registrations_to_create.append(Registration(
                    event=ev,
                    participant=part
                ))

        Registration.objects.bulk_create(registrations_to_create, ignore_conflicts=True)
        self.stdout.write(self.style.SUCCESS("Banco de dados populado com sucesso!"))
