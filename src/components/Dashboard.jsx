import React, { useState, useEffect, useRef } from 'react';
import Navigation from './Navigation';

import { motion } from 'framer-motion';
import { LIQUID_SPRING } from '../lib/constants';
// Note: Dashboard relies more on layout animations, but we can standardise entries.

const Dashboard = ({ navigate }) => {
    // ... (state and effects remain the same)
    const [stats, setStats] = useState({
        metrics: { total_scans: 0, active_scans: 0, vulnerabilities: 0, critical: 0 },
        graph_data: [],
        recent_activity: []
    });

    const wsRef = useRef(null);

    useEffect(() => {
        const fetchStats = async () => {
            try {
                const res = await fetch("http://127.0.0.1:8000/api/dashboard/stats");
                const data = await res.json();
                setStats(data);
            } catch (e) {
                console.error("Failed to fetch dashboard stats", e);
            }
        };

        fetchStats();
        // Optional: Poll every 5s for live effect aggregation
        const interval = setInterval(fetchStats, 5000);

        // WebSocket for Real-Time Graph
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/stream?client_type=ui`;

        wsRef.current = new WebSocket(wsUrl);
        wsRef.current.onopen = () => console.log("Dashboard: Connected to Real-time Stream");

        wsRef.current.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);

                // If attack hit or recon, spike the graph
                if (data.type === 'VULN_UPDATE') {
                    // AUTHORITATIVE SYNC FROM BACKEND
                    setStats(prev => ({
                        ...prev,
                        metrics: data.payload.metrics || data.payload, // Handle direct stats object
                        graph_data: data.payload.history || prev.graph_data,
                        // Add a notification log
                        recent_activity: [{
                            text: "Real-time: Vulnerability Confirmed",
                            time: "Just now",
                            type: "critical"
                        }, ...(prev.recent_activity || [])].slice(0, 5)
                    }));
                }

                // If attack hit or recon, spike the graph (Visual only, stats come from VULN_UPDATE now)
                else if (data.type === 'ATTACK_HIT' || data.type === 'RECON_PACKET' || data.type === 'GI5_CRITICAL') {
                    setStats(prev => {
                        // SYNC GRAPH WITH REALITY:
                        // Push current vulnerability count + slight jitter for liveness
                        const currentVal = prev.metrics.vulnerabilities || 0;
                        const jitter = Math.random() * 0.5;
                        const activePoint = currentVal + jitter;

                        const newGraphData = [...(prev.graph_data || []), activePoint].slice(-30);

                        return {
                            ...prev,
                            graph_data: newGraphData,
                            // Don't mess with metrics here, wait for VULN_UPDATE
                            recent_activity: [{
                                text: `Event: ${data.type}`,
                                time: 'Just now',
                                type: 'info'
                            }, ...(prev.recent_activity || [])].slice(0, 5)
                        };
                    });
                } else if (data.type === 'GI5_LOG') {
                    // Visualizing AI "Thoughts" without creating a graph spike, just log
                    setStats(prev => {
                        const newActivity = {
                            text: `BRAIN: ${typeof data.payload === 'string' ? data.payload : JSON.stringify(data.payload)}`,
                            time: 'Thinking...',
                            type: 'info'
                        };
                        return {
                            ...prev,
                            recent_activity: [newActivity, ...(prev.recent_activity || [])].slice(0, 5)
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

    // Generate Path for Graph
    const generateGraphPath = React.useCallback((data) => {
        if (!data || data.length === 0) return "";
        const maxVal = Math.max(...data, 1);
        const width = 1000;
        const height = 300;
        const pointWidth = width / (data.length - 1);

        let path = `M0,${height} `; // Start bottom left

        data.forEach((val, i) => {
            const x = i * pointWidth;
            const y = height - (val / maxVal) * (height * 0.8); // Scale to 80% height
            path += `L${x},${y} `;
        });

        path += `L${width},${height} Z`; // Close to bottom right
        return path;
    }, []);

    const generateLinePath = React.useCallback((data) => {
        if (!data || data.length === 0) return "";
        const maxVal = Math.max(...data, 1);
        const width = 1000;
        const height = 300;
        const pointWidth = width / (data.length - 1);

        // Creating a smooth curve (simple implementation) or straight lines
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
            {/* Background is now global in App component */}

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

                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                        {[
                            { title: 'Total Scans', value: stats?.metrics?.total_scans || 0, icon: 'assignment', color: 'purple', glow: 'card-glow-purple', bgIcon: 'bg-purple-500/20 text-purple-300', trend: 5 },
                            { title: 'Active Scans', value: stats?.metrics?.active_scans || 0, icon: 'sensors', color: 'green', glow: 'card-glow-green', bgIcon: 'bg-green-500/20 text-green-300', isLive: true, trend: -2 },
                            { title: 'Vulnerabilities', value: stats?.metrics?.vulnerabilities || 0, icon: 'warning_amber', color: 'orange', glow: 'card-glow-orange', bgIcon: 'bg-orange-500/20 text-orange-300', trend: 10 },
                            { title: 'Critical Issues', value: stats?.metrics?.critical || 0, icon: 'report_problem', color: 'red', glow: 'card-glow-red', bgIcon: 'bg-red-500/20 text-red-300', trend: 0 }
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
                                    <div className={`p-2 rounded-lg ${item.color} bg-opacity-20`}>
                                        <span className={`material-symbols-outlined text-xl ${item.color.replace('bg-', 'text-')}`}>{item.icon}</span>
                                    </div>
                                    <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${item.trend > 0 ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'}`}>
                                        {item.trend > 0 ? '+' : ''}{item.trend}%
                                    </span>
                                </div>
                                <div className="relative z-10">
                                    <h3 className="text-gray-400 text-sm font-medium">{item.title}</h3>
                                    <p className="text-2xl font-bold text-white mt-1">{item.value}</p>
                                </div>
                            </motion.div>
                        ))}
                    </div>

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

                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ ...LIQUID_SPRING, delay: 0.3 }}
                        className="glass-panel-dash rounded-2xl p-6"
                    >
                        <h3 className="text-sm font-medium text-gray-200 mb-4">Recent Activity</h3>
                        <div className="space-y-0">
                            {stats.recent_activity && stats.recent_activity.length > 0 ? stats.recent_activity.map((item, idx) => {
                                const color = item.type === 'critical' ? 'bg-red-500' : item.type === 'info' ? 'bg-purple-500' : 'bg-green-500';
                                const shadow = item.type === 'critical' ? 'shadow-[0_0_5px_rgba(239,68,68,0.6)]' : item.type === 'info' ? 'shadow-[0_0_5px_rgba(168,85,247,0.6)]' : 'shadow-[0_0_5px_rgba(34,197,94,0.6)]';

                                return (
                                    <motion.div
                                        key={idx}
                                        initial={{ x: -20, opacity: 0 }}
                                        animate={{ x: 0, opacity: 1 }}
                                        transition={{ ...LIQUID_SPRING, delay: idx * 0.05 }}
                                        className="flex items-center justify-between py-3 border-b border-white/5 hover:bg-white/5 transition-colors px-2 -mx-2 rounded-lg cursor-default group"
                                    >
                                        <div className="flex items-center gap-3">
                                            <div className={`w-2 h-2 rounded-full ${color} ${shadow}`}></div>
                                            <span className="text-sm text-gray-300">{item.text}</span>
                                        </div>
                                        <span className="text-xs text-gray-400 group-hover:text-gray-200 transition-colors">{item.time}</span>
                                    </motion.div>
                                )
                            }) : <div className="text-gray-400 text-sm py-4">No recent activity</div>}
                        </div>
                    </motion.div>
                </main>

                <footer className="w-full text-center py-6 text-xs text-gray-600 relative z-10">
                    Antigravity API Endpoint Scanning System
                </footer>
            </div >
        </div >
    );
};

export default Dashboard;
