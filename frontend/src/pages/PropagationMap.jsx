import { useState, useEffect } from 'react';
import { MapContainer, TileLayer, CircleMarker, Popup, useMap } from 'react-leaflet';
import { Shield, Globe, Activity, AlertTriangle, TrendingUp, ChevronRight, Zap } from 'lucide-react';
import 'leaflet/dist/leaflet.css';
import api from '../api/axios';

// Component to handle map centering
function ChangeView({ center }) {
  const map = useMap();
  map.setView(center, map.getZoom());
  return null;
}

const AnomalyAlert = ({ message, time }) => (
  <div className="p-3 bg-crimson/5 border-l-2 border-crimson rounded-r-lg flex items-start gap-3">
    <AlertTriangle size={14} className="text-crimson mt-0.5 shrink-0" />
    <div className="min-w-0">
      <p className="text-[10px] font-bold text-white leading-tight">{message}</p>
      <p className="text-[8px] text-slate-500 uppercase mt-0.5">{time}</p>
    </div>
  </div>
);

export default function PropagationMap() {
  const [data, setData] = useState({ total_nodes: 0, platform_breakdown: {}, geo_clusters: [] });
  const [selectedAsset, setSelectedAsset] = useState('All Assets');
  const [mapCenter, setMapCenter] = useState([20, 0]);

  useEffect(() => {
    const fetchMapData = async () => {
      try {
        const res = await api.get('/propagation');
        setData(res.data.propagation_data || { total_nodes: 0, platform_breakdown: {}, geo_clusters: [] });
      } catch (err) {
        console.error(err);
      }
    };
    fetchMapData();
  }, []);

  const getMarkerColor = (count) => {
    if (count > 50) return '#EF4444';
    if (count > 10) return '#F59E0B';
    return '#10B981';
  };

  return (
    <div className="h-[calc(100vh-14rem)] flex gap-8 animate-slide-up">
      <div className="flex-1 glass-card overflow-hidden relative border-border-base shadow-2xl">
        <div className="absolute top-6 left-6 z-[40] flex flex-col gap-3">
          <div className="bg-background/80 backdrop-blur-md border border-border-base p-4 rounded-2xl flex items-center gap-4">
             <div className="flex flex-col">
                <span className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Global Monitoring</span>
                <div className="flex items-center gap-2">
                   <div className="w-2 h-2 rounded-full bg-emerald animate-pulse"></div>
                   <span className="text-sm font-black text-white">Live Edge Nodes: {data.total_nodes || 142}</span>
                </div>
             </div>
          </div>
        </div>

        <MapContainer 
          center={mapCenter} 
          zoom={2.5} 
          style={{ height: '100%', width: '100%', filter: 'invert(100%) hue-rotate(180deg) brightness(95%) contrast(90%)' }}
          zoomControl={false}
        >
          <TileLayer
            url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png"
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
          />
          {data.geo_clusters?.map((cluster, i) => (
            <CircleMarker 
              key={i}
              center={[cluster.lat, cluster.lng]}
              radius={Math.max(6, Math.min(cluster.count * 2, 20))}
              pathOptions={{ 
                fillColor: getMarkerColor(cluster.count), 
                fillOpacity: 0.6, 
                color: getMarkerColor(cluster.count),
                weight: 1,
                className: cluster.count < 10 ? '' : 'animate-pulse' 
              }}
            >
              <Popup className="dark-popup">
                <div className="p-1">
                   <p className="text-xs font-bold text-slate-900">{cluster.country} Cluster</p>
                   <p className="text-[10px] text-slate-500 uppercase font-bold mt-1">Status: {cluster.count > 10 ? 'CRITICAL' : 'MONITORING'}</p>
                   <p className="text-[10px] text-slate-900 font-bold">{cluster.count} Nodes Detected</p>
                </div>
              </Popup>
            </CircleMarker>
          ))}
          <ChangeView center={mapCenter} />
        </MapContainer>

        <div className="absolute bottom-6 left-6 z-[40] bg-background/80 backdrop-blur-md border border-border-base p-4 rounded-xl flex gap-6">
           <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-emerald"></div>
              <span className="text-[10px] font-bold uppercase text-slate-300">Authorized</span>
           </div>
           <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-amber animate-pulse"></div>
              <span className="text-[10px] font-bold uppercase text-slate-300">Suspicious</span>
           </div>
           <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-crimson animate-pulse"></div>
              <span className="text-[10px] font-bold uppercase text-slate-300">Violations</span>
           </div>
        </div>
      </div>

      <div className="w-80 flex flex-col gap-6">
         <div className="glass-card p-6">
            <h3 className="text-xs font-black text-slate-400 uppercase tracking-[0.2em] mb-4">Propagation Insights</h3>
            <div className="space-y-4">
               <div>
                  <label className="text-[10px] font-bold text-slate-500 uppercase tracking-widest block mb-2">Focus Asset</label>
                  <select 
                    className="w-full bg-[#0D1117] border border-border-base rounded-lg px-3 py-2 text-xs font-bold text-white focus:outline-none focus:border-primary"
                    onChange={(e) => setSelectedAsset(e.target.value)}
                  >
                     <option>All Active Protection</option>
                     <option>IPL_2025_Final_A1</option>
                     <option>UCL_Highlights_V9</option>
                  </select>
               </div>
               
               <div className="grid grid-cols-2 gap-3">
                  <div className="bg-background rounded-xl p-3 border border-border-base">
                     <p className="text-[9px] font-bold text-slate-500 uppercase">Velocity</p>
                     <p className="text-lg font-black text-white mt-1">14<span className="text-[10px] text-crimson ml-1">/24h</span></p>
                  </div>
                  <div className="bg-background rounded-xl p-3 border border-border-base">
                     <p className="text-[9px] font-bold text-slate-500 uppercase">Latency</p>
                     <p className="text-lg font-black text-white mt-1 text-emerald">12<span className="text-[10px] text-slate-500 ml-1">min</span></p>
                  </div>
               </div>
            </div>
         </div>

         <div className="glass-card flex-1 flex flex-col min-h-0">
            <div className="p-6 border-b border-border-base">
               <h3 className="text-xs font-black text-slate-400 uppercase tracking-[0.2em] flex items-center gap-2">
                  <Activity size={14} className="text-primary" /> Edge Telemetry
               </h3>
            </div>
            <div className="flex-1 overflow-y-auto p-6 space-y-3 custom-scrollbar">
               <AnomalyAlert message="Content appeared on piracy domain within 2h of upload" time="JUST NOW" />
               <AnomalyAlert message="Cluster detection in Southeast Asia servers" time="14 MIN AGO" />
               <AnomalyAlert message="High spread velocity detected on Telegram" time="2H AGO" />
               <AnomalyAlert message="YouTube Content ID bypass attempted" time="5H AGO" />
            </div>
            <div className="p-6 bg-primary/5 border-t border-primary/10 rounded-b-xl">
               <div className="flex justify-between items-center text-[10px] font-bold italic">
                  <span className="text-slate-400 uppercase tracking-widest">Auto-Alert Pattern:</span>
                  <span className="text-primary tracking-widest uppercase">STRICT</span>
               </div>
            </div>
         </div>
      </div>
    </div>
  );
}
