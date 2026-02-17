/**
 * PreviewPanel — Read-only preview of the next queue action.
 *
 * WHY this exists:
 *   Operators need to see what WOULD happen before committing
 *   to serve or skip. This calls the read-only /preview endpoint
 *   and shows projected outcomes without side effects.
 */

import { useState } from "react";

interface PreviewData {
    next_if_served: string;
    next_if_skipped: string;
    skip_target: string;
    projected_wait_change: string;
    waiting_count: number;
}

interface Props {
    onPreview: () => Promise<PreviewData | null>;
}

export default function PreviewPanel({ onPreview }: Props) {
    const [preview, setPreview] = useState<PreviewData | null>(null);
    const [loading, setLoading] = useState(false);

    const handlePreview = async () => {
        setLoading(true);
        try {
            const data = await onPreview();
            setPreview(data);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="card">
            <div className="card-title">🔍 Preview Next Action</div>
            <button
                className="btn btn-primary"
                onClick={handlePreview}
                disabled={loading}
                style={{ marginBottom: preview ? "0.6rem" : 0 }}
            >
                {loading ? "Loading..." : "Preview"}
            </button>

            {preview && (
                <div style={{ fontSize: "0.85rem", lineHeight: 1.6 }}>
                    <div><strong>If served →</strong> {preview.next_if_served}</div>
                    <div><strong>If skipped →</strong> next up: {preview.next_if_skipped}</div>
                    <div style={{ color: "#8888a8", marginTop: "0.25rem" }}>
                        {preview.projected_wait_change}
                    </div>
                </div>
            )}
        </div>
    );
}
