import Image from "next/image";

export function AppScreenshot({
  src,
  alt,
  label,
}: {
  src: string;
  alt: string;
  label?: string;
}) {
  return (
    <div className="flex flex-col items-center gap-3">
      <div className="relative w-[280px] rounded-[36px] bg-obsidian p-[8px] shadow-[0_20px_60px_rgba(0,0,0,0.3)]">
        <div className="rounded-[28px] overflow-hidden">
          <Image
            src={src}
            alt={alt}
            width={560}
            height={1218}
            className="w-full h-auto"
            priority
          />
        </div>
      </div>
      {label && (
        <span className="text-sm font-body font-medium text-gravel">
          {label}
        </span>
      )}
    </div>
  );
}
