import Link from "next/link";

export default function Home() {
  return (
    <div className="min-h-screen bg-zinc-50 dark:bg-zinc-900">
      <div className="max-w-4xl mx-auto px-4 py-16">
        <header className="text-center mb-16">
          <h1 className="text-4xl font-bold text-zinc-900 dark:text-white mb-4">
            INHEIF Label SaaS
          </h1>
          <p className="text-xl text-zinc-600 dark:text-zinc-400">
            Professional label printing for the beverage industry
          </p>
        </header>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Beer Labels */}
          <Link
            href="/beer"
            className="group bg-white dark:bg-zinc-800 rounded-xl p-8 shadow-sm hover:shadow-md transition-all border border-zinc-200 dark:border-zinc-700 hover:border-amber-500"
          >
            <div className="text-4xl mb-4">🍺</div>
            <h2 className="text-xl font-semibold text-zinc-900 dark:text-white mb-2 group-hover:text-amber-600">
              Beer Labels
            </h2>
            <p className="text-zinc-600 dark:text-zinc-400 mb-4">
              Labels for cans and bottles. Standard Dutch formats from 25cl to 50cl.
            </p>
            <div className="flex flex-wrap gap-2">
              <span className="text-xs px-2 py-1 bg-amber-100 dark:bg-amber-900/30 text-amber-700 dark:text-amber-300 rounded">
                25cl Slim
              </span>
              <span className="text-xs px-2 py-1 bg-amber-100 dark:bg-amber-900/30 text-amber-700 dark:text-amber-300 rounded">
                33cl Standard
              </span>
              <span className="text-xs px-2 py-1 bg-amber-100 dark:bg-amber-900/30 text-amber-700 dark:text-amber-300 rounded">
                50cl Standard
              </span>
            </div>
          </Link>

          {/* Generic Labels - Coming Soon */}
          <div className="bg-white dark:bg-zinc-800 rounded-xl p-8 shadow-sm border border-zinc-200 dark:border-zinc-700 opacity-60">
            <div className="text-4xl mb-4">🏷️</div>
            <h2 className="text-xl font-semibold text-zinc-900 dark:text-white mb-2">
              Custom Labels
            </h2>
            <p className="text-zinc-600 dark:text-zinc-400 mb-4">
              Custom dimensions for any product. Upload your design and get a quote.
            </p>
            <span className="text-xs px-2 py-1 bg-zinc-200 dark:bg-zinc-700 text-zinc-500 dark:text-zinc-400 rounded">
              Coming Soon
            </span>
          </div>

          {/* Wine Labels - Coming Soon */}
          <div className="bg-white dark:bg-zinc-800 rounded-xl p-8 shadow-sm border border-zinc-200 dark:border-zinc-700 opacity-60">
            <div className="text-4xl mb-4">🍷</div>
            <h2 className="text-xl font-semibold text-zinc-900 dark:text-white mb-2">
              Wine Labels
            </h2>
            <p className="text-zinc-600 dark:text-zinc-400 mb-4">
              Premium labels for wine bottles. Front, back, and neck labels.
            </p>
            <span className="text-xs px-2 py-1 bg-zinc-200 dark:bg-zinc-700 text-zinc-500 dark:text-zinc-400 rounded">
              Coming Soon
            </span>
          </div>

          {/* Spirits Labels - Coming Soon */}
          <div className="bg-white dark:bg-zinc-800 rounded-xl p-8 shadow-sm border border-zinc-200 dark:border-zinc-700 opacity-60">
            <div className="text-4xl mb-4">🥃</div>
            <h2 className="text-xl font-semibold text-zinc-900 dark:text-white mb-2">
              Spirits Labels
            </h2>
            <p className="text-zinc-600 dark:text-zinc-400 mb-4">
              Labels for spirits and liquor bottles. Various shapes and sizes.
            </p>
            <span className="text-xs px-2 py-1 bg-zinc-200 dark:bg-zinc-700 text-zinc-500 dark:text-zinc-400 rounded">
              Coming Soon
            </span>
          </div>
        </div>

        {/* Features */}
        <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-6 text-center">
          <div>
            <div className="text-2xl mb-2">🎨</div>
            <h3 className="font-medium text-zinc-900 dark:text-white">CMYK Print Ready</h3>
            <p className="text-sm text-zinc-500 dark:text-zinc-400">Professional color accuracy</p>
          </div>
          <div>
            <div className="text-2xl mb-2">💧</div>
            <h3 className="font-medium text-zinc-900 dark:text-white">Waterproof Options</h3>
            <p className="text-sm text-zinc-500 dark:text-zinc-400">Perfect for chilled beverages</p>
          </div>
          <div>
            <div className="text-2xl mb-2">🌱</div>
            <h3 className="font-medium text-zinc-900 dark:text-white">Eco-Friendly</h3>
            <p className="text-sm text-zinc-500 dark:text-zinc-400">Biodegradable substrates available</p>
          </div>
        </div>

        <footer className="mt-16 text-center text-sm text-zinc-400 dark:text-zinc-500">
          Powered by OGOS Label Printing
        </footer>
      </div>
    </div>
  );
}
