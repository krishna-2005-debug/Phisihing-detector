import React, { useState, useEffect } from "react";
import axios from "axios";
import "./App.css";

/* ── Minimal SVG icons ─────────────────────────────────── */
const Icon = ({ d, size = 15, style = {} }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none"
    stroke="currentColor" strokeWidth="1.8" strokeLinecap="round"
    strokeLinejoin="round" style={{ display: "inline-block", flexShrink: 0, ...style }}>
    {typeof d === "string" ? <path d={d} /> : d}
  </svg>
);

const icons = {
  shield:  "M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z",
  globe:   <><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></>,
  search:  <><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></>,
  check:   "M22 11.08V12a10 10 0 1 1-5.93-9.14M22 4 12 14.01l-3-3",
  close:   <><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></>,
  x:       <><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></>,
  warn:    <><path d="M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></>,
  lock:    <><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></>,
  unlock:  <><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 9.9-1"/></>,
  hash:    <><line x1="4" y1="9" x2="20" y2="9"/><line x1="4" y1="15" x2="20" y2="15"/><line x1="10" y1="3" x2="8" y2="21"/><line x1="16" y1="3" x2="14" y2="21"/></>,
  layers:  "M12 2 2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5",
  server:  <><rect x="2" y="2" width="20" height="8" rx="2"/><rect x="2" y="14" width="20" height="8" rx="2"/><line x1="6" y1="6" x2="6.01" y2="6"/><line x1="6" y1="18" x2="6.01" y2="18"/></>,
  trash:   <><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></>,
  settings:<><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/></>,
  list:    <><line x1="8" y1="6" x2="21" y2="6"/><line x1="8" y1="12" x2="21" y2="12"/><line x1="8" y1="18" x2="21" y2="18"/><line x1="3" y1="6" x2="3.01" y2="6"/><line x1="3" y1="12" x2="3.01" y2="12"/><line x1="3" y1="18" x2="3.01" y2="18"/></>,
};

const API_BASE = process.env.REACT_APP_API_URL || "http://localhost:8000";

function App() {
  const [url, setUrl]                 = useState("");
  const [threshold, setThreshold]     = useState(0.5);
  const [deepMode, setDeepMode]       = useState(true);
  const [demoMode, setDemoMode]       = useState(false);
  const [result, setResult]           = useState(null);
  const [isLoading, setIsLoading]     = useState(false);
  const [loadingStep, setLoadingStep] = useState("");
  const [backendOk, setBackendOk]     = useState(true);
  const [urlError, setUrlError]       = useState("");

  const defaultHistory = [
    { url: "http://secure-login-bank-verification.com/login.html", label: "PHISH", prob: 0.88, time: "10:24 AM",
      features: { url_length: 56, is_https: false, has_ip: false, subdomain_depth: 3 }, risk: "High" },
    { url: "https://www.google.com", label: "SAFE", prob: 0.04, time: "10:20 AM",
      features: { url_length: 22, is_https: true, has_ip: false, subdomain_depth: 2 }, risk: "Low" },
  ];

  const [history, setHistory] = useState(() => {
    try { return JSON.parse(localStorage.getItem("pd_history")) || defaultHistory; }
    catch { return defaultHistory; }
  });

  useEffect(() => {
    axios.get(`${API_BASE}/health`, { timeout: 3000 })
      .then(() => setBackendOk(true))
      .catch(() => { setBackendOk(false); setDemoMode(true); });
  }, []);

  useEffect(() => {
    localStorage.setItem("pd_history", JSON.stringify(history));
  }, [history]);

  /* local heuristic fallback */
  const localScan = (raw) => {
    const isHttps = raw.toLowerCase().startsWith("https");
    const len = raw.length;
    const hasIp = /\d{1,3}(\.\d{1,3}){3}/.test(raw);
    const domain = raw.replace(/^https?:\/\//i, "").split("/")[0];
    const depth = (domain.match(/\./g) || []).length;
    const hasSensitive = /login|verify|secure|bank|paypal|update|account/i.test(raw);

    let p = 0.15;
    if (!isHttps) p += 0.22;
    if (len > 50)  p += 0.14;
    if (hasIp)     p += 0.22;
    if (depth > 3) p += 0.12;
    if (hasSensitive) p += 0.18;
    p = Math.min(0.97, Math.max(0.03, p + (Math.random() * 0.06 - 0.03)));
    const prob = Math.round(p * 100) / 100;
    const risk = prob > 0.7 ? "High" : prob > 0.4 ? "Medium" : "Low";
    return {
      url: raw, probability: prob, is_phishing: prob > threshold,
      risk_level: risk,
      features_extracted: { url_length: len, is_https: isHttps, has_ip: hasIp, subdomain_depth: depth }
    };
  };

  const scan = async () => {
    const raw = url.trim();
    if (!raw) { setUrlError("Please enter a URL."); return; }
    setUrlError("");

    let target = raw;
    if (!/^https?:\/\//i.test(target)) target = "http://" + target;

    setIsLoading(true);
    setResult(null);

    const steps = [
      "Resolving hostname…",
      "Checking SSL/TLS certificate…",
      "Extracting URL features…",
      "Running classifier…",
    ];
    for (let s of steps) {
      setLoadingStep(s);
      await new Promise(r => setTimeout(r, 280));
    }

    let data;
    try {
      if (demoMode) throw new Error("demo");
      const res = await axios.post(`${API_BASE}/predict`, {
        url: target, include_content: deepMode, threshold: Number(threshold)
      });
      data = res.data;
    } catch (err) {
      // 422 = validation error from backend — surface to user, don't fall back
      if (err?.response?.status === 422) {
        const detail = err.response.data?.detail || "Invalid URL format.";
        setUrlError(detail);
        setIsLoading(false);
        return;
      }
      data = localScan(target);
      setBackendOk(false);
    }

    setResult(data);
    const item = {
      url: target, label: data.is_phishing ? "PHISH" : "SAFE",
      prob: data.probability, time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      features: data.features_extracted, risk: data.risk_level
    };
    setHistory(prev => [item, ...prev.filter(h => h.url !== target)].slice(0, 15));
    setIsLoading(false);
  };

  const loadItem = (h) => {
    setUrl(h.url);
    setResult({ url: h.url, probability: h.prob, is_phishing: h.label === "PHISH", risk_level: h.risk, features_extracted: h.features });
  };

  /* colour helpers */
  const riskColor = (risk) => risk === "High" ? "var(--red)" : risk === "Medium" ? "var(--yellow)" : "var(--green)";
  const pct = result ? Math.round(result.probability * 100) : 0;
  const bannerCls = result
    ? result.is_phishing ? "banner banner-danger"
    : result.risk_level === "Medium" ? "banner banner-warning"
    : "banner banner-safe"
    : "";

  return (
    <div className="app">
      {/* ── Topbar ── */}
      <header className="topbar">
        <div className="topbar-brand">
          <Icon d={icons.shield} size={17} />
          ShieldAI
        </div>
        <div className="topbar-status">
          <span className={`status-dot${!backendOk ? " offline" : ""}`} />
          {demoMode ? "Demo mode" : backendOk ? "ML classifier active" : "Offline — local mode"}
        </div>
      </header>

      <div className="main">
        {/* ── Sidebar ── */}
        <aside className="sidebar">
          {/* Settings */}
          <div className="sidebar-card">
            <div className="sidebar-card-title">
              <Icon d={icons.settings} size={12} /> Settings
            </div>

            <div className="setting-row">
              <div className="setting-label">
                <span>Sensitivity</span>
                <span>{Number(threshold).toFixed(2)}</span>
              </div>
              <input type="range" className="slider"
                min="0.3" max="0.9" step="0.05"
                value={threshold} onChange={e => setThreshold(e.target.value)} />
            </div>

            <label className="toggle-row">
              <span className="toggle-label">Deep HTML analysis</span>
              <input type="checkbox" className="toggle-input"
                checked={deepMode} onChange={e => setDeepMode(e.target.checked)} />
              <div className="toggle-track" />
            </label>

            <label className="toggle-row">
              <span className="toggle-label">Force offline demo</span>
              <input type="checkbox" className="toggle-input"
                checked={demoMode} onChange={e => setDemoMode(e.target.checked)} />
              <div className="toggle-track" />
            </label>
          </div>

          {/* History */}
          <div className="sidebar-card">
            <div className="sidebar-card-title">
              <Icon d={icons.list} size={12} /> Recent scans
            </div>

            {history.length === 0
              ? <p className="empty-note">No scans yet.</p>
              : (
                <div className="history-list">
                  {history.map((h, i) => (
                    <div key={i} className="history-item" onClick={() => loadItem(h)}>
                      <div className="history-item-top">
                        <span className="history-time">{h.time}</span>
                        <span className={`pill ${h.label === "PHISH" ? "pill-phish" : "pill-safe"}`}>
                          {h.label}
                        </span>
                      </div>
                      <span className="history-url">{h.url}</span>
                      <span className="history-score">{Math.round(h.prob * 100)}% risk</span>
                    </div>
                  ))}
                </div>
              )
            }

            {history.length > 0 && (
              <button className="clear-link"
                onClick={() => { setHistory([]); localStorage.removeItem("pd_history"); }}>
                <Icon d={icons.trash} size={12} /> Clear history
              </button>
            )}
          </div>
        </aside>

        {/* ── Content ── */}
        <div className="content">
          <div>
            <h1 className="page-title">Phishing URL Scanner</h1>
            <p className="page-sub">Paste a URL to check whether it shows signs of phishing.</p>
          </div>

          {/* Input card */}
          <div className="input-card">
            <div className="input-label">
              <Icon d={icons.globe} size={12} />
              Enter a URL to scan
            </div>
            <div className="input-row">
              <div className="url-wrap">
                <span className="url-prefix">
                  <Icon d={icons.globe} size={12} />
                  URL
                </span>
                <input className="url-input"
                  type="text"
                  placeholder="https://example.com/path"
                  value={url}
                  onChange={e => { setUrl(e.target.value); setUrlError(""); }}
                  onKeyDown={e => e.key === "Enter" && scan()}
                  disabled={isLoading}
                  style={urlError ? { borderColor: "var(--red, #dc2626)" } : {}}
                />
                {url && (
                  <button
                    className="url-clear"
                    onClick={() => setUrl("")}
                    title="Clear"
                    tabIndex={-1}
                  >
                    <Icon d={icons.close} size={13} />
                  </button>
                )}
              </div>
              <button className="scan-btn" onClick={scan} disabled={isLoading}>
                {isLoading
                  ? <><div className="spin" /> Scanning</>
                  : <><Icon d={icons.search} size={14} /> Scan URL</>
                }
              </button>
            </div>
          </div>
          {/* URL Error */}
          {urlError && (
            <div className="url-error-banner">
              <Icon d={icons.warn} size={14} style={{ flexShrink: 0 }} />
              <span>{urlError}</span>
            </div>
          )}

          {/* Loading */}
          {isLoading && (
            <div className="loading-card">
              <div className="loading-spin" />
              <div className="loading-title">Analyzing…</div>
              <div className="loading-step">{loadingStep}</div>
            </div>
          )}

          {/* Results */}
          {!isLoading && result && (
            <>
              {/* Banner */}
              <div className={bannerCls}>
                <div className="banner-left">
                  <div className="banner-icon">
                    {result.is_phishing
                      ? <Icon d={icons.x} size={18} />
                      : result.risk_level === "Medium"
                      ? <Icon d={icons.warn} size={18} />
                      : <Icon d={icons.check} size={18} />
                    }
                  </div>
                  <div className="banner-text">
                    <h2>
                      {result.is_phishing
                        ? "Phishing detected"
                        : result.risk_level === "Medium"
                        ? "Looks suspicious"
                        : "Looks safe"}
                    </h2>
                    <p>{result.url}</p>
                  </div>
                </div>
                <div className="banner-score">{pct}%</div>
              </div>

              {/* Two-col cards */}
              <div className="result-grid">
                {/* Risk meter */}
                <div className="result-card">
                  <div className="result-card-header">
                    <Icon d={icons.server} size={13} /> Threat score
                  </div>
                  <div className="result-card-body">
                    <div className="gauge-row">
                      <div className="gauge-bar-wrap">
                        <div className="gauge-bar-fill" style={{
                          width: `${pct}%`,
                          background: riskColor(result.risk_level)
                        }} />
                      </div>
                      <div className="gauge-pct" style={{ color: riskColor(result.risk_level) }}>
                        {pct}%
                      </div>
                    </div>

                    <div className="gauge-details">
                      <div className="gauge-detail-row">
                        <span>Classification</span>
                        <span style={{ color: riskColor(result.risk_level) }}>
                          {result.is_phishing ? "Dangerous" : result.risk_level === "Medium" ? "Suspicious" : "Clean"}
                        </span>
                      </div>
                      <div className="gauge-detail-row">
                        <span>Risk level</span>
                        <span>{result.risk_level}</span>
                      </div>
                      <div className="gauge-detail-row">
                        <span>Sensitivity</span>
                        <span>{Number(threshold).toFixed(2)}</span>
                      </div>
                      <div className="gauge-detail-row">
                        <span>Deep mode</span>
                        <span>{deepMode ? "On" : "Off"}</span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Feature breakdown */}
                <div className="result-card">
                  <div className="result-card-header">
                    <Icon d={icons.layers} size={13} /> URL features
                  </div>
                  <div className="result-card-body">
                    <div className="feature-list">
                      {/* HTTPS */}
                      <div className="feature-row">
                        <div className="feature-name">
                          <Icon d={result.features_extracted?.is_https ? icons.lock : icons.unlock} size={13} />
                          Connection
                        </div>
                        <span className={`feature-val ${result.features_extracted?.is_https ? "val-good" : "val-bad"}`}>
                          {result.features_extracted?.is_https ? "HTTPS" : "HTTP"}
                        </span>
                      </div>

                      {/* Length */}
                      <div className="feature-row">
                        <div className="feature-name">
                          <Icon d={icons.hash} size={13} />
                          URL length
                        </div>
                        <span className={`feature-val ${(result.features_extracted?.url_length || 0) > 45 ? "val-bad" : "val-good"}`}>
                          {result.features_extracted?.url_length} chars
                        </span>
                      </div>

                      {/* Subdomain depth */}
                      <div className="feature-row">
                        <div className="feature-name">
                          <Icon d={icons.layers} size={13} />
                          Subdomain depth
                        </div>
                        <span className={`feature-val ${(result.features_extracted?.subdomain_depth || 0) > 3 ? "val-warn" : "val-neutral"}`}>
                          {result.features_extracted?.subdomain_depth}
                        </span>
                      </div>

                      {/* IP in URL */}
                      <div className="feature-row">
                        <div className="feature-name">
                          <Icon d={icons.server} size={13} />
                          Raw IP in URL
                        </div>
                        <span className={`feature-val ${result.features_extracted?.has_ip ? "val-bad" : "val-good"}`}>
                          {result.features_extracted?.has_ip ? "Yes" : "No"}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Recommendations */}
              <div className="recs-card">
                <div className="recs-card-header">
                  <Icon d={icons.shield} size={13} /> Recommendations
                </div>
                <div className="rec-list">
                  {result.is_phishing ? (
                    <>
                      <div className="rec">
                        <div className="rec-dot rec-dot-red" />
                        <div><strong>Do not enter any credentials.</strong> This URL has strong phishing signals — avoid submitting passwords, card numbers, or personal info.</div>
                      </div>
                      <div className="rec">
                        <div className="rec-dot rec-dot-red" />
                        <div><strong>Verify the domain spelling carefully.</strong> Attackers buy lookalike domains (e.g. "paypa1.com") to impersonate real services.</div>
                      </div>
                      <div className="rec">
                        <div className="rec-dot rec-dot-red" />
                        <div><strong>Report it.</strong> You can report phishing to Google Safe Browsing or your browser's security team.</div>
                      </div>
                    </>
                  ) : result.risk_level === "Medium" ? (
                    <>
                      <div className="rec">
                        <div className="rec-dot rec-dot-yellow" />
                        <div><strong>Proceed with caution.</strong> Some signals are ambiguous. Double-check the domain and look for a valid SSL certificate.</div>
                      </div>
                      <div className="rec">
                        <div className="rec-dot rec-dot-yellow" />
                        <div>Avoid submitting sensitive information until you can verify the site's legitimacy through a trusted source.</div>
                      </div>
                    </>
                  ) : (
                    <>
                      <div className="rec">
                        <div className="rec-dot rec-dot-green" />
                        <div><strong>This URL appears safe.</strong> No phishing indicators were found. Still, always verify that you meant to visit this domain.</div>
                      </div>
                      <div className="rec">
                        <div className="rec-dot rec-dot-green" />
                        <div>Keep your browser and security software up to date even for trusted sites.</div>
                      </div>
                    </>
                  )}
                </div>
              </div>
            </>
          )}

          <footer className="footer">ShieldAI v1.2 · FastAPI + Random Forest · local heuristic fallback</footer>
        </div>
      </div>
    </div>
  );
}

export default App;
