export interface TelegramMainButton {
  setText(text: string): void;
  show(): void;
  hide(): void;
  enable?(): void;
  disable?(): void;
  showProgress?(leaveActive?: boolean): void;
  hideProgress?(): void;
  onClick(callback: () => void): void;
  offClick(callback: () => void): void;
}

export interface TelegramBackButton {
  show(): void;
  hide(): void;
  onClick(callback: () => void): void;
  offClick(callback: () => void): void;
}

export interface TelegramWebApp {
  initData: string;
  initDataUnsafe?: { start_param?: string };
  colorScheme?: "light" | "dark";
  ready(): void;
  expand(): void;
  close(): void;
  disableVerticalSwipes?(): void;
  enableVerticalSwipes?(): void;
  onEvent(event: string, callback: () => void): void;
  offEvent(event: string, callback: () => void): void;
  MainButton?: TelegramMainButton;
  BackButton?: TelegramBackButton;
  HapticFeedback?: {
    impactOccurred(style: "light" | "medium" | "heavy"): void;
    notificationOccurred(type: "success" | "warning" | "error"): void;
  };
  showPopup?(params: {
    title?: string;
    message: string;
    buttons?: Array<{ id?: string; type?: string; text?: string }>;
  }): void;
}

declare global {
  interface Window {
    Telegram?: { WebApp?: TelegramWebApp };
  }
}
