import { useState, useEffect } from 'react';
import { Search, Filter, Download, ChevronRight, Activity, ShieldCheck, AlertCircle, Clock, Globe } from 'lucide-react';
import api from '../api/axios';

const StatusTag = ({ status }) => {
  if (status === 'CLEAN') return (
    <div className="flex items-center gap-1.5 text-emerald font-bold text-[10px] uppercase tracking-widest bg-emerald/10 border border-emerald/20 px-2.5 py-1 rounded-md">
       <ShieldCheck size={12} /> CLEAN
    </div>
  );
  return (
    <div className="flex items-center gap-1.5 text-crimson font-bold text-[10px] uppercase tracking-widest bg-crimson/10 border border-crimson/20 px-2.5 py-1 rounded-md">
       <AlertCircle size={12} /> RISK DETECTED
    </div>
  );
};

export default function ScanHistory() {
  const [scans, setScans] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchScans();
  }, []);

  const fetchScans = async () => {
    setLoading(true);
    try {
      const res = await api.get('/scans');
      setScans(res.data.scans || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col gap-8 animate-slide-up">
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-4xl font-black text-white tracking-tighter uppercase italic">Scan Command</h1>
          <p className="text-slate-500 font-medium mt-1">Audit log of all background crawling and deep-scan operations.</p>
        </div>
        <div className="flex gap-3">
          <button className="btn-secondary">
             <Download size={18} /> Export Log
          </button>
        </div>
      </div>

      <div className="glass-card overflow-hidden">
        <div className="p-4 border-b border-border-base flex gap-4 bg-[#0D1117]/30">
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" size={16} />
            <input 
              type="text" 
              placeholder="Search by Scan ID or Asset..." 
              className="w-full bg-[#0D1117] border border-border-base rounded-lg pl-10 pr-4 py-2 text-xs text-white focus:outline-none focus:border-primary/50"
            />
          </div>
          <button className="btn-secondary py-2">
            <Filter size={16} />
            Filter By Status
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-[#0D1117]/50 border-b border-border-base">
                <th className="px-6 py-4 text-[10px] font-black text-slate-500 uppercase tracking-widest">Operation ID</th>
                <th className="px-6 py-4 text-[10px] font-black text-slate-500 uppercase tracking-widest">Protected Asset</th>
                <th className="px-6 py-4 text-[10px] font-black text-slate-500 uppercase tracking-widest">Platform</th>
                <th className="px-6 py-4 text-[10px] font-black text-slate-500 uppercase tracking-widest">Results</th>
                <th className="px-6 py-4 text-[10px] font-black text-slate-500 uppercase tracking-widest">Timestamp</th>
                <th className="px-6 py-4 text-[10px] font-black text-slate-500 uppercase tracking-widest text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border-base">
              {scans.map((scan) => (
                <tr key={scan.scan_id} className="hover:bg-white/[0.02] transition-colors group">
                  <td className="px-6 py-4">
                     <div className="flex items-center gap-3">
                        <Activity size={14} className="text-primary" />
                        <span className="text-xs font-mono font-bold text-white uppercase">{scan.scan_id || 'SCN_88291'}</span>
                     </div>
                  </td>
                  <td className="px-6 py-4">
                     <div className="flex flex-col">
                        <span className="text-xs font-bold text-white">{scan.asset_id || 'UCL_FINAL_2024'}</span>
                        <span className="text-[10px] text-slate-500 font-mono italic">#cricket #high-res</span>
                     </div>
                  </td>
                  <td className="px-6 py-4">
                     <div className="flex items-center gap-2">
                        <Globe size={14} className="text-slate-500" />
                        <span className="text-[10px] font-black text-slate-300 uppercase">WEB_CRAWLER_V2</span>
                     </div>
                  </td>
                  <td className="px-6 py-4">
                    <StatusTag status={scan.status} />
                  </td>
                  <td className="px-6 py-4">
                     <div className="flex items-center gap-2 text-xs font-bold text-slate-400">
                        <Clock size={12} /> {new Date(scan.timestamp).toLocaleString()}
                     </div>
                  </td>
                  <td className="px-6 py-4 text-right">
                    <button className="text-slate-500 hover:text-white transition-colors">
                       <ChevronRight size={18} />
                    </button>
                  </td>
                </tr>
              ))}
              
              {/* Mock for demo if empty */}
              {scans.length === 0 && [1, 2, 3, 4, 5].map(i => (
                <tr key={i} className="opacity-40 grayscale group hover:grayscale-0 hover:opacity-100 transition-all cursor-pointer">
                   <td className="px-6 py-4 font-mono text-xs text-white">OP_X882{i}</td>
                   <td className="px-6 py-4">
                      <div className="flex flex-col">
                        <span className="text-xs font-bold text-white">MOCK_IPL_FOOTAGE_{i}</span>
                        <span className="text-[9px] text-slate-500 font-mono">#ipl #2025</span>
                      </div>
                   </td>
                   <td className="px-6 py-4">
                      <div className="flex items-center gap-2">
                         <Globe size={12} className="text-slate-600" />
                         <span className="text-[10px] font-black text-slate-500 uppercase">YOUTUBE_DEEP_SCAN</span>
                      </div>
                   </td>
                   <td className="px-6 py-4"><StatusTag status={i % 3 === 0 ? 'RISK' : 'CLEAN'} /></td>
                   <td className="px-6 py-4 text-[10px] text-slate-400 font-bold">Today, 14:0{i}</td>
                   <td className="px-6 py-4 text-right"><ChevronRight size={18} className="text-slate-700" /></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
