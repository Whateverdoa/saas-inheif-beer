'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { beerApi, BeerLabelType, BeerSubstrate, BeerCategory } from '@/lib/api/beer'

export default function BeerLabelsPage() {
  const [categories, setCategories] = useState<BeerCategory[]>([])
  const [labelTypes, setLabelTypes] = useState<BeerLabelType[]>([])
  const [substrates, setSubstrates] = useState<BeerSubstrate[]>([])
  const [selectedCategory, setSelectedCategory] = useState<string>('')
  const [selectedLabelType, setSelectedLabelType] = useState<BeerLabelType | null>(null)
  const [selectedSubstrate, setSelectedSubstrate] = useState<BeerSubstrate | null>(null)
  const [quantity, setQuantity] = useState<number>(1000)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function loadData() {
      try {
        setLoading(true)
        const [cats, labels, subs] = await Promise.all([
          beerApi.getCategories(),
          beerApi.getLabelTypes(),
          beerApi.getSubstrates(),
        ])
        setCategories(cats)
        setLabelTypes(labels)
        setSubstrates(subs)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load data')
      } finally {
        setLoading(false)
      }
    }
    loadData()
  }, [])

  const filteredLabelTypes = selectedCategory
    ? labelTypes.filter(lt => lt.category === selectedCategory)
    : labelTypes

  const recommendedSubstrates = selectedLabelType
    ? substrates.filter(s => selectedLabelType.recommended_substrates.includes(s.name))
    : substrates

  if (loading) {
    return (
      <div className="min-h-screen bg-zinc-50 dark:bg-zinc-900 flex items-center justify-center">
        <div className="text-lg">Loading beer label options...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-zinc-50 dark:bg-zinc-900 flex items-center justify-center">
        <div className="text-red-500 text-lg">{error}</div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-zinc-50 dark:bg-zinc-900">
      <div className="max-w-6xl mx-auto px-4 py-8">
        <header className="mb-8">
          <Link href="/" className="text-amber-600 hover:text-amber-700 text-sm mb-2 inline-block">
            ← Back to Home
          </Link>
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-zinc-900 dark:text-white mb-2">
                🍺 Beer Label Orders
              </h1>
              <p className="text-zinc-600 dark:text-zinc-400">
                Select your label format, substrate, and quantity
              </p>
            </div>
            <Link
              href="/beer/compliance"
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-medium flex items-center gap-2"
            >
              🇪🇺 EU Compliance Text
            </Link>
          </div>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Step 1: Category & Label Type */}
          <div className="bg-white dark:bg-zinc-800 rounded-xl p-6 shadow-sm">
            <h2 className="text-lg font-semibold mb-4 text-zinc-900 dark:text-white">
              1. Select Label Format
            </h2>
            
            {/* Category Filter */}
            <div className="mb-4">
              <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-2">
                Category
              </label>
              <select
                value={selectedCategory}
                onChange={(e) => {
                  setSelectedCategory(e.target.value)
                  setSelectedLabelType(null)
                }}
                className="w-full px-3 py-2 border border-zinc-300 dark:border-zinc-600 rounded-lg bg-white dark:bg-zinc-700 text-zinc-900 dark:text-white"
              >
                <option value="">All Categories</option>
                {categories.map(cat => (
                  <option key={cat.value} value={cat.value}>
                    {cat.label}
                  </option>
                ))}
              </select>
            </div>

            {/* Label Types */}
            <div className="space-y-2 max-h-80 overflow-y-auto">
              {filteredLabelTypes.map(lt => (
                <button
                  key={lt.id}
                  onClick={() => setSelectedLabelType(lt)}
                  className={`w-full text-left p-3 rounded-lg border transition-colors ${
                    selectedLabelType?.id === lt.id
                      ? 'border-amber-500 bg-amber-50 dark:bg-amber-900/20'
                      : 'border-zinc-200 dark:border-zinc-600 hover:border-amber-300'
                  }`}
                >
                  <div className="font-medium text-zinc-900 dark:text-white">
                    {lt.name}
                  </div>
                  <div className="text-sm text-zinc-500 dark:text-zinc-400">
                    {lt.width_mm} × {lt.height_mm} mm
                  </div>
                  {lt.description && (
                    <div className="text-xs text-zinc-400 dark:text-zinc-500 mt-1">
                      {lt.description}
                    </div>
                  )}
                </button>
              ))}
            </div>
          </div>

          {/* Step 2: Substrate */}
          <div className="bg-white dark:bg-zinc-800 rounded-xl p-6 shadow-sm">
            <h2 className="text-lg font-semibold mb-4 text-zinc-900 dark:text-white">
              2. Select Substrate
            </h2>
            
            {selectedLabelType && (
              <div className="mb-4 p-3 bg-amber-50 dark:bg-amber-900/20 rounded-lg text-sm">
                <span className="font-medium">Recommended for {selectedLabelType.name}:</span>
                <div className="text-amber-700 dark:text-amber-300">
                  {selectedLabelType.recommended_substrates.join(', ')}
                </div>
              </div>
            )}

            <div className="space-y-2 max-h-96 overflow-y-auto">
              {(selectedLabelType ? recommendedSubstrates : substrates).map(sub => (
                <button
                  key={sub.code}
                  onClick={() => setSelectedSubstrate(sub)}
                  className={`w-full text-left p-3 rounded-lg border transition-colors ${
                    selectedSubstrate?.code === sub.code
                      ? 'border-amber-500 bg-amber-50 dark:bg-amber-900/20'
                      : 'border-zinc-200 dark:border-zinc-600 hover:border-amber-300'
                  }`}
                >
                  <div className="font-medium text-zinc-900 dark:text-white">
                    {sub.name}
                  </div>
                  <div className="flex gap-2 mt-1">
                    {sub.is_waterproof && (
                      <span className="text-xs px-2 py-0.5 bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300 rounded">
                        Waterproof
                      </span>
                    )}
                    {sub.is_biodegradable && (
                      <span className="text-xs px-2 py-0.5 bg-green-100 dark:bg-green-900 text-green-700 dark:text-green-300 rounded">
                        Eco-friendly
                      </span>
                    )}
                    <span className="text-xs px-2 py-0.5 bg-zinc-100 dark:bg-zinc-700 text-zinc-600 dark:text-zinc-300 rounded capitalize">
                      {sub.finish}
                    </span>
                  </div>
                  {sub.description && (
                    <div className="text-xs text-zinc-400 dark:text-zinc-500 mt-2">
                      {sub.description}
                    </div>
                  )}
                </button>
              ))}
            </div>
          </div>

          {/* Step 3: Summary & Order */}
          <div className="bg-white dark:bg-zinc-800 rounded-xl p-6 shadow-sm">
            <h2 className="text-lg font-semibold mb-4 text-zinc-900 dark:text-white">
              3. Order Summary
            </h2>

            {/* Quantity */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-2">
                Quantity
              </label>
              <input
                type="number"
                min="100"
                step="100"
                value={quantity}
                onChange={(e) => setQuantity(parseInt(e.target.value) || 100)}
                className="w-full px-3 py-2 border border-zinc-300 dark:border-zinc-600 rounded-lg bg-white dark:bg-zinc-700 text-zinc-900 dark:text-white"
              />
            </div>

            {/* Summary */}
            <div className="space-y-3 mb-6">
              <div className="flex justify-between text-sm">
                <span className="text-zinc-500 dark:text-zinc-400">Label Format:</span>
                <span className="font-medium text-zinc-900 dark:text-white">
                  {selectedLabelType?.name || '—'}
                </span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-zinc-500 dark:text-zinc-400">Dimensions:</span>
                <span className="font-medium text-zinc-900 dark:text-white">
                  {selectedLabelType 
                    ? `${selectedLabelType.width_mm} × ${selectedLabelType.height_mm} mm`
                    : '—'}
                </span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-zinc-500 dark:text-zinc-400">Substrate:</span>
                <span className="font-medium text-zinc-900 dark:text-white">
                  {selectedSubstrate?.name || '—'}
                </span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-zinc-500 dark:text-zinc-400">Quantity:</span>
                <span className="font-medium text-zinc-900 dark:text-white">
                  {quantity.toLocaleString()} labels
                </span>
              </div>
            </div>

            <hr className="my-4 border-zinc-200 dark:border-zinc-700" />

            {/* PDF Upload Placeholder */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-2">
                Upload Label Design (PDF)
              </label>
              <div className="border-2 border-dashed border-zinc-300 dark:border-zinc-600 rounded-lg p-6 text-center">
                <div className="text-zinc-400 dark:text-zinc-500">
                  <svg className="mx-auto h-12 w-12 mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                  </svg>
                  <p className="text-sm">Drag & drop PDF or click to browse</p>
                  <p className="text-xs mt-1">CMYK, 300 DPI, with bleed</p>
                </div>
                <input type="file" accept=".pdf" className="hidden" />
              </div>
            </div>

            {/* Order Button */}
            <button
              disabled={!selectedLabelType || !selectedSubstrate}
              className={`w-full py-3 px-4 rounded-lg font-medium transition-colors ${
                selectedLabelType && selectedSubstrate
                  ? 'bg-amber-500 hover:bg-amber-600 text-white'
                  : 'bg-zinc-200 dark:bg-zinc-700 text-zinc-400 cursor-not-allowed'
              }`}
            >
              Continue to Checkout
            </button>

            {(!selectedLabelType || !selectedSubstrate) && (
              <p className="text-xs text-zinc-400 dark:text-zinc-500 text-center mt-2">
                Select a label format and substrate to continue
              </p>
            )}
          </div>
        </div>

        {/* Label Types Reference Table */}
        <div className="mt-12 bg-white dark:bg-zinc-800 rounded-xl p-6 shadow-sm">
          <h2 className="text-lg font-semibold mb-4 text-zinc-900 dark:text-white">
            📏 Standard Beer Label Formats
          </h2>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-zinc-200 dark:border-zinc-700">
                  <th className="text-left py-2 px-3 font-medium text-zinc-500 dark:text-zinc-400">Format</th>
                  <th className="text-left py-2 px-3 font-medium text-zinc-500 dark:text-zinc-400">Dimensions</th>
                  <th className="text-left py-2 px-3 font-medium text-zinc-500 dark:text-zinc-400">Category</th>
                  <th className="text-left py-2 px-3 font-medium text-zinc-500 dark:text-zinc-400">Description</th>
                </tr>
              </thead>
              <tbody>
                {labelTypes.map(lt => (
                  <tr key={lt.id} className="border-b border-zinc-100 dark:border-zinc-700/50">
                    <td className="py-2 px-3 font-medium text-zinc-900 dark:text-white">{lt.name}</td>
                    <td className="py-2 px-3 text-zinc-600 dark:text-zinc-300">{lt.width_mm} × {lt.height_mm} mm</td>
                    <td className="py-2 px-3">
                      <span className="px-2 py-0.5 bg-zinc-100 dark:bg-zinc-700 rounded text-xs capitalize">
                        {lt.category.replace('_', ' ')}
                      </span>
                    </td>
                    <td className="py-2 px-3 text-zinc-500 dark:text-zinc-400">{lt.description || '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  )
}
