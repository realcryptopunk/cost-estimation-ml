export function SectionLabel({ children }: { children: React.ReactNode }) {
  return (
    <p className="text-sm font-body font-normal text-gravel tracking-wide uppercase">
      {children}
    </p>
  );
}
