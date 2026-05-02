# 🚀 OmniExtract SaaS

> Inteligência de Mercado, Arbitragem de Preços e Automação para Afiliados.

O **OmniExtract** é uma plataforma full-stack focada em mineração de dados avançada. Desenvolvida para contornar bloqueios, extrair preços em tempo real e consolidar oportunidades de mercado em um painel gerencial de alta performance.

## 🏗️ Arquitetura e Tecnologias

Este projeto foi construído utilizando as melhores práticas de RPA (Robotic Process Automation) e arquitetura assíncrona, garantindo que o servidor nunca trave durante varreduras pesadas.

**Frontend:**
* Next.js 14 & React
* Tailwind CSS
* Fetch API para comunicação assíncrona

**Backend & Engenharia de Dados:**
* FastAPI (Python)
* PostgreSQL (Persistência via SQLModel)
* Redis & RQ (Fila de processamento em background / Mensageria)
* BeautifulSoup4 & Requests (Motores de extração e RPA)

## ⚙️ Como funciona o Motor de Extração

1. O usuário aciona um alvo no painel B2B.
2. A requisição bate na FastAPI, que delega o trabalho pesado para uma fila do **Redis**.
3. Os *Workers* (operários em segundo plano) assumem a tarefa, fazem o bypass de segurança do site alvo (ex: Mercado Livre) e raspam os dados HTML.
4. Os dados são limpos, tipados e salvos no PostgreSQL.
5. O painel reage em tempo real exibindo as oportunidades com tags de precificação inteligente.

---
*Desenvolvido por Carlos Redoan - Foco em Automação, RPA & Infraestrutura*