/**
 * EventTimeline — Animated event log with hover-reveal trace IDs.
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

const ACTION_ICONS: Record<string, string> = {
    JOIN: "➕",
    SERVE: "⚡",
    SKIP: "⏭",
    PAUSED: "⏸",
    RESUMED: "▶",
    JOIN_ATTEMPT: "🚫",
};

export default function EventTimeline({ events }: Props) {
    if (events.length === 0) return null;

    return (
        <div className="card">
            <div className="card-title">📜 Event Timeline</div>
            <div className="event-timeline">
                {events.map((evt, i) => (
                    <div
                        key={evt.id}
                        className="event-item"
                        style={{ animationDelay: `${i * 0.03}s` }}
                    >
                        <span className="event-item-text">
                            {ACTION_ICONS[evt.action] || "•"}{" "}
                            <span className="event-item-action">{evt.action}</span>{" "}
                            <span className={`event-item-result ${evt.result === "BLOCKED" ? "blocked" : "ok"}`}>
                                {evt.result}
                            </span>
                        </span>
                        <span className="event-item-trace">
                            {evt.request_id?.slice(0, 8)}
                        </span>
                    </div>
                ))}
            </div>
        </div>
    );
}
