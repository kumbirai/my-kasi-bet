import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import type { GameConfig, MiniAppApi, PlayResponse } from "../services/api";
import type { TelegramWebApp } from "../types/telegram";
import { ColorGame } from "./ColorGame";

const config: GameConfig = {
  id: "color",
  name: "Color Game",
  limits: { minimum: "5.00", maximum: "500.00" },
  rules: {
    colors: ["red", "green", "blue", "yellow"],
    multiplier: "3.0",
  },
};

const telegram: TelegramWebApp = {
  initData: "signed",
  ready: vi.fn(),
  expand: vi.fn(),
  close: vi.fn(),
  onEvent: vi.fn(),
  offEvent: vi.fn(),
};

function deferred<T>() {
  let resolve!: (value: T) => void;
  const promise = new Promise<T>((done) => {
    resolve = done;
  });
  return { promise, resolve };
}

describe("ColorGame", () => {
  it("reveals only the result returned by the server", async () => {
    const request = deferred<PlayResponse>();
    const api: MiniAppApi = {
      getConfig: vi.fn(),
      getMe: vi.fn(),
      playColor: vi.fn(() => request.promise),
    };
    const user = userEvent.setup();
    render(
      <ColorGame
        api={api}
        config={config}
        onBack={vi.fn()}
        onBalanceChange={vi.fn()}
        telegram={telegram}
        userId={7}
      />,
    );

    await user.click(screen.getByRole("button", { name: "Red" }));
    await user.click(screen.getByRole("button", { name: "Bet R5.00" }));
    expect(screen.queryByText("You matched")).not.toBeInTheDocument();

    request.resolve({
      bet_id: 42,
      balance: "110.00",
      result: {
        selected_color: "red",
        drawn_color: "red",
        is_win: true,
        stake: 5,
        payout: 15,
        multiplier: 3,
      },
    });

    expect(await screen.findByText("You matched")).toBeInTheDocument();
    expect(screen.getByText("Bet reference #42")).toBeInTheDocument();
  });

  it("reuses an uncertain attempt after a network failure and remount", async () => {
    const settledResponse: PlayResponse = {
      bet_id: 77,
      balance: "90.00",
      result: {
        selected_color: "blue",
        drawn_color: "red",
        is_win: false,
        stake: 10,
        payout: 0,
        multiplier: 0,
      },
    };
    const playColor = vi
      .fn<MiniAppApi["playColor"]>()
      .mockRejectedValueOnce(new TypeError("connection lost"))
      .mockResolvedValueOnce(settledResponse);
    const api: MiniAppApi = {
      getConfig: vi.fn(),
      getMe: vi.fn(),
      playColor,
    };
    const firstView = render(
      <ColorGame
        api={api}
        config={config}
        onBack={vi.fn()}
        onBalanceChange={vi.fn()}
        telegram={telegram}
        userId={11}
      />,
    );
    const user = userEvent.setup();

    await user.click(screen.getByRole("button", { name: "Blue" }));
    await user.clear(screen.getByRole("textbox"));
    await user.type(screen.getByRole("textbox"), "10.00");
    await user.click(screen.getByRole("button", { name: "Bet R10.00" }));

    expect(await screen.findByText("Result not confirmed")).toBeInTheDocument();
    const firstIdempotencyKey = playColor.mock.calls[0][2];
    firstView.unmount();

    render(
      <ColorGame
        api={api}
        config={config}
        onBack={vi.fn()}
        onBalanceChange={vi.fn()}
        telegram={telegram}
        userId={11}
      />,
    );
    await user.click(screen.getByRole("button", { name: "Check result" }));

    expect(playColor).toHaveBeenCalledTimes(2);
    expect(playColor.mock.calls[1]).toEqual(["10.00", "blue", firstIdempotencyKey]);
    expect(await screen.findByText("No match this time")).toBeInTheDocument();
    expect(screen.getByText("Bet reference #77")).toBeInTheDocument();
  });
});
