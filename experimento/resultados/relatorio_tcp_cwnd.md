# Relatório de Transporte TCP e Janela de Congestionamento (cwnd)

Este relatório apresenta a análise empírica da camada de transporte TCP durante o **carregamento inicial completo (Cold Start)** 
da página principal (**Home**), englobando todo o tráfego de rede (HTML, JavaScript, CSS, chamadas de API e imagens do catálogo em `/media/`), 
avaliado no cenário **sem latência adicional (NoThrottling / Rede Local)** com isolamento estrito entre as coletas.

## 1. Síntese Comparativa de Transporte TCP

| Parâmetro de Transporte | HTMX 2 (HDA) | React 19 (SPA) | Variação / Relação |
| :--- | :--- | :--- | :--- |
| Carga Total Transferida (Wire Payload) | 932.88 KB | 1027.34 KB | +10.1% no React |
| Pico de Bytes em Trânsito (Max Bytes in Flight) | 98.60 KB | 119.09 KB | React demanda 1.2x mais buffer |
| Janela Inicial Padrão Linux (initcwnd) | 14.6 KB (10 MSS) | 14.6 KB (10 MSS) | Base idêntica de kernel |
| Fator de Expansão sobre a Janela Inicial | 6.8x a initcwnd | 8.2x a initcwnd | Aumento substancial no React |
| Conexões TCP Paralelas Utilizadas | 4 conexão(ões) | 6 conexão(ões) | Concorrência de streams |
| Duração da Transferência de Rede Local | 54.38 ms | 251.08 ms | Velocidade basal de esgotamento |

---

## 2. Discussão da Dinâmica de Janela e Entrega de Ativos

### 2.1 Demanda de Buffer no Servidor

Mesmo no ambiente local sem latência, a pilha de rede do kernel Linux (Nginx) precisou expandir a janela de trânsito para **119.1 KB** no React, 
contra **98.6 KB** no HTMX. Isso demonstra que o modelo SPA impõe uma pressão de alocação de buffers de socket significativamente maior ao sistema operacional.

### 2.2 Perfil Temporal: Fluxo Unificado vs. Cascata em Duas Ondas

- **HTMX (Fluxo Unificado):** Ao receber o documento HTML renderizado no servidor com as tags de imagem já declaradas, o navegador dispara as conexões para estilos, scripts e imagens em um único bloco paralelo e contínuo.

- **React (Cascata em Duas Fases):** O navegador precisa primeiro receber e executar o bundle JavaScript e estilos (comprimidos via Gzip em ~118 KB) e aguardar o retorno da API REST antes que as URLs das imagens possam ser descobertas. Isso cria uma divisão nítida no tráfego TCP em duas ondas sequenciais, retardando a inicialização das conexões de mídia.
