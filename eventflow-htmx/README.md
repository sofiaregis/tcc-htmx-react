# EventFlow (Django + HTMX)

Esta e a implementacao sob a arquitetura de Aplicacao Orientada a Hipermidia (Hypermedia-Driven Application - HDA) da plataforma **EventFlow**, desenvolvida com **Django 5.2** e **HTMX 2.0**.

A aplicacao foi projetada para manter estrita paridade funcional, visual e de dados com a versao desenvolvida em React (SPA), servindo como base para os experimentos comparativos de desempenho e produtividade de software no Trabalho de Conclusao de Curso (TCC).

---

## 1. Caracteristicas Tecnicas

* **Backend e Renderizacao:** Django 5.2 utilizando o padrao Model-View-Template (MVT), unificando roteamento e apresentacao no servidor.
* **Interacoes Dinamicas:** HTMX 2.0 (distribuido localmente em `static/js/htmx.min.js`), gerenciando requisicoes assincronas e substituicao parcial do DOM via atributos `hx-get`, `hx-post`, `hx-delete`, `hx-target` e `hx-swap`.
* **Estilizacao:** CSS nativo (`static/css/index.css`) com variaveis customizadas em Light Mode, identico ao design system da versao React.
* **Componentes Interativos:** Script nativo em JavaScript (`static/js/carousel.js`) para suporte a rolagem horizontal nos carrosseis da pagina inicial com degradacao progressiva.
* **Banco de Dados:** SQLite com base deterministica sincronizada via comando de seed.
* **Sessao e Autenticacao:** Gerenciamento nativo de sessao do Django via cookies HttpOnly.

---

## 2. Execucao Local em Desenvolvimento

### 2.1. Pre-requisitos

* Python 3.10 ou superior instalado.

### 2.2. Configuracao do Ambiente Virtual

```bash
# 1. Navegar ate o diretorio do projeto
cd eventflow-htmx

# 2. Criar ambiente virtual
python -m venv .venv

# 3. Ativar o ambiente virtual
# No Windows:
.venv\Scripts\activate
# No Linux / macOS:
source .venv/bin/activate

# 4. Instalar as dependencias
pip install -r requirements.txt
```

### 2.3. Banco de Dados e Populacao (Seed)

O arquivo `db.sqlite3` ja contem a massa inicial deterministica de dados. Caso deseje resetar e repopular a base:

```bash
# Executar migracoes pendentes
python manage.py migrate

# Popular com valores padrao (30 organizadores, 1000 participantes, 300 eventos)
python manage.py seed_db

# Limpar tabelas antes de popular
python manage.py seed_db --clear

# Customizar quantidade de registros
python manage.py seed_db --events 500 --organizers 50 --participants 2000
```

### 2.4. Inicializacao do Servidor

```bash
python manage.py runserver 8080
```

A aplicacao ficara disponivel em: `http://localhost:8080/`

---

## 3. Execucao em Modo Producao (Conteinerizada)

Para execucao conteinerizada e benchmarking sob Nginx e Gunicorn, utilize a configuracao centralizada disponivel no diretorio `experimento/`:

```bash
cd ../experimento
docker compose up -d --build htmx-backend htmx-frontend
```

Nessa configuracao:
* O servico `htmx-backend` (conteiner `efp-htmx-back`) executa o Django via Gunicorn na porta interna 8000.
* O servico `htmx-frontend` (conteiner `efp-htmx-front`) executa o Nginx na porta 8080, servindo arquivos estaticos e de midia diretamente e encaminhando requisicoes dinamicas ao Gunicorn.
