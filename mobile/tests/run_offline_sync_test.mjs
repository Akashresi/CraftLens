import assert from "node:assert/strict";
import { createRequire } from "node:module";

const require = createRequire(import.meta.url);
const {
  OfflineSyncManager,
  InMemoryStorageAdapter,
  computeBackoffMs,
} = require("../.tmp_test_dist/offlineSync.js");
const { telemetry } = require("../.tmp_test_dist/telemetry.js");

async function main() {
  // 1. Telemetry Consent Guard & PII Scrubbing
  telemetry.setConsent(false);
  assert.equal(telemetry.trackEvent("draft_created", { email: "secret@x.com" }), false);
  assert.equal(telemetry.getEvents().length, 0);

  telemetry.setConsent(true);
  assert.equal(
    telemetry.trackEvent("draft_synced", {
      language: "ta",
      email: "artisan@craftlens.org",
      token: "jwt-secret",
      aadhaar: "1234",
    }),
    true
  );
  const events = telemetry.getEvents();
  assert.equal(events.length, 1);
  assert.equal(events[0].metadata.language, "ta");
  assert.equal(events[0].metadata.email, undefined);
  assert.equal(events[0].metadata.token, undefined);
  assert.equal(events[0].metadata.aadhaar, undefined);

  // 2. Exponential backoff check
  assert.equal(computeBackoffMs(1), 1000);
  assert.equal(computeBackoffMs(2), 2000);
  assert.equal(computeBackoffMs(3), 4000);

  // 3. Offline create listing -> LWW conflict -> failed retry -> reconnect sync (zero data loss)
  const storage = new InMemoryStorageAdapter();
  const manager = new OfflineSyncManager(storage);

  const t1 = 10000;
  const saved = await manager.saveDraft({
    id: "offline-craft-1",
    title: "Kanchipuram Handloom Silk Saree",
    description: "Pure mulberry silk woven on pit loom",
    categorySlug: "handloom-textiles",
    primaryMaterial: "Mulberry Silk",
    technique: "Korvai Weaving",
    voiceTranscript: "இது காஞ்சிபுரம் பட்டுப் புடவை",
    language: "ta",
    updatedAtMs: t1,
  });
  assert.equal(saved.conflictLogged, false);
  assert.equal(saved.draft.syncStatus, "PENDING");
  assert.equal(saved.draft.idempotencyKey, "idem-offline-craft-1");

  // Stale edit (t0 < t1) must NOT overwrite newer draft and must append conflict_log
  const stale = await manager.saveDraft({
    id: "offline-craft-1",
    title: "Stale Old Title",
    description: "Old desc",
    updatedAtMs: t1 - 5000,
  });
  assert.equal(stale.conflictLogged, true);
  assert.equal(stale.draft.title, "Kanchipuram Handloom Silk Saree");
  const conflicts = await manager.getConflicts();
  assert.equal(conflicts.length, 1);
  assert.equal(conflicts[0].policy, "LAST_WRITE_WINS");

  // Simulated offline/network failure on first sync attempt
  const failTransport = async () => {
    throw new Error("ENETUNREACH: Airplane mode");
  };
  const r1 = await manager.syncPendingDrafts("jwt-token", "http://127.0.0.1:8000/api/v1", failTransport, 20000);
  assert.equal(r1.failedCount, 1);
  assert.equal(r1.syncedCount, 0);
  let drafts = await manager.getDrafts();
  assert.equal(drafts[0].attempts, 1);
  assert.equal(drafts[0].nextRetryAt, 21000); // 20000 + 1000ms backoff

  // Calling sync before backoff window elapses defers cleanly
  let calledCount = 0;
  const successTransport = async (_url, headers, body) => {
    calledCount += 1;
    assert.equal(headers["X-Idempotency-Key"], "idem-offline-craft-1");
    assert.equal(body.artisan_confirmed, true);
    return { ok: true, status: 200, data: { product_id: "prod-sync-999" } };
  };
  const r2 = await manager.syncPendingDrafts("jwt-token", "http://127.0.0.1:8000/api/v1", successTransport, 20500);
  assert.equal(r2.deferredCount, 1);
  assert.equal(calledCount, 0);

  // Reconnect after backoff window -> succeeds and persists remoteProductId
  const r3 = await manager.syncPendingDrafts("jwt-token", "http://127.0.0.1:8000/api/v1", successTransport, 21500);
  assert.equal(r3.syncedCount, 1);
  assert.equal(calledCount, 1);
  drafts = await manager.getDrafts();
  assert.equal(drafts[0].syncStatus, "SYNCED");
  assert.equal(drafts[0].remoteProductId, "prod-sync-999");

  console.log("PASS: Mobile offline create -> conflict LWW -> backoff -> reconnect sync (zero data loss) & consent telemetry verified.");
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
