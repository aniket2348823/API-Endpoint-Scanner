import React, { useRef, useEffect, useState } from 'react';
import { Terminal, Cpu, Wifi, Activity } from 'lucide-react';
import { io } from 'socket.io-client';
import Ledger from './Ledger';

const Dashboard = ({ status, logs, history, transactions, onReplay }) => {
    // Local state for the Ledger since it's the main view now
    const [transactions, setTransactions] = useState([]);
    const socketRef = useRef(null);

    // Initial setup for socket listeners specific to Dashboard (if any)
    // Note: Parent App.jsx handles the main socket connection, but we might want to listen here too or pass socket down.
    // Ideally, App.jsx manages the socket and passes data down. 
    // BUT, App.jsx was passing `logs`. We need `transactions`.
    // Let's assume App.jsx will be updated to pass `transactions` or we listen here.
    // For simplicity, let's listen here using the SAME socket logic or expect App.jsx to pass it.
    // Actually, App.jsx was initializing the socket. Let's rely on App.jsx passing props or context.
    // The previous App.jsx passed `logs`. We need to update App.jsx too.

    // HOWEVER, I am editing Dashboard.jsx. I can just make it purely presentational 
    // and updated App.jsx to handle the 'ledger_update' event.

    return (
        <div className="space-y-6">

            {/* HEADER METRICS */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="bg-gray-900/40 border border-cyan-500/30 p-4 rounded-lg flex items-center justify-between">
                    <div>
                        <div className="text-xs text-cyan-500/60 uppercase">System Status</div>
                        <div className="text-xl font-bold text-cyan-400">ONLINE</div>
                    </div>
                    <Wifi className="text-cyan-500 animate-pulse" />
                </div>
                <div className="bg-gray-900/40 border border-purple-500/30 p-4 rounded-lg flex items-center justify-between">
                    <div>
                        <div className="text-xs text-purple-500/60 uppercase">Captured Packets</div>
                        <div className="text-xl font-bold text-white">{logs.length}</div>
                    </div>
                    <Cpu className="text-purple-500" />
                </div>
                <div className="bg-gray-900/40 border border-red-500/30 p-4 rounded-lg flex items-center justify-between">
                    <div>
                        <div className="text-xs text-red-500/60 uppercase">Race Candidates</div>
                        <div className="text-xl font-bold text-white">
                            {transactions ? transactions.filter(t => t.status.includes('CANDIDATE')).length : 0}
                        </div>
                    </div>
                    <Activity className="text-red-500" />
                </div>
            </div>

            {/* LEDGER COMPONENT (The Auditor) */}
            <div className="min-h-[500px]">
                {/* We need to pass transactions and onReplay. 
                    Since App.jsx isn't updated to pass these yet, this might break if we rely on props.
                    I will update App.jsx NEXT. 
                */}
                <Ledger
                    transactions={transactions}
                    onReplay={onReplay}
                />
            </div>

            {/* INSTRUCTIONS */}
            <div className="bg-black/30 border border-gray-800 p-4 rounded text-xs text-gray-500 font-mono">
                <p className="mb-2 font-bold text-gray-400">INFILTRATION INSTRUCTIONS:</p>
                <ol className="list-decimal pl-4 space-y-1">
                    <li>Ensure "Antigravity Leech" Extension is Active.</li>
                    <li>Navigate to Target Application (Authenticated Session).</li>
                    <li>Perform high-value actions (Transfer, Update Profile).</li>
                    <li>Observe "The Auditor" Ledger above for intercepted traffic.</li>
                    <li>If "RACE_CONDITION_DETECTED", click "LIVE REPLAY" to execute "The Hammer".</li>
                </ol>
            </div>

        </div>
    );
};

export default Dashboard;
