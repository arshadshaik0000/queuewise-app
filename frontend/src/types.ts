/** Shared TypeScript types matching the backend API responses. */

export interface QueueEntry {
    id: number;
    user_name: string;
    position: number;
    status: "WAITING" | "SERVED" | "SKIPPED";
    joined_at: string;
}

export interface QueueStatus {
    queue_id: number;
    queue_name: string;
    queue_status: string;
    entries: QueueEntry[];
    explanation: string;
    wait_explanations: Record<string, string>;
}

/** Dashboard list item (GET /queues). */
export interface QueueSummary {
    id: number;
    name: string;
    status: string;
    waiting_count: number;
    total_count: number;
    created_at: string | null;
}

/** Derived-data summary (GET /queues/{id}/summary). */
export interface SummaryResponse {
    queue_id: number;
    queue_name: string;
    waiting_count: number;
    served_count: number;
    skipped_count: number;
    estimated_wait: string;
    explanation: string;
}

/** Preview response (GET /queues/{id}/preview). */
export interface PreviewResponse {
    next_if_served: string;
    next_if_skipped: string;
    skip_target: string;
    projected_wait_change: string;
    waiting_count: number;
}

/** Event timeline item (GET /queues/{id}/events). */
export interface EventItem {
    id: number;
    queue_id: number;
    action: string;
    result: string;
    detail: string;
    request_id: string;
    created_at: string;
}

export interface CreateQueueResponse {
    id: number;
    name: string;
}

export interface JoinQueueResponse {
    entry_id: number;
    user_name: string;
    position: number;
    status: string;
}

export interface ServeResponse {
    entry_id: number;
    user_name: string;
    status: string;
}

export interface SkipResponse {
    entry_id: number;
    user_name: string;
    status: string;
}

/** Dry-run response shape returned when ?dry_run=true. */
export interface DryRunResponse {
    dry_run: true;
    result: "would_succeed" | "would_fail";
    user_name?: string;
    reason?: string;
    rule_code?: string;
    explanation?: string;
}

/** Action result shown in the ExplanationPanel after an action. */
export interface ActionResult {
    type: "success" | "blocked" | "dry_run";
    message: string;
    reason?: string;
    ruleCode?: string;
    requestId: string;
}

export interface ApiError {
    error?: string;
    rule_code?: string;
    errors?: Record<string, string[]>;
}
