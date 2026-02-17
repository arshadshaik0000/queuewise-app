/**
 * EventTimeline — Read-only list of recent queue events.
 *
 * WHY this exists:
 *   Provides observability into what happened in the queue.
 *   Operators can trace actions (JOIN, SERVE, SKIP, PAUSED, etc.)
 *   without checking backend logs directly. Simple list — no animations.
 */

interface EventItem {
    id: number;
    action: string;
    result: string;
    detail: string;
    request_id: string;
    created_at: string;
}

interface Props {
    events: EventItem[];
}

// Map action types to simple icons for scanability
const ACTION_ICONS: Record<string, string> = {
    JOIN: "➕",
    SERVE: "⚡",
    SKIP: "⏭",
    PAUSED: "⏸",
    RESUMED: "▶",
};

export default function EventTimeline({ events }: Props) {
    if (events.length === 0) return null;

    return (
        <div className="card">
            <div className="card-title">📜 Event Timeline</div>
            <div style={{ maxHeight: "220px", overflowY: "auto" }}>
                {events.map((evt) => (
                    <div
                        key={evt.id}
                        style={{
                            display: "flex",
                            justifyContent: "space-between",
                            alignItems: "center",
                            padding: "0.35rem 0",
                            borderBottom: "1px solid rgba(255,255,255,0.05)",
                            fontSize: "0.8rem",
                        }}
                    >
                        <span>
                            {ACTION_ICONS[evt.action] || "•"}{" "}
                            <strong>{evt.action}</strong>{" "}
                            <span style={{ color: evt.result === "BLOCKED" ? "#f04e5e" : "#8888a8" }}>
                                {evt.result}
                            </span>
                        </span>
                        <span style={{ color: "#555578", fontSize: "0.7rem", fontFamily: "monospace" }}>
                            {evt.request_id?.slice(0, 8)}
                        </span>
                    </div>
                ))}
            </div>
        </div>
    );
}
