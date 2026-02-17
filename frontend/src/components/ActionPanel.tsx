/**
 * ActionPanel — Dynamic control panel with animated toggles and gradient buttons.
 */

interface Props {
    hasWaiting: boolean;
    dryRun: boolean;
    onToggleDryRun: () => void;
    onServe: () => void;
    onSkip: () => void;
    isPaused: boolean;
    onTogglePause: () => void;
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
                <div className="paused-indicator">
                    ⏸ Queue Paused — joins blocked, serve/skip still allowed
                </div>
            )}

            {/* Dry-run toggle */}
            <label className="dry-run-toggle">
                <input type="checkbox" checked={dryRun} onChange={onToggleDryRun} />
                <span className={`dry-run-label ${dryRun ? "active" : "inactive"}`}>
                    {dryRun ? "🔸 Dry Run ON — actions are simulated" : "Dry Run OFF"}
                </span>
            </label>

            {/* Action buttons */}
            <div className="action-buttons">
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
                    style={{ flex: 1, padding: "0.7rem 0.85rem", fontSize: "0.9rem" }}
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
