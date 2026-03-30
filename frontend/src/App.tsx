import { useEffect, useState } from 'react';

function App() {
  const [leads, setLeads] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  // Fetch leads
  const fetchLeads = async () => {
    try {
      const res = await fetch('http://localhost:3001/api/leads');
      const data = await res.json();
      setLeads(data || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLeads();
    
    // Scroll reveal setup
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) entry.target.classList.add('active');
        });
    }, { threshold: 0.1 });
    document.querySelectorAll('.reveal').forEach(el => observer.observe(el));
    return () => observer.disconnect();
  }, []);

  // Update Closer via API
  const handleUpdateCloser = async (username: string, newCloser: string) => {
    // Optimistic update
    setLeads(prev => prev.map(l => l.username === username ? { ...l, closer: newCloser } : l));
    
    try {
      await fetch(`http://localhost:3001/api/leads/${username}/closer`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ closer: newCloser })
      });
    } catch (err) {
      console.error(err);
      fetchLeads(); // revert on fail
    }
  };

  // Organize by score logic (from old app logic)
  // Quente >= 60, Morno >= 30, Frio < 30
  const quentes = leads.filter(l => l.score >= 60);
  const mornos = leads.filter(l => l.score >= 30 && l.score < 60);
  const pendentes = leads.filter(l => !l.score || l.score < 30); // Or frios/pendentes

  const availableClosers = ['', 'Gabriel', 'Lucas', 'João (SDR)'];

  const renderLeadCard = (lead: any, colorTheme: 'hot' | 'warm' | 'cold') => {
    const borderColor = colorTheme === 'hot' ? 'border-[#5070b0]/40 hover:border-[#5070b0]' 
                     : colorTheme === 'warm' ? 'border-yellow-500/30 hover:border-yellow-500'
                     : 'border-[#306090]/30 hover:border-[#5070b0]/50';
    
    const labelColor = colorTheme === 'hot' ? 'text-[#90c0e0] bg-[#204080]/30 border-[#5070b0]/20'
                    : colorTheme === 'warm' ? 'text-zinc-500 bg-black border-zinc-800'
                    : 'text-zinc-500 bg-black border-zinc-800';

    const scoreColor = colorTheme === 'hot' ? 'text-[#90c0e0]' 
                    : colorTheme === 'warm' ? 'text-yellow-400' 
                    : 'text-[#6090c0]';

    return (
        <div key={lead.username} className={`p-4 bg-zinc-950/50 backdrop-blur-sm border rounded-lg transition-all group relative ${borderColor}`}>
            <div className="flex justify-between items-start mb-2">
                <h4 className={`text-sm font-semibold text-white truncate max-w-[150px] group-hover:${scoreColor} transition-colors`}>
                    {lead.nome_ou_razao || lead.username || "Desconhecido"}
                </h4>
                <span className={`text-[9px] uppercase font-bold px-1.5 py-0.5 rounded border ${labelColor}`}>
                    {lead.oab ? 'OAB' : lead.cnpj ? 'CNPJ' : 'IG'}
                </span>
            </div>
            <p className="text-xs text-zinc-400 mb-2 truncate">
                {lead.email || lead.telefone || (lead.seguidores ? `${lead.seguidores} Seg.` : 'S/ Contato')}
            </p>
            
            <div className="flex items-center justify-between mb-3">
                <span className={`text-xs font-bold ${scoreColor} glow-sm`}>Score: {lead.score || 0}</span>
            </div>

            {/* ATRIBUIR CLOSER */}
            <div className="border-t border-white/5 pt-3 mt-1 flex flex-col gap-1">
                <label className="text-[10px] text-zinc-500 font-bold uppercase tracking-wider">Atribuir p/ Closer</label>
                <select 
                   value={lead.closer || ''} 
                   onChange={(e) => handleUpdateCloser(lead.username, e.target.value)}
                   className="w-full bg-black/40 border border-zinc-800 text-xs text-white rounded p-1.5 outline-none focus:border-[#5070b0]/50 transition-colors cursor-pointer"
                >
                    <option value="">(Sem Closer)</option>
                    {availableClosers.filter(c => c !== '').map(c => (
                        <option key={c} value={c}>{c}</option>
                    ))}
                </select>
            </div>
        </div>
    );
  };

  return (
    <div className="selection-blue min-h-screen bg-black text-white font-inter relative overflow-x-hidden">
        {/* Global Background */}
        <div className="fixed inset-0 z-0 pointer-events-none">
            <div className="absolute inset-0 bg-gradient-to-b from-[#0c1a35] via-[#050a15] to-black"></div>
            <div className="absolute top-0 left-0 w-[1px] h-[1px] bg-transparent stars-1 animate-[animStar_50s_linear_infinite]"></div>
            <div className="absolute top-0 left-0 w-[2px] h-[2px] bg-transparent stars-2 animate-[animStar_80s_linear_infinite]"></div>
            <div className="absolute top-0 left-0 w-[3px] h-[3px] bg-transparent stars-3 animate-[animStar_120s_linear_infinite]"></div>
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-[#204080]/10 rounded-full blur-[120px]"></div>
            <div className="absolute top-[20%] left-[10%] w-[400px] h-[400px] bg-[#306090]/5 rounded-full blur-[100px]"></div>
            <div className="absolute bottom-[0%] right-[0%] w-[500px] h-[500px] bg-[#5070b0]/5 rounded-full blur-[120px]"></div>
        </div>

        {/* Top Blur Header */}
        <div className="gradient-blur"></div>

        {/* Navbar */}
        <header className="fixed top-0 left-0 w-full z-50 pt-4 md:pt-6 px-4">
            <nav className="max-w-5xl mx-auto flex items-center justify-between bg-black/40 backdrop-blur-xl border border-white/10 rounded-full px-4 md:px-6 py-3 shadow-2xl">
                <div className="flex items-center gap-2">
                    <span className="text-sm font-bold tracking-widest text-[#90c0e0] hidden sm:inline">AVESTRA CRM</span>
                </div>

                <div className="hidden md:flex items-center gap-8">
                    <a href="#pipeline" className="text-sm font-medium text-[#f0f0f0] transition-colors hover:text-[#90c0e0]">Pipeline</a>
                    <a href="#" className="text-sm font-medium text-[#b0c0d0] hover:text-[#f0f0f0] transition-colors">Desempenho</a>
                </div>

                <div className="flex items-center gap-4">
                    <div className="bg-white/5 px-4 py-1.5 rounded-full border border-white/10 flex items-center gap-2 text-xs font-bold text-[#e0e0d0]">
                        {loading ? 'Sincronizando...' : `${leads.length} LEADS`}
                    </div>
                </div>
            </nav>
        </header>

        <main className="relative z-10 pt-32 pb-24">
            <section id="pipeline" className="px-6">
                <div className="max-w-[1400px] mx-auto">
                    {/* Section Header */}
                    <div className="mb-12 text-center max-w-3xl mx-auto reveal active">
                        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/5 border border-white/10 text-xs font-bold uppercase tracking-widest text-[#7090c0] mb-6">
                            <iconify-icon icon="lucide:kanban" className="w-3 h-3"></iconify-icon>
                            Pipeline Ativo
                        </div>
                        <h2 className="text-4xl md:text-5xl font-semibold text-white tracking-tight font-manrope mb-4">
                            Gestão de <span className="text-transparent bg-clip-text bg-gradient-to-r from-[#5070b0] to-[#90c0e0]">Oportunidades</span>
                        </h2>
                    </div>

                    {/* Pipeline Kanban View */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 reveal active">
                        
                        <div className="bg-zinc-900/40 border border-[#5070b0]/20 rounded-xl p-4 flex flex-col h-[750px] relative overflow-hidden group/col">
                            <div className="absolute top-0 right-0 w-32 h-32 bg-[#5070b0]/10 rounded-full blur-[60px] pointer-events-none group-hover/col:bg-[#5070b0]/20 transition-colors"></div>
                            <div className="flex items-center justify-between mb-4 relative z-10">
                                <h3 className="font-semibold text-white flex items-center gap-2">
                                    <span className="w-2 h-2 rounded-full bg-[#5070b0] animate-pulse shadow-[0_0_10px_#5070b0]"></span>
                                    Leads Quentes (+60)
                                </h3>
                                <span className="bg-[#5070b0]/20 text-[#90c0e0] text-xs font-bold px-2 py-1 rounded-md">{quentes.length}</span>
                            </div>
                            <div className="flex-1 overflow-y-auto space-y-3 pr-2 custom-scrollbar relative z-10">
                                {loading ? <p className="text-xs text-zinc-500">Carregando...</p> :
                                  quentes.length > 0 ? quentes.map(l => renderLeadCard(l, 'hot')) : <p className="text-xs text-zinc-600 italic">Nenhum lead quente.</p>
                                }
                            </div>
                        </div>

                        <div className="bg-zinc-900/40 border border-yellow-500/20 rounded-xl p-4 flex flex-col h-[750px]">
                            <div className="flex items-center justify-between mb-4">
                                <h3 className="font-semibold text-white flex items-center gap-2">
                                    <span className="w-2 h-2 rounded-full bg-yellow-500 shadow-[0_0_10px_rgba(234,179,8,0.5)]"></span>
                                    Leads Mornos (30-59)
                                </h3>
                                <span className="bg-yellow-500/20 text-yellow-500 text-xs font-bold px-2 py-1 rounded-md">{mornos.length}</span>
                            </div>
                            <div className="flex-1 overflow-y-auto space-y-3 pr-2 custom-scrollbar">
                                {loading ? <p className="text-xs text-zinc-500">Carregando...</p> :
                                  mornos.length > 0 ? mornos.map(l => renderLeadCard(l, 'warm')) : <p className="text-xs text-zinc-600 italic">Nenhum lead morno.</p>
                                }
                            </div>
                        </div>

                        <div className="bg-zinc-900/40 border border-white/5 rounded-xl p-4 flex flex-col h-[750px]">
                            <div className="flex items-center justify-between mb-4">
                                <h3 className="font-semibold text-white flex items-center gap-2">
                                    <span className="w-2 h-2 rounded-full bg-[#306090]"></span>
                                    Pendentes / Frios
                                </h3>
                                <span className="bg-white/10 text-xs font-bold px-2 py-1 rounded-md text-zinc-300">{pendentes.length}</span>
                            </div>
                            <div className="flex-1 overflow-y-auto space-y-3 pr-2 custom-scrollbar">
                                {loading ? <p className="text-xs text-zinc-500">Carregando...</p> :
                                  pendentes.length > 0 ? pendentes.map(l => renderLeadCard(l, 'cold')) : <p className="text-xs text-zinc-600 italic">Nenhum lead pendente.</p>
                                }
                            </div>
                        </div>

                    </div>
                </div>
            </section>
        </main>
    </div>
  );
}

export default App;
