import React, { useState, useEffect } from 'react';
import { RefreshCw, Zap, ShieldAlert, ShoppingCart } from 'lucide-react';

const API_URL = "http://localhost:5001/api";

function App() {
    const [balance, setBalance] = useState(0);
    const [logs, setLogs] = useState([]);
    const [loading, setLoading] = useState(false);
    const [lastDiff, setLastDiff] = useState(0);

    // 1. POLLING MECHANISM (The "Tell")
    useEffect(() => {
        const interval = setInterval(fetchBalance, 1000);
        return () => clearInterval(interval);
    }, [balance]);

    const fetchBalance = async () => {
        try {
            const res = await fetch(`${API_URL}/balance`);
            const data = await res.json();

            // Check for sudden jumps (The Glitch Visual)
            if (data.balance !== balance && balance !== 0) {
                const diff = data.balance - balance;
                setLastDiff(diff);
                if (diff > 50) {
                    addLog(`⚠️ ANOMALY DETECTED: Balance jump of $${diff}`, 'danger');
                }
            }
            setBalance(data.balance);
        } catch (err) {
            console.error("API Down");
        }
    };

    const addLog = (msg, type = 'info') => {
        setLogs(prev => [{ id: Date.now(), msg, type }, ...prev].slice(0, 5));
    };

    const applyCoupon = async () => {
        setLoading(true);
        addLog("Sending Coupon Request...", 'info');

        try {
            const res = await fetch(`${API_URL}/apply`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ code: "WELCOME50" })
            });
            const data = await res.json();

            if (res.ok) {
                addLog(`Success: ${data.message}`, 'success');
                fetchBalance(); // Immediate refresh
            } else {
                addLog(`Error: ${data.error}`, 'danger');
            }
        } catch (err) {
            addLog("Network Error", 'danger');
        }
        setLoading(false);
    };

    const resetSystem = async () => {
        await fetch(`${API_URL}/reset`, { method: 'POST' });
        setBalance(100);
        setLogs([]);
        setLastDiff(0);
        addLog("System Reset Complete", 'info');
    };

    return (
        <div className="min-h-screen bg-background text-white font-sans p-8 selection:bg-primary selection:text-black">
            {/* HEADER */}
            <nav className="flex justify-between items-center mb-12 border-b border-white/10 pb-6">
                <div className="flex items-center gap-2">
                    <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
                    <h1 className="text-2xl font-bold tracking-tighter">NEXUS<span className="text-primary">MARKET</span></h1>
                </div>
                <div className="flex items-center gap-4 text-sm text-gray-400">
                    <span>Status: <span className="text-green-400">Operational</span></span>
                    <span>v2.4.0</span>
                </div>
            </nav>

            <main className="max-w-6xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-12">

                {/* LEFT COL: WALLET & ACTIONS */}
                <div className="space-y-8">
                    {/* WALLET CARD */}
                    <div className="bg-surface border border-white/5 rounded-2xl p-8 relative overflow-hidden group">
                        <div className="absolute top-0 right-0 p-32 bg-primary/5 blur-[100px] rounded-full group-hover:bg-primary/10 transition-all"></div>

                        <h2 className="text-gray-400 text-sm font-mono mb-2 flex items-center gap-2">
                            <Zap size={16} /> CURRENT BALANCE
                        </h2>
                        <div className="flex items-baseline gap-2">
                            <span className={`text-6xl font-bold tracking-tight transition-all duration-300 ${lastDiff > 50 ? 'text-green-400 animate-pulse' : 'text-white'}`}>
                                ${balance.toFixed(2)}
                            </span>
                            <span className="text-xl text-gray-500">USD</span>
                        </div>
                    </div>

                    {/* COUPON ACTION */}
                    <div className="bg-surface border border-white/5 rounded-2xl p-8">
                        <div className="flex justify-between items-center mb-6">
                            <h3 className="text-lg font-bold">Promotions</h3>
                            <span className="bg-primary/20 text-primary px-3 py-1 rounded-full text-xs font-mono">NEW USER</span>
                        </div>

                        <div className="flex gap-4">
                            <input
                                disabled
                                value="WELCOME50"
                                className="bg-black/50 border border-white/10 rounded-lg px-4 py-3 w-full font-mono text-gray-400 cursor-not-allowed"
                            />
                            <button
                                onClick={applyCoupon}
                                disabled={loading}
                                className="bg-primary hover:bg-cyan-400 text-black font-bold px-8 py-3 rounded-lg transition-all active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                            >
                                {loading ? <RefreshCw className="animate-spin" size={20} /> : "APPLY"}
                            </button>
                        </div>
                        <p className="text-xs text-gray-500 mt-4">*One-time use only. Terms apply.</p>
                    </div>
                </div>

                {/* RIGHT COL: TRANSACTION LOG (THE EVIDENCE) */}
                <div className="bg-black/30 border border-white/10 rounded-xl p-6 h-fit">
                    <div className="flex justify-between items-center mb-6 border-b border-white/5 pb-4">
                        <h3 className="font-mono text-sm text-gray-400">SYSTEM LOGS</h3>
                        <button onClick={resetSystem} className="text-xs text-red-400 hover:text-red-300 underline">RESET DEMO</button>
                    </div>

                    <div className="space-y-3 font-mono text-sm">
                        {logs.length === 0 && <span className="text-gray-600 italic">Waiting for transactions...</span>}
                        {logs.map((log) => (
                            <div key={log.id} className={`flex items-start gap-3 animate-in fade-in slide-in-from-right-4 duration-300
                ${log.type === 'danger' ? 'text-red-400' : log.type === 'success' ? 'text-green-400' : 'text-gray-300'}
              `}>
                                <span className="opacity-50">[{new Date(log.id).toLocaleTimeString().split(' ')[0]}]</span>
                                <span>{log.msg}</span>
                            </div>
                        ))}
                    </div>
                </div>

            </main>
        </div>
    );
}

export default App;
