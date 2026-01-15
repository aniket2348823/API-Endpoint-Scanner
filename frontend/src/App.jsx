import React, { useState, useEffect, useRef } from 'react'
import Dashboard from './components/Dashboard';
import { Shield, Search, AlertTriangle, FileText, Activity } from 'lucide-react';
import './App.css'

function App() {
    const [isScanning, setIsScanning] = useState(false)
    const [history, setHistory] = useState([])
    const [statusMessage, setStatusMessage] = useState('')
    const [targetUrl, setTargetUrl] = useState('')
    const [logs, setLogs] = useState([])
    const logsEndRef = useRef(null)

    // Use Prod URL if Env Var is missing (Fallback for easy deployment)
    const API_URL = '' // Use relative path to leverage Vite proxy

    const fetchStatus = async () => {
        try {
            const res = await fetch(`${API_URL}/api/status`)
            const data = await res.json()
            setIsScanning(data.is_scanning)
            if (data.logs) {
                setLogs(data.logs)
            }
        } catch (err) {
            console.error("Failed to fetch status", err)
        }
    }

    const fetchHistory = async () => {
        try {
            const res = await fetch(`${API_URL}/api/history`)
            const data = await res.json()
            setHistory(data)
        } catch (err) {
            console.error("Failed to fetch history", err)
        }
    }

    useEffect(() => {
        fetchStatus()
        fetchHistory()
        const interval = setInterval(() => {
            fetchStatus()
            fetchHistory() // Polling for updates
        }, 1000) // Faster polling for real-time feel
        return () => clearInterval(interval)
    }, [])

    useEffect(() => {
        logsEndRef.current?.scrollIntoView({ behavior: 'smooth' })
    }, [logs])

    const startScan = async () => {
        if (!targetUrl) {
            setStatusMessage("Please enter a Target URL.")
            return
        }
        try {
            setStatusMessage("Inducing Singularity...")
            setLogs([]) // Clear previous logs
            const res = await fetch(`${API_URL}/api/scan`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ target_url: targetUrl })
            })
            if (res.status === 409) {
                setStatusMessage("Singularity Induction in progress.")
            } else if (res.ok) {
                setStatusMessage("Singularity Induction started.")
                setIsScanning(true)
            } else {
                setStatusMessage("Error starting Singularity.")
            }
            fetchHistory()
        } catch (err) {
            setStatusMessage("Network error.")
        }
    }

    const downloadReport = (scanId) => {
        const url = `${API_URL}/api/report/${scanId}`;
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', '');
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }

    return (
        <div className="container">
            <h1>Antigravity Logic Assessment Engine</h1>

            {/* V100 Sovereign Midnight Cyber Dashboard */}
            <Dashboard />

            <div className="grid">
                <div className="card control-panel" style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                    <h2>Assessment Control</h2>
                    <div className="input-group">
                        <input
                            type="text"
                            placeholder="Enter Target URL (e.g., http://localhost:5001)"
                            value={targetUrl}
                            onChange={(e) => setTargetUrl(e.target.value)}
                            disabled={isScanning}
                        />
                    </div>

                    <div className="actions">
                        <button onClick={startScan} disabled={isScanning} className="start-btn">
                            {isScanning ? 'ASSESSMENT IN PROGRESS...' : 'START LOGIC SCAN'}
                        </button>
                    </div>
                    {statusMessage && <p className="message">{statusMessage}</p>}
                </div>

                <div className="card console-card">
                    <h2>Live Logic Stream</h2>
                    <div className="console-window">
                        {logs.length === 0 && <span className="console-placeholder">Waiting for target...</span>}
                        {logs.map((log, index) => (
                            <div key={index} className="log-entry">{log}</div>
                        ))}
                        <div ref={logsEndRef} />
                    </div>
                </div>
            </div>

            <div className="card full-width">
                <h2>Assessment History</h2>
                <table>
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Time</th>
                            <th>Status</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {history.map(scan => (
                            <tr key={scan.id}>
                                <td>{scan.id}</td>
                                <td>{new Date(scan.timestamp).toLocaleString()}</td>
                                <td className={scan.status.toLowerCase()}>{scan.status}</td>
                                <td className="text-right">
                                    {scan.status === 'Completed' && (
                                        <button onClick={() => downloadReport(scan.id)}>Download Report</button>
                                    )}
                                </td>
                            </tr>
                        ))}
                        {history.length === 0 && <tr><td colSpan="4">No scans found.</td></tr>}
                    </tbody>
                </table>
            </div>
        </div >
    )
}

export default App
