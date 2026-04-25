import { useState, useEffect } from 'react';
import { AlertTriangle, ShieldCheck, ExternalLink, X, FileText, Download, Loader2, Eye, Filter, Globe, Video } from 'lucide-react';
import api from '../api/axios';

/* ─── Confidence Meter ─── */
const ConfidenceMeter = ({ score }) => {
  const pct = Math.round(score * 100);
  const color = pct >= 80 ? 'bg-red-500' : pct >= 50 ? 'bg-amber-500' : 'bg-emerald-500';
  return (
    <div className="flex items-center gap-3">
      <div className="flex-1 h-2 rounded-full bg-surfaceHighlight overflow-hidden">
        <div className={`h-full rounded-full ${color} transition-all duration-700`} style={{ width: `${pct}%` }} />
      </div>
      <span className="text-sm font-bold text-white w-12 text-right">{pct}%</span>
    </div>
  );
};

/* ─── Detail Modal ─── */
const ViolationDetailModal = ({ violation, onClose }) => {
  const [generating, setGenerating] = useState(false);
  const [reportUrl, setReportUrl] = useState(violation?.dmca_report_url || null);

  if (!violation) return null;

  const handleGenerateDMCA = async () => {
    setGenerating(true);
    try {
      const res = await api.post(`/reports/dmca/${violation.id}`);
      setReportUrl(res.data.report_url);
    } catch (err) {
      console.error('DMCA generation failed:', err);
    } finally {
      setGenerating(false);
    }
  };

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4">
      {/* Backdrop */}
      <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={onClose} />

      {/* Modal */}
      <div className="relative w-full max-w-3xl max-h-[90vh] overflow-y-auto glass-panel p-0 animate-fade-in">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-white/5">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-danger/10 text-danger flex items-center justify-center border border-danger/20">
              <AlertTriangle size={20} />
            </div>
            <div>
              <h2 className="text-lg font-bold text-white">Violation Detail</h2>
              <p className="text-xs text-gray-500">{violation.id}</p>
            </div>
          </div>
          <button onClick={onClose} className="p-2 rounded-lg hover:bg-surfaceHighlight transition-colors text-gray-400 hover:text-white">
            <X size={20} />
          </button>
        </div>

        {/* Side-by-Side Comparison */}
        <div className="p-6 border-b border-white/5">
          <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-4">Visual Comparison</h3>
          <div className="grid grid-cols-2 gap-4">
            {/* Original Asset */}
            <div className="flex flex-col gap-2">
              <span className="badge badge-success w-fit">Original Asset</span>
              <div className="aspect-video rounded-xl bg-surfaceHighlight border border-white/5 overflow-hidden flex items-center justify-center">
                {violation.original_asset?.original_url ? (
                  <img
                    src={`${import.meta.env.VITE_API_BASE || 'http://127.0.0.1:5000'}${violation.original_asset.original_url}`}
                    alt="Original asset"
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <div className="text-gray-600 text-sm flex flex-col items-center gap-2">
                    <ShieldCheck size={32} className="opacity-30" />
                    <span>Original on file</span>
                  </div>
                )}
              </div>
              <p className="text-xs text-gray-500 truncate">ID: {violation.original_asset?.asset_id || 'N/A'}</p>
            </div>

            {/* Infringing Content */}
            <div className="flex flex-col gap-2">
              <span className="badge badge-danger w-fit">Infringing Content</span>
              <div className="aspect-video rounded-xl bg-surfaceHighlight border border-white/5 overflow-hidden flex items-center justify-center">
                {violation.thumbnail_url ? (
                  <img
                    src={violation.thumbnail_url}
                    alt="Infringing content"
                    className="w-full h-full object-cover"
                    onError={(e) => { e.target.style.display = 'none'; }}
                  />
                ) : (
                  <div className="text-gray-600 text-sm flex flex-col items-center gap-2">
                    <AlertTriangle size={32} className="opacity-30" />
                    <span>No thumbnail</span>
                  </div>
                )}
              </div>
              <a href={violation.source_url} target="_blank" rel="noopener noreferrer"
                className="text-xs text-primary hover:text-primaryHover truncate flex items-center gap-1">
                <ExternalLink size={12} />{violation.source_url}
              </a>
            </div>
          </div>
        </div>

        {/* Forensic Evidence */}
        <div className="p-6 border-b border-white/5">
          <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-4">Forensic Evidence</h3>
          <div className="grid grid-cols-2 gap-4">
            <div className="glass-card p-4">
              <p className="text-xs text-gray-500 mb-1">Confidence Score</p>
              <ConfidenceMeter score={violation.confidence_score} />
            </div>
            <div className="glass-card p-4">
              <p className="text-xs text-gray-500 mb-1">Watermark Match</p>
              <p className={`text-lg font-bold ${violation.watermark_match ? 'text-emerald-400' : 'text-red-400'}`}>
                {violation.watermark_match ? '✓ Verified' : '✗ Not Found'}
              </p>
            </div>
            <div className="glass-card p-4">
              <p className="text-xs text-gray-500 mb-1">pHash Distance</p>
              <p className="text-lg font-bold text-white">
                {violation.phash_distance !== null ? violation.phash_distance : 'N/A'}
                <span className="text-xs text-gray-500 ml-2">(≤10 = match)</span>
              </p>
            </div>
            <div className="glass-card p-4">
              <p className="text-xs text-gray-500 mb-1">Classification</p>
              <p className={`text-lg font-bold ${violation.classification === 'VIOLATION' ? 'text-red-400' : violation.classification === 'SUSPICIOUS' ? 'text-amber-400' : 'text-gray-300'}`}>
                {violation.classification}
              </p>
            </div>
          </div>
          {violation.classification_reason && (
            <div className="mt-4 glass-card p-4">
              <p className="text-xs text-gray-500 mb-1">AI Reasoning</p>
              <p className="text-sm text-gray-300">{violation.classification_reason}</p>
            </div>
          )}
        </div>

        {/* DMCA Action */}
        <div className="p-6 flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-white">Legal Action</p>
            <p className="text-xs text-gray-500">Generate an AI-powered DMCA takedown notice</p>
          </div>
          <div className="flex items-center gap-3">
            {reportUrl && (
              <a
                href={`${import.meta.env.VITE_API_BASE || 'http://127.0.0.1:5000'}${reportUrl}`}
                target="_blank"
                rel="noopener noreferrer"
                className="btn-secondary text-sm"
              >
                <Download size={16} />
                Download PDF
              </a>
            )}
            <button
              className="btn-primary text-sm"
              onClick={handleGenerateDMCA}
              disabled={generating}
            >
              {generating ? (
                <><Loader2 size={16} className="animate-spin" />Generating...</>
              ) : (
                <><FileText size={16} />{reportUrl ? 'Regenerate DMCA' : 'Generate DMCA'}</>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

/* ─── Main Violations Page ─── */
export default function Violations() {
  const [violations, setViolations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedViolation, setSelectedViolation] = useState(null);
  const [filterPlatform, setFilterPlatform] = useState('all');
  const [filterStatus, setFilterStatus] = useState('all');

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

  const openDetail = async (violation) => {
    try {
      // Fetch full detail (includes original_asset info)
      const res = await api.get(`/violations/${violation.id}`);
      setSelectedViolation(res.data);
    } catch {
      setSelectedViolation(violation);
    }
  };

  const filtered = violations.filter(v => {
    if (filterPlatform !== 'all' && v.platform !== filterPlatform) return false;
    if (filterStatus !== 'all' && v.status !== filterStatus) return false;
    return true;
  });

  const statusColors = {
    detected: 'badge-warning',
    confirmed: 'badge-primary',
    dmca_sent: 'badge-success',
    resolved: 'badge-success',
  };

  const platformIcons = {
    web: <Globe size={14} />,
    youtube: <Video size={14} />,
    youtube_shorts: <Video size={14} />,
  };

  return (
    <div className="flex flex-col gap-8 animate-slide-up">
      {/* Header */}
      <div className="flex justify-between items-end flex-wrap gap-4">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2 tracking-tight">Violations Panel</h1>
          <p className="text-gray-400">Review detected infringements and take legal action.</p>
        </div>
        <div className="flex items-center gap-3">
          {/* Platform Filter */}
          <div className="flex items-center gap-2">
            <Filter size={16} className="text-gray-500" />
            <select
              value={filterPlatform}
              onChange={(e) => setFilterPlatform(e.target.value)}
              className="input-field py-2 text-sm w-32"
            >
              <option value="all">All Platforms</option>
              <option value="web">Web</option>
              <option value="youtube">YouTube</option>
              <option value="youtube_shorts">Shorts</option>
            </select>
          </div>
          {/* Status Filter */}
          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
            className="input-field py-2 text-sm w-32"
          >
            <option value="all">All Status</option>
            <option value="detected">Detected</option>
            <option value="confirmed">Confirmed</option>
            <option value="dmca_sent">DMCA Sent</option>
            <option value="resolved">Resolved</option>
          </select>
        </div>
      </div>

      {/* Violations Table */}
      <div className="glass-card overflow-hidden">
        {loading ? (
          <div className="flex items-center justify-center py-20">
            <Loader2 size={32} className="animate-spin text-primary" />
          </div>
        ) : filtered.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-20 text-gray-500">
            <ShieldCheck size={48} className="mb-4 opacity-30" />
            <p className="text-lg font-medium">No violations found</p>
            <p className="text-sm">Your assets are currently safe.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left">
              <thead>
                <tr className="border-b border-white/5 bg-surfaceHighlight/30">
                  <th className="px-6 py-4 text-xs font-semibold text-gray-400 uppercase tracking-wider">Platform</th>
                  <th className="px-6 py-4 text-xs font-semibold text-gray-400 uppercase tracking-wider">Domain / Source</th>
                  <th className="px-6 py-4 text-xs font-semibold text-gray-400 uppercase tracking-wider">Confidence</th>
                  <th className="px-6 py-4 text-xs font-semibold text-gray-400 uppercase tracking-wider">Classification</th>
                  <th className="px-6 py-4 text-xs font-semibold text-gray-400 uppercase tracking-wider">Status</th>
                  <th className="px-6 py-4 text-xs font-semibold text-gray-400 uppercase tracking-wider">Detected</th>
                  <th className="px-6 py-4 text-xs font-semibold text-gray-400 uppercase tracking-wider text-right">Action</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map((v) => (
                  <tr
                    key={v.id}
                    className="border-b border-white/5 hover:bg-surfaceHighlight/30 transition-colors cursor-pointer group"
                    onClick={() => openDetail(v)}
                  >
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2 text-sm text-gray-300">
                        {platformIcons[v.platform] || <Globe size={14} />}
                        <span className="capitalize">{v.platform?.replace('_', ' ')}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <p className="text-sm font-medium text-white truncate max-w-[240px]">{v.domain || v.video_title || 'Unknown'}</p>
                      <p className="text-xs text-gray-500 truncate max-w-[240px]">{v.source_url}</p>
                    </td>
                    <td className="px-6 py-4 w-44">
                      <ConfidenceMeter score={v.confidence_score} />
                    </td>
                    <td className="px-6 py-4">
                      <span className={`badge ${v.classification === 'VIOLATION' ? 'badge-danger' : v.classification === 'SUSPICIOUS' ? 'badge-warning' : 'badge-primary'}`}>
                        {v.classification}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <span className={`badge ${statusColors[v.status] || 'badge-primary'}`}>
                        {v.status?.replace('_', ' ')}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-400">
                      {v.detected_at ? new Date(v.detected_at).toLocaleDateString() : 'N/A'}
                    </td>
                    <td className="px-6 py-4 text-right">
                      <button
                        className="opacity-0 group-hover:opacity-100 transition-opacity btn-secondary py-1.5 px-3 text-xs"
                        onClick={(e) => { e.stopPropagation(); openDetail(v); }}
                      >
                        <Eye size={14} />
                        Inspect
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Detail Modal */}
      {selectedViolation && (
        <ViolationDetailModal
          violation={selectedViolation}
          onClose={() => setSelectedViolation(null)}
        />
      )}
    </div>
  );
}
