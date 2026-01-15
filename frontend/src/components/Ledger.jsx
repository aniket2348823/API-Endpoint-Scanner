import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Activity, Shield, Zap, RefreshCw, AlertTriangle, CheckCircle } from 'lucide-react';

const Ledger = ({ transactions, onReplay }) => {
    return (
        <div className="bg-black/40 border border-cyan-500/20 rounded-lg backdrop-blur-md overflow-hidden font-mono text-sm">
            <div className="bg-cyan-900/20 p-3 border-b border-cyan-500/20 flex justify-between items-center">
                <h3 className="text-cyan-400 font-bold flex items-center gap-2">
                    <Activity size={16} /> FORENSIC_LEDGER
                </h3>
                <span className="text-xs text-cyan-500/60">LIVE_AUDIT_STREAM</span>
            </div>

            <table className="w-full text-left border-collapse">
                <thead>
                    <tr className="text-xs text-cyan-500/50 uppercase bg-black/50">
                        <th className="p-3">Time</th>
                        <th className="p-3">Request ID</th>
                        <th className="p-3">Method / Endpoint</th>
                        <th className="p-3">Analysis Verdict</th>
                        <th className="p-3 text-right">Counter-Measures</th>
                    </tr>
                </thead>
                <tbody className="divide-y divide-cyan-900/30">
                    <AnimatePresence>
                        {transactions.slice().reverse().map((tx) => (
                            <motion.tr
                                key={tx.id}
                                initial={{ opacity: 0, x: -20 }}
                                animate={{ opacity: 1, x: 0 }}
                                exit={{ opacity: 0 }}
                                className={`hover:bg-cyan-900/10 transition-colors ${tx.status.includes('CANDIDATE') ? 'bg-red-900/10' : ''}`}
                            >
                                <td className="p-3 text-cyan-600/70">{new Date(tx.timestamp).toLocaleTimeString()}</td>
                                <td className="p-3 text-cyan-700">{tx.id.substring(0, 8)}...</td>
                                <td className="p-3">
                                    <span className="text-purple-400 font-bold mr-2">{tx.method}</span>
                                    <span className="text-gray-400 text-xs">{tx.url}</span>
                                </td>
                                <td className="p-3">
                                    {tx.status === 'SAFE' && (
                                        <span className="flex items-center gap-1 text-green-500/70">
                                            <CheckCircle size={12} /> PROTOCOL_COMPLIANT
                                        </span>
                                    )}
                                    {tx.status === 'RACE_CANDIDATE' && (
                                        <div className="flex flex-col">
                                            <span className="flex items-center gap-1 text-red-500 font-bold">
                                                <AlertTriangle size={12} /> RACE_CONDITION_DETECTED
                                            </span>
                                            <span className="text-xs text-red-400/60">{tx.details}</span>
                                        </div>
                                    )}
                                    {tx.status === 'IDOR_CANDIDATE' && (
                                        <div className="flex flex-col">
                                            <span className="flex items-center gap-1 text-yellow-500 font-bold">
                                                <Shield size={12} /> IDOR_VULNERABILITY
                                            </span>
                                            <span className="text-xs text-yellow-400/60">{tx.details}</span>
                                        </div>
                                    )}
                                </td>
                                <td className="p-3 text-right">
                                    {tx.status.includes('CANDIDATE') && (
                                        <button
                                            onClick={() => onReplay(tx.id)}
                                            className="bg-red-600/20 hover:bg-red-600/40 border border-red-600/50 text-red-400 text-xs px-3 py-1 rounded flex items-center gap-1 ml-auto transition-all"
                                        >
                                            <Zap size={12} /> LIVE_REPLAY
                                        </button>
                                    )}
                                </td>
                            </motion.tr>
                        ))}
                    </AnimatePresence>
                    {transactions.length === 0 && (
                        <tr>
                            <td colSpan="5" className="p-8 text-center text-cyan-900 italic">
                                Awaiting Traffic Ingestion...
                            </td>
                        </tr>
                    )}
                </tbody>
            </table>
        </div>
    );
};

export default Ledger;
