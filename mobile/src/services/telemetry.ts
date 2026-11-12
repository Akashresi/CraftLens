/**
 * Privacy-respecting, DPDP Act 2023 consent-gated analytics & crash reporting hook.
 * Zero events are captured or forwarded unless the user explicitly grants analytics consent.
 */

export interface TelemetryEvent {
  type: "event" | "crash";
  name: string;
  timestamp: string;
  metadata: Record<string, string | number | boolean>;
}

const PII_KEYS = new Set(["email", "phone", "password", "token", "aadhaar", "pan", "address"]);

function scrubMetadata(raw?: Record<string, unknown>): Record<string, string | number | boolean> {
  const safe: Record<string, string | number | boolean> = {};
  if (!raw) return safe;
  for (const [k, v] of Object.entries(raw)) {
    if (PII_KEYS.has(k.toLowerCase())) continue;
    if (typeof v === "string" || typeof v === "number" || typeof v === "boolean") {
      safe[k] = v;
    }
  }
  return safe;
}

class ConsentGatedTelemetry {
  private consentGranted = false;
  private buffer: TelemetryEvent[] = [];

  setConsent(granted: boolean): void {
    this.consentGranted = Boolean(granted);
    if (!this.consentGranted) {
      this.buffer = [];
    }
  }

  isConsentGranted(): boolean {
    return this.consentGranted;
  }

  trackEvent(name: string, metadata?: Record<string, unknown>): boolean {
    if (!this.consentGranted) return false;
    this.buffer.push({
      type: "event",
      name,
      timestamp: new Date().toISOString(),
      metadata: scrubMetadata(metadata),
    });
    return true;
  }

  captureCrash(err: unknown, context?: Record<string, unknown>): boolean {
    if (!this.consentGranted) return false;
    const message = err instanceof Error ? err.message : String(err);
    this.buffer.push({
      type: "crash",
      name: message.slice(0, 200),
      timestamp: new Date().toISOString(),
      metadata: scrubMetadata(context),
    });
    // STUB: External Sentry DSN forwarding is invoked only if EXPO_PUBLIC_SENTRY_DSN is configured
    return true;
  }

  getEvents(): TelemetryEvent[] {
    return [...this.buffer];
  }
}

export const telemetry = new ConsentGatedTelemetry();
