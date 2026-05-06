# 🚀 OmniExtract SaaS

### Inteligência de Mercado, Arbitragem de Preços e Automação para Afiliados.

O **OmniExtract** é uma plataforma full-stack focada em mineração de dados avançada. Desenvolvida para contornar bloqueios, extrair preços em tempo real e consolidar oportunidades de mercado em um painel gerencial de alta performance.

> **⚠️ Status do Projeto: Prova de Conceito (PoC)**
> Este repositório é um laboratório técnico focado em demonstrar **arquitetura de microsserviços, processamento assíncrono e engenharia de dados**. Como os e-commerces alvo alteram constantemente suas estruturas de segurança e HTML, os scripts de scraping podem necessitar de ajustes periódicos nos seletores de dados.

---

## 🏗️ Arquitetura e Tecnologias

Este projeto foi construído utilizando as melhores práticas de **RPA (Robotic Process Automation)** e arquitetura distribuída, garantindo que o sistema permaneça responsivo mesmo durante varreduras pesadas.

### **Frontend:**
* **Framework:** Next.js 14 & React
* **Estilização:** Tailwind CSS
* **Comunicação:** Fetch API integrada ao fluxo assíncrono do backend.

### **Backend & Engenharia de Dados:**
* **API:** FastAPI (Python) - Processamento de alta performance.
* **Banco de Dados:** PostgreSQL (Persistência via SQLModel).
* **Mensageria/Fila:** Redis & RQ (Redis Queue) para orquestração de tarefas em background.
* **Motores de Extração:** BeautifulSoup4 e lógica de bypass de segurança.

---

## ⚙️ Como funciona o Motor de Extração

1.  **Requisição:** O usuário aciona um termo de busca no painel.
2.  **Fila (Broker):** A API recebe o pedido e delega a tarefa para o **Redis**, liberando o servidor imediatamente.
3.  **Processamento:** Os **Workers** (operários em segundo plano) detectam o novo trabalho, acessam o site alvo e extraem os dados.
4.  **Persistência:** Os dados são limpos, tipados e salvos no **PostgreSQL**.
5.  **Visualização:** O frontend consome os dados salvos e exibe as oportunidades com tags de precificação inteligente.

---

## 🛠️ Como rodar o ecossistema localmente

Siga esta sequência para garantir que todos os serviços se comuniquem:

### **1. Banco de Dados e Cache (Docker)**
Certifique-se de que os serviços de infraestrutura estão online:
```bash
docker start omniextract_db redis-omniextract
```

### **2. Backend (API)**
Na pasta `/backend` (com o venv ativo):
```bash
uvicorn main:app --reload --port 8002
```

### **3. Worker (Motor de Raspagem)**
Em um novo terminal (com o venv ativo na pasta do backend):
```bash
rq worker --url redis://localhost:6380
```

### **4. Frontend (Interface)**
Na pasta `/frontend`:
```bash
npm run dev
```
Acesse: `http://localhost:3000`

---

## 👨‍💻 Desenvolvido por
**Carlos Redoan** - *Foco em Automação, RPA & Infraestrutura*
