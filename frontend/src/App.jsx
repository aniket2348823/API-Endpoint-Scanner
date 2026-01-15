import { useState, useEffect, useRef } from 'react'
import { io } from 'socket.io-client'
import Dashboard from './components/Dashboard'
import './App.css'

function App() {
    const [transactions, setTransactions] = useState([])

    // Real-Time Socket Connection
    useEffect(() => {
        const socket = io('http://localhost:5000');

        socket.on('connect', () => {
            setLogs(prev => [...prev, `[SYSTEM] Uplink Established (SocketIO Active)`])
        });

        socket.on('status', (data) => {
            if (data.msg) setStatusMessage(data.msg);
        });

        socket.on('traffic_log', (data) => {
            const timestamp = new Date().toLocaleTimeString();
            // Optional: Filter out noisy static assets
            const msg = `[MIRROR] ${data.method} ${data.url}`;
            setLogs(prev => {
                const newLogs = [...prev, `[${timestamp}] ${msg}`];
                return newLogs.slice(-50);
            });
            setStatusMessage(`Analyzing: ${data.url}`);
        });

        // Listen for Retroactive Analysis Verdicts
        socket.on('ledger_update', (tx) => {
            setTransactions(prev => [...prev, tx]);
            // Also log it
            setLogs(prev => [...prev, `[AUDITOR] New Transaction Logged: ${tx.id} (${tx.status})`]);
        });

        // Polling fallback
        const interval = setInterval(fetchStatus, 2000);

        return () => {
            socket.disconnect();
            clearInterval(interval);
        }
    }, []);

    const triggerReplay = (id) => {
        // Emit replay event
        const socket = io('http://localhost:5000'); // Re-using connection or keeping a ref would be better
        // ideally store socket in ref, but for now:
        socket.emit('replay_race', { id });
        setStatusMessage(`EXECUTING HAMMER PROTOCOL ON ${id}...`);
    }

    // ... (keep fetchStatus)

    return (
        <div className="bg-black min-h-screen text-cyan-500 font-mono selection:bg-cyan-900 selection:text-white">
            {/* Background Grid Effect */}
            <div className="fixed inset-0 z-0 pointer-events-none opacity-10"
                style={{
                    backgroundImage: 'linear-gradient(#06b6d4 1px, transparent 1px), linear-gradient(90deg, #06b6d4 1px, transparent 1px)',
                    backgroundSize: '40px 40px'
                }}>
            </div>

            <div className="relative z-10 p-6 max-w-7xl mx-auto space-y-6">
                {/* Header */}
                <header className="flex justify-between items-end border-b border-cyan-900/50 pb-4">
                    <div>
                        <h1 className="text-4xl font-black tracking-tighter text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-600">
                            ANTIGRAVITY
                        </h1>
                        <p className="text-xs text-cyan-400/60 mt-1 uppercase tracking-[0.2em]">
                            Logic Assessment Engine v2.0 // SINGULARITY
                        </p>
                    </div>
                    <div className="text-right">
                        <div className="text-xs text-cyan-500/50 uppercase">System Status</div>
                        <div className="text-sm font-bold animate-pulse text-green-400">
                            {isScanning ? 'ACTIVE SCANNING' : 'OPERATIONAL'}
                        </div>
                    </div>
                </header>

                {/* Control Deck */}
                <Dashboard
                    status={statusMessage}
                    logs={logs}
                    history={history}
                    transactions={transactions}
                    onReplay={triggerReplay}
                />


                <div className="card full-width mt-6 p-4 border border-cyan-900 bg-black/50 backdrop-blur-md">
                    <h2 className="text-xl font-bold mb-4">Assessment History</h2>
                    <table className="w-full text-left">
                        <thead>
                            <tr className="border-b border-cyan-800 text-cyan-300">
                                <th className="p-2">ID</th>
                                <th>Time</th>
                                <th>Status</th>
                                <th className="text-right">Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {history.map(scan => (
                                <tr key={scan.id} className="border-b border-cyan-900/30 hover:bg-cyan-900/20">
                                    <td className="p-2 text-cyan-600">#{scan.id}</td>
                                    <td>{new Date(scan.timestamp).toLocaleString()}</td>
                                    <td className={scan.status === 'Completed' ? 'text-green-500' : 'text-yellow-500'}>{scan.status}</td>
                                    <td className="text-right">
                                        {scan.status === 'Completed' && (
                                            <button onClick={() => downloadReport(scan.id)} className="text-xs bg-cyan-900 hover:bg-cyan-700 text-white px-2 py-1 rounded">Download Report</button>
                                        )}
                                    </td>
                                </tr>
                            ))}
                            {history.length === 0 && <tr><td colSpan="4" className="p-4 text-center text-gray-500">No scans found.</td></tr>}
                        </tbody>
                    </table>
                </div>

            </div>
        </div>
    )
}

export default App
