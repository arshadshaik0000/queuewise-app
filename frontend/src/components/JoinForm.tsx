import { useState } from "react";

/**
 * Name validation matching backend Rule 8.
 * Letters, spaces, hyphens, and apostrophes only. Min 2 chars.
 */
const NAME_REGEX = /^[A-Za-z][A-Za-z \-']*[A-Za-z]$/;

function validateName(name: string): string | null {
    const trimmed = name.trim();
    if (trimmed.length < 2) {
        return "Name must be at least 2 characters.";
    }
    if (!NAME_REGEX.test(trimmed)) {
        return "Letters only — spaces, hyphens, and apostrophes allowed.";
    }
    return null; // valid
}

interface Props {
    onJoin: (userName: string) => Promise<void>;
}

export default function JoinForm({ onJoin }: Props) {
    const [name, setName] = useState("");
    const [submitting, setSubmitting] = useState(false);
    const [validationError, setValidationError] = useState<string | null>(null);

    const handleChange = (value: string) => {
        setName(value);
        // Clear error as user types, re-validate on submit
        if (validationError) {
            const err = validateName(value);
            if (!err) setValidationError(null);
        }
    };

    const handleSubmit = async () => {
        const trimmed = name.trim();
        if (!trimmed || submitting) return;

        const error = validateName(trimmed);
        if (error) {
            setValidationError(error);
            return;
        }

        setSubmitting(true);
        setValidationError(null);
        try {
            await onJoin(trimmed);
            setName("");
        } finally {
            setSubmitting(false);
        }
    };

    return (
        <div className="card">
            <div className="card-title">➕ Join Queue</div>
            <div className="join-form">
                <div style={{ flex: 1 }}>
                    <input
                        type="text"
                        placeholder="Your name"
                        value={name}
                        onChange={(e) => handleChange(e.target.value)}
                        onKeyDown={(e) => e.key === "Enter" && handleSubmit()}
                        disabled={submitting}
                        style={validationError ? { borderColor: "var(--color-error)" } : {}}
                    />
                    {validationError && (
                        <div style={{
                            color: "var(--color-error)",
                            fontSize: "0.75rem",
                            marginTop: "0.25rem",
                            paddingLeft: "0.25rem",
                        }}>
                            {validationError}
                        </div>
                    )}
                </div>
                <button
                    className="btn btn-primary"
                    onClick={handleSubmit}
                    disabled={!name.trim() || submitting}
                >
                    Join
                </button>
            </div>
        </div>
    );
}
