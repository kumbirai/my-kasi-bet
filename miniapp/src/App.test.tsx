import { render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";

import App from "./App";

describe("App", () => {
  afterEach(() => {
    delete window.Telegram;
  });

  it("renders a safe fallback outside Telegram", () => {
    render(<App />);

    expect(
      screen.getByRole("heading", { name: "Open in Telegram" }),
    ).toBeInTheDocument();
    expect(
      screen.getByText(/uses Telegram to verify your account/i),
    ).toBeInTheDocument();
  });
});
