# MCP Tool – Funcionalidades

## 1. Interações com a Página

### 1.1 browser_snapshot  
- **Título:** Page snapshot  
- **Descrição:** Captura um “snapshot” de acessibilidade da página atual (melhor que um screenshot).  
- **Parâmetros:** nenhum  
- **Read‑only:** sim  

### 1.2 browser_click  
- **Título:** Click  
- **Descrição:** Executa um clique em um elemento da página.  
- **Parâmetros:**  
  - `element` (string): descrição legível para solicitar permissão.  
  - `ref` (string): referência exata do elemento.  
- **Read‑only:** não  

### 1.3 browser_drag  
- **Título:** Drag mouse  
- **Descrição:** Arrasta (drag & drop) de um elemento de origem para um elemento de destino.  
- **Parâmetros:**  
  - `startElement` (string), `startRef` (string): fonte.  
  - `endElement` (string), `endRef` (string): destino.  
- **Read‑only:** não  

### 1.4 browser_hover  
- **Título:** Hover mouse  
- **Descrição:** Posiciona o cursor sobre um elemento.  
- **Parâmetros:**  
  - `element` (string)  
  - `ref` (string)  
- **Read‑only:** sim  

### 1.5 browser_type  
- **Título:** Type text  
- **Descrição:** Digita texto em um campo editável.  
- **Parâmetros:**  
  - `element` (string), `ref` (string)  
  - `text` (string): texto a digitar  
  - `submit` (boolean, opcional): pressiona Enter ao fim  
  - `slowly` (boolean, opcional): digita caractere a caractere  
- **Read‑only:** não  

### 1.6 browser_select_option  
- **Título:** Select option  
- **Descrição:** Seleciona opção(s) em um dropdown.  
- **Parâmetros:**  
  - `element` (string), `ref` (string)  
  - `values` (array): valor ou valores a selecionar  
- **Read‑only:** não  

### 1.7 browser_press_key  
- **Título:** Press a key  
- **Descrição:** Pressiona uma tecla no teclado.  
- **Parâmetros:**  
  - `key` (string): nome da tecla ou caractere (ex.: ArrowLeft, “a”)  
- **Read‑only:** não  

### 1.8 browser_wait_for  
- **Título:** Wait for  
- **Descrição:**
