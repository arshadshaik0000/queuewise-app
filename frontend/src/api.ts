/**
 * API client for communicating with the Flask backend.
 * All requests go through the Vite proxy (/queues → localhost:5000).
 *
 * WHY requestId is captured:
 *   The backend attaches X-Request-ID to every response for
 *   traceability. We surface it in the UI so operators can
 *   correlate frontend actions to backend logs.
 *
 * WHY apiVersion is captured:
 *   The backend returns X-API-Version in every response.
 *   We expose it in the UI footer for version visibility.
 */

import type {
    CreateQueueResponse,
    JoinQueueResponse,
    QueueStatus,
    QueueSummary,
    ServeResponse,
    SkipResponse,
    DryRunResponse,
    SummaryResponse,
    PreviewResponse,
    EventItem,
} from "./types";

const HEADERS = { "Content-Type": "application/json" };

/**
 * Every API response includes X-Request-ID and X-API-Version.
 */
export interface ApiResult<T> {
    data: T;
    requestId: string;
    apiVersion: string;
}

async function handleResponse<T>(res: Response): Promise<ApiResult<T>> {
    const data = await res.json();
    if (!res.ok) {
        // Attach rule_code to the error so callers can access it
        const err = new Error(data.error || JSON.stringify(data.errors) || "Request failed");
        (err as any).ruleCode = data.rule_code;
        throw err;
    }
    const requestId = res.headers.get("X-Request-ID") || "unknown";
    const apiVersion = res.headers.get("X-API-Version") || "unknown";
    return { data: data as T, requestId, apiVersion };
}

// --- Queue Management ---

export async function listQueues(): Promise<QueueSummary[]> {
    const res = await fetch("/queues");
    const { data } = await handleResponse<QueueSummary[]>(res);
    return data;
}

export async function createQueue(name: string): Promise<CreateQueueResponse> {
    const res = await fetch("/queues", {
        method: "POST",
        headers: HEADERS,
        body: JSON.stringify({ name }),
    });
    const { data } = await handleResponse<CreateQueueResponse>(res);
    return data;
}

export async function getQueueStatus(queueId: number): Promise<ApiResult<QueueStatus>> {
    const res = await fetch(`/queues/${queueId}/status`);
    return handleResponse<QueueStatus>(res);
}

// --- Actions (with dry-run and request-ID capture) ---

export async function joinQueue(
    queueId: number,
    userName: string,
    opts?: { dryRun?: boolean },
): Promise<ApiResult<JoinQueueResponse | DryRunResponse>> {
    const url = opts?.dryRun
        ? `/queues/${queueId}/join?dry_run=true`
        : `/queues/${queueId}/join`;
    const res = await fetch(url, {
        method: "POST",
        headers: HEADERS,
        body: JSON.stringify({ user_name: userName }),
    });
    return handleResponse<JoinQueueResponse | DryRunResponse>(res);
}

export async function serveNext(
    queueId: number,
    opts?: { dryRun?: boolean },
): Promise<ApiResult<ServeResponse | DryRunResponse>> {
    const url = opts?.dryRun
        ? `/queues/${queueId}/serve?dry_run=true`
        : `/queues/${queueId}/serve`;
    const res = await fetch(url, {
        method: "PATCH",
        headers: HEADERS,
    });
    return handleResponse<ServeResponse | DryRunResponse>(res);
}

export async function skipNext(
    queueId: number,
    opts?: { dryRun?: boolean },
): Promise<ApiResult<SkipResponse | DryRunResponse>> {
    const url = opts?.dryRun
        ? `/queues/${queueId}/skip?dry_run=true`
        : `/queues/${queueId}/skip`;
    const res = await fetch(url, {
        method: "PATCH",
        headers: HEADERS,
    });
    return handleResponse<SkipResponse | DryRunResponse>(res);
}

/** Skip a specific entry by ID (used by QueueBoard inline buttons). */
export async function skipUser(queueId: number, entryId: number): Promise<SkipResponse> {
    const res = await fetch(`/queues/${queueId}/skip/${entryId}`, {
        method: "PATCH",
        headers: HEADERS,
    });
    const { data } = await handleResponse<SkipResponse>(res);
    return data;
}

// --- Read-only endpoints ---

export async function getSummary(queueId: number): Promise<SummaryResponse> {
    const res = await fetch(`/queues/${queueId}/summary`);
    const { data } = await handleResponse<SummaryResponse>(res);
    return data;
}

export async function getPreview(queueId: number): Promise<PreviewResponse | null> {
    const res = await fetch(`/queues/${queueId}/preview`);
    if (!res.ok) return null;  // preview is best-effort (empty queue = no preview)
    const { data } = await handleResponse<PreviewResponse>(res);
    return data;
}

export async function getEvents(queueId: number, limit: number = 20): Promise<EventItem[]> {
    const res = await fetch(`/queues/${queueId}/events?limit=${limit}`);
    const { data } = await handleResponse<EventItem[]>(res);
    return data;
}

// --- Pause / Resume ---

export async function pauseQueue(queueId: number): Promise<ApiResult<{ queue_id: number; status: string }>> {
    const res = await fetch(`/queues/${queueId}/pause`, {
        method: "PATCH",
        headers: HEADERS,
    });
    return handleResponse<{ queue_id: number; status: string }>(res);
}

export async function resumeQueue(queueId: number): Promise<ApiResult<{ queue_id: number; status: string }>> {
    const res = await fetch(`/queues/${queueId}/resume`, {
        method: "PATCH",
        headers: HEADERS,
    });
    return handleResponse<{ queue_id: number; status: string }>(res);
}
