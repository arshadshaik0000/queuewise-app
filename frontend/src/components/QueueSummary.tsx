/**
 * QueueSummary — Animated dashboard widget with stat counters.
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
            <div className="summary-stats">
                <div className="summary-stat">
                    <div className="summary-stat-value accent">{summary.waiting_count}</div>
                    <div className="summary-stat-label">Waiting</div>
                </div>
                <div className="summary-stat">
                    <div className="summary-stat-value success">{summary.served_count}</div>
                    <div className="summary-stat-label">Served</div>
                </div>
                <div className="summary-stat">
                    <div className="summary-stat-value warning">{summary.skipped_count}</div>
                    <div className="summary-stat-label">Skipped</div>
                </div>
            </div>
            {summary.estimated_wait && (
                <p style={{ fontSize: "0.82rem", color: "var(--text-secondary)", margin: 0, textAlign: "center" }}>
                    ⏱ {summary.estimated_wait}
                </p>
            )}
        </div>
    );
}
