export function PillButton({
  children,
  variant = "filled",
  href,
  onClick,
}: {
  children: React.ReactNode;
  variant?: "filled" | "ghost";
  href?: string;
  onClick?: () => void;
}) {
  const base =
    "inline-flex items-center justify-center rounded-full px-6 py-2.5 text-sm font-medium font-body tracking-wide transition-opacity hover:opacity-80";
  const styles =
    variant === "filled"
      ? "bg-obsidian text-eggshell shadow-button"
      : "bg-white text-obsidian border border-chalk shadow-button";

  if (href) {
    return (
      <a href={href} className={`${base} ${styles}`}>
        {children}
      </a>
    );
  }

  return (
    <button onClick={onClick} className={`${base} ${styles}`}>
      {children}
    </button>
  );
}
