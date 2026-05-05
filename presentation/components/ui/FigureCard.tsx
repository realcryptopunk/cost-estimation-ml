import Image from "next/image";

export function FigureCard({
  src,
  alt,
  caption,
  width = 1000,
  height = 600,
}: {
  src: string;
  alt: string;
  caption?: string;
  width?: number;
  height?: number;
}) {
  return (
    <div className="rounded-2xl bg-white p-4 shadow-card">
      <Image
        src={src}
        alt={alt}
        width={width}
        height={height}
        className="w-full h-auto rounded-lg"
      />
      {caption && (
        <p className="mt-3 text-center text-sm font-body font-normal text-gravel">
          {caption}
        </p>
      )}
    </div>
  );
}
