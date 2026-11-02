# EventFlow Frontend (React 19 + Vite)

Este diretorio contem o codigo-fonte da interface de usuario da versao SPA da plataforma **EventFlow**, desenvolvida em **React 19** utilizando **Vite 6** como ferramenta de construcao e empacotamento.

---

## 1. Scripts Disponiveis

No diretorio do frontend, estao disponiveis os seguintes comandos via npm:

* `npm install`: Instala todas as dependencias declaradas no `package.json`.
* `npm run dev`: Inicia o servidor local de desenvolvimento com Hot Module Replacement (HMR) na porta 5173.
* `npm run build`: Compila e minifica a aplicacao para producao, gerando os artefatos estaticos no diretorio `dist/`.
* `npm run lint`: Executa a verificacao estatica de codigo com ESLint.
* `npm run preview`: Executa um servidor local para inspecionar o pacote compilado em `dist/`.

---

## 2. Estrutura de Diretorios

```
frontend/
├── index.html           # Ponto de entrada HTML da aplicacao
├── vite.config.js       # Configuracoes do Vite e proxy reverso local
├── package.json         # Manifesto de dependencias e scripts
├── public/              # Arquivos publicos estaticos (favicons e icones SVG)
└── src/                 # Codigo-fonte React
    ├── api/             # Modulos de comunicacao HTTP (Axios) e gerenciamento de CSRF
    ├── assets/          # Imagens e ilustracoes estaticas
    ├── components/      # Componentes reutilizaveis (cards, navbar, carrosseis, formularios)
    ├── context/         # Contextos globais (autenticacao e sessao de usuario)
    ├── pages/           # Telas e visoes da aplicacao
    └── routes/          # Configuracao de rotas publicas e protegidas (React Router)
```
