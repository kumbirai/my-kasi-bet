export interface PendingColorAttempt {
  idempotencyKey: string;
  selectedColor: string;
  stake: string;
}

const STORAGE_PREFIX = "mykasibets:pending-color-attempt";
const UUID_PATTERN =
  /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;

function storageKey(userId: number): string {
  return `${STORAGE_PREFIX}:${userId}`;
}

function localStorageOrNull(): Storage | null {
  try {
    return window.localStorage;
  } catch {
    return null;
  }
}

function isPendingColorAttempt(value: unknown): value is PendingColorAttempt {
  if (!value || typeof value !== "object") return false;
  const attempt = value as Record<string, unknown>;
  return (
    typeof attempt.idempotencyKey === "string" &&
    UUID_PATTERN.test(attempt.idempotencyKey) &&
    typeof attempt.selectedColor === "string" &&
    typeof attempt.stake === "string"
  );
}

export function loadPendingColorAttempt(userId: number): PendingColorAttempt | null {
  const storage = localStorageOrNull();
  if (!storage) return null;

  const key = storageKey(userId);
  try {
    const serialized = storage.getItem(key);
    if (!serialized) return null;
    const attempt: unknown = JSON.parse(serialized);
    if (isPendingColorAttempt(attempt)) return attempt;
    storage.removeItem(key);
  } catch {
    return null;
  }
  return null;
}

export function savePendingColorAttempt(
  userId: number,
  attempt: PendingColorAttempt,
): void {
  try {
    localStorageOrNull()?.setItem(storageKey(userId), JSON.stringify(attempt));
  } catch {
    // The in-memory attempt remains authoritative when persistence is unavailable.
  }
}

export function clearPendingColorAttempt(userId: number): void {
  try {
    localStorageOrNull()?.removeItem(storageKey(userId));
  } catch {
    // Storage cleanup is best-effort in restricted WebViews.
  }
}
