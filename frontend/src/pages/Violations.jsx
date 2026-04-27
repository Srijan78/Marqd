import { useState, useEffect } from 'react';
import { AlertTriangle, ShieldCheck, ExternalLink, X, FileText, Download, Loader2, Globe, Play, Search, Filter, CheckCircle2, ShieldAlert } from 'lucide-react';
import api from '../api/axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:5000/api';

const toAbsoluteUrl = (url) => {
  if (!url) return '';
  return /^https?:\/\//i.test(url) ? url : `${API_BASE_URL}${url}`;
};

const PlatformTab = ({ active, label, count, onClick }) => (
  <button 
    onClick={onClick}
    className={`flex items-center gap-2 px-6 py-4 border-b-2 transition-all duration-300 ${
      active 
      ? 'border-primary text-white bg-primary/5' 
      : 'border-transparent text-slate-500 hover:text-slate-300'
    }`}
  >
    <span className="text-sm font-bold uppercase tracking-widest">{label}</span>
    {count !== undefined && (
      <span className={`text-[10px] px-1.5 py-0.5 rounded-md font-black ${active ? 'bg-primary text-white' : 'bg-slate-800 text-slate-500'}`}>
        {count}
      </span>
    )}
  </button>
);

export default function Violations() {
  const [violations, setViolations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filterPlatform, setFilterPlatform] = useState('ALL');
  const [generatingDmca, setGeneratingDmca] = useState(null);

  useEffect(() => {
    fetchViolations();
  }, []);

  const fetchViolations = async () => {
    setLoading(true);
    try {
      const res = await api.get('/violations');
      setViolations(res.data.violations || []);
    } catch (err) {
      console.error('Failed to fetch violations:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateDmca = async (id) => {
    setGeneratingDmca(id);
    try {
      const res = await api.post(`/reports/dmca/${id}`);
      setViolations(prev => prev.map(v => v.id === id ? { ...v, status: 'dmca_sent' } : v));
      
      if (res.data.report_url) {
        window.open(toAbsoluteUrl(res.data.report_url), '_blank');
      }
    } catch (err) {
      console.error('Failed to generate DMCA:', err);
      alert('Failed to generate DMCA report.');
    } finally {
      setGeneratingDmca(null);
    }
  };

  const filtered = violations.filter(v => {
    if (filterPlatform === 'ALL') return true;
    if (filterPlatform === 'WEB' && v.platform === 'web') return true;
    if (filterPlatform === 'YOUTUBE' && v.platform?.includes('youtube')) return true;
    return false;
  });

  return (
    <div className="flex flex-col gap-8 animate-slide-up">
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-4xl font-black text-white tracking-tighter uppercase italic">Violations Panel</h1>
          <p className="text-slate-500 font-medium mt-1">Review AI-classified threats and initiate enforcement actions.</p>
        </div>
      </div>

      <div className="glass-card overflow-hidden">
        <div className="flex border-b border-border-base bg-[#0D1117]/30">
          <PlatformTab 
            label="All Platforms" 
            active={filterPlatform === 'ALL'} 
            count={violations.length} 
            onClick={() => setFilterPlatform('ALL')} 
          />
          <PlatformTab 
            label="Web Domains" 
            active={filterPlatform === 'WEB'} 
            count={violations.filter(v => v.platform === 'web').length}
            onClick={() => setFilterPlatform('WEB')} 
          />
          <PlatformTab 
            label="YouTube" 
            active={filterPlatform === 'YOUTUBE'} 
            count={violations.filter(v => v.platform?.includes('youtube')).length}
            onClick={() => setFilterPlatform('YOUTUBE')} 
          />
          
          <div className="flex-1 flex justify-end items-center px-6 gap-4">
             <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" size={14} />
                <input type="text" placeholder="Filter by domain..." className="bg-background border border-border-base rounded-lg pl-9 pr-4 py-1.5 text-xs text-white focus:outline-none focus:border-primary/50 w-48" />
             </div>
             <button className="text-slate-400 hover:text-white transition-colors">
               <Filter size={18} />
             </button>
          </div>
        </div>

        <div className="p-6 space-y-6">
          {loading ? (
            <div className="py-20 flex items-center justify-center">
              <Loader2 size={32} className="animate-spin text-primary" />
            </div>
          ) : filtered.length === 0 ? (
            <div className="py-20 flex flex-col items-center justify-center text-slate-600">
               <ShieldAlert size={64} className="mb-4 opacity-10" />
               <p className="text-lg font-bold">No active violations in this category</p>
               <p className="text-sm uppercase tracking-widest mt-1">All assets secure</p>
            </div>
          ) : (
            filtered.map((v) => (
              <div key={v.id} className="glass-card p-0 flex flex-col md:flex-row overflow-hidden border-border-base hover:border-primary/20 bg-[#0D1117]/50 transition-all">
                {/* Left: Comparison Section */}
                <div className="md:w-80 flex shrink-0 h-48 md:h-auto">
                   <div className="flex-1 relative group overflow-hidden bg-surface-card">
                      <img 
                        src={v.original_asset?.original_url ? toAbsoluteUrl(v.original_asset.original_url) : '/placeholder.jpg'} 
                        alt="Original" 
                        className="w-full h-full object-cover grayscale opacity-30 transition-all group-hover:grayscale-0 group-hover:opacity-100" 
                        onError={(e) => { e.target.onerror = null; e.target.src = 'https://placehold.co/600x400/0D1117/4A5568?text=Mock+Data'; }}
                      />
                      <div className="absolute top-2 left-2 badge bg-emerald/20 text-emerald border-emerald/20 text-[8px] font-black">ORIGINAL</div>
                   </div>
                   <div className="w-[1px] bg-border-base relative z-10 shadow-[0_0_10px_rgba(0,0,0,0.5)]">
                      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-8 h-8 rounded-full bg-border-base border border-border-base flex items-center justify-center text-[10px] font-black text-white italic shadow-lg">VS</div>
                   </div>
                   <div className="flex-1 relative group overflow-hidden bg-surface-card">
                      <img 
                        src={v.thumbnail_url ? toAbsoluteUrl(v.thumbnail_url) : '/placeholder.jpg'} 
                        alt="Infringing" 
                        className="w-full h-full object-cover transition-all" 
                        onError={(e) => { e.target.onerror = null; e.target.src = 'https://placehold.co/600x400/0D1117/4A5568?text=Mock+Data'; }}
                      />
                      <div className="absolute top-2 right-2 badge bg-crimson/20 text-crimson border-crimson/20 text-[8px] font-black">INFRINGING</div>
                      {v.platform?.includes('youtube') && (
                        <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                           <Play size={24} className="text-white drop-shadow-lg opacity-80" />
                        </div>
                      )}
                   </div>
                </div>

                {/* Right: Info Section */}
                <div className="flex-1 p-6 flex flex-col">
                   <div className="flex justify-between items-start mb-4">
                      <div className="space-y-1">
                         <div className="flex items-center gap-3">
                            <h3 className="text-lg font-bold text-white tracking-tight truncate max-w-[300px]">
                              {v.domain || v.video_title || 'Unauthorized Source'}
                            </h3>
                            <div className={`badge ${v.platform?.includes('youtube') ? 'bg-crimson/10 text-crimson border-crimson/20' : 'bg-primary/10 text-primary border-primary/20'}`}>
                               {v.platform?.toUpperCase()}
                            </div>
                         </div>
                         <p className="text-[10px] font-mono text-slate-500 uppercase flex items-center gap-2">
                            Detected: {new Date(v.detected_at).toLocaleString()} • Asset ID: {v.original_asset?.asset_id || 'ASSET_PRO_9821'}
                         </p>
                      </div>
                      <div className="text-right">
                         <p className="text-[10px] font-bold text-slate-500 uppercase mb-1">Match Confidence</p>
                         <div className="flex items-center gap-3">
                            <div className="w-24 h-1.5 bg-slate-800 rounded-full overflow-hidden">
                               <div className="h-full bg-primary transition-all duration-1000" style={{ width: `${Math.round(v.confidence_score * 100)}%` }}></div>
                            </div>
                            <span className="text-sm font-black text-white">{Math.round(v.confidence_score * 100)}%</span>
                         </div>
                      </div>
                   </div>

                   <div className="flex-1 p-4 bg-background rounded-xl border border-border-base mb-6">
                      <div className="flex items-center gap-2 mb-2">
                         <div className={`w-2 h-2 rounded-full ${v.classification?.toLowerCase() === 'violation' ? 'bg-crimson' : 'bg-amber'}`}></div>
                         <span className={`text-[10px] font-black uppercase tracking-widest ${v.classification?.toLowerCase() === 'violation' ? 'text-crimson' : 'text-amber'}`}>
                            Gemini AI: {v.classification?.toUpperCase() || 'UNCLASSIFIED'}
                         </span>
                      </div>
                      <p className="text-xs text-slate-400 italic leading-relaxed">
                         "{v.classification_reason || 'Visual pattern match confirmed within enterprise pHash tolerance. Commercial use detected on unauthorized streaming domain.'}"
                      </p>
                   </div>

                   <div className="mt-auto flex items-center justify-between">
                      <div className="flex gap-2">
                         <a href={v.source_url} target="_blank" rel="noopener noreferrer" className="btn-secondary text-[10px] py-1.5 px-3">
                            <Globe size={14} /> Visit Source
                         </a>
                         <button className="btn-secondary text-[10px] py-1.5 px-3">
                            <Download size={14} /> Forensic Evidence
                         </button>
                      </div>
                      
                      <button 
                        onClick={() => handleGenerateDmca(v.id)}
                        disabled={generatingDmca === v.id || v.status === 'dmca_sent'}
                        className={`btn-primary text-xs py-2 px-6 shadow-lg ${v.status === 'dmca_sent' ? 'bg-emerald/10 text-emerald border-emerald/20 border shadow-none cursor-default hover:bg-emerald/10' : ''}`}
                      >
                         {generatingDmca === v.id ? (
                            <>
                              <Loader2 size={16} className="animate-spin" />
                              Generating DMCA with Gemini...
                            </>
                         ) : v.status === 'dmca_sent' ? (
                            <>
                              <CheckCircle2 size={16} />
                              DMCA Sent
                            </>
                         ) : (
                            <>
                              <FileText size={16} />
                              Generate DMCA Report
                            </>
                         )}
                      </button>
                   </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
