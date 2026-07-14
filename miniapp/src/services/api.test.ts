import { afterEach, describe, expect, it, vi } from "vitest";

import { ApiError, MiniAppApiClient } from "./api";

describe("MiniAppApiClient", () => {
  afterEach(() => vi.restoreAllMocks());

  it("sends raw Telegram initData on authenticated requests", async () => {
    const fetchMock = vi.spyOn(globalThis, "fetch").mockResolvedValue(
      new Response(JSON.stringify({ id: 1, balance: "0.00" }), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      }),
    );
    const client = new MiniAppApiClient("raw=signed&hash=value");

    await client.getMe();

    expect(fetchMock).toHaveBeenCalledWith(
      "/api/miniapp/me",
      expect.objectContaining({
        headers: expect.objectContaining({
          "X-Init-Data": "raw=signed&hash=value",
        }),
      }),
    );
  });

  it("preserves backend status and detail for recovery decisions", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(
      new Response(JSON.stringify({ detail: "insufficient balance" }), {
        status: 409,
        headers: { "Content-Type": "application/json" },
      }),
    );
    const client = new MiniAppApiClient("signed");

    await expect(
      client.playColor("10.00", "red", crypto.randomUUID()),
    ).rejects.toEqual(new ApiError(409, "insufficient balance"));
  });
});
