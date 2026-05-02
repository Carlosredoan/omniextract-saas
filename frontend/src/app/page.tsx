"use client";
import { useEffect, useState } from "react";

export default function Home() {
  const [produtos, setProdutos] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  
  const [termoBusca, setTermoBusca] = useState("");
  const [siteAlvo, setSiteAlvo] = useState("mercadolivre");
  const [isRoboRodando, setIsRoboRodando] = useState(false);

  const carregarProdutos = () => {
    fetch("http://127.0.0.1:8002/produtos/")
      .then((res) => res.json())
      .then((data) => {
        setProdutos(data);
        setLoading(false);
      })
      .catch(() => {}); // Falha silenciosa no radar
  };

  useEffect(() => {
    carregarProdutos(); 
    const intervalo = setInterval(carregarProdutos, 5000);
    return () => clearInterval(intervalo);
  }, []);

  const iniciarRastreamento = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!termoBusca) return;
    
    setIsRoboRodando(true);
    
    try {
      // Dispara a ordem sem esperar a resposta completa para não travar a tela
      fetch("http://127.0.0.1:8002/buscar", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ termo: termoBusca, site: siteAlvo }),
      }).catch(() => {}); // Ignora o falso-positivo de CORS do navegador
      
    } finally {
      // Libera a tela imediatamente. O robô já está trabalhando no fundo!
      setTimeout(() => {
        setIsRoboRodando(false);
        setTermoBusca(""); 
      }, 500);
    }
  };

  return (
    <main className="min-h-screen bg-gray-950 text-gray-100 p-8 font-sans">
      <div className="max-w-7xl mx-auto">
        
        <header className="mb-8 flex items-center justify-between border-b border-gray-800 pb-6">
          <div>
            <h1 className="text-4xl font-extrabold tracking-tight text-white">
              Omni<span className="text-blue-500">Extract</span>
            </h1>
            <p className="text-gray-400 mt-2">Inteligência de Mercado & Afiliados</p>
          </div>
          <div className="bg-gray-900 px-4 py-2 rounded-lg border border-gray-800 shadow-sm">
            <span className="text-sm text-gray-400">Total Rastreado: </span>
            <span className="text-lg font-bold text-blue-400">{produtos.length}</span>
          </div>
        </header>

        <div className="mb-10 bg-gray-900 p-6 rounded-xl border border-gray-800 shadow-lg">
          <form onSubmit={iniciarRastreamento} className="flex flex-col md:flex-row gap-4 items-end">
            <div className="flex-1 w-full">
              <label className="block text-sm font-medium text-gray-400 mb-2">O que deseja minerar?</label>
              <input 
                type="text" 
                value={termoBusca}
                onChange={(e) => setTermoBusca(e.target.value)}
                placeholder="Ex: Monitor Gamer 144hz" 
                className="w-full bg-gray-950 border border-gray-700 rounded-lg px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            
            <div className="w-full md:w-64">
              <label className="block text-sm font-medium text-gray-400 mb-2">Alvo da Extração</label>
              <select 
                value={siteAlvo}
                onChange={(e) => setSiteAlvo(e.target.value)}
                className="w-full bg-gray-950 border border-gray-700 rounded-lg px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent appearance-none"
              >
                <option value="mercadolivre">Mercado Livre</option>
                <option value="amazon">Amazon Brasil</option>
                <option value="kabum">KaBuM!</option>
                <option value="shopee">Shopee</option>
              </select>
            </div>

            <button 
              type="submit" 
              disabled={isRoboRodando || !termoBusca}
              className={`w-full md:w-auto px-8 py-3 rounded-lg font-bold transition-all ${
                isRoboRodando || !termoBusca 
                ? "bg-gray-700 text-gray-500 cursor-not-allowed" 
                : "bg-blue-600 hover:bg-blue-500 text-white shadow-[0_0_15px_rgba(37,99,235,0.4)]"
              }`}
            >
              {isRoboRodando ? "Enviando..." : "Iniciar Varredura"}
            </button>
          </form>
        </div>

        {loading ? (
          <div className="flex justify-center items-center py-20">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
          </div>
        ) : (
          <div className="overflow-hidden rounded-xl border border-gray-800 bg-gray-900 shadow-2xl">
            <table className="w-full text-left text-sm text-gray-400">
              <thead className="bg-gray-950/50 text-xs uppercase text-gray-300">
                <tr>
                  <th className="px-6 py-4 font-semibold">Status</th>
                  <th className="px-6 py-4 font-semibold">Produto</th>
                  <th className="px-6 py-4 font-semibold">Preço</th>
                  <th className="px-6 py-4 font-semibold hidden md:table-cell">Condição</th>
                  <th className="px-6 py-4 font-semibold text-right">Ação</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-800">
                {produtos.map((item) => (
                  <tr key={item.id} className="hover:bg-gray-800/50 transition-colors">
                    <td className="px-6 py-4">
                      {item.is_oportunidade ? (
                        <span className="inline-flex items-center gap-1.5 rounded-full bg-emerald-500/10 px-3 py-1 text-xs font-medium text-emerald-400 border border-emerald-500/20">
                          🔥 Oportunidade
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1.5 rounded-full bg-gray-500/10 px-3 py-1 text-xs font-medium text-gray-400 border border-gray-500/20">
                          ✅ Comum
                        </span>
                      )}
                    </td>
                    <td className="px-6 py-4">
                      <div className="font-medium text-gray-200 line-clamp-2" title={item.titulo}>
                        {item.titulo}
                      </div>
                      <div className="text-xs text-gray-500 mt-1 uppercase tracking-wider">
                        {item.termo_busca}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="font-bold text-white text-lg">
                        R$ {item.preco_a_vista.toFixed(2)}
                      </div>
                    </td>
                    <td className="px-6 py-4 hidden md:table-cell">
                      {item.max_parcelas === 1 ? (
                        <span className="inline-flex items-center rounded-md bg-gray-800 px-2 py-1 text-xs font-medium text-gray-500">
                          Apenas à vista
                        </span>
                      ) : (
                        <>
                          <div className="text-gray-300">
                            {item.max_parcelas}x de R$ {item.valor_parcela.toFixed(2)}
                          </div>
                          <div className="text-xs text-gray-500 mt-0.5">
                            {item.taxa_juros ? 'Com juros' : 'Sem juros'}
                          </div>
                        </>
                      )}
                    </td>
                    <td className="px-6 py-4 text-right">
                      <a 
                        href={item.link} 
                        target="_blank" 
                        rel="noreferrer"
                        className="inline-flex items-center justify-center rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:ring-offset-gray-900"
                      >
                        Ver Link
                      </a>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </main>
  );
}
