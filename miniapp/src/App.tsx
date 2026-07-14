import { useCallback, useEffect, useMemo, useState } from "react";

import { ColorGame } from "./components/ColorGame";
import { Lobby } from "./components/Lobby";
import {
  ApiError,
  MiniAppApiClient,
  type GameConfig,
  type MiniAppConfig,
  type MiniAppUser,
} from "./services/api";
type Screen = "lobby" | "color";

function LoadingScreen() {
  return (
    <main className="state-screen" aria-busy="true" aria-label="Loading MyKasiBets">
      <div className="brand-mark" aria-hidden="true">MK</div>
      <div className="skeleton-line wide" />
      <div className="skeleton-line" />
    </main>
  );
}

function MessageScreen({ title, message }: { title: string; message: string }) {
  return (
    <main className="state-screen">
      <div className="brand-mark" aria-hidden="true">MK</div>
      <h1>{title}</h1>
      <p>{message}</p>
    </main>
  );
}

export default function App() {
  const telegram = window.Telegram?.WebApp;
  const [config, setConfig] = useState<MiniAppConfig | null>(null);
  const [user, setUser] = useState<MiniAppUser | null>(null);
  const [screen, setScreen] = useState<Screen>(
    telegram?.initDataUnsafe?.start_param === "color" ? "color" : "lobby",
  );
  const [fatalError, setFatalError] = useState<{ title: string; message: string } | null>(null);
  const api = useMemo(
    () => (telegram?.initData ? new MiniAppApiClient(telegram.initData) : null),
    [telegram],
  );

  useEffect(() => {
    if (!telegram) return;
    telegram.ready();
    telegram.expand();
    telegram.disableVerticalSwipes?.();
    const applyTheme = () => {
      document.documentElement.dataset.theme = telegram.colorScheme ?? "light";
    };
    applyTheme();
    telegram.onEvent("themeChanged", applyTheme);
    return () => {
      telegram.offEvent("themeChanged", applyTheme);
      telegram.enableVerticalSwipes?.();
    };
  }, [telegram]);

  useEffect(() => {
    if (!api) return;
    let active = true;
    Promise.all([api.getConfig(), api.getMe()])
      .then(([nextConfig, nextUser]) => {
        if (!active) return;
        setConfig(nextConfig);
        setUser(nextUser);
      })
      .catch((error: unknown) => {
        if (!active) return;
        if (error instanceof ApiError && error.status === 403) {
          setFatalError({
            title: "Account unavailable",
            message: "Contact support if you believe this is a mistake.",
          });
          return;
        }
        setFatalError({
          title: "Could not load your games",
          message: "Check your connection, then reopen MyKasiBets from Telegram.",
        });
      });
    return () => {
      active = false;
    };
  }, [api]);

  useEffect(() => {
    if (!api) return;
    const refreshBalance = () => {
      if (document.visibilityState !== "visible") return;
      api.getMe().then(setUser).catch(() => undefined);
    };
    window.addEventListener("focus", refreshBalance);
    document.addEventListener("visibilitychange", refreshBalance);
    return () => {
      window.removeEventListener("focus", refreshBalance);
      document.removeEventListener("visibilitychange", refreshBalance);
    };
  }, [api]);

  const openLobby = useCallback(() => setScreen("lobby"), []);

  if (!telegram || !telegram.initData) {
    return (
      <MessageScreen
        title="Open in Telegram"
        message="This game uses Telegram to verify your account. Open MyKasiBets from the bot menu."
      />
    );
  }
  if (fatalError) return <MessageScreen {...fatalError} />;
  if (!api || !config || !user) return <LoadingScreen />;

  const colorConfig = config.games.find((game): game is GameConfig => game.id === "color");
  if (!colorConfig) {
    return <MessageScreen title="Game unavailable" message="The Colour Game configuration is missing." />;
  }

  return (
    <div className="app-shell">
      <div className="balance-bar" aria-label={`Wallet balance R${user.balance}`}>
        <span>MyKasiBets</span>
        <strong><small>Balance</small> R{user.balance}</strong>
      </div>
      {screen === "lobby" ? (
        <Lobby games={config.games} onOpenColor={() => setScreen("color")} />
      ) : (
        <ColorGame
          api={api}
          config={colorConfig}
          key={user.id}
          onBack={openLobby}
          onBalanceChange={(balance) => setUser((current) => current ? { ...current, balance } : current)}
          telegram={telegram}
          userId={user.id}
        />
      )}
    </div>
  );
}
