import { useState, useEffect } from 'react';
import { Activity, ShieldAlert, CheckCircle2, TrendingUp, AlertTriangle } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import api from '../api/axios';

const StatCard = ({ title, value, change, icon: Icon, type }) => {
  const isPositive = change > 0;
  
  return (
    <div className="glass-card p-6 relative overflow-hidden group">
      <div className={`absolute top-0 right-0 w-32 h-32 -mr-10 -mt-10 rounded-full opacity-10 transition-transform duration-500 group-hover:scale-150 ${
        type === 'primary' ? 'bg-primary' : 
        type === 'danger' ? 'bg-danger' : 
        type === 'warning' ? 'bg-warning' : 'bg-accent'
      }`} />
      
      <div className="flex justify-between items-start mb-4 relative">
        <div className="p-3 rounded-xl bg-surfaceHighlight border border-white/5">
          <Icon className={
            type === 'primary' ? 'text-primary' : 
            type === 'danger' ? 'text-danger' : 
            type === 'warning' ? 'text-warning' : 'text-accent'
          } size={24} />
        </div>
        <div className={`flex items-center gap-1 text-sm font-medium ${isPositive ? 'text-accent' : 'text-danger'}`}>
          {isPositive ? <TrendingUp size={16} /> : <TrendingUp size={16} className="rotate-180" />}
          <span>{Math.abs(change)}%</span>
        </div>
      </div>
      
      <div className="relative">
        <h3 className="text-gray-400 font-medium text-sm mb-1">{title}</h3>
        <p className="text-3xl font-bold text-white tracking-tight">{value}</p>
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
    // Fetch initial data
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
        
        setRecentViolations(violations.slice(0, 5));
      } catch (error) {
        console.error("Failed to load dashboard data", error);
      }
    };
    
    fetchData();
  }, []);

  return (
    <div className="flex flex-col gap-8 animate-slide-up">
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2 tracking-tight">Intelligence Hub</h1>
          <p className="text-gray-400">Real-time overview of your digital asset protection.</p>
        </div>
        <button 
          className="btn-primary"
          onClick={async () => {
            await api.post('/scans/trigger');
            window.location.reload();
          }}
        >
          <Activity size={18} />
          Run Global Scan
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard 
          title="Protected Assets" 
          value={stats.totalAssets} 
          change={12} 
          icon={CheckCircle2} 
          type="success" 
        />
        <StatCard 
          title="Total Violations" 
          value={stats.totalViolations} 
          change={-5} 
          icon={AlertTriangle} 
          type="warning" 
        />
        <StatCard 
          title="Active Threats" 
          value={stats.activeThreats} 
          change={8} 
          icon={ShieldAlert} 
          type="danger" 
        />
        <StatCard 
          title="Successful Takedowns" 
          value={stats.takedowns} 
          change={24} 
          icon={Activity} 
          type="primary" 
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="glass-card p-6 lg:col-span-2 flex flex-col h-96">
          <h2 className="text-lg font-semibold text-white mb-6">Threat Detection Volume</h2>
          <div className="flex-1 flex items-center justify-center border border-white/5 rounded-xl bg-surfaceHighlight/30 relative">
            {/* Simple CSS Chart placeholder */}
            <div className="absolute inset-0 flex items-end justify-between px-8 py-4 opacity-50">
              {[40, 70, 45, 90, 65, 85, 30].map((h, i) => (
                <div key={i} className="w-12 bg-gradient-to-t from-primary/80 to-primary/20 rounded-t-sm" style={{height: `${h}%`}}></div>
              ))}
            </div>
            <p className="text-gray-500 font-medium z-10">Chart Integration Pending</p>
          </div>
        </div>

        <div className="glass-card p-0 overflow-hidden flex flex-col">
          <div className="p-6 border-b border-white/5 flex justify-between items-center bg-surfaceHighlight/30">
            <h2 className="text-lg font-semibold text-white">Recent Threats</h2>
            <button onClick={() => navigate('/violations')} className="text-primary hover:text-primaryHover text-sm font-medium">View All</button>
          </div>
          <div className="flex-1 overflow-y-auto p-2">
            {recentViolations.length === 0 ? (
              <div className="h-full flex flex-col items-center justify-center text-gray-500 p-6 text-center">
                <ShieldAlert size={32} className="mb-3 opacity-50" />
                <p>No active threats detected.</p>
              </div>
            ) : (
              <div className="flex flex-col gap-1">
                {recentViolations.map((v) => (
                  <div key={v.id} className="p-4 rounded-xl hover:bg-surfaceHighlight/50 transition-colors flex items-center gap-4 cursor-pointer">
                    <div className="w-10 h-10 rounded-lg bg-danger/10 text-danger flex items-center justify-center shrink-0 border border-danger/20">
                      <AlertTriangle size={18} />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-white truncate">{v.domain}</p>
                      <p className="text-xs text-gray-400 truncate">{v.classification_reason || 'Unauthorized use'}</p>
                    </div>
                    <div className={`badge ${v.classification === 'VIOLATION' ? 'badge-danger' : 'badge-warning'}`}>
                      {v.classification === 'VIOLATION' ? 'HIGH' : 'MED'}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
