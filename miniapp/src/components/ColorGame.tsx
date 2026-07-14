import { useCallback, useEffect, useMemo, useRef, useState } from "react";

import {
  ApiError,
  createIdempotencyKey,
  type GameConfig,
  type MiniAppApi,
  type PlayResponse,
} from "../services/api";
import {
  clearPendingColorAttempt,
  loadPendingColorAttempt,
  type PendingColorAttempt,
  savePendingColorAttempt,
} from "../services/pendingAttempt";
import type { TelegramWebApp } from "../types/telegram";

interface ColorGameProps {
  api: MiniAppApi;
  config: GameConfig;
  telegram: TelegramWebApp;
  userId: number;
  onBalanceChange(balance: string): void;
  onBack(): void;
}

const colorLabels: Record<string, string> = {
  red: "Red",
  green: "Green",
  blue: "Blue",
  yellow: "Yellow",
};

function isUncertainOutcome(error: unknown): boolean {
  if (!(error instanceof ApiError)) return true;
  if (error.status >= 500) return true;
  return error.status === 409 && error.message === "bet settlement pending";
}

function errorMessage(error: unknown, uncertain: boolean): string {
  if (uncertain) {
    return "Your result was not confirmed. Check the same bet again before playing another.";
  }
  if (error instanceof ApiError) {
    if (error.status === 401) return "Your Telegram session expired. Reopen the app to continue.";
    if (error.status === 403) return "This account is unavailable.";
    if (error.status === 409 && error.message === "insufficient balance") {
      return "Your balance is too low for this stake.";
    }
    if (error.status === 409 && error.message === "bet refunded") {
      return "The unsettled bet was refunded to your wallet.";
    }
    if (error.status === 409) return "That bet is still settling. Check again shortly.";
    if (error.status === 429) return "You are playing too quickly. Wait a moment and try again.";
  }
  return "We could not place this bet. Check your connection and try again.";
}

export function ColorGame({
  api,
  config,
  telegram,
  userId,
  onBalanceChange,
  onBack,
}: ColorGameProps) {
  const colors = config.rules.colors as string[];
  const minimumStake = Number(config.limits.minimum);
  const maximumStake = Number(config.limits.maximum);
  const [activeAttempt, setActiveAttempt] = useState<PendingColorAttempt | null>(
    () => {
      const stored = loadPendingColorAttempt(userId);
      const storedStake = Number(stored?.stake);
      const isValid =
        stored !== null &&
        colors.includes(stored.selectedColor) &&
        /^\d+(\.\d{1,2})?$/.test(stored.stake) &&
        Number.isFinite(storedStake) &&
        storedStake >= minimumStake &&
        storedStake <= maximumStake;
      if (isValid) return stored;
      clearPendingColorAttempt(userId);
      return null;
    },
  );
  const [selectedColor, setSelectedColor] = useState<string | null>(
    activeAttempt?.selectedColor ?? null,
  );
  const [stake, setStake] = useState(activeAttempt?.stake ?? config.limits.minimum);
  const [playResponse, setPlayResponse] = useState<PlayResponse | null>(null);
  const [revealed, setRevealed] = useState(false);
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string | null>(
    activeAttempt
      ? "A previous result still needs confirmation. Check it before playing again."
      : null,
  );
  const pendingRef = useRef(false);

  const stakeNumber = Number(stake);
  const validStake =
    Number.isFinite(stakeNumber) &&
    stakeNumber >= minimumStake &&
    stakeNumber <= maximumStake &&
    /^\d+(\.\d{1,2})?$/.test(stake);
  const canSubmit =
    (activeAttempt !== null || (selectedColor !== null && validStake)) && !pending;

  const submit = useCallback(async () => {
    if (pendingRef.current) return;
    if (!activeAttempt && (!selectedColor || !validStake)) return;

    const attempt = activeAttempt ?? {
      idempotencyKey: createIdempotencyKey(),
      selectedColor: selectedColor as string,
      stake,
    };
    if (!activeAttempt) {
      savePendingColorAttempt(userId, attempt);
      setActiveAttempt(attempt);
    }
    pendingRef.current = true;
    setPending(true);
    setError(null);
    setPlayResponse(null);
    setRevealed(false);
    telegram.HapticFeedback?.impactOccurred("medium");
    try {
      const response = await api.playColor(
        attempt.stake,
        attempt.selectedColor,
        attempt.idempotencyKey,
      );
      clearPendingColorAttempt(userId);
      setActiveAttempt(null);
      setPlayResponse(response);
      setRevealed(document.visibilityState === "visible");
      onBalanceChange(response.balance);
      telegram.HapticFeedback?.notificationOccurred(
        response.result.is_win ? "success" : "error",
      );
    } catch (requestError) {
      const uncertain = isUncertainOutcome(requestError);
      if (!uncertain) {
        clearPendingColorAttempt(userId);
        setActiveAttempt(null);
      }
      setError(errorMessage(requestError, uncertain));
      if (
        requestError instanceof ApiError &&
        requestError.status === 409 &&
        requestError.message === "bet refunded"
      ) {
        void api
          .getMe()
          .then((user) => onBalanceChange(user.balance))
          .catch(() => undefined);
      }
      if (requestError instanceof ApiError && requestError.status === 401) {
        telegram.showPopup?.({
          title: "Session expired",
          message: "Reopen MyKasiBets from Telegram to continue.",
          buttons: [{ type: "close" }],
        });
      }
    } finally {
      pendingRef.current = false;
      setPending(false);
    }
  }, [
    activeAttempt,
    api,
    onBalanceChange,
    selectedColor,
    stake,
    telegram,
    userId,
    validStake,
  ]);

  const navigateBack = useCallback(() => {
    if (pendingRef.current || activeAttempt) {
      telegram.showPopup?.({
        title: activeAttempt ? "Result not confirmed" : "Bet settling",
        message: activeAttempt
          ? "Check this result before leaving so the same bet is not submitted twice."
          : "Wait for the server to confirm this result before leaving.",
        buttons: [{ type: "close" }],
      });
      return;
    }
    onBack();
  }, [activeAttempt, onBack, telegram]);

  useEffect(() => {
    const backButton = telegram.BackButton;
    backButton?.show();
    backButton?.onClick(navigateBack);
    return () => {
      backButton?.offClick(navigateBack);
      backButton?.hide();
    };
  }, [navigateBack, telegram]);

  useEffect(() => {
    const mainButton = telegram.MainButton;
    if (!mainButton) return;
    mainButton.show();
    return () => mainButton.hide();
  }, [telegram]);

  useEffect(() => {
    const mainButton = telegram.MainButton;
    if (!mainButton) return;
    mainButton.onClick(submit);
    return () => mainButton.offClick(submit);
  }, [submit, telegram]);

  useEffect(() => {
    const mainButton = telegram.MainButton;
    if (!mainButton) return;
    mainButton.setText(
      activeAttempt
        ? "Check result"
        : selectedColor
          ? `Bet R${stake || "0"}`
          : "Choose a colour",
    );
    if (canSubmit) mainButton.enable?.();
    else mainButton.disable?.();
    if (pending) mainButton.showProgress?.();
    else mainButton.hideProgress?.();
    return () => {
      mainButton.hideProgress?.();
    };
  }, [activeAttempt, canSubmit, pending, selectedColor, stake, telegram]);

  useEffect(() => {
    const finishReveal = () => {
      if (!document.hidden && playResponse) setRevealed(true);
    };
    document.addEventListener("visibilitychange", finishReveal);
    return () => document.removeEventListener("visibilitychange", finishReveal);
  }, [playResponse]);

  const result = playResponse?.result ?? null;

  const stakeError = useMemo(() => {
    if (!stake) return "Enter a stake.";
    if (!/^\d+(\.\d{1,2})?$/.test(stake)) return "Use no more than two decimal places.";
    if (!validStake) {
      return `Stake must be between R${config.limits.minimum} and R${config.limits.maximum}.`;
    }
    return null;
  }, [config.limits.maximum, config.limits.minimum, stake, validStake]);

  return (
    <main className="screen game-screen" aria-labelledby="color-title">
      <button
        className="text-back"
        disabled={pending || Boolean(activeAttempt)}
        onClick={navigateBack}
        type="button"
      >
        <span aria-hidden="true">←</span> Games
      </button>

      <header className="screen-heading compact-heading">
        <p className="eyebrow">Instant result</p>
        <h1 id="color-title">Colour Game</h1>
        <p>Pick a colour. A match returns 3× your stake.</p>
      </header>

      <section aria-labelledby="colour-choice-title">
        <div className="section-label">
          <h2 id="colour-choice-title">Choose one colour</h2>
          <span>Required</span>
        </div>
        <div className="color-grid">
          {colors.map((color) => {
            const selected = color === selectedColor;
            const drawn = revealed && color === result?.drawn_color;
            return (
              <button
                aria-label={`${colorLabels[color]}${drawn ? ", drawn colour" : ""}`}
                aria-pressed={selected}
                className={`color-choice color-${color}${drawn ? " is-drawn" : ""}`}
                disabled={pending || Boolean(activeAttempt)}
                key={color}
                onClick={() => {
                  setSelectedColor(color);
                  setPlayResponse(null);
                  setError(null);
                }}
                type="button"
              >
                <span className="color-swatch" aria-hidden="true" />
                <span>{colorLabels[color]}</span>
                <span className="choice-mark" aria-hidden="true">
                  {selected ? "✓" : ""}
                </span>
              </button>
            );
          })}
        </div>
      </section>

      <section className="stake-section" aria-labelledby="stake-title">
        <div className="section-label">
          <h2 id="stake-title">Your stake</h2>
          <span>
            R{config.limits.minimum}–R{config.limits.maximum}
          </span>
        </div>
        <label className={`money-input${stakeError ? " has-error" : ""}`}>
          <span>R</span>
          <input
            aria-describedby="stake-help"
            aria-invalid={Boolean(stakeError)}
            disabled={pending || Boolean(activeAttempt)}
            inputMode="decimal"
            onChange={(event) => setStake(event.target.value)}
            type="text"
            value={stake}
          />
        </label>
        <p className={stakeError ? "field-error" : "field-help"} id="stake-help">
          {stakeError ?? `Possible return on a match: R${(stakeNumber * 3).toFixed(2)}`}
        </p>
      </section>

      {pending && (
        <div className="settling" role="status">
          <span className="settling-dot" aria-hidden="true" />
          Server is settling your bet…
        </div>
      )}

      {error && (
        <div className="inline-message error-message" role="alert">
          <strong>{activeAttempt ? "Result not confirmed" : "Bet not placed"}</strong>
          <span>{error}</span>
        </div>
      )}

      {result && revealed && (
        <div
          className={`inline-message result-message ${result.is_win ? "win" : "loss"}`}
          role="status"
          aria-live="polite"
        >
          <strong>{result.is_win ? "You matched" : "No match this time"}</strong>
          <span>
            Drawn colour: {colorLabels[result.drawn_color]}. {result.is_win
              ? `R${result.payout.toFixed(2)} returned to your wallet.`
              : `R${result.stake.toFixed(2)} stake settled.`}
          </span>
          <small>Bet reference #{playResponse?.bet_id}</small>
        </div>
      )}

      {!telegram.MainButton && (
        <button
          className="fallback-primary"
          disabled={!canSubmit}
          onClick={submit}
          type="button"
        >
          {pending
            ? "Settling…"
            : activeAttempt
              ? "Check result"
              : `Bet R${stake || "0"}`}
        </button>
      )}
    </main>
  );
}
