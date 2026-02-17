/**
 * ActionPanel — System control panel for backend actions.
 *
 * Exposes: [Serve Next] [Skip Next] [Dry Run Toggle] [Pause/Resume]
 *
 * WHY this component exists:
 *   The frontend needs a clear, single place to trigger backend
 *   operations. This keeps controls separate from display.
 *   No business logic here — just calls the API client.
 */

interface Props {
    /** Whether any users are waiting (disables serve/skip when false) */
    hasWaiting: boolean;
    /** Whether dry-run mode is active */
    dryRun: boolean;
    /** Toggle dry-run mode on/off */
    onToggleDryRun: () => void;
    /** Trigger serve-next action */
    onServe: () => void;
    /** Trigger skip-next action */
    onSkip: () => void;
    /** Whether the queue is currently paused */
    isPaused: boolean;
    /** Toggle pause/resume */
    onTogglePause: () => void;
    /** True while an action is in progress */
    disabled?: boolean;
}

export default function ActionPanel({
    hasWaiting,
    dryRun,
    onToggleDryRun,
    onServe,
    onSkip,
    isPaused,
    onTogglePause,
    disabled = false,
}: Props) {
    return (
        <div className="card">
            <div className="card-title">⚙ Actions</div>

            {/* Paused indicator */}
            {isPaused && (
                <div style={{ fontSize: "0.78rem", color: "#f0a030", fontWeight: 700, marginBottom: "0.5rem" }}>
                    ⏸ Queue Paused — joins blocked, serve/skip allowed
                </div>
            )}

            {/* Dry-run toggle */}
            <label style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "0.75rem", cursor: "pointer" }}>
                <input type="checkbox" checked={dryRun} onChange={onToggleDryRun} />
                <span style={{ fontSize: "0.85rem", color: dryRun ? "#f0a030" : "#8888a8" }}>
                    {dryRun ? "🔸 Dry Run ON — actions are simulated" : "Dry Run OFF"}
                </span>
            </label>

            {/* Action buttons */}
            <div style={{ display: "flex", gap: "0.5rem" }}>
                <button
                    className="btn btn-serve"
                    style={{ flex: 1 }}
                    onClick={onServe}
                    disabled={!hasWaiting || disabled}
                >
                    {dryRun ? "⚡ Preview Serve" : "⚡ Serve Next"}
                </button>
                <button
                    className="btn btn-skip"
                    style={{ flex: 1, padding: "0.65rem 0.8rem", fontSize: "0.9rem" }}
                    onClick={onSkip}
                    disabled={!hasWaiting || disabled}
                >
                    {dryRun ? "⏭ Preview Skip" : "⏭ Skip Next"}
                </button>
                <button
                    className="btn btn-primary"
                    style={{ minWidth: "6rem", fontSize: "0.85rem" }}
                    onClick={onTogglePause}
                    disabled={disabled}
                >
                    {isPaused ? "▶ Resume" : "⏸ Pause"}
                </button>
            </div>
        </div>
    );
}
