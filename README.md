# 🚀 OmniExtract SaaS

> Inteligência de Mercado, Arbitragem de Preços e Automação para Afiliados.

O **OmniExtract** é uma plataforma full-stack focada em mineração de dados avançada e RPA (Robotic Process Automation). Desenvolvida para contornar bloqueios anti-bot de alta complexidade (como Cloudflare), extrair preços em tempo real de grandes e-commerces (Mercado Livre, KaBuM!) e consolidar oportunidades de mercado em um painel gerencial de alta performance.

## 🏆 Destaques Técnicos (Por que este projeto se destaca?)

*   **Bypass de Proteções Anti-Bot (Cloudflare):** Implementação de motores furtivos utilizando `undetected-chromedriver` para simular tráfego humano realista e contornar verificações de segurança ("Verify you are human") sem uso de APIs pagas.
*   **Parsing Inteligente e Resiliente:** Uso avançado de Expressões Regulares (Regex) e BeautifulSoup para identificar e extrair dados (como separação de parcelas vs. preço à vista), ignorando completamente a ofuscação de classes CSS dinâmica gerada por frameworks modernos (React/Next.js).
*   **Arquitetura Assíncrona Escalável:** Desacoplamento total entre a API Web e os processos pesados de automação utilizando mensageria com **Redis e RQ**. O servidor web nunca trava, independentemente do volume de varreduras simultâneas.

## 🏗️ Arquitetura e Tecnologias

**Frontend:**
* Next.js 14 & React
* Tailwind CSS
* Fetch API (Comunicação assíncrona com o backend)

**Backend & Engenharia de Dados:**
* FastAPI (Python)
* PostgreSQL (Persistência relacional via SQLModel)
* Redis & RQ (Fila de processamento em background)
* undetected-chromedriver & Selenium (Motores de navegação furtiva)
* BeautifulSoup4 & Regex (Limpeza e estruturação de dados brutos)

## ⚙️ Como funciona o fluxo do sistema

1. **Gatilho:** O usuário define um alvo (ex: Placa de Vídeo) e a loja desejada no painel B2B.
2. **Mensageria:** A requisição atinge a FastAPI, que imediatamente devolve uma resposta de sucesso para o usuário e delega o trabalho pesado para uma fila do **Redis**.
3. **Automação Furtiva:** Os *Workers* (operários em segundo plano) assumem a tarefa, abrem instâncias invisíveis de navegadores Chrome, fazem o bypass de segurança do alvo e renderizam a página completa.
4. **ETL (Extract, Transform, Load):** Os dados HTML são lidos, os textos sofrem sanitização e tipagem (removendo lixos comerciais e formatando valores decimais) e são persistidos no PostgreSQL.
5. **Dashboard:** O painel lista os dados formatados e limpos, permitindo a identificação rápida de anomalias de preço e oportunidades de arbitragem.

---
*Desenvolvido por Carlos Redoan - Foco em Automação, RPA, DevOps & Infraestrutura*