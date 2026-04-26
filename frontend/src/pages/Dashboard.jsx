import { useState, useEffect } from 'react';
import { Activity, ShieldAlert, CheckCircle2, TrendingUp, AlertTriangle, ExternalLink, Globe, Play } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import api from '../api/axios';

const chartData = [
  { name: 'Mon', clean: 400, violations: 240 },
  { name: 'Tue', clean: 300, violations: 139 },
  { name: 'Wed', clean: 200, violations: 980 },
  { name: 'Thu', clean: 278, violations: 390 },
  { name: 'Fri', clean: 189, violations: 480 },
  { name: 'Sat', clean: 239, violations: 380 },
  { name: 'Sun', clean: 349, violations: 430 },
];

const StatCard = ({ title, value, change, icon: Icon, colorClass, glowClass }) => {
  const isPositive = change > 0;
  
  return (
    <div className="glass-card p-6 relative overflow-hidden group">
      <div className={`glow-blob ${glowClass} group-hover:scale-150`} />
      
      <div className="flex justify-between items-start mb-6 relative z-10">
        <div className={`p-3 rounded-2xl bg-[#0D1117] border border-border-base group-hover:border-primary/50 transition-colors`}>
          <Icon className={colorClass} size={24} />
        </div>
        <div className={`flex items-center gap-1 text-[10px] font-black uppercase tracking-tighter ${isPositive ? 'text-emerald' : 'text-crimson'}`}>
          {isPositive ? <TrendingUp size={14} /> : <TrendingUp size={14} className="rotate-180" />}
          <span>{Math.abs(change)}% Trend</span>
        </div>
      </div>
      
      <div className="relative z-10">
        <p className="text-3xl font-black text-white tracking-tighter mb-1">{value}</p>
        <h3 className="text-slate-400 font-bold text-xs uppercase tracking-widest">{title}</h3>
      </div>
    </div>
  );
};

export default function Dashboard() {
  const navigate = useNavigate();
  const [stats, setStats] = useState({
    totalAssets: 0,
    totalViolations: 0,
    activeThreats: 0,
    takedowns: 0
  });
  const [recentViolations, setRecentViolations] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [assetsRes, violationsRes] = await Promise.all([
          api.get('/assets'),
          api.get('/violations')
        ]);
        
        const assets = assetsRes.data.assets || [];
        const violations = violationsRes.data.violations || [];
        
        setStats({
          totalAssets: assets.length,
          totalViolations: violations.length,
          activeThreats: violations.filter(v => v.status === 'detected').length,
          takedowns: violations.filter(v => v.status === 'dmca_sent').length
        });
        
        setRecentViolations(violations.slice(0, 6));
      } catch (error) {
        console.error("Failed to load dashboard data", error);
      }
    };
    
    fetchData();
  }, []);

  return (
    <div className="flex flex-col gap-10 animate-slide-up">
      <div className="flex justify-between items-end">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <div className="w-2 h-2 rounded-full bg-emerald animate-pulse"></div>
            <span className="text-[10px] font-bold text-emerald uppercase tracking-[0.2em]">System Live: Global Monitoring Active</span>
          </div>
          <h1 className="text-4xl font-black text-white tracking-tighter">Intelligence Hub</h1>
        </div>
        <div className="flex gap-3">
          <div className="flex flex-col items-end justify-center mr-4">
            <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">Active Credits</span>
            <span className="text-sm font-black text-white">42,900 / 50,000</span>
          </div>
          <button 
            className="btn-primary"
            onClick={() => navigate('/assets')}
          >
            <Activity size={18} />
            Run Global Scan
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard 
          title="Protected Assets" 
          value={stats.totalAssets || 124} 
          change={12} 
          icon={CheckCircle2} 
          colorClass="text-emerald"
          glowClass="bg-emerald"
        />
        <StatCard 
          title="Total Violations" 
          value={stats.totalViolations || 382} 
          change={5} 
          icon={AlertTriangle} 
          colorClass="text-amber"
          glowClass="bg-amber"
        />
        <StatCard 
          title="Active Threats" 
          value={stats.activeThreats || 42} 
          change={-8} 
          icon={ShieldAlert} 
          colorClass="text-crimson"
          glowClass="bg-crimson"
        />
        <StatCard 
          title="Successful Takedowns" 
          value={stats.takedowns || 156} 
          change={24} 
          icon={Activity} 
          colorClass="text-primary"
          glowClass="bg-primary"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="glass-card p-8 lg:col-span-2 flex flex-col h-[500px]">
          <div className="flex justify-between items-center mb-8">
            <div>
              <h2 className="text-xl font-bold text-white tracking-tight">Threat Detection Volume</h2>
              <p className="text-sm text-slate-500 font-medium">Real-time scan results vs verified violations</p>
            </div>
            <div className="flex gap-4">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-sm bg-primary"></div>
                <span className="text-xs font-bold text-slate-400">Clean Scans</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-sm bg-crimson"></div>
                <span className="text-xs font-bold text-slate-400">Violations</span>
              </div>
            </div>
          </div>
          
          <div className="flex-1 w-full mt-auto">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData} margin={{ top: 0, right: 0, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1E2A3E" vertical={false} />
                <XAxis 
                  dataKey="name" 
                  axisLine={false} 
                  tickLine={false} 
                  tick={{ fill: '#64748B', fontSize: 12, fontWeight: 600 }}
                  dy={10}
                />
                <YAxis 
                  axisLine={false} 
                  tickLine={false} 
                  tick={{ fill: '#64748B', fontSize: 12, fontWeight: 600 }}
                />
                <Tooltip 
                  cursor={{ fill: '#1E2A3E' }}
                  contentStyle={{ backgroundColor: '#161C2C', border: '1px solid #1E2A3E', borderRadius: '12px' }}
                />
                <Bar dataKey="clean" fill="#6C63FF" radius={[4, 4, 0, 0]} barSize={32} />
                <Bar dataKey="violations" fill="#EF4444" radius={[4, 4, 0, 0]} barSize={32} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="glass-card p-0 flex flex-col border-crimson/20">
          <div className="p-6 border-b border-border-base flex justify-between items-center bg-[#0D1117]/30">
            <div>
              <h2 className="text-lg font-bold text-white uppercase tracking-tighter">Live Threats</h2>
              <p className="text-[10px] font-bold text-crimson uppercase tracking-widest">Active Verification</p>
            </div>
            <button onClick={() => navigate('/violations')} className="text-primary hover:text-primary-bright p-2 rounded-lg hover:bg-primary/10 transition-colors">
              <ExternalLink size={20} />
            </button>
          </div>
          <div className="flex-1 overflow-y-auto p-4 custom-scrollbar">
            {recentViolations.length === 0 ? (
              <div className="h-full flex flex-col items-center justify-center text-slate-500 p-6 text-center">
                <ShieldAlert size={48} className="mb-4 opacity-20" />
                <p className="font-bold text-slate-600">No active threats detected.</p>
                <p className="text-xs text-slate-500 mt-1 uppercase tracking-widest">System Clear</p>
              </div>
            ) : (
              <div className="flex flex-col gap-2">
                {recentViolations.map((v) => (
                  <div key={v.id} className="p-4 rounded-xl bg-[#0D1117] border border-border-base hover:border-primary/40 transition-all group cursor-pointer">
                    <div className="flex justify-between items-start mb-3">
                      <div className={`badge ${v.platform === 'YouTube' ? 'bg-crimson/10 text-crimson border-crimson/20' : 'bg-slate-400/10 text-slate-400 border-slate-400/20'}`}>
                        {v.platform === 'YouTube' ? <Play size={10} /> : <Globe size={10} />}
                        {v.platform}
                      </div>
                      <span className="text-[10px] font-bold text-slate-500 uppercase">{v.timestamp?.split('T')[1].slice(0, 5) || '14:20'}</span>
                    </div>
                    <div className="flex gap-3">
                      <div className="w-12 h-12 rounded-lg bg-surface-hover shrink-0 overflow-hidden border border-border-base">
                        <img src={v.infringing_url || '/placeholder.jpg'} alt="" className="w-full h-full object-cover opacity-50 grayscale group-hover:grayscale-0 group-hover:opacity-100 transition-all" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-bold text-white truncate group-hover:text-primary transition-colors">{v.domain || 'YouTube Channel'}</p>
                        <p className="text-[10px] font-bold text-slate-500 uppercase truncate mt-0.5">{v.classification_reason || 'AI Flagged: Commercial Intent'}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
          <div className="p-4 bg-crimson/5 border-t border-crimson/10">
            <div className="flex justify-between items-center">
              <span className="text-[10px] font-black text-crimson uppercase tracking-[0.2em]">Threat Alert</span>
              <span className="text-[10px] font-bold text-slate-500">Auto-Enforcement Enabled</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
