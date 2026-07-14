export interface GameConfig {
  id: string;
  name: string;
  limits: { minimum: string; maximum: string };
  rules: Record<string, unknown>;
}

export interface MiniAppConfig {
  currency: string;
  games: GameConfig[];
}

export interface MiniAppUser {
  id: number;
  telegram_chat_id: string;
  username: string | null;
  balance: string;
}

export interface ColorResult {
  selected_color: string;
  drawn_color: string;
  is_win: boolean;
  stake: number;
  payout: number;
  multiplier: number;
}

export interface PlayResponse {
  result: ColorResult;
  balance: string;
  bet_id: number;
}

export interface MiniAppApi {
  getConfig(): Promise<MiniAppConfig>;
  getMe(): Promise<MiniAppUser>;
  playColor(stake: string, selectedColor: string, idempotencyKey: string): Promise<PlayResponse>;
}

export class ApiError extends Error {
  constructor(
    public readonly status: number,
    message: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

export function createIdempotencyKey(): string {
  if (typeof crypto.randomUUID === "function") return crypto.randomUUID();
  const bytes = crypto.getRandomValues(new Uint8Array(16));
  bytes[6] = (bytes[6] & 0x0f) | 0x40;
  bytes[8] = (bytes[8] & 0x3f) | 0x80;
  const hex = Array.from(bytes, (byte) => byte.toString(16).padStart(2, "0"));
  return [
    hex.slice(0, 4).join(""),
    hex.slice(4, 6).join(""),
    hex.slice(6, 8).join(""),
    hex.slice(8, 10).join(""),
    hex.slice(10).join(""),
  ].join("-");
}

export class MiniAppApiClient implements MiniAppApi {
  constructor(private readonly initData: string) {}

  private async request<T>(path: string, options: RequestInit = {}): Promise<T> {
    const controller = new AbortController();
    const timeout = window.setTimeout(() => controller.abort(), 15_000);
    try {
      const response = await fetch(`/api/miniapp${path}`, {
        ...options,
        headers: {
          "Content-Type": "application/json",
          "X-Init-Data": this.initData,
          ...options.headers,
        },
        signal: options.signal ?? controller.signal,
      });
      if (!response.ok) {
        const payload = (await response.json().catch(() => null)) as {
          detail?: string;
        } | null;
        throw new ApiError(response.status, payload?.detail ?? "Request failed");
      }
      return (await response.json()) as T;
    } finally {
      window.clearTimeout(timeout);
    }
  }

  getConfig(): Promise<MiniAppConfig> {
    return this.request<MiniAppConfig>("/config");
  }

  getMe(): Promise<MiniAppUser> {
    return this.request<MiniAppUser>("/me");
  }

  playColor(
    stake: string,
    selectedColor: string,
    idempotencyKey: string,
  ): Promise<PlayResponse> {
    return this.request<PlayResponse>("/play", {
      method: "POST",
      body: JSON.stringify({
        game: "color",
        stake,
        data: { selected_color: selectedColor },
        idempotency_key: idempotencyKey,
      }),
    });
  }
}
