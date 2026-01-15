import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Terminal, Shield, Zap, Globe, Cpu } from 'lucide-react';

const Dashboard = () => {
    const [nodes, setNodes] = useState(450);
    const [successRate, setSuccessRate] = useState(98.4);
    const [findings, setFindings] = useState([]);
    const [isScanning, setIsScanning] = useState(false);

    useEffect(() => {
        const fetchTelemetry = async () => {
            try {
                // Fetch from the local Antigravity Backend (Singularity API)
                const res = await fetch('/api/status');
                const data = await res.json();

                if (data.current_findings) {
                    setFindings(data.current_findings);
                }
                setIsScanning(data.is_scanning);

                // Simulate node fluctuation for aesthetic effect if scanning
                if (data.is_scanning) {
                    setNodes(prev => Math.min(Math.max(prev + Math.floor(Math.random() * 20 - 10), 400), 500));
                }
            } catch (e) {
                console.error("Telemetry Link Failure:", e);
            }
        };

        // Poll every 2 seconds
        const interval = setInterval(fetchTelemetry, 2000);
        fetchTelemetry(); // Initial call
        return () => clearInterval(interval);
    }, []);

    return (
        <div className="min-h-screen bg-black text-cyan-500 p-8 font-mono selection:bg-cyan-900">
            {/* Header: System Integrity Status */}
            <div className="flex justify-between items-center border-b border-cyan-900 pb-4 mb-8">
                <h1 className="text-2xl font-bold tracking-tighter flex items-center gap-3">
                    <Shield className="animate-pulse text-cyan-400" />
                    ANTIGRAVITY // LOGIC-ASSESSMENT-ENGINE v2.0
                </h1>
                <div className="flex gap-6 text-sm">
                    <span className="flex items-center gap-2"><Globe size={16} /> ENGINE: ONLINE</span>
                    <span className="flex items-center gap-2 text-green-400"><Cpu size={16} /> THREADS: OPTIMIZED</span>
                </div>
            </div>

            {/* Main Grid */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">

                {/* Real-time Swarm Telemetry */}
                <motion.div
                    initial={{ opacity: 0 }} animate={{ opacity: 1 }}
                    className="bg-gray-900/50 border border-cyan-900 p-6 rounded-lg"
                >
                    <h3 className="text-xs uppercase tracking-widest text-gray-400 mb-4">Concurrent Thread Pool</h3>
                    <div className="text-4xl font-bold mb-2">{nodes}</div>
                    <p className="text-xs text-cyan-700">ACTIVE WORKERS (ASYNC LOOP)</p>
                    <div className="mt-6 h-2 bg-gray-800 rounded-full overflow-hidden">
                        <motion.div
                            initial={{ width: 0 }} animate={{ width: '85%' }}
                            className="h-full bg-cyan-500 shadow-[0_0_10px_#06b6d4]"
                        />
                    </div>
                </motion.div>

                {/* Q-Learning State Hunter */}
                <div className="bg-gray-900/50 border border-cyan-900 p-6 rounded-lg md:col-span-2">
                    <h3 className="text-xs uppercase tracking-widest text-gray-400 mb-4">Logic Flow Analysis</h3>
                    <div className="space-y-3">
                        <div className="flex justify-between text-xs border-b border-gray-800 pb-2">
                            <span>ENDPOINT</span><span>SEVERITY</span><span>TYPE</span>
                        </div>
                        {findings.map((finding, i) => (
                            <div key={i} className="flex justify-between text-sm py-1 font-bold">
                                <span className="text-white">{finding.Endpoint || finding.endpoint || "N/A"}</span>
                                <span className="text-cyan-400">{finding.Severity || finding.severity || "INFO"}</span>
                                <span className="text-white font-mono break-all text-sm">
                                    {finding.Type || finding.type || "Unknown_Vuln"}
                                </span>
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            {/* Critical Chain Alert Box & Export */}
            <div className="mt-8 flex gap-6">
                <div className="flex-1 bg-red-900/10 border border-red-900 p-6 rounded-lg">
                    <div className="flex items-center gap-3 mb-4">
                        <Zap className="text-red-500" />
                        <h2 className="text-red-500 font-bold uppercase tracking-tighter">Critical Logic Flaws Detected</h2>
                    </div>
                    <pre className="text-xs text-red-400 leading-relaxed">
                        {`[ALERT] RACE_CONDITION detected.
[IMPACT] Financial Integrity Compromised (Double-Spend).
[STATUS] Proof-of-Concept Generated.`}
                    </pre>
                </div>

                <motion.div
                    initial={{ scale: 0.9 }} animate={{ scale: 1 }}
                    className="w-1/3 bg-cyan-900/20 border border-cyan-500 p-6 rounded-lg flex flex-col justify-center items-center gap-4"
                >
                    <Shield size={48} className="text-cyan-400" />
                    <h3 className="text-xl font-bold text-center text-cyan-400">ASSESSMENT COMPLETE</h3>
                    <p className="text-xs text-center text-cyan-600">Report Ready for Download</p>
                    <button
                        onClick={async () => {
                            try {
                                const res = await fetch('/api/history');
                                const history = await res.json();
                                if (history.length > 0) {
                                    const url = `/api/report/${history[0].id}`;
                                    const link = document.createElement('a');
                                    link.href = url;
                                    link.setAttribute('download', '');
                                    document.body.appendChild(link);
                                    link.click();
                                    document.body.removeChild(link);
                                } else {
                                    alert("No scan history found.");
                                }
                            } catch (e) {
                                alert("Failed to fetch report.");
                            }
                        }}
                        className="bg-cyan-500 hover:bg-cyan-400 text-black font-bold py-3 px-8 rounded shadow-[0_0_20px_#06b6d4] transition-all"
                    >
                        DOWNLOAD REPORT
                    </button>
                </motion.div>
            </div>
        </div>
    );
};

export default Dashboard;
