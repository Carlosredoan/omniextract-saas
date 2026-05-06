import os
import time
import random
import re
import pandas as pd
from bs4 import BeautifulSoup
from sqlmodel import Session, create_engine
from dotenv import load_dotenv
import undetected_chromedriver as uc

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

def extrair_detalhes_pagamento(texto_bruto):
    """Lógica inteligente para dissecar preços e parcelas do texto bruto"""
    detalhes = {
        "preco_a_vista": 0.0,
        "preco_prazo": 0.0,
        "max_parcelas": 1,
        "valor_parcela": 0.0,
        "taxa_juros": True,
        "status_estoque": "disponivel"
    }
    
    texto_lower = texto_bruto.lower()
    
    # 1. Scanner de Parcelas
    match_parcela = re.search(r'(\d+)\s*x\s*(?:de\s*)?(?:r\$)?\s*([\d\.,]+)', texto_lower)
    if match_parcela:
        detalhes["max_parcelas"] = int(match_parcela.group(1))
        val_str = match_parcela.group(2).replace('.', '').replace(',', '.')
        try:
            detalhes["valor_parcela"] = float(val_str)
        except: pass

    if "sem juros" in texto_lower:
        detalhes["taxa_juros"] = False
    if "estoque indisponível" in texto_lower or "esgotado" in texto_lower:
        detalhes["status_estoque"] = "esgotado"

    # 2. Scanner de preços R$
    matches = re.findall(r'r\$\s*\n*\s*([\d\.,]+)', texto_lower)
    precos = []
    for m in matches:
        v = m.replace('.', '').replace(',', '.')
        try:
            precos.append(float(v))
        except: pass

    if precos:
        precos_filtrados = [p for p in precos if abs(p - detalhes["valor_parcela"]) > 0.01]
        if not precos_filtrados:
            precos_filtrados = precos

        detalhes["preco_a_vista"] = min(precos_filtrados)

        if detalhes["max_parcelas"] > 1 and detalhes["valor_parcela"] > 0:
            estimativa = detalhes["max_parcelas"] * detalhes["valor_parcela"]
            detalhes["preco_prazo"] = min(precos_filtrados, key=lambda x: abs(x - estimativa))
        else:
            detalhes["preco_prazo"] = detalhes["preco_a_vista"]

    return detalhes

def extrair_mercado_livre(produto_alvo):
    from main import ProdutoMinerado 

    print(f"\n🕵️‍♂️ [ML] Iniciando varredura FURTIVA por: {produto_alvo}...")
    
    options = uc.ChromeOptions()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    driver = uc.Chrome(options=options, version_main=147)
    
    termo_busca = produto_alvo.replace(' ', '-')
    url = f"https://lista.mercadolivre.com.br/{termo_busca}"
    
    lista_temp = []
    
    try:
        driver.get(url)
        print("⏳ [ML] Aguardando renderização da página...")
        time.sleep(6) # Aumentei 1 segundinho para garantir
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # --- O NOVO CAÇADOR DO MERCADO LIVRE ---
        # Procura pelo padrão antigo OU pelo novo padrão "poly-card"
        itens = soup.select('.ui-search-layout__item, .poly-card, .ui-search-result__wrapper')
        
        if not itens:
            print("⚠️ [ML] Nenhum item achado no HTML! Tirando foto de segurança...")
            driver.save_screenshot('debug_ml.png')
            print("📸 [ML] Foto salva como debug_ml.png. Verifique o arquivo!")
            return
        
        print(f"🎯 [ML] Achamos {len(itens)} produtos! Extraindo...")

        for item in itens:
            try:
                texto_bruto = item.get_text(separator="\n")
                linhas = [l.strip() for l in texto_bruto.split('\n') if l.strip()]
                
                titulo = next((l for l in linhas if len(l) > 20 and "venda" not in l.lower()), "Sem Título")
                link_elem = item.find('a')
                link = link_elem['href'] if link_elem else ""
                
                dados_pagamento = extrair_detalhes_pagamento(texto_bruto)
                
                if dados_pagamento["preco_a_vista"] > 0:
                    lista_temp.append({
                        "termo_busca": produto_alvo,
                        "titulo": titulo,
                        "link": link,
                        **dados_pagamento
                    })
            except: continue

        if lista_temp:
            precos = [p['preco_a_vista'] for p in lista_temp]
            mediana = pd.Series(precos).median()
            piso = mediana * 0.40
            
            with Session(engine) as session:
                for dado in lista_temp:
                    is_op = bool(piso <= dado["preco_a_vista"] <= mediana)
                    
                    novo_prod = ProdutoMinerado(
                        **dado,
                        is_oportunidade=is_op
                    )
                    session.add(novo_prod)
                    
                    status = "🔥 [OP]" if is_op else "✅ [OK]"
                    print(f"{status} Gravado: R${dado['preco_a_vista']:.2f} - {dado['titulo'][:30]}...")
                
                session.commit()
                print(f"🏁 [ML] Extração concluída! {len(lista_temp)} itens processados.")

    except Exception as e:
        print(f"❌ [ML] Erro no motor furtivo: {e}")
    finally:
        driver.quit()
        print("🧹 [ML] Navegador fechado e rastro limpo.")

if __name__ == "__main__":
    termo = input("Teste manual ML - digite o termo: ")
    extrair_mercado_livre(termo)