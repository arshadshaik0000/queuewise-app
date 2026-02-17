/**
 * PreviewPanel — Read-only preview with animated result display.
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
                style={{ marginBottom: preview ? "0.75rem" : 0 }}
            >
                {loading ? "⏳ Loading..." : "🔮 Preview"}
            </button>

            {preview && (
                <div className="preview-result">
                    <div className="preview-result-item">
                        <span className="preview-result-label">If served →</span>
                        <span className="preview-result-value">{preview.next_if_served}</span>
                    </div>
                    <div className="preview-result-item">
                        <span className="preview-result-label">If skipped →</span>
                        <span className="preview-result-value">next up: {preview.next_if_skipped}</span>
                    </div>
                    <div className="preview-result-muted">
                        ⏱ {preview.projected_wait_change}
                    </div>
                </div>
            )}
        </div>
    );
}
