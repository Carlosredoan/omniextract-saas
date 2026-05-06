import os
import time
import re
from bs4 import BeautifulSoup
from sqlmodel import Session, create_engine
from dotenv import load_dotenv
import undetected_chromedriver as uc

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

def extrair_kabum(termo: str):
    from main import ProdutoMinerado 
    
    print(f"🤖 [KABUM] Iniciando varredura FURTIVA por: {termo}...")
    
    termo_formatado = termo.replace(' ', '-')
    url = f"https://www.kabum.com.br/busca/{termo_formatado}"
    
    options = uc.ChromeOptions()
    options.add_argument('--headless=new')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    driver = None
    try:
        print("🕵️‍♂️ [KABUM] Abrindo navegador indetectável...")
        driver = uc.Chrome(options=options, version_main=147)
        
        driver.get(url)
        
        print("⏳ [KABUM] Aguardando 10s para renderização e bypass...")
        time.sleep(10)
        
        html_completo = driver.page_source
        soup = BeautifulSoup(html_completo, 'html.parser')

        # Pega TODOS os links de produtos da página
        links_produtos = soup.select('a[href*="/produto/"]')
        
        # Filtra links duplicados
        links_unicos = []
        urls_vistas = set()
        for link in links_produtos:
            href = link.get('href')
            if href not in urls_vistas:
                urls_vistas.add(href)
                links_unicos.append(link)

        if not links_unicos:
            print("⚠️ [KABUM] Nenhum produto encontrado no HTML da página.")
            return

        print(f"🎯 [KABUM] Cardápio cheio: {len(links_unicos)} produtos localizados. Extraindo dados...")

        with Session(engine) as session:
            for link_elem in links_unicos[:12]: 
                
                # 1. O RAIO-X
                no_atual = link_elem
                texto_card = ""
                for _ in range(4): 
                    texto_card = no_atual.get_text(separator=' | ', strip=True)
                    if "R$" in texto_card:
                        break
                    if no_atual.parent:
                        no_atual = no_atual.parent

                # 2. CAÇA AO PREÇO DEFINITIVA
                # O \s\| é a mágica aqui: diz ao robô para ignorar barras e espaços entre o R$ e o número
                matches = re.findall(r'R\$[\s\|]*([\d\.,]+)', texto_card)
                preco_a_vista = 0.0
                if matches:
                    precos = []
                    for m in matches:
                        v = m.replace('.', '').replace(',', '.')
                        try:
                            precos.append(float(v))
                        except: pass
                    
                    if precos:
                        maior_preco = max(precos)
                        # Descarta as parcelas (valores abaixo de 30% do maior valor encontrado)
                        precos_cheios = [p for p in precos if p > maior_preco * 0.3]
                        # O PIX sempre é o menor preço entre os valores "cheios"
                        preco_a_vista = min(precos_cheios) if precos_cheios else maior_preco
                
                # 3. CAÇA AO TÍTULO
                img = no_atual.find('img')
                titulo = img.get('alt') if img and img.get('alt') else ""
                
                if len(titulo) < 15:
                    pedacos = texto_card.split(' | ')
                    titulo = max(pedacos, key=len) if pedacos else "Sem Título"

                # 4. FILTRO FINAL
                if preco_a_vista == 0.0 or len(titulo) < 10:
                    continue

                link_final = "https://www.kabum.com.br" + link_elem['href'] if not link_elem['href'].startswith('http') else link_elem['href']

                novo_produto = ProdutoMinerado(
                    termo_busca=termo,
                    titulo=titulo[:200], 
                    link=link_final,
                    preco_a_vista=preco_a_vista,
                    status_estoque="disponivel"
                )
                session.add(novo_produto)
                print(f"✅ [KABUM] Capturado: {titulo[:35]}... | R$ {preco_a_vista}")
            
            session.commit()
            print("🏁 [KABUM] Extração finalizada com sucesso!")

    except Exception as e:
        print(f"❌ [KABUM] Erro: {e}")
        
    finally:
        if driver:
            driver.quit()
            print("🧹 [KABUM] Navegador fechado.")

if __name__ == "__main__":
    teste = input("Teste manual KaBuM - digite o termo: ")
    extrair_kabum(teste)