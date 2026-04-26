import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import { ShieldCheck, Activity, Map, Search, Menu, Bell, Hexagon, AlertTriangle, History, X, Shield, Globe } from 'lucide-react';
import { useState, useEffect } from 'react';

// Pages
import Dashboard from './pages/Dashboard';
import AssetRegistry from './pages/AssetRegistry';
import PropagationMap from './pages/PropagationMap';
import Violations from './pages/Violations';
import ScanHistory from './pages/ScanHistory';

const SidebarItem = ({ icon: Icon, label, path, active }) => (
  <Link 
    to={path} 
    className={`flex items-center gap-3 px-4 py-3 transition-all duration-300 relative group ${
      active 
      ? 'text-white' 
      : 'text-slate-400 hover:text-gray-200'
    }`}
  >
    {active && (
      <div className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-6 bg-primary rounded-r-full" />
    )}
    <Icon size={20} className={active ? 'text-primary' : 'text-slate-500 group-hover:text-slate-300 transition-colors'} />
    <span className="font-semibold text-sm">{label}</span>
  </Link>
);

const GlobalScanOverlay = ({ isOpen, onClose }) => {
  if (!isOpen) return null;
  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center bg-background/90 backdrop-blur-md">
      <div className="max-w-md w-full p-8 flex flex-col items-center text-center">
        <div className="relative mb-8">
          <div className="w-32 h-32 rounded-full border-2 border-primary/20 flex items-center justify-center">
            <Globe size={64} className="text-primary animate-pulse" />
          </div>
          <div className="absolute inset-0 w-full h-full animate-scanner border-t-2 border-primary-bright shadow-[0_-10px_20px_-5px_rgba(108,99,255,0.5)]" />
        </div>
        <h2 className="text-2xl font-bold text-white mb-2">Global Scan in Progress</h2>
        <p className="text-slate-400 mb-8">Scanning 10,000+ domains and YouTube channels for asset violations...</p>
        
        <div className="w-full bg-surface-card border border-border-base rounded-xl p-4 text-left font-mono text-xs text-emerald space-y-1 h-32 overflow-hidden relative">
          <div className="animate-slide-up">[INFO] Initializing Fingerprint Matcher...</div>
          <div className="animate-slide-up delay-75">[INFO] Connecting to SerpApi (Google Lens Mode)...</div>
          <div className="animate-slide-up delay-150">[SCAN] Checking domain: piracy-sports.tv...</div>
          <div className="animate-slide-up delay-300 text-crimson">[WARN] High-confidence match found!</div>
          <div className="animate-slide-up delay-500">[SCAN] Processing YouTube Metadata...</div>
          <div className="absolute bottom-0 left-0 right-0 h-10 bg-gradient-to-t from-surface-card to-transparent" />
        </div>

        <button 
          onClick={onClose}
          className="mt-8 text-slate-500 hover:text-white transition-colors flex items-center gap-2"
        >
          <X size={16} /> Close Background Task
        </button>
      </div>
    </div>
  );
};

const AppLayout = ({ children }) => {
  const location = useLocation();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [isScanning, setIsScanning] = useState(false);

  // Close mobile menu on route change
  useEffect(() => {
    setMobileMenuOpen(false);
  }, [location]);

  return (
    <div className="min-h-screen bg-background flex text-gray-100 overflow-hidden relative">
      <GlobalScanOverlay isOpen={isScanning} onClose={() => setIsScanning(false)} />

      {/* Sidebar */}
      <aside className={`w-64 bg-[#0D1117] border-r border-border-base flex flex-col h-screen fixed md:relative z-50 transition-transform duration-300 ${mobileMenuOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'}`}>
        <div className="p-8 flex items-center gap-3">
          <img src="/logo.png" alt="Marqd Logo" className="h-8 w-auto object-contain drop-shadow-[0_0_15px_rgba(108,99,255,0.4)]" />
          <h1 className="text-2xl font-black tracking-tighter text-white uppercase italic">Marqd</h1>
        </div>

        <nav className="flex-1 py-4 flex flex-col">
          <SidebarItem icon={Activity} label="Intelligence Hub" path="/" active={location.pathname === '/'} />
          <SidebarItem icon={ShieldCheck} label="Asset Registry" path="/assets" active={location.pathname === '/assets'} />
          <SidebarItem icon={AlertTriangle} label="Violations" path="/violations" active={location.pathname === '/violations'} />
          <SidebarItem icon={Map} label="Propagation Map" path="/map" active={location.pathname === '/map'} />
          <SidebarItem icon={History} label="Scan History" path="/scans" active={location.pathname === '/scans'} />
        </nav>

        <div className="p-6">
          <div className="bg-surface-card border border-border-base rounded-2xl p-4 flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary to-primary-bright flex items-center justify-center font-bold text-white">
              IC
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-bold text-white truncate">IOC Olympic</p>
              <div className="flex items-center gap-1.5 mt-0.5">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald"></span>
                <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest leading-none">Enterprise</span>
              </div>
            </div>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col h-screen overflow-hidden">
        {/* Header */}
        <header className="h-20 border-b border-border-base flex items-center justify-between px-10 z-40 bg-background/50 backdrop-blur-md sticky top-0">
          <button 
            className="md:hidden text-slate-400 hover:text-white"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          >
            <Menu size={24} />
          </button>
          
          <div className="flex items-center gap-4 flex-1 max-w-xl mx-auto">
            <div className="relative w-full hidden md:block">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500" size={18} />
              <input 
                type="text" 
                placeholder="Search assets, violations, or hash signatures..." 
                className="input-field pl-12 bg-surface-card/50 border-border-base focus:border-primary/50"
              />
            </div>
          </div>

          <div className="flex items-center gap-6">
            <div className="relative p-2 text-slate-400 hover:text-white cursor-pointer transition-colors">
              <Bell size={22} />
              <span className="absolute top-2 right-2 w-2 h-2 bg-crimson rounded-full border-2 border-background"></span>
            </div>
            
            <button 
              onClick={() => setIsScanning(true)}
              className="btn-primary text-sm shadow-[0_0_20px_rgba(108,99,255,0.3)]"
            >
              <ShieldCheck size={18} />
              Protect New Asset
            </button>
          </div>
        </header>

        {/* Page Content */}
        <div className="flex-1 overflow-y-auto p-10 scroll-smooth">
          <div className="max-w-7xl mx-auto animate-fade-in">
            {children}
          </div>
        </div>
      </main>
      
      {/* Mobile Overlay */}
      {mobileMenuOpen && (
        <div 
          className="fixed inset-0 bg-black/80 backdrop-blur-sm z-40 md:hidden"
          onClick={() => setMobileMenuOpen(false)}
        />
      )}
    </div>
  );
};

function App() {
  return (
    <Router>
      <AppLayout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/assets" element={<AssetRegistry />} />
          <Route path="/violations" element={<Violations />} />
          <Route path="/map" element={<PropagationMap />} />
          <Route path="/scans" element={<ScanHistory />} />
        </Routes>
      </AppLayout>
    </Router>
  );
}

export default App;
