import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import pandas as pd
import time
import random
import requests
import re

API_URL = "http://127.0.0.1:8002/produtos/"

def extrair_detalhes_pagamento(texto_bruto):
    detalhes = {
        "preco_a_vista": 0.0,
        "preco_prazo": 0.0,
        "max_parcelas": 1,
        "valor_parcela": 0.0,
        "taxa_juros": True,
        "status_estoque": "Disponível"
    }
    
    texto_lower = texto_bruto.lower()
    
    # 1. Scanner de Parcelas Exato
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
        detalhes["status_estoque"] = "Esgotado"

    # 2. Scanner de todos os números "R$" soltos na tela
    matches = re.findall(r'r\$\s*\n*\s*([\d\.,]+)', texto_lower)
    precos = []
    for m in matches:
        v = m.replace('.', '').replace(',', '.')
        try:
            precos.append(float(v))
        except: pass

    # 3. O CÉREBRO DA OPERAÇÃO: Caçador de Desconto PIX
    if precos:
        # Tira a parcela da lista para não atrapalhar
        precos_filtrados = [p for p in precos if abs(p - detalhes["valor_parcela"]) > 0.01]
        if not precos_filtrados:
            precos_filtrados = precos

        # O Segredo: O menor preço na tela (sem contar as parcelas) é SEMPRE o PIX/Desconto!
        detalhes["preco_a_vista"] = min(precos_filtrados)

        # O preço a prazo continua usando a prova real das parcelas
        if detalhes["max_parcelas"] > 1 and detalhes["valor_parcela"] > 0:
            estimativa = detalhes["max_parcelas"] * detalhes["valor_parcela"]
            detalhes["preco_prazo"] = min(precos_filtrados, key=lambda x: abs(x - estimativa))
        else:
            detalhes["preco_prazo"] = detalhes["preco_a_vista"]

    return detalhes

def extrair_mercado_livre(produto_alvo):
    print("\n" + "="*55)
    print(f"🚀 OmniExtract Worker: Recebi a ordem da FILA para buscar '{produto_alvo}'")
    print("="*55 + "\n")
    
    limite_paginas = 1 

    options = uc.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    options.binary_location = '/usr/bin/chromium'
    
    driver = uc.Chrome(options=options, version_main=147)
    
    termo_busca = produto_alvo.replace(' ', '-')
    url = f"https://lista.mercadolivre.com.br/{termo_busca}"
    
    lista_final = []
    pagina_atual = 1
    
    try:
        driver.get(url)
        while pagina_atual <= limite_paginas:
            print(f"📦 Minerando página {pagina_atual}...")
            
            try:
                WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.ui-search-layout__item')))
            except TimeoutException:
                print("⚠️ Demora na resposta ou bloqueio do site (Anti-bot). Pulando...")
                break
            
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
            time.sleep(2)
            
            produtos = driver.find_elements(By.CSS_SELECTOR, '.ui-search-layout__item')
            
            for item in produtos:
                try:
                    texto_bruto = item.get_attribute("innerText")
                    linhas = [l.strip() for l in texto_bruto.split('\n') if l.strip()]
                    titulo = next((l for l in linhas if len(l) > 20 and "venda" not in l.lower()), "Sem Título")
                    link = item.find_element(By.TAG_NAME, 'a').get_attribute('href')
                    
                    dados_pagamento = extrair_detalhes_pagamento(texto_bruto)
                    
                    if dados_pagamento["preco_a_vista"] > 0:
                        lista_final.append({
                            "termo_busca": produto_alvo,
                            "titulo": titulo,
                            "link": link,
                            **dados_pagamento
                        })
                except: continue
                
            if pagina_atual < limite_paginas:
                try:
                    btn_next = driver.find_element(By.CSS_SELECTOR, '.andes-pagination__button--next a')
                    url_proxima = btn_next.get_attribute('href')
                    if url_proxima:
                        driver.get(url_proxima)
                        pagina_atual += 1
                        time.sleep(random.uniform(3.0, 5.0))
                    else: break
                except: break
            else: break

        if lista_final:
            precos = [p['preco_a_vista'] for p in lista_final]
            mediana = pd.Series(precos).median()
            piso = mediana * 0.40
            
            print(f"\n📊 Processando {len(lista_final)} itens. Mediana: R${mediana:.2f}")
            
            for item in lista_final:
                item["is_oportunidade"] = bool(piso <= item["preco_a_vista"] <= mediana)
                
                try:
                    response = requests.post(API_URL, json=item)
                    if response.status_code == 200:
                        status = "🔥 [OPORTUNIDADE]" if item["is_oportunidade"] else "✅ [COMUM]"
                        print(f"{status} Gravado no Banco: R${item['preco_a_vista']:.2f} - {item['titulo'][:30]}...")
                except Exception as e:
                    print(f"❌ Sem conexão com o Backend: {e}")
                
    finally:
        driver.quit()
        print("🏁 Extração concluída com sucesso.")

if __name__ == "__main__":
    teste = input("Teste manual - digite o termo: ")
    extrair_mercado_livre(teste)
