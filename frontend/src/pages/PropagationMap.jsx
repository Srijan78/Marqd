import { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, CircleMarker } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import { RefreshCw, Filter, Globe2 } from 'lucide-react';
import api from '../api/axios';

// Fix Leaflet default icon issue in React
import L from 'leaflet';
import icon from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';

let DefaultIcon = L.icon({
    iconUrl: icon,
    shadowUrl: iconShadow,
    iconSize: [25, 41],
    iconAnchor: [12, 41]
});
L.Marker.prototype.options.icon = DefaultIcon;

export default function PropagationMap() {
  const [data, setData] = useState({ total_nodes: 0, platform_breakdown: {}, geo_clusters: [] });
  const [loading, setLoading] = useState(true);

  const fetchMapData = async () => {
    setLoading(true);
    try {
      const res = await api.get('/propagation');
      setData(res.data.propagation_data);
    } catch (err) {
      console.error("Failed to fetch map data", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMapData();
  }, []);

  return (
    <div className="flex flex-col gap-6 animate-slide-up h-[calc(100vh-120px)]">
      <div className="flex justify-between items-end shrink-0">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2 tracking-tight">Propagation Map</h1>
          <p className="text-gray-400">Global visualization of unauthorized asset distribution.</p>
        </div>
        
        <div className="flex gap-3">
          <button className="btn-secondary" onClick={fetchMapData}>
            <RefreshCw size={16} className={loading ? "animate-spin" : ""} />
            Refresh
          </button>
          <button className="btn-secondary">
            <Filter size={16} />
            Filters
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 flex-1 min-h-0">
        {/* Sidebar Stats */}
        <div className="lg:col-span-1 flex flex-col gap-4 overflow-y-auto pr-2">
          <div className="glass-card p-5">
            <div className="flex items-center gap-3 mb-4 text-primary">
              <Globe2 size={20} />
              <h2 className="font-semibold text-white">Global Nodes</h2>
            </div>
            <p className="text-4xl font-bold text-white mb-1">{data.total_nodes}</p>
            <p className="text-sm text-gray-400">Active unauthorized distributions tracked worldwide.</p>
          </div>

          <div className="glass-card p-5">
            <h2 className="font-semibold text-white mb-4">Platform Breakdown</h2>
            <div className="flex flex-col gap-3">
              {Object.entries(data.platform_breakdown || {}).map(([platform, count]) => {
                const percentage = Math.round((count / Math.max(data.total_nodes, 1)) * 100);
                return (
                  <div key={platform}>
                    <div className="flex justify-between text-sm mb-1">
                      <span className="text-gray-300 capitalize">{platform.replace('_', ' ')}</span>
                      <span className="text-white font-medium">{count}</span>
                    </div>
                    <div className="h-2 bg-surfaceHighlight rounded-full overflow-hidden">
                      <div 
                        className={`h-full rounded-full ${platform === 'web' ? 'bg-primary' : 'bg-danger'}`} 
                        style={{ width: `${percentage}%` }} 
                      />
                    </div>
                  </div>
                )
              })}
            </div>
          </div>
          
          <div className="glass-card p-5 flex-1 min-h-[200px] flex flex-col">
            <h2 className="font-semibold text-white mb-4">Top Geo Clusters</h2>
            <div className="flex flex-col gap-2 flex-1">
              {data.geo_clusters?.length === 0 ? (
                <p className="text-sm text-gray-500 m-auto text-center">No geo data available yet.</p>
              ) : (
                data.geo_clusters?.map((cluster, i) => (
                  <div key={i} className="flex justify-between items-center p-2 rounded-lg hover:bg-surfaceHighlight/50 transition-colors">
                    <div className="flex items-center gap-2">
                      <span className="text-lg">{cluster.country === 'US' ? '🇺🇸' : cluster.country === 'IN' ? '🇮🇳' : cluster.country === 'RU' ? '🇷🇺' : '🌍'}</span>
                      <span className="text-sm text-gray-300">{cluster.country}</span>
                    </div>
                    <div className="badge badge-warning">{cluster.count} nodes</div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>

        {/* Map Container */}
        <div className="lg:col-span-3 glass-panel overflow-hidden relative z-0">
          <MapContainer 
            center={[20, 0]} 
            zoom={2} 
            scrollWheelZoom={true} 
            className="w-full h-full bg-[#0B0F19]"
            zoomControl={false}
          >
            <TileLayer
              attribution='&copy; <a href="https://carto.com/">CartoDB</a>'
              url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
            />
            
            {data.geo_clusters?.map((cluster, i) => {
              // Add a tiny bit of jitter to coordinates so markers don't perfectly overlap
              const lat = cluster.lat + (Math.random() - 0.5) * 2;
              const lng = cluster.lng + (Math.random() - 0.5) * 2;
              
              return (
                <CircleMarker 
                  key={i}
                  center={[lat, lng]} 
                  radius={Math.max(8, Math.min(cluster.count * 2, 30))}
                  fillColor="#EF4444"
                  color="#EF4444"
                  weight={1}
                  opacity={0.8}
                  fillOpacity={0.4}
                >
                  <Popup className="bg-surfaceHighlight text-white border-0">
                    <div className="text-center">
                      <strong className="text-white block mb-1">{cluster.country}</strong>
                      <span className="text-danger font-medium">{cluster.count} Violations</span>
                    </div>
                  </Popup>
                </CircleMarker>
              )
            })}
          </MapContainer>
          
          {/* Custom overlay controls */}
          <div className="absolute bottom-6 right-6 z-[1000] flex flex-col gap-2 pointer-events-auto">
            <button className="w-10 h-10 bg-surfaceHighlight hover:bg-surface border border-white/10 rounded-xl flex items-center justify-center text-white shadow-lg backdrop-blur-md transition-colors" onClick={() => document.querySelector('.leaflet-control-zoom-in').click()}>+</button>
            <button className="w-10 h-10 bg-surfaceHighlight hover:bg-surface border border-white/10 rounded-xl flex items-center justify-center text-white shadow-lg backdrop-blur-md transition-colors" onClick={() => document.querySelector('.leaflet-control-zoom-out').click()}>-</button>
          </div>
        </div>
      </div>
    </div>
  );
}
