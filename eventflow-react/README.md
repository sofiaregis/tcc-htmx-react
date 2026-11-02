# EventFlow (React + Django REST Framework)

Esta e a implementacao sob a arquitetura de Aplicacao de Pagina Unica (Single-Page Application - SPA) da plataforma **EventFlow**, composta por uma API desacoplada em **Django REST Framework** e um cliente web em **React 19** com empacotador **Vite 6**.

A aplicacao foi projetada para manter estrita paridade funcional, visual e de dados com a versao desenvolvida em HTMX (HDA), constituindo o contraponto arquitetural avaliado no Trabalho de Conclusao de Curso (TCC).

---

## 1. Caracteristicas Tecnicas

* **Backend / API:** Django 5.2 e Django REST Framework, expondo endpoints JSON para eventos, inscricoes e autenticacao com politicas de CORS (`django-cors-headers`).
* **Frontend:** React 19 estruturado com componentes funcionais, hooks nativos (`useState`, `useEffect`, `useContext`) e roteamento client-side com React Router 7.
* **Ferramenta de Build:** Vite 6 para compilacao otimizada em producao e servidor de desenvolvimento com Hot Module Replacement (HMR).
* **Estilizacao:** CSS nativo (`index.css`) com variaveis customizadas em Light Mode, identico ao design system da versao HTMX.
* **Comunicacao HTTP:** Axios configurado para envio de credenciais de sessao e tratamento de tokens CSRF.
* **Banco de Dados:** SQLite com base deterministica sincronizada com a versao HTMX.

---

## 2. Execucao Local em Desenvolvimento

A execucao em ambiente de desenvolvimento requer dois processos simultaneos: o servidor da API (Django) e o servidor de desenvolvimento do frontend (Vite).

### 2.1. Pre-requisitos

* Python 3.10 ou superior instalado.
* Node.js 20 ou superior instalado.

### 2.2. Backend (API Django REST)

```bash
# 1. Navegar ate a pasta do backend
cd eventflow-react/backend

# 2. Criar e ativar o ambiente virtual
# No Windows:
python -m venv .venv
.venv\Scripts\activate
# No Linux / macOS:
python3 -m venv .venv
source .venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Executar migracoes
python manage.py migrate

# 5. Iniciar servidor da API na porta 8000
python manage.py runserver 8000
```
A API estara acessivel em: `http://localhost:8000/api/`

### 2.3. Frontend (React 19 + Vite)

Em uma nova janela de terminal:

```bash
# 1. Navegar ate a pasta do frontend
cd eventflow-react/frontend

# 2. Instalar dependencias npm
npm install

# 3. Iniciar servidor de desenvolvimento do Vite
npm run dev
```
A interface do usuario estara acessivel em: `http://localhost:5173/`

---

## 3. Execucao Local via Docker Compose

Para executar o par backend e frontend em desenvolvimento utilizando os conteineres locais do diretorio:

```bash
cd eventflow-react
docker compose up --build
```

Os servicos iniciados serao:
* `eventflow-react-backend` na porta 8000.
* `eventflow-react-frontend` na porta 5173.

---

## 4. Execucao em Modo Producao (Conteinerizada para Benchmarks)

Para os experimentos cientificos e medicao de desempenho em ambiente de producao com limites estritos de CPU e memoria (sob Nginx e Gunicorn), utilize a configuracao centralizada em `experimento/`:

```bash
cd ../experimento
docker compose up -d --build react-backend react-frontend
```

Nessa configuracao:
* O servico `react-backend` (conteiner `efp-react-back`) executa o Django REST via Gunicorn na porta interna 8000.
* O servico `react-frontend` (conteiner `efp-react-front`) executa o Nginx na porta 5173, servindo a versao minificada e compilada do React (`dist/`) e realizando proxy reverso das requisicoes `/api/` e `/media/` para o backend.
