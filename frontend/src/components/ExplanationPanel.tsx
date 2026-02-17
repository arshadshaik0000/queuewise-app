/**
 * ExplanationPanel — Displays AI explanation, action results, and rule feedback.
 *
 * WHY action results are shown here:
 *   This is the existing "system message" area. Adding action
 *   feedback here keeps a single source of system communication
 *   rather than scattering status messages across components.
 */

import type { ActionResult } from "../types";

interface Props {
    /** AI-generated queue explanation text */
    explanation: string;
    /** Most recent action result (serve, skip, dry-run, or blocked) */
    actionResult?: ActionResult | null;
}

export default function ExplanationPanel({ explanation, actionResult }: Props) {
    return (
        <div>
            {/* AI explanation */}
            <div className="explanation-panel">
                <span className="explanation-icon">🤖</span>
                <p className="explanation-text">{explanation}</p>
            </div>

            {/* Action result feedback */}
            {actionResult && (
                <div
                    className="card"
                    style={{
                        marginTop: "0.5rem",
                        borderLeft: `3px solid ${actionResult.type === "blocked" ? "#f04e5e"
                                : actionResult.type === "dry_run" ? "#f0a030"
                                    : "#2cc984"
                            }`,
                    }}
                >
                    {/* Dry-run indicator */}
                    {actionResult.type === "dry_run" && (
                        <div style={{ fontSize: "0.78rem", color: "#f0a030", fontWeight: 700, marginBottom: "0.3rem" }}>
                            🔸 Simulation Mode — No changes applied
                        </div>
                    )}

                    {/* Blocked indicator */}
                    {actionResult.type === "blocked" && (
                        <div style={{ fontSize: "0.78rem", color: "#f04e5e", fontWeight: 700, marginBottom: "0.3rem" }}>
                            🚫 Action Blocked
                        </div>
                    )}

                    {/* Success indicator */}
                    {actionResult.type === "success" && (
                        <div style={{ fontSize: "0.78rem", color: "#2cc984", fontWeight: 700, marginBottom: "0.3rem" }}>
                            ✅ Action Completed
                        </div>
                    )}

                    {/* Message */}
                    <div style={{ fontSize: "0.85rem" }}>{actionResult.message}</div>

                    {/* Rule code when blocked */}
                    {actionResult.ruleCode && (
                        <div style={{
                            fontSize: "0.75rem",
                            color: "#8888a8",
                            marginTop: "0.3rem",
                            fontFamily: "monospace",
                        }}>
                            Blocked by rule: {actionResult.ruleCode}
                        </div>
                    )}

                    {/* Legacy reason fallback */}
                    {actionResult.reason && !actionResult.ruleCode && (
                        <div style={{ fontSize: "0.78rem", color: "#8888a8", marginTop: "0.25rem" }}>
                            Reason: {actionResult.reason}
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}
