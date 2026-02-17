/**
 * QueueSummary — Derived-data widget showing queue counts.
 *
 * Fetches GET /queues/{id}/summary and displays:
 *   - Waiting / Served / Skipped counts
 *   - AI-generated estimated wait text
 *
 * WHY this component exists:
 *   Provides a quick at-a-glance view of queue health without
 *   needing to scan the full entry list. Read-only — no actions.
 */

interface SummaryData {
    queue_id: number;
    queue_name: string;
    waiting_count: number;
    served_count: number;
    skipped_count: number;
    estimated_wait: string;
    explanation: string;
}

interface Props {
    summary: SummaryData | null;
}

export default function QueueSummary({ summary }: Props) {
    if (!summary) return null;

    return (
        <div className="card">
            <div className="card-title">📊 Queue Summary</div>
            <div style={{ display: "flex", gap: "1rem", marginBottom: "0.6rem" }}>
                <div style={{ flex: 1, textAlign: "center" }}>
                    <div style={{ fontSize: "1.4rem", fontWeight: 700, color: "#7c5cfc" }}>
                        {summary.waiting_count}
                    </div>
                    <div style={{ fontSize: "0.75rem", color: "#8888a8" }}>Waiting</div>
                </div>
                <div style={{ flex: 1, textAlign: "center" }}>
                    <div style={{ fontSize: "1.4rem", fontWeight: 700, color: "#2cc984" }}>
                        {summary.served_count}
                    </div>
                    <div style={{ fontSize: "0.75rem", color: "#8888a8" }}>Served</div>
                </div>
                <div style={{ flex: 1, textAlign: "center" }}>
                    <div style={{ fontSize: "1.4rem", fontWeight: 700, color: "#f0a030" }}>
                        {summary.skipped_count}
                    </div>
                    <div style={{ fontSize: "0.75rem", color: "#8888a8" }}>Skipped</div>
                </div>
            </div>
            {summary.estimated_wait && (
                <p style={{ fontSize: "0.82rem", color: "#8888a8", margin: 0 }}>
                    {summary.estimated_wait}
                </p>
            )}
        </div>
    );
}
