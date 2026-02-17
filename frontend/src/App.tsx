import { useState, useCallback, useEffect } from "react";
import * as api from "./api";
import type { QueueStatus, QueueSummary, ActionResult, SummaryResponse, EventItem } from "./types";
import QueueBoard from "./components/QueueBoard";
import QueueDashboard from "./components/QueueDashboard";
import JoinForm from "./components/JoinForm";
import ExplanationPanel from "./components/ExplanationPanel";
import ActionPanel from "./components/ActionPanel";
import QueueSummaryWidget from "./components/QueueSummary";
import PreviewPanel from "./components/PreviewPanel";
import EventTimeline from "./components/EventTimeline";

// localStorage helpers for persistent queue selection
const STORAGE_KEY = "queuewise_active_queue";

function loadSavedQueue(): { id: number; name: string } | null {
    try {
        const raw = localStorage.getItem(STORAGE_KEY);
        if (raw) return JSON.parse(raw);
    } catch { /* ignore parse errors */ }
    return null;
}

function saveQueue(id: number, name: string) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify({ id, name }));
}

function clearSavedQueue() {
    localStorage.removeItem(STORAGE_KEY);
}

export default function App() {
    const saved = loadSavedQueue();

    const [queueId, setQueueId] = useState<number | null>(saved?.id ?? null);
    const [queueName, setQueueName] = useState(saved?.name ?? "");
    const [status, setStatus] = useState<QueueStatus | null>(null);
    const [queues, setQueues] = useState<QueueSummary[]>([]);
    const [newQueueName, setNewQueueName] = useState("");
    const [showDashboard, setShowDashboard] = useState(queueId === null);
    const [toast, setToast] = useState<{ message: string; type: "error" | "success" } | null>(null);
    const [loading, setLoading] = useState(false);

    // System control panel state
    const [dryRun, setDryRun] = useState(false);
    const [actionResult, setActionResult] = useState<ActionResult | null>(null);
    const [lastRequestId, setLastRequestId] = useState("");
    const [apiVersion, setApiVersion] = useState("");
    const [summary, setSummary] = useState<SummaryResponse | null>(null);
    const [events, setEvents] = useState<EventItem[]>([]);
    const [isPaused, setIsPaused] = useState(false);

    const showToast = useCallback((message: string, type: "error" | "success" = "error") => {
        setToast({ message, type });
        setTimeout(() => setToast(null), 3500);
    }, []);

    // Refresh queue status from the backend
    const refreshStatus = useCallback(async (id: number) => {
        try {
            const { data, apiVersion: ver } = await api.getQueueStatus(id);
            setStatus(data);
            setApiVersion(ver);
            // Track pause state from backend response
            setIsPaused(data.queue_status === "PAUSED");
        } catch (err: any) {
            showToast(err.message);
        }
    }, [showToast]);

    // Refresh summary widget
    const refreshSummary = useCallback(async (id: number) => {
        try {
            const data = await api.getSummary(id);
            setSummary(data);
        } catch { /* non-critical */ }
    }, []);

    // Refresh event timeline
    const refreshEvents = useCallback(async (id: number) => {
        try {
            const data = await api.getEvents(id, 20);
            setEvents(data);
        } catch { /* non-critical */ }
    }, []);

    // Fetch all queues for the dashboard
    const refreshQueues = useCallback(async () => {
        try {
            const data = await api.listQueues();
            setQueues(data);
        } catch (err: any) {
            showToast(err.message);
        }
    }, [showToast]);

    // Poll every 3 seconds when a queue is active
    useEffect(() => {
        if (queueId === null) return;
        refreshStatus(queueId);
        refreshSummary(queueId);
        refreshEvents(queueId);
        const interval = setInterval(() => {
            refreshStatus(queueId);
            refreshSummary(queueId);
            refreshEvents(queueId);
        }, 3000);
        return () => clearInterval(interval);
    }, [queueId, refreshStatus, refreshSummary, refreshEvents]);

    // Load queues when dashboard is shown
    useEffect(() => {
        if (showDashboard) refreshQueues();
    }, [showDashboard, refreshQueues]);

    // Select an existing queue
    const selectQueue = (id: number, name: string) => {
        setQueueId(id);
        setQueueName(name);
        setShowDashboard(false);
        setActionResult(null);
        setEvents([]);
        saveQueue(id, name);
    };

    // Create a new queue
    const handleCreateQueue = async () => {
        if (!newQueueName.trim()) return;
        setLoading(true);
        try {
            const res = await api.createQueue(newQueueName.trim());
            selectQueue(res.id, res.name);
            setNewQueueName("");
            showToast(`Queue "${res.name}" created!`, "success");
        } catch (err: any) {
            showToast(err.message);
        } finally {
            setLoading(false);
        }
    };

    // Join the active queue
    const handleJoin = async (userName: string) => {
        if (queueId === null) return;
        try {
            const { data, requestId } = await api.joinQueue(queueId, userName, { dryRun });
            setLastRequestId(requestId);

            if ("dry_run" in data && data.dry_run) {
                setActionResult({
                    type: data.result === "would_succeed" ? "dry_run" : "blocked",
                    message: data.result === "would_succeed"
                        ? `Join would succeed for "${userName}"`
                        : `Join would fail for "${userName}"`,
                    reason: data.reason,
                    ruleCode: data.rule_code,
                    requestId,
                });
            } else {
                await refreshStatus(queueId);
                showToast(`${userName} joined the queue!`, "success");
                setActionResult(null);
            }
        } catch (err: any) {
            showToast(err.message);
            setActionResult({
                type: "blocked",
                message: err.message,
                ruleCode: err.ruleCode,
                requestId: lastRequestId,
            });
        }
    };

    // Serve next via ActionPanel
    const handleServe = async () => {
        if (queueId === null) return;
        setLoading(true);
        try {
            const { data, requestId } = await api.serveNext(queueId, { dryRun });
            setLastRequestId(requestId);

            if ("dry_run" in data && data.dry_run) {
                setActionResult({
                    type: data.result === "would_succeed" ? "dry_run" : "blocked",
                    message: data.result === "would_succeed"
                        ? `Serve would succeed: "${data.user_name}"`
                        : "Serve would fail",
                    reason: data.reason,
                    ruleCode: data.rule_code,
                    requestId,
                });
            } else {
                await refreshStatus(queueId);
                await refreshSummary(queueId);
                showToast(`${data.user_name} has been served!`, "success");
                setActionResult({
                    type: "success",
                    message: `Served: ${data.user_name}`,
                    requestId,
                });
            }
        } catch (err: any) {
            showToast(err.message);
            setActionResult({
                type: "blocked",
                message: err.message,
                ruleCode: err.ruleCode,
                requestId: lastRequestId,
            });
        } finally {
            setLoading(false);
        }
    };

    // Skip next via ActionPanel
    const handleSkipNext = async () => {
        if (queueId === null) return;
        setLoading(true);
        try {
            const { data, requestId } = await api.skipNext(queueId, { dryRun });
            setLastRequestId(requestId);

            if ("dry_run" in data && data.dry_run) {
                setActionResult({
                    type: data.result === "would_succeed" ? "dry_run" : "blocked",
                    message: data.result === "would_succeed"
                        ? `Skip would succeed: "${data.user_name}"`
                        : "Skip would fail",
                    reason: data.reason,
                    ruleCode: data.rule_code,
                    requestId,
                });
            } else {
                await refreshStatus(queueId);
                await refreshSummary(queueId);
                showToast(`${data.user_name} has been skipped.`, "success");
                setActionResult({
                    type: "success",
                    message: `Skipped: ${data.user_name}`,
                    requestId,
                });
            }
        } catch (err: any) {
            showToast(err.message);
            setActionResult({
                type: "blocked",
                message: err.message,
                ruleCode: err.ruleCode,
                requestId: lastRequestId,
            });
        } finally {
            setLoading(false);
        }
    };

    // Skip a specific user (from QueueBoard inline button)
    const handleSkipUser = async (entryId: number) => {
        if (queueId === null) return;
        try {
            const res = await api.skipUser(queueId, entryId);
            await refreshStatus(queueId);
            showToast(`${res.user_name} has been skipped.`, "success");
        } catch (err: any) {
            showToast(err.message);
        }
    };

    // Pause / Resume toggle
    const handleTogglePause = async () => {
        if (queueId === null) return;
        setLoading(true);
        try {
            if (isPaused) {
                const { requestId } = await api.resumeQueue(queueId);
                setLastRequestId(requestId);
                setIsPaused(false);
                showToast("Queue resumed — accepting joins", "success");
            } else {
                const { requestId } = await api.pauseQueue(queueId);
                setLastRequestId(requestId);
                setIsPaused(true);
                showToast("Queue paused — joins blocked", "success");
            }
        } catch (err: any) {
            showToast(err.message);
        } finally {
            setLoading(false);
        }
    };

    // Preview handler for PreviewPanel
    const handlePreview = async () => {
        if (queueId === null) return null;
        return api.getPreview(queueId);
    };

    // Go back to dashboard
    const goToDashboard = () => {
        setShowDashboard(true);
        setQueueId(null);
        setStatus(null);
        setSummary(null);
        setActionResult(null);
        setEvents([]);
        clearSavedQueue();
    };

    const waitingEntries = status?.entries.filter((e) => e.status === "WAITING") ?? [];
    const servedEntries = status?.entries.filter((e) => e.status === "SERVED") ?? [];
    const skippedEntries = status?.entries.filter((e) => e.status === "SKIPPED") ?? [];

    return (
        <div className="app">
            {/* Header */}
            <header className="app-header">
                <h1>QueueWise</h1>
                <p>Smart queue management for clinics, salons &amp; service centers</p>
            </header>

            {showDashboard ? (
                <>
                    {/* Create Queue */}
                    <div className="setup-section">
                        <input
                            type="text"
                            placeholder="New queue name (e.g. Clinic A)"
                            value={newQueueName}
                            onChange={(e) => setNewQueueName(e.target.value)}
                            onKeyDown={(e) => e.key === "Enter" && handleCreateQueue()}
                        />
                        <button className="btn btn-primary" onClick={handleCreateQueue} disabled={loading}>
                            Create
                        </button>
                    </div>

                    {/* Queue List */}
                    <QueueDashboard
                        queues={queues}
                        activeQueueId={null}
                        onSelect={selectQueue}
                        onCreateNew={() => document.querySelector<HTMLInputElement>("input")?.focus()}
                    />
                </>
            ) : (
                <>
                    {/* Active Queue Header */}
                    <div className="queue-header">
                        <div className="queue-header-left">
                            <button className="btn btn-back" onClick={goToDashboard} title="Back to all queues">
                                ←
                            </button>
                            <span className="queue-name">{queueName}</span>
                            {isPaused && (
                                <span style={{ fontSize: "0.7rem", color: "#f0a030", marginLeft: "0.5rem" }}>
                                    ⏸ PAUSED
                                </span>
                            )}
                        </div>
                        <span className="queue-id-tag">ID #{queueId}</span>
                    </div>

                    {/* Queue Summary Widget */}
                    <div className="section-gap">
                        <QueueSummaryWidget summary={summary} />
                    </div>

                    {/* AI Explanation + Action Results */}
                    {status && (
                        <ExplanationPanel
                            explanation={status.explanation}
                            actionResult={actionResult}
                        />
                    )}

                    {/* Join Form */}
                    <div className="section-gap">
                        <JoinForm onJoin={handleJoin} />
                    </div>

                    {/* Action Panel — Serve / Skip / Dry Run / Pause */}
                    <div className="section-gap">
                        <ActionPanel
                            hasWaiting={waitingEntries.length > 0}
                            dryRun={dryRun}
                            onToggleDryRun={() => setDryRun((v) => !v)}
                            onServe={handleServe}
                            onSkip={handleSkipNext}
                            isPaused={isPaused}
                            onTogglePause={handleTogglePause}
                            disabled={loading}
                        />
                    </div>

                    {/* Preview Panel */}
                    <div className="section-gap">
                        <PreviewPanel onPreview={handlePreview} />
                    </div>

                    {/* Queue Board */}
                    <QueueBoard
                        waiting={waitingEntries}
                        served={servedEntries}
                        skipped={skippedEntries}
                        waitExplanations={status?.wait_explanations ?? {}}
                        onSkip={handleSkipUser}
                    />

                    {/* Event Timeline */}
                    <div className="section-gap">
                        <EventTimeline events={events} />
                    </div>

                    {/* Footer — Request ID + API Version */}
                    <div className="app-footer">
                        {lastRequestId && <span>Request ID: {lastRequestId}</span>}
                        {lastRequestId && apiVersion && <span> · </span>}
                        {apiVersion && <span>API {apiVersion}</span>}
                    </div>
                </>
            )}

            {/* Toast */}
            {toast && <div className={`toast ${toast.type}`}>{toast.message}</div>}
        </div>
    );
}
