import { useState, useEffect, useRef } from 'react';
import { Upload, FileImage, Shield, Search, Filter, MoreVertical, Hash } from 'lucide-react';
import api from '../api/axios';

export default function AssetRegistry() {
  const [assets, setAssets] = useState([]);
  const [uploading, setUploading] = useState(false);
  const fileInputRef = useRef(null);

  const fetchAssets = async () => {
    try {
      const res = await api.get('/assets');
      setAssets(res.data.assets || []);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    fetchAssets();
  }, []);

  const handleFileUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);
    formData.append('org_name', 'IOC Olympic');
    formData.append('keywords', file.name.split('.')[0].replace(/[-_]/g, ' '));

    setUploading(true);
    try {
      await api.post('/assets', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      await fetchAssets();
    } catch (err) {
      console.error(err);
      alert('Upload failed: ' + (err.response?.data?.error || err.message));
    } finally {
      setUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  return (
    <div className="flex flex-col gap-6 animate-slide-up">
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2 tracking-tight">Asset Registry</h1>
          <p className="text-gray-400">Upload and protect your digital media with invisible watermarks.</p>
        </div>
        
        <input 
          type="file" 
          ref={fileInputRef} 
          onChange={handleFileUpload} 
          className="hidden" 
          accept="image/*,video/*"
        />
        <button 
          className="btn-primary"
          onClick={() => fileInputRef.current?.click()}
          disabled={uploading}
        >
          {uploading ? (
            <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
          ) : (
            <Upload size={18} />
          )}
          {uploading ? 'Protecting...' : 'Upload Asset'}
        </button>
      </div>

      <div className="glass-card overflow-hidden">
        <div className="p-4 border-b border-white/5 flex gap-4 bg-surfaceHighlight/30">
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" size={16} />
            <input 
              type="text" 
              placeholder="Search by Asset ID or keywords..." 
              className="w-full bg-surface border border-white/10 rounded-lg pl-10 pr-4 py-2 text-sm text-gray-200 focus:outline-none focus:border-primary/50"
            />
          </div>
          <button className="btn-secondary py-2">
            <Filter size={16} />
            Filter
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-surfaceHighlight/20 border-b border-white/5">
                <th className="p-4 text-xs font-semibold text-gray-400 uppercase tracking-wider">Asset</th>
                <th className="p-4 text-xs font-semibold text-gray-400 uppercase tracking-wider">Protection</th>
                <th className="p-4 text-xs font-semibold text-gray-400 uppercase tracking-wider">Keywords</th>
                <th className="p-4 text-xs font-semibold text-gray-400 uppercase tracking-wider">Date Added</th>
                <th className="p-4 text-xs font-semibold text-gray-400 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5">
              {assets.length === 0 ? (
                <tr>
                  <td colSpan="5" className="p-8 text-center text-gray-500">
                    <div className="flex flex-col items-center justify-center gap-3">
                      <FileImage size={48} className="opacity-20" />
                      <p>No protected assets found. Upload one to get started.</p>
                    </div>
                  </td>
                </tr>
              ) : (
                assets.map((asset) => (
                  <tr key={asset.id} className="hover:bg-white/[0.02] transition-colors group">
                    <td className="p-4">
                      <div className="flex items-center gap-4">
                        <div className="w-12 h-12 rounded-lg bg-surfaceHighlight flex items-center justify-center border border-white/10 overflow-hidden shrink-0">
                          {asset.watermarked_url ? (
                            <img src={import.meta.env.VITE_API_URL ? import.meta.env.VITE_API_URL.replace('/api', asset.watermarked_url) : `http://127.0.0.1:5000${asset.watermarked_url}`} alt={asset.asset_id} className="w-full h-full object-cover" />
                          ) : (
                            <FileImage size={24} className="text-gray-500" />
                          )}
                        </div>
                        <div>
                          <p className="font-medium text-white font-mono text-sm">{asset.asset_id}</p>
                          <p className="text-xs text-gray-500">{asset.file_name} • {(asset.file_size / 1024).toFixed(1)} KB</p>
                        </div>
                      </div>
                    </td>
                    <td className="p-4">
                      <div className="flex flex-col gap-2">
                        <div className="flex items-center gap-2">
                          <Shield size={14} className={asset.watermark_status === 'embedded' ? 'text-primary' : 'text-warning'} />
                          <span className={`text-xs font-medium ${asset.watermark_status === 'embedded' ? 'text-primary' : 'text-warning'}`}>
                            {asset.watermark_status === 'embedded' ? 'DWT+DCT Watermark' : 'Pending'}
                          </span>
                        </div>
                        <div className="flex items-center gap-2">
                          <Hash size={14} className="text-accent" />
                          <span className="text-xs font-medium text-accent">pHash Active</span>
                        </div>
                      </div>
                    </td>
                    <td className="p-4">
                      <div className="flex flex-wrap gap-1">
                        {asset.keywords?.map((kw, i) => (
                          <span key={i} className="px-2 py-1 bg-surfaceHighlight rounded-md text-xs text-gray-300 border border-white/5">
                            {kw}
                          </span>
                        ))}
                      </div>
                    </td>
                    <td className="p-4 text-sm text-gray-400">
                      {new Date(asset.created_at).toLocaleDateString()}
                    </td>
                    <td className="p-4">
                      <button className="p-2 text-gray-500 hover:text-white hover:bg-surfaceHighlight rounded-lg transition-colors opacity-0 group-hover:opacity-100">
                        <MoreVertical size={18} />
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
