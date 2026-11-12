/**
 * Persistent Offline-First Sync Service for CraftLens Artisans
 *
 * - Persists drafts in expo-sqlite (`craftlens_offline.db`) on native devices
 *   with a clean StorageAdapter abstraction for automated integration testing.
 * - Explicit Conflict Resolution Policy: LAST_WRITE_WINS (LWW) by `updatedAtMs`,
 *   logging discarded stale edits into a durable conflict_log.
 * - Exponential backoff retries + deterministic `X-Idempotency-Key` headers.
 */

import { API_BASE_URL } from "./apiClient";

declare const require: ((moduleName: string) => Record<string, unknown>) | undefined;

export type SyncStatus = "PENDING" | "SYNCED" | "FAILED";

export interface OfflineDraft {
  id: string;
  idempotencyKey: string;
  title: string;
  description: string;
  categorySlug: string;
  primaryMaterial: string;
  technique: string;
  voiceTranscript?: string;
  language: string;
  retailPrice?: number;
  artisanConfirmed: boolean;
  syncStatus: SyncStatus;
  attempts: number;
  nextRetryAt: number;
  updatedAtMs: number;
  createdAt: string;
  remoteProductId?: string;
  lastError?: string;
}

export interface ConflictLogEntry {
  draftId: string;
  policy: "LAST_WRITE_WINS";
  winnerUpdatedAtMs: number;
  discardedUpdatedAtMs: number;
  summary: string;
  recordedAt: string;
}

export interface StorageAdapter {
  loadDrafts(): Promise<OfflineDraft[]>;
  saveDraft(draft: OfflineDraft): Promise<void>;
  deleteDraft(id: string): Promise<void>;
  loadConflicts(): Promise<ConflictLogEntry[]>;
  appendConflict(entry: ConflictLogEntry): Promise<void>;
}

export class InMemoryStorageAdapter implements StorageAdapter {
  private drafts = new Map<string, OfflineDraft>();
  private conflicts: ConflictLogEntry[] = [];

  async loadDrafts(): Promise<OfflineDraft[]> {
    return Array.from(this.drafts.values());
  }

  async saveDraft(draft: OfflineDraft): Promise<void> {
    this.drafts.set(draft.id, { ...draft });
  }

  async deleteDraft(id: string): Promise<void> {
    this.drafts.delete(id);
  }

  async loadConflicts(): Promise<ConflictLogEntry[]> {
    return [...this.conflicts];
  }

  async appendConflict(entry: ConflictLogEntry): Promise<void> {
    this.conflicts.push({ ...entry });
  }
}

export class ExpoSQLiteStorageAdapter implements StorageAdapter {
  private initialized = false;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  private db: any = null;
  private fallback = new InMemoryStorageAdapter();

  private async ensureDb(): Promise<boolean> {
    if (this.initialized) return this.db !== null;
    this.initialized = true;
    try {
      const req = typeof require === "function" ? require : null;
      const sqlite = req ? (req("expo-sqlite") as { openDatabaseSync?: (n: string) => unknown; default?: { openDatabaseSync?: (n: string) => unknown } }) : null;
      const openFn = sqlite?.openDatabaseSync || sqlite?.default?.openDatabaseSync;
      if (typeof openFn !== "function") return false;
      this.db = openFn("craftlens_offline.db");
      this.db.execSync(
        `CREATE TABLE IF NOT EXISTS offline_drafts (
          id TEXT PRIMARY KEY NOT NULL,
          payload TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS conflict_log (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          payload TEXT NOT NULL
        );`
      );
      return true;
    } catch {
      this.db = null;
      return false;
    }
  }

  async loadDrafts(): Promise<OfflineDraft[]> {
    if (!(await this.ensureDb())) return this.fallback.loadDrafts();
    const rows = this.db.getAllSync("SELECT payload FROM offline_drafts") as Array<{ payload: string }>;
    return rows.map((r) => JSON.parse(r.payload) as OfflineDraft);
  }

  async saveDraft(draft: OfflineDraft): Promise<void> {
    if (!(await this.ensureDb())) return this.fallback.saveDraft(draft);
    this.db.runSync(
      "INSERT OR REPLACE INTO offline_drafts (id, payload) VALUES (?, ?)",
      [draft.id, JSON.stringify(draft)]
    );
  }

  async deleteDraft(id: string): Promise<void> {
    if (!(await this.ensureDb())) return this.fallback.deleteDraft(id);
    this.db.runSync("DELETE FROM offline_drafts WHERE id = ?", [id]);
  }

  async loadConflicts(): Promise<ConflictLogEntry[]> {
    if (!(await this.ensureDb())) return this.fallback.loadConflicts();
    const rows = this.db.getAllSync("SELECT payload FROM conflict_log ORDER BY id DESC") as Array<{ payload: string }>;
    return rows.map((r) => JSON.parse(r.payload) as ConflictLogEntry);
  }

  async appendConflict(entry: ConflictLogEntry): Promise<void> {
    if (!(await this.ensureDb())) return this.fallback.appendConflict(entry);
    this.db.runSync("INSERT INTO conflict_log (payload) VALUES (?)", [JSON.stringify(entry)]);
  }
}

export type SyncTransport = (
  url: string,
  headers: Record<string, string>,
  body: Record<string, unknown>
) => Promise<{ ok: boolean; status: number; data?: { product_id?: string }; error?: string }>;

export async function defaultHttpTransport(
  url: string,
  headers: Record<string, string>,
  body: Record<string, unknown>
): Promise<{ ok: boolean; status: number; data?: { product_id?: string }; error?: string }> {
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...headers },
    body: JSON.stringify(body),
  });
  const json = await res.json().catch(() => null);
  if (!res.ok) {
    return {
      ok: false,
      status: res.status,
      error: (json && (json.detail || json.message)) || `HTTP ${res.status}`,
    };
  }
  return { ok: true, status: res.status, data: json?.data || {} };
}

export function computeBackoffMs(attempt: number, baseMs = 1000, maxMs = 60000): number {
  return Math.min(maxMs, baseMs * Math.pow(2, Math.max(0, attempt - 1)));
}

export class OfflineSyncManager {
  constructor(private storage: StorageAdapter = new ExpoSQLiteStorageAdapter()) {}

  async saveDraft(input: {
    id?: string;
    title: string;
    description: string;
    category?: string;
    categorySlug?: string;
    materials?: string;
    primaryMaterial?: string;
    technique?: string;
    voiceTranscript?: string;
    language?: string;
    retailPrice?: number;
    artisanConfirmed?: boolean;
    updatedAtMs?: number;
  }): Promise<{ draft: OfflineDraft; conflictLogged: boolean }> {
    const existingList = await this.storage.loadDrafts();
    const id = input.id || `draft_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;
    const nowMs = input.updatedAtMs ?? Date.now();
    const existing = existingList.find((d) => d.id === id);

    // Explicit LAST_WRITE_WINS conflict policy when stale incoming write collides with newer record
    if (existing && nowMs < existing.updatedAtMs) {
      await this.storage.appendConflict({
        draftId: id,
        policy: "LAST_WRITE_WINS",
        winnerUpdatedAtMs: existing.updatedAtMs,
        discardedUpdatedAtMs: nowMs,
        summary: `Preserved newer draft '${existing.title}' over stale edit '${input.title}'.`,
        recordedAt: new Date().toISOString(),
      });
      return { draft: existing, conflictLogged: true };
    }

    const draft: OfflineDraft = {
      id,
      idempotencyKey: existing?.idempotencyKey || `idem-${id}`,
      title: input.title,
      description: input.description,
      categorySlug: input.categorySlug || input.category || "handloom-textiles",
      primaryMaterial: input.primaryMaterial || input.materials || "Natural Handcrafted Material",
      technique: input.technique || "Traditional Indian Handicraft",
      voiceTranscript: input.voiceTranscript,
      language: input.language || "ta",
      retailPrice: input.retailPrice,
      artisanConfirmed: input.artisanConfirmed ?? true,
      syncStatus: "PENDING",
      attempts: 0,
      nextRetryAt: 0,
      updatedAtMs: nowMs,
      createdAt: existing?.createdAt || new Date().toISOString(),
      remoteProductId: existing?.remoteProductId,
    };
    await this.storage.saveDraft(draft);
    return { draft, conflictLogged: false };
  }

  async getDrafts(): Promise<OfflineDraft[]> {
    return this.storage.loadDrafts();
  }

  async getPendingDrafts(): Promise<OfflineDraft[]> {
    const all = await this.storage.loadDrafts();
    return all.filter((d) => d.syncStatus !== "SYNCED");
  }

  async getConflicts(): Promise<ConflictLogEntry[]> {
    return this.storage.loadConflicts();
  }

  async syncPendingDrafts(
    token: string,
    apiBaseUrl: string = API_BASE_URL,
    transport: SyncTransport = defaultHttpTransport,
    nowMs: number = Date.now()
  ): Promise<{ syncedCount: number; deferredCount: number; failedCount: number }> {
    const drafts = await this.storage.loadDrafts();
    let syncedCount = 0;
    let deferredCount = 0;
    let failedCount = 0;

    for (const draft of drafts) {
      if (draft.syncStatus === "SYNCED") continue;
      if (draft.nextRetryAt > nowMs) {
        deferredCount += 1;
        continue;
      }

      try {
        const res = await transport(
          `${apiBaseUrl}/voice/apply-to-product`,
          {
            Authorization: `Bearer ${token}`,
            "X-Idempotency-Key": draft.idempotencyKey,
          },
          {
            title: draft.title,
            summary: draft.description,
            primary_material: draft.primaryMaterial,
            technique: draft.technique,
            category_slug: draft.categorySlug,
            source_transcript: draft.voiceTranscript || "",
            source_language: draft.language,
            artisan_confirmed: draft.artisanConfirmed,
          }
        );

        if (res.ok) {
          draft.syncStatus = "SYNCED";
          draft.remoteProductId = res.data?.product_id;
          draft.lastError = undefined;
          await this.storage.saveDraft(draft);
          syncedCount += 1;
        } else {
          draft.attempts += 1;
          draft.syncStatus = "FAILED";
          draft.nextRetryAt = nowMs + computeBackoffMs(draft.attempts);
          draft.lastError = res.error || `HTTP ${res.status}`;
          await this.storage.saveDraft(draft);
          failedCount += 1;
        }
      } catch (err) {
        draft.attempts += 1;
        draft.syncStatus = "FAILED";
        draft.nextRetryAt = nowMs + computeBackoffMs(draft.attempts);
        draft.lastError = err instanceof Error ? err.message : "Network error";
        await this.storage.saveDraft(draft);
        failedCount += 1;
      }
    }

    return { syncedCount, deferredCount, failedCount };
  }

  async syncDraftsToServer(token = ""): Promise<{ syncedCount: number; deferredCount: number; failedCount: number }> {
    if (!token) {
      return { syncedCount: 0, deferredCount: (await this.getPendingDrafts()).length, failedCount: 0 };
    }
    return this.syncPendingDrafts(token);
  }
}

export const offlineSyncService = new OfflineSyncManager();

export async function queueOfflineDraft(draft: Parameters<OfflineSyncManager["saveDraft"]>[0]) {
  return offlineSyncService.saveDraft(draft);
}

export async function getOfflineDrafts() {
  return offlineSyncService.getDrafts();
}
