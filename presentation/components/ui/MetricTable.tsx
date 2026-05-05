export function MetricTable({
  headers,
  rows,
  highlightRow,
}: {
  headers: string[];
  rows: (string | number)[][];
  highlightRow?: number;
}) {
  return (
    <div className="overflow-hidden rounded-2xl bg-white shadow-card">
      <table className="w-full text-left text-sm font-body">
        <thead>
          <tr className="border-b border-chalk">
            {headers.map((h) => (
              <th
                key={h}
                className="px-5 py-3 text-sm font-medium text-obsidian"
              >
                {h}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, i) => (
            <tr
              key={i}
              className={`border-b border-chalk last:border-0 ${
                i === highlightRow
                  ? "bg-obsidian text-eggshell"
                  : i % 2 === 1
                    ? "bg-powder"
                    : ""
              }`}
            >
              {row.map((cell, j) => (
                <td
                  key={j}
                  className={`px-5 py-3 ${j === 0 ? "font-medium" : "font-mono text-xs"}`}
                >
                  {cell}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
