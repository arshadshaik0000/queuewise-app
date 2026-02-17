import type { QueueEntry } from "../types";

interface Props {
    waiting: QueueEntry[];
    served: QueueEntry[];
    skipped: QueueEntry[];
    waitExplanations: Record<string, string>;
    onSkip: (entryId: number) => void;
}

export default function QueueBoard({ waiting, served, skipped, waitExplanations, onSkip }: Props) {
    return (
        <>
            {/* Waiting List */}
            <div className="card">
                <div className="card-title">🕐 Waiting ({waiting.length})</div>
                {waiting.length === 0 ? (
                    <div className="empty-state">No one is waiting — queue is clear!</div>
                ) : (
                    <ul className="queue-list">
                        {waiting.map((entry) => (
                            <li key={entry.id} className="queue-item">
                                <div className="queue-item-left">
                                    <span className="position-badge">{entry.position}</span>
                                    <div>
                                        <span className="queue-item-name">{entry.user_name}</span>
                                        {waitExplanations[entry.user_name] && (
                                            <span className="queue-item-wait">
                                                {waitExplanations[entry.user_name]}
                                            </span>
                                        )}
                                    </div>
                                </div>
                                <div className="queue-item-actions">
                                    <button
                                        className="btn btn-skip"
                                        onClick={() => onSkip(entry.id)}
                                        title={`Skip ${entry.user_name}`}
                                    >
                                        Skip
                                    </button>
                                    <span className="status-tag waiting">Waiting</span>
                                </div>
                            </li>
                        ))}
                    </ul>
                )}
            </div>

            {/* Served List */}
            {served.length > 0 && (
                <div className="card">
                    <div className="card-title">✅ Served ({served.length})</div>
                    <ul className="queue-list">
                        {served.map((entry) => (
                            <li key={entry.id} className="queue-item">
                                <div className="queue-item-left">
                                    <span className="position-badge">{entry.position}</span>
                                    <span className="queue-item-name">{entry.user_name}</span>
                                </div>
                                <span className="status-tag served">Served</span>
                            </li>
                        ))}
                    </ul>
                </div>
            )}

            {/* Skipped List */}
            {skipped.length > 0 && (
                <div className="card">
                    <div className="card-title">⏭️ Skipped ({skipped.length})</div>
                    <ul className="queue-list">
                        {skipped.map((entry) => (
                            <li key={entry.id} className="queue-item">
                                <div className="queue-item-left">
                                    <span className="position-badge">{entry.position}</span>
                                    <span className="queue-item-name">{entry.user_name}</span>
                                </div>
                                <span className="status-tag skipped">Skipped</span>
                            </li>
                        ))}
                    </ul>
                </div>
            )}
        </>
    );
}
