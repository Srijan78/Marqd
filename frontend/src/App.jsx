import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import { ShieldCheck, Activity, Map, Search, Menu, Bell, Hexagon, AlertTriangle } from 'lucide-react';
import { useState } from 'react';

// Pages (to be implemented)
import Dashboard from './pages/Dashboard';
import AssetRegistry from './pages/AssetRegistry';
import PropagationMap from './pages/PropagationMap';
import Violations from './pages/Violations';

const SidebarItem = ({ icon: Icon, label, path, active }) => (
  <Link 
    to={path} 
    className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-300 group ${
      active 
      ? 'bg-primary/10 text-primary border border-primary/20 shadow-inner' 
      : 'text-gray-400 hover:bg-surfaceHighlight hover:text-gray-200'
    }`}
  >
    <Icon size={20} className={active ? 'text-primary' : 'text-gray-500 group-hover:text-gray-300 transition-colors'} />
    <span className={`font-medium ${active ? 'text-primary' : ''}`}>{label}</span>
    {active && (
      <div className="ml-auto w-1.5 h-1.5 rounded-full bg-primary animate-pulse" />
    )}
  </Link>
);

const AppLayout = ({ children }) => {
  const location = useLocation();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <div className="min-h-screen bg-background flex text-gray-100 overflow-hidden relative">
      {/* Background Orbs */}
      <div className="absolute top-[-20%] left-[-10%] w-[50%] h-[50%] rounded-full bg-primary/5 blur-[120px] pointer-events-none" />
      <div className="absolute bottom-[-20%] right-[-10%] w-[50%] h-[50%] rounded-full bg-accent/5 blur-[120px] pointer-events-none" />

      {/* Sidebar */}
      <aside className={`w-72 glass-panel border-y-0 border-l-0 rounded-none border-r flex flex-col h-screen fixed md:relative z-50 transition-transform duration-300 ${mobileMenuOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'}`}>
        <div className="p-6 flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary to-accent flex items-center justify-center shadow-lg shadow-primary/20">
            <Hexagon size={24} className="text-white fill-white/20" />
          </div>
          <div>
            <h1 className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-gray-400 tracking-tight">Marqd.</h1>
            <p className="text-xs text-gray-500 font-medium tracking-wider">ASSET PROTECTION</p>
          </div>
        </div>

        <nav className="flex-1 px-4 py-6 flex flex-col gap-2">
          <SidebarItem icon={Activity} label="Intelligence Hub" path="/" active={location.pathname === '/'} />
          <SidebarItem icon={ShieldCheck} label="Asset Registry" path="/assets" active={location.pathname === '/assets'} />
          <SidebarItem icon={AlertTriangle} label="Violations" path="/violations" active={location.pathname === '/violations'} />
          <SidebarItem icon={Map} label="Propagation Map" path="/map" active={location.pathname === '/map'} />
        </nav>

        <div className="p-4 mt-auto">
          <div className="glass-card p-4 flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-surfaceHighlight flex items-center justify-center border border-white/10">
              <span className="text-sm font-bold text-gray-300">IO</span>
            </div>
            <div>
              <p className="text-sm font-medium text-gray-200">IOC Olympic</p>
              <p className="text-xs text-gray-500">Enterprise Plan</p>
            </div>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col h-screen overflow-hidden">
        {/* Header */}
        <header className="h-20 glass-panel border-x-0 border-t-0 rounded-none flex items-center justify-between px-8 z-40 sticky top-0">
          <button 
            className="md:hidden text-gray-400 hover:text-white"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          >
            <Menu size={24} />
          </button>
          
          <div className="flex items-center gap-4 flex-1 md:ml-0 ml-4">
            <div className="relative w-full max-w-md hidden md:block">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" size={18} />
              <input 
                type="text" 
                placeholder="Search assets, violations, or hash signatures..." 
                className="input-field pl-10 bg-surfaceHighlight/50 border-transparent focus:border-primary/50"
              />
            </div>
          </div>

          <div className="flex items-center gap-4">
            <button className="relative p-2 text-gray-400 hover:text-white transition-colors">
              <Bell size={20} />
              <span className="absolute top-1 right-1 w-2 h-2 bg-danger rounded-full border border-background"></span>
            </button>
            <button className="btn-primary py-2 px-4 text-sm hidden md:flex">
              <ShieldCheck size={16} />
              Protect New Asset
            </button>
          </div>
        </header>

        {/* Page Content */}
        <div className="flex-1 overflow-y-auto p-8 relative z-10 scroll-smooth">
          <div className="max-w-7xl mx-auto animate-fade-in">
            {children}
          </div>
        </div>
      </main>
      
      {/* Mobile Overlay */}
      {mobileMenuOpen && (
        <div 
          className="fixed inset-0 bg-black/50 backdrop-blur-sm z-40 md:hidden"
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
        </Routes>
      </AppLayout>
    </Router>
  );
}

export default App;
