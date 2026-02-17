/**
 * ExplanationPanel — AI explanation with animated results.
 */

import type { ActionResult } from "../types";

interface Props {
    explanation: string;
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
                <div className={`action-result ${actionResult.type}`}>
                    {/* Header */}
                    {actionResult.type === "dry_run" && (
                        <div className="action-result-header dry_run">
                            🔸 Simulation Mode — No changes applied
                        </div>
                    )}
                    {actionResult.type === "blocked" && (
                        <div className="action-result-header blocked">
                            🚫 Action Blocked
                        </div>
                    )}
                    {actionResult.type === "success" && (
                        <div className="action-result-header success">
                            ✅ Action Completed
                        </div>
                    )}

                    {/* Message */}
                    <div className="action-result-message">{actionResult.message}</div>

                    {/* Rule code */}
                    {actionResult.ruleCode && (
                        <div className="action-result-meta">
                            Blocked by rule: {actionResult.ruleCode}
                        </div>
                    )}

                    {/* Reason fallback */}
                    {actionResult.reason && !actionResult.ruleCode && (
                        <div className="action-result-meta">
                            Reason: {actionResult.reason}
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}
