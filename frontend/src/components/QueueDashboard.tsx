import type { QueueSummary } from "../types";

interface Props {
    queues: QueueSummary[];
    activeQueueId: number | null;
    onSelect: (id: number, name: string) => void;
    onCreateNew: () => void;
}

export default function QueueDashboard({ queues, activeQueueId, onSelect, onCreateNew }: Props) {
    return (
        <div className="card">
            <div className="card-title">📋 All Queues</div>
            {queues.length === 0 ? (
                <div className="empty-state">No queues yet — create your first one!</div>
            ) : (
                <ul className="queue-list">
                    {queues.map((q) => (
                        <li
                            key={q.id}
                            className={`queue-item queue-item-clickable ${q.id === activeQueueId ? "queue-item-active" : ""}`}
                            onClick={() => onSelect(q.id, q.name)}
                        >
                            <div className="queue-item-left">
                                <span className="position-badge">{q.id}</span>
                                <div>
                                    <span className="queue-item-name">{q.name}</span>
                                    <span className="queue-item-meta">
                                        {q.waiting_count} waiting · {q.total_count} total
                                    </span>
                                </div>
                            </div>
                            <span className="status-tag waiting">{q.waiting_count}</span>
                        </li>
                    ))}
                </ul>
            )}
            <button className="btn btn-primary btn-create-new" onClick={onCreateNew}>
                + New Queue
            </button>
        </div>
    );
}
