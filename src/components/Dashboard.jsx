import React, { useState, useEffect, useRef } from 'react';
import Navigation from './Navigation';
import { motion } from 'framer-motion';
import { LIQUID_SPRING } from '../lib/constants';


const Dashboard = ({ navigate }) => {
    const [stats, setStats] = useState({
        metrics: { total_scans: 0, active_scans: 0, vulnerabilities: 0, critical: 0 },
        // V6: New Metrics
        v6_metrics: {
            injections_blocked: 0,
            deceptive_ui_blocked: 0,
            risk_score: 0
        },
        graph_data: [],
        threat_feed: []
    });

    const [latestThreat, setLatestThreat] = useState(null); // [NEW] For Explainability Panel

    const wsRef = useRef(null);

    useEffect(() => {
        const fetchStats = async () => {
            try {
                const res = await fetch("http://127.0.0.1:8000/api/dashboard/stats");
                const data = await res.json();

                // DEFENSIVE MERGE: Ensure v6_metrics exists even if backend is old
                setStats(prev => ({
                    ...prev,
                    ...data,
                    v6_metrics: data.v6_metrics || { injections_blocked: 0, deceptive_ui_blocked: 0, risk_score: 0 }
                }));
            } catch (e) {
                console.error("Failed to fetch dashboard stats", e);
            }
        };

        fetchStats();
        const interval = setInterval(fetchStats, 5000);

        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/stream?client_type=ui`;

        wsRef.current = new WebSocket(wsUrl);
        wsRef.current.onopen = () => console.log("Dashboard: Connected to Real-time Stream");

        wsRef.current.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);

                if (data.type === 'VULN_UPDATE') {
                    setStats(prev => ({
                        ...prev,
                        metrics: data.payload.metrics || data.payload,
                        graph_data: data.payload.history || prev.graph_data
                    }));
                }
                else if (data.type === 'LIVE_THREAT_LOG') {
                    // Update Panel
                    setLatestThreat(data.payload);

                    setStats(prev => {
                        // V6: Calculate new metrics (Defensive)
                        const defaultV6 = { injections_blocked: 0, deceptive_ui_blocked: 0, risk_score: 0 };
                        const currentV6 = prev.v6_metrics || defaultV6;
                        const newMetrics = { ...currentV6 };
                        const threat = data.payload;

                        if (['PROMPT_INJECTION', 'INVISIBLE_TEXT', 'HIDDEN_TEXT'].includes(threat.threat_type)) {
                            newMetrics.injections_blocked += 1;
                        } else if (['DECEPTIVE_UI', 'PHISHING', 'ROACH_MOTEL', 'DARK_PATTERN_BLOCK'].includes(threat.threat_type)) {
                            newMetrics.deceptive_ui_blocked += 1;
                        }

                        let score = threat.risk_score || (threat.severity === 'CRITICAL' ? 95 : 50);
                        newMetrics.risk_score = score;

                        return {
                            ...prev,
                            v6_metrics: newMetrics,
                            threat_feed: [data.payload, ...(prev.threat_feed || [])].slice(0, 50)
                        };
                    });
                }
                else if (data.type === 'ATTACK_HIT' || data.type === 'RECON_PACKET' || data.type === 'GI5_CRITICAL') {
                    setStats(prev => {
                        const currentVal = prev.metrics.vulnerabilities || 0;
                        const jitter = Math.random() * 0.5;
                        const activePoint = currentVal + jitter;
                        const newGraphData = [...(prev.graph_data || []), activePoint].slice(-30);
                        return {
                            ...prev,
                            graph_data: newGraphData
                        };
                    });
                }
            } catch (e) {
                console.error("WS Graph Error", e);
            }
        };

        return () => {
            clearInterval(interval);
            if (wsRef.current) wsRef.current.close();
        };
    }, []);

    const generateGraphPath = React.useCallback((data) => {
        if (!data || data.length === 0) return "";
        const maxVal = Math.max(...data, 1);
        const width = 1000;
        const height = 300;
        const pointWidth = width / (data.length - 1);
        let path = `M0,${height} `;
        data.forEach((val, i) => {
            const x = i * pointWidth;
            const y = height - (val / maxVal) * (height * 0.8);
            path += `L${x},${y} `;
        });
        path += `L${width},${height} Z`;
        return path;
    }, []);

    const generateLinePath = React.useCallback((data) => {
        if (!data || data.length === 0) return "";
        const maxVal = Math.max(...data, 1);
        const width = 1000;
        const height = 300;
        const pointWidth = width / (data.length - 1);
        let d = "";
        data.forEach((val, i) => {
            const x = i * pointWidth;
            const y = height - (val / maxVal) * (height * 0.8);
            if (i === 0) d += `M${x},${y}`;
            else d += ` L${x},${y}`;
        });
        return d;
    }, []);

    return (
        <div className="min-h-screen relative overflow-x-hidden" style={{ fontFamily: "'Space Grotesk', sans-serif" }}>
            <div className="relative z-10 flex flex-col min-h-screen">
                <Navigation navigate={navigate} activePage="dashboard" />

                <main className="flex-grow px-6 pb-6 w-full max-w-7xl mx-auto space-y-6">
                    <motion.div
                        initial={{ opacity: 0, y: -20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ ...LIQUID_SPRING, duration: 0.5 }}
                        className="mt-4 mb-6"
                    >
                        <h1 className="text-3xl font-bold mb-1 text-white">Dashboard</h1>
                        <p className="text-gray-400 text-sm">View and manage your security assessments overview.</p>
                    </motion.div>

                    {stats && (
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                            {[
                                { title: 'Injections Blocked', value: stats?.v6_metrics?.injections_blocked || 0, icon: 'shield', color: 'purple', glow: 'card-glow-purple', bgIcon: 'bg-purple-500/20 text-purple-300', trend: 0 },
                                { title: 'Deceptive UI', value: stats?.v6_metrics?.deceptive_ui_blocked || 0, icon: 'visibility_off', color: 'orange', glow: 'card-glow-orange', bgIcon: 'bg-orange-500/20 text-orange-300', trend: 0 },
                                {
                                    title: 'Live Risk Score',
                                    value: (stats?.v6_metrics?.risk_score || 0) + '%',
                                    icon: 'speed',
                                    color: (stats?.v6_metrics?.risk_score || 0) > 80 ? 'red' : 'green',
                                    glow: (stats?.v6_metrics?.risk_score || 0) > 80 ? 'card-glow-red' : 'card-glow-green',
                                    bgIcon: (stats?.v6_metrics?.risk_score || 0) > 80 ? 'bg-red-500/20 text-red-300' : 'bg-green-500/20 text-green-300',
                                    trend: 0
                                },
                                { title: 'Active Scans', value: stats?.metrics?.active_scans || 0, icon: 'sensors', color: 'blue', glow: 'card-glow-blue', bgIcon: 'bg-blue-500/20 text-blue-300', isLive: true, trend: 0 }
                            ].map((item, i) => (
                                <motion.div
                                    key={i}
                                    initial={{ opacity: 0, scale: 0.9 }}
                                    animate={{ opacity: 1, scale: 1 }}
                                    transition={{ ...LIQUID_SPRING, delay: i * 0.1 }}
                                    whileHover={{ scale: 1.02, y: -5, transition: { duration: 0.2 } }}
                                    className="glass-panel-dash p-5 rounded-2xl relative overflow-hidden group"
                                >
                                    <div className={`absolute inset-0 ${item.glow} transition-opacity duration-300 opacity-60 group-hover:opacity-100`}></div>
                                    <div className="flex justify-between items-start mb-4 relative z-10">
                                        <div className={`p-2 rounded-lg ${item.color.startsWith('bg') ? item.color : `${item.color.replace('text-', 'bg-').replace('500', '500/20')}`} ${item.bgIcon ? '' : 'text-' + item.color + '-300'}`}>
                                            <span className={`material-symbols-outlined text-xl ${item.bgIcon ? '' : 'text-current'}`}>{item.icon}</span>
                                        </div>
                                        <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${item.trend >= 0 ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'}`}>
                                            LIVE
                                        </span>
                                    </div>
                                    <div className="relative z-10">
                                        <h3 className="text-gray-400 text-sm font-medium">{item.title}</h3>
                                        <p className="text-2xl font-bold text-white mt-1">{item.value}</p>
                                    </div>
                                </motion.div>
                            ))}
                        </div>
                    )}

                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ ...LIQUID_SPRING, delay: 0.2 }}
                        className="glass-panel-dash rounded-2xl p-6 relative overflow-hidden flex flex-col h-[380px]"
                    >
                        <div className="flex justify-between items-center mb-4 relative z-10">
                            <h2 className="text-sm font-medium text-gray-200">Scan Activity (Last 30 Days)</h2>
                        </div>
                        <div className="flex-grow w-full h-full relative z-0 mt-2">
                            {stats?.graph_data && Array.isArray(stats.graph_data) && stats.graph_data.length > 0 && (
                                <svg className="w-full h-full drop-shadow-[0_0_15px_rgba(139,92,246,0.3)]" preserveAspectRatio="none" viewBox="0 0 1000 300">
                                    <defs>
                                        <linearGradient id="lineGradient" x1="0%" x2="100%" y1="0%" y2="0%">
                                            <stop offset="0%" stopColor="#d946ef"></stop>
                                            <stop offset="50%" stopColor="#8b5cf6"></stop>
                                            <stop offset="100%" stopColor="#06b6d4"></stop>
                                        </linearGradient>
                                        <linearGradient id="areaGradient" x1="0%" x2="0%" y1="0%" y2="100%">
                                            <stop offset="0%" stopColor="#8b5cf6" stopOpacity="0.4"></stop>
                                            <stop offset="100%" stopColor="#8b5cf6" stopOpacity="0"></stop>
                                        </linearGradient>
                                    </defs>
                                    <motion.path
                                        initial={{ pathLength: 0, opacity: 0 }}
                                        animate={{ pathLength: 1, opacity: 0.8 }}
                                        transition={{ duration: 1.5, ease: "easeInOut" }}
                                        className="transition-all duration-700 ease-in-out"
                                        d={generateGraphPath(stats.graph_data)}
                                        fill="url(#areaGradient)"
                                    ></motion.path>
                                    <motion.path
                                        initial={{ pathLength: 0 }}
                                        animate={{ pathLength: 1 }}
                                        transition={{ duration: 2, ease: "easeInOut" }}
                                        className="animate-draw transition-all duration-700 ease-in-out"
                                        d={generateLinePath(stats.graph_data)}
                                        fill="none"
                                        stroke="url(#lineGradient)"
                                        strokeLinecap="round"
                                        strokeWidth="6"
                                    ></motion.path>
                                </svg>
                            )}
                        </div>
                    </motion.div>

                    {/* Main Content Grid: Live Threat Monitor (Full Width) */}
                    <div className="grid grid-cols-1 gap-6 h-[400px]">
                        {/* LIVE THREAT MONITOR */}
                        <motion.div
                            initial={{ opacity: 0, scale: 0.95 }}
                            animate={{ opacity: 1, scale: 1 }}
                            transition={{ ...LIQUID_SPRING, delay: 0.3 }}
                            className="glass-panel-dash rounded-2xl p-0 relative overflow-hidden flex flex-col h-full"
                        >
                            <div className="p-4 border-b border-white/10 bg-black/20 flex justify-between items-center">
                                <h3 className="text-sm font-medium text-gray-200 flex items-center gap-2">
                                    <span className="w-2 h-2 bg-red-500 rounded-full animate-pulse shadow-[0_0_10px_red]"></span>
                                    LIVE THREAT MONITOR
                                </h3>
                                <div className="flex gap-4 text-xs font-mono text-gray-500">
                                    <span>STATUS: {stats?.metrics?.active_scans > 0 ? 'ONLINE' : 'STANDBY'}</span>
                                </div>
                            </div>

                            {/* TABLE HEADER */}
                            <div className="grid grid-cols-12 gap-2 px-4 py-2 bg-black/40 text-[10px] font-mono text-gray-500 uppercase tracking-wider border-b border-white/5">
                                <div className="col-span-2">Time</div>
                                <div className="col-span-2">Agent</div>
                                <div className="col-span-2">Threat Type</div>
                                <div className="col-span-4">Target / Payload</div>
                                <div className="col-span-1">Severity</div>
                                <div className="col-span-1 text-right">Risk</div>
                            </div>

                            <div className="flex-grow overflow-y-auto font-mono text-xs bg-black/40 relative">
                                <div className="absolute inset-0 pointer-events-none bg-[url('https://media.giphy.com/media/oEI9uBYSzLpBK/giphy.gif')] opacity-[0.02]"></div>

                                {stats.threat_feed && stats.threat_feed.length > 0 ? stats.threat_feed.map((item, idx) => {
                                    // Agent Mapping logic
                                    let agentName = "UNKNOWN";
                                    let agentColor = "text-gray-400";

                                    if (item.agent?.includes('theta')) { agentName = "THE SENTINEL"; agentColor = "text-purple-400"; }
                                    else if (item.agent?.includes('iota')) { agentName = "THE INSPECTOR"; agentColor = "text-orange-400"; }
                                    else if (item.agent?.includes('beta')) { agentName = "BETA (BREAKER)"; agentColor = "text-red-400"; }

                                    return (
                                        <motion.div
                                            key={`threat-${idx}`}
                                            initial={{ x: -20, opacity: 0 }}
                                            animate={{ x: 0, opacity: 1 }}
                                            transition={{ duration: 0.2 }}
                                            className={`grid grid-cols-12 gap-2 px-4 py-2 border-b border-white/5 hover:bg-white/5 transition-colors items-center ${item.severity === 'CRITICAL' ? 'bg-red-500/5' : ''
                                                }`}
                                        >
                                            <div className="col-span-2 text-gray-500">{item.timestamp}</div>
                                            <div className={`col-span-2 font-bold ${agentColor}`}>{agentName}</div>
                                            <div className="col-span-2 text-gray-300 truncate" title={item.threat_type}>{item.threat_type}</div>
                                            <div className="col-span-4 text-gray-400 truncate font-light" title={item.url}>{item.url}</div>
                                            <div className="col-span-1">
                                                <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${item.severity === 'CRITICAL' ? 'bg-red-500 text-black' :
                                                    item.severity === 'HIGH' ? 'bg-orange-500 text-black' :
                                                        'bg-blue-500 text-black'
                                                    }`}>
                                                    {item.severity}
                                                </span>
                                            </div>
                                            <div className="col-span-1 text-right font-bold text-white">
                                                {item.risk_score || 0}%
                                            </div>
                                        </motion.div>
                                    );
                                }) : (
                                    <div className="flex flex-col items-center justify-center h-full text-gray-600 opacity-50">
                                        <span className="material-icons text-4xl mb-2">security</span>
                                        <p>SYSTEM SECURE // NO ACTIVE THREATS</p>
                                    </div>
                                )}
                            </div>
                        </motion.div>
                    </div>
                </main>

                <footer className="w-full text-center py-6 text-xs text-gray-600 relative z-10">
                    Antigravity API Endpoint Scanning System
                </footer>
            </div>
        </div>
    );
};

export default Dashboard;
