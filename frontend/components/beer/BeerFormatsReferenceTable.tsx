import type { BeerLabelType } from "@/lib/api/beer"
import type { BeerToolMessages } from "@/lib/i18n/types"

export function BeerFormatsReferenceTable({
  labelTypes,
  t,
}: {
  labelTypes: BeerLabelType[]
  t: BeerToolMessages
}) {
  return (
    <div className="mt-12 bg-white dark:bg-zinc-800 rounded-xl p-6 shadow-sm border border-zinc-200/80 dark:border-zinc-700/80">
      <h2 className="text-lg font-semibold mb-4 text-zinc-900 dark:text-white">{t.refTitle}</h2>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-zinc-200 dark:border-zinc-700">
              <th className="text-left py-2 px-3 font-medium text-zinc-500 dark:text-zinc-400">
                {t.thFormat}
              </th>
              <th className="text-left py-2 px-3 font-medium text-zinc-500 dark:text-zinc-400">
                {t.thDimensions}
              </th>
              <th className="text-left py-2 px-3 font-medium text-zinc-500 dark:text-zinc-400">
                {t.thCategory}
              </th>
              <th className="text-left py-2 px-3 font-medium text-zinc-500 dark:text-zinc-400">
                {t.thDescription}
              </th>
            </tr>
          </thead>
          <tbody>
            {labelTypes.map((lt) => (
              <tr key={lt.id} className="border-b border-zinc-100 dark:border-zinc-700/50">
                <td className="py-2 px-3 font-medium text-zinc-900 dark:text-white">{lt.name}</td>
                <td className="py-2 px-3 text-zinc-600 dark:text-zinc-300">
                  {lt.width_mm} × {lt.height_mm} mm
                </td>
                <td className="py-2 px-3">
                  <span className="px-2 py-0.5 bg-zinc-100 dark:bg-zinc-700 rounded text-xs capitalize">
                    {lt.category.replace("_", " ")}
                  </span>
                </td>
                <td className="py-2 px-3 text-zinc-500 dark:text-zinc-400">{lt.description || "—"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
