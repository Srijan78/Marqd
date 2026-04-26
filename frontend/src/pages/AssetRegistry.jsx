import { useState, useEffect, useRef } from 'react';
import { Upload, Plus, Search, Tag, X, FileText, Film, Lock, Clock, Zap, Download } from 'lucide-react';
import api from '../api/axios';

export default function AssetRegistry() {
  const fileInputRef = useRef(null);
  const [assets, setAssets] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [activeTags, setActiveTags] = useState(['IPL 2025', 'Cricket', 'High-Res']);
  const [tagInput, setTagInput] = useState('');
  const [downloadStates, setDownloadStates] = useState({});

  useEffect(() => {
    fetchAssets();
  }, []);

  const fetchAssets = async () => {
    try {
      const res = await api.get('/assets');
      setAssets(res.data.assets || []);
    } catch (err) {
      console.error(err);
    }
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    const formData = new FormData();
    formData.append('file', file);
    formData.append('keywords', activeTags.join(','));

    try {
      await api.post('/assets', formData);
      fetchAssets();
    } catch (err) {
      const errorMsg = err.response?.data?.error || err.message;
      console.error('Upload failed:', errorMsg);
      alert('Upload failed: ' + errorMsg);
    } finally {
      setUploading(false);
    }
  };

  const handleAddTag = (e) => {
    if (e.key === 'Enter' && tagInput.trim()) {
      if (!activeTags.includes(tagInput.trim())) {
        setActiveTags([...activeTags, tagInput.trim()]);
      }
      setTagInput('');
    }
  };

  const removeTag = (tag) => {
    setActiveTags(activeTags.filter(t => t !== tag));
  };

  const handleDownload = async (asset) => {
    const assetId = asset.id;
    setDownloadStates(prev => ({ ...prev, [assetId]: 'loading' }));
    try {
      const url = `${import.meta.env.VITE_API_URL || 'http://127.0.0.1:5000/api'}${asset.watermarked_url || ''}`;
      const response = await fetch(url);
      if (!response.ok) throw new Error('Download failed');
      const blob = await response.blob();
      const ext = asset.file_name?.split('.').pop() || 'jpg';
      const baseName = asset.file_name?.replace(/\.[^.]+$/, '') || 'asset';
      const filename = `marqd_protected_${baseName}.${ext}`;
      const objectUrl = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = objectUrl;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(objectUrl);
      setDownloadStates(prev => ({ ...prev, [assetId]: 'done' }));
      setTimeout(() => setDownloadStates(prev => ({ ...prev, [assetId]: null })), 2000);
    } catch (err) {
      console.error('Download error:', err);
      setDownloadStates(prev => ({ ...prev, [assetId]: null }));
    }
  };

  return (
    <div className="flex flex-col gap-10 animate-slide-up">
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-4xl font-black text-white tracking-tighter uppercase italic">Asset Registry</h1>
          <p className="text-slate-500 font-medium mt-1">Register and watermark official media for global tracking.</p>
        </div>
        <button className="btn-primary" onClick={() => fileInputRef.current?.click()}>
          <Plus size={18} />
          Register New Asset
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-10">
        {/* Upload Zone */}
        <div className="lg:col-span-1 space-y-6">
          <div className="glass-card p-10 border-dashed border-2 border-primary/30 flex flex-col items-center text-center group cursor-pointer relative overflow-hidden">
            {uploading && (
              <div className="absolute inset-0 bg-background/80 backdrop-blur-sm z-10 flex flex-col items-center justify-center">
                <div className="w-16 h-16 rounded-full border-2 border-primary/20 flex items-center justify-center relative">
                  <Zap className="text-primary animate-pulse" size={32} />
                  <div className="absolute inset-0 border-2 border-primary border-t-transparent rounded-full animate-spin" />
                </div>
                <p className="mt-4 text-sm font-bold text-white uppercase tracking-widest">Embedding Watermark...</p>
              </div>
            )}
            <div className="w-20 h-20 rounded-full bg-primary/5 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform relative">
              <Upload className="text-primary" size={32} />
              <div className="absolute inset-0 rounded-full border-2 border-primary/20 animate-ripple" />
            </div>
            <h3 className="text-lg font-bold text-white mb-2">Drop Official Media</h3>
            <p className="text-xs text-slate-500 uppercase tracking-widest font-bold">Supports UHD JPG, PNG, MP4 (Max 500MB)</p>
            <input type="file" ref={fileInputRef} className="absolute inset-0 opacity-0 cursor-pointer" onChange={handleFileUpload} />
          </div>

          <div className="glass-card p-6">
            <h4 className="text-xs font-black text-slate-400 uppercase tracking-[0.2em] mb-4 flex items-center gap-2">
              <Tag size={14} /> Organization Tags
            </h4>
            <div className="flex flex-wrap gap-2 mb-4">
              {activeTags.map(tag => (
                <span key={tag} className="badge bg-primary/10 text-primary-bright border-primary/20 rounded-lg px-2 py-1.5 lowercase font-mono">
                  #{tag}
                  <button onClick={() => removeTag(tag)} className="hover:text-white transition-colors">
                    <X size={12} />
                  </button>
                </span>
              ))}
            </div>
            <div className="relative">
              <Plus className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" size={14} />
              <input 
                type="text" 
                value={tagInput}
                onChange={(e) => setTagInput(e.target.value)}
                onKeyDown={handleAddTag}
                placeholder="Add metadata tag..." 
                className="input-field pl-9 text-xs py-2 bg-[#0D1117] border-border-base"
              />
            </div>
          </div>
        </div>

        {/* Asset Grid */}
        <div className="lg:col-span-2 space-y-6">
          <div className="flex items-center justify-between">
            <div className="relative flex-1 max-w-sm">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" size={16} />
              <input type="text" placeholder="Filter by ID or Hash..." className="input-field pl-10 py-2 border-none bg-surface-card" />
            </div>
            <div className="flex items-center gap-2">
              <span className="text-[10px] font-bold text-slate-500 uppercase">Sort by:</span>
              <select className="bg-transparent text-xs font-bold text-white focus:outline-none cursor-pointer">
                <option>Newest First</option>
                <option>Size (Large)</option>
              </select>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {assets.map((asset) => (
              <div key={asset.id} className="glass-card overflow-hidden group">
                <div className="aspect-video bg-[#0D1117] relative">
                  <img src={`${import.meta.env.VITE_API_URL || 'http://127.0.0.1:5000/api'}${asset.watermarked_url || ''}`} alt="" className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500 opacity-60 group-hover:opacity-100" />
                  <div className="absolute top-3 left-3">
                    <div className="badge bg-background/80 backdrop-blur-md text-white border-white/10 px-3">
                      {asset.asset_type === 'video' ? <Film size={12} /> : <FileText size={12} />}
                      {asset.asset_type?.toUpperCase()}
                    </div>
                  </div>
                  <div className="absolute bottom-3 right-3">
                    <div className="badge badge-success backdrop-blur-md">
                      <Lock size={12} /> Protected
                    </div>
                  </div>
                </div>
                <div className="p-4 space-y-3">
                  <div>
                    <h3 className="text-sm font-bold text-white truncate">{asset.file_name}</h3>
                    <p className="text-[10px] font-mono text-slate-400 uppercase mt-1 tracking-tight">ID: {asset.asset_id}</p>
                  </div>
                  
                  <div className="flex items-center justify-between py-3 border-y border-border-base">
                    <div>
                      <p className="text-[9px] font-bold text-slate-500 uppercase">pHash Fingerprint</p>
                      <p className="text-[11px] font-mono text-primary-bright mt-0.5">{asset.phash?.slice(0, 16)}...</p>
                    </div>
                    <div className="text-right">
                      <p className="text-[9px] font-bold text-slate-500 uppercase">Created</p>
                      <div className="flex items-center justify-end gap-1 text-[11px] font-bold text-white mt-0.5">
                        <Clock size={10} className="text-slate-500" /> {new Date(asset.created_at).toLocaleDateString()}
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-2 justify-between">
                    <div className="flex gap-1 overflow-hidden">
                      {(asset.keywords || []).slice(0, 3).map(t => (
                        <span key={t} className="text-[9px] font-bold text-slate-500 border border-slate-700/50 rounded px-1.5">#{t}</span>
                      ))}
                    </div>
                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => handleDownload(asset)}
                        disabled={downloadStates[asset.id] === 'loading'}
                        className="flex items-center gap-1 text-[10px] font-black uppercase px-2 py-1 rounded border border-primary/30 bg-primary/5 text-primary hover:bg-primary/20 hover:text-white transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        <Download size={10} />
                        {downloadStates[asset.id] === 'loading' ? 'Downloading...' : downloadStates[asset.id] === 'done' ? 'Downloaded!' : 'Download'}
                      </button>
                      <button className="text-[10px] font-black text-primary uppercase hover:text-white transition-colors underline underline-offset-4">Actions</button>
                    </div>
                  </div>
                </div>
              </div>
            ))}
            
            {/* Mock for demo if empty */}
            {assets.length === 0 && [1, 2, 3, 4].map(i => (
               <div key={i} className="glass-card overflow-hidden opacity-30 grayscale pointer-events-none">
                 <div className="aspect-video bg-surface-hover animate-pulse"></div>
                 <div className="p-4 space-y-4">
                   <div className="h-4 w-32 bg-surface-hover rounded"></div>
                   <div className="h-10 w-full bg-surface-hover rounded"></div>
                 </div>
               </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
