import type { GameConfig } from "../services/api";

interface LobbyProps {
  games: GameConfig[];
  onOpenColor(): void;
}

const gameDescriptions: Record<string, string> = {
  color: "Pick one of four colours. A match pays 3×.",
  wheel: "Choose a number from 1 to 12.",
  pick3: "Choose three unique numbers from 1 to 36.",
  football: "Answer yes or no on active football markets.",
};

export function Lobby({ games, onOpenColor }: LobbyProps) {
  return (
    <main className="screen" aria-labelledby="lobby-title">
      <header className="screen-heading">
        <p className="eyebrow">Games</p>
        <h1 id="lobby-title">Choose your game</h1>
        <p>Limits and outcomes come directly from the game server.</p>
      </header>

      <div className="game-list">
        {games.map((game, index) => {
          const isColor = game.id === "color";
          return (
            <button
              className="game-row"
              disabled={!isColor}
              key={game.id}
              onClick={isColor ? onOpenColor : undefined}
              type="button"
            >
              <span className="game-index" aria-hidden="true">
                {String(index + 1).padStart(2, "0")}
              </span>
              <span className="game-copy">
                <strong>{game.name}</strong>
                <span>{gameDescriptions[game.id]}</span>
                <small>
                  R{game.limits.minimum} to R{game.limits.maximum}
                </small>
              </span>
              <span className="game-status">
                {isColor ? "Play" : "Available in chat"}
              </span>
            </button>
          );
        })}
      </div>
    </main>
  );
}
