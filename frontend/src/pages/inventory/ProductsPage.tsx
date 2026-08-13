import { useState, useMemo, useRef } from "react"
import { useSKUs, useCreateSKU, useUpdateSKU, useCreateInventoryItem, useUnitsOfMeasure, type SKUResponse } from "@/api/masters"
import { useInventoryBalances } from "@/api/inventory"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Search, X, Package, AlertCircle, Plus, Upload } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import Papa from "papaparse"
import { ExecutiveSummary } from "@/components/products/ExecutiveSummary"
import { InventoryItemFormDialog } from "@/components/products/InventoryItemFormDialog"
import { ProductWorkspaceDialog } from "@/components/products/ProductWorkspaceDialog"
import { formatQuantityValue } from "@/lib/utils"

export function ProductsPage() {
  const { data: skus, isLoading: isLoadingSkus } = useSKUs()
  const { data: balances, isLoading: isLoadingBalances } = useInventoryBalances()
  const { data: uoms } = useUnitsOfMeasure()
  
  const [searchQuery, setSearchQuery] = useState("")
  const [activeTab, setActiveTab] = useState("All")
  const [selectedCategory, setSelectedCategory] = useState("All")
  const [selectedSubcategory, setSelectedSubcategory] = useState("All")
  const [selectedSku, setSelectedSku] = useState<SKUResponse | null>(null)
  
  type SortOption = "name_asc" | "name_desc" | "price_asc" | "price_desc" | "stock_asc" | "stock_desc" | "updated_desc"
  const [sortBy, setSortBy] = useState<SortOption>("updated_desc")
  const [isAddDialogOpen, setIsAddDialogOpen] = useState(false)
  
  const createMutation = useCreateSKU()
  const createInventoryItemMutation = useCreateInventoryItem()
  const updateMutation = useUpdateSKU()
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [isImporting, setIsImporting] = useState(false)

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    setIsImporting(true)
    Papa.parse(file, {
      header: true,
      skipEmptyLines: true,
      complete: async (results) => {
        try {
          let updated = 0
          let created = 0
          for (const row of results.data as any[]) {
            const skuId = row["Sku Id"] || row["sku_code"];
            const name = row["Name"] || row["new_product_name"];
            const category = row["Product Type"] || row["new_category_name"];
            if (!skuId || !name) continue;
            
            const existingSku = skus?.find(s => s.item_code === skuId || s.sku_code === skuId)

            if (existingSku) {
              const payload = {
                color: row["Colour"] || row.color,
                size: row["Size"] || row.size,
                material: row["attr_Material"] || row.material,
                thread_count: row["attr_Thread Count (TC)"] || row.thread_count,
              }
              await updateMutation.mutateAsync({ id: existingSku.id, data: payload })
              updated++
            } else {
              const payload = {
                item_type: "FINISHED_GOODS",
                new_category_name: category || "Uncategorized",
                new_product_name: name,
                item_code: skuId,
                sku_code: skuId,
                color: row["Colour"] || row.color,
                size: row["Size"] || row.size,
                material: row["attr_Material"] || row.material,
                thread_count: row["attr_Thread Count (TC)"] || row.thread_count,
              }
              await createInventoryItemMutation.mutateAsync(payload)
              created++
            }
          }
          alert(`Import complete: ${created} created, ${updated} updated.`)
        } catch (error) {
          console.error("Import failed:", error)
          alert("Import failed. Check console for details.")
        } finally {
          setIsImporting(false)
          if (fileInputRef.current) fileInputRef.current.value = ""
        }
      }
    })
  }

  const isLoading = isLoadingSkus || isLoadingBalances

  const getInventoryCount = (skuId: string) => {
    if (!balances) return 0;
    const skuBalances = balances.filter((b: any) => b.sku_id === skuId);
    return skuBalances.reduce((total: number, b: any) => total + (Number(b.balance) || 0), 0);
  }

  const getInventoryConfidence = (skuId: string) => {
    if (!balances) return 100;
    const skuBalances = balances.filter((b: any) => b.sku_id === skuId);
    if (skuBalances.length === 0) return 100;
    return skuBalances[0].confidence_score ?? 100;
  }

  // Derive available categories and brands from current SKUs
  const availableCategories = useMemo(() => {
    if (!skus) return []
    const set = new Set(skus.map(s => s.product?.product_type).filter(Boolean))
    return Array.from(set).sort() as string[]
  }, [skus])

  const availableBrands = useMemo(() => {
    if (!skus) return []
    const set = new Set(skus.map(s => s.product?.brand).filter(Boolean))
    return Array.from(set).sort() as string[]
  }, [skus])

  // Filter Logic
  const filteredSkus = useMemo(() => {
    if (!skus) return []

    return skus.filter(sku => {
      // 1. Search (Global)
      if (searchQuery) {
        const q = searchQuery.toLowerCase()
        const matchesSearch = 
          sku?.sku_code?.toLowerCase().includes(q) ||
          sku?.product?.product_name?.toLowerCase().includes(q) ||
          sku?.product?.brand?.toLowerCase().includes(q)
        if (!matchesSearch) return false
      }

      // 2. Tab Filter
      if (activeTab !== "All") {
        if (!sku.product?.item_type || sku.product.item_type !== activeTab) return false
      }

      // 3. Category
      if (selectedCategory !== "All") {
        if (!sku.product?.product_type || sku.product.product_type !== selectedCategory) return false
      }

      // 4. Subcategory (Brand)
      if (selectedSubcategory !== "All") {
        if (!sku.product?.brand || sku.product.brand !== selectedSubcategory) return false
      }

      return true
    }).sort((a, b) => {
      const aStock = getInventoryCount(a.id)
      const bStock = getInventoryCount(b.id)
      const aPrice = a.pricing?.selling_price || 0
      const bPrice = b.pricing?.selling_price || 0
      const aName = a.product?.product_name || a.sku_code || ""
      const bName = b.product?.product_name || b.sku_code || ""

      switch (sortBy) {
        case "name_asc": return aName.localeCompare(bName)
        case "name_desc": return bName.localeCompare(aName)
        case "price_asc": return aPrice - bPrice
        case "price_desc": return bPrice - aPrice
        case "stock_asc": return aStock - bStock
        case "stock_desc": return bStock - aStock
        case "updated_desc":
        default:
          return new Date(b.updated_on || 0).getTime() - new Date(a.updated_on || 0).getTime()
      }
    })
  }, [skus, searchQuery, activeTab, selectedCategory, selectedSubcategory, balances, sortBy])

  // Calculate active UI filters count
  const activeUiFiltersCount = 
    (activeTab !== "All" ? 1 : 0) +
    (selectedCategory !== "All" ? 1 : 0) + 
    (selectedSubcategory !== "All" ? 1 : 0)

  return (
    <div className="space-y-6 animate-in fade-in duration-500 pb-12">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-slate-900">Inventory Master</h1>
        <p className="text-slate-500">Universal Inventory Item Management</p>
      </div>

      {skus && balances && (
        <ExecutiveSummary skus={skus} balances={balances} />
      )}

      {/* Main Layout */}
      <div className="flex flex-col gap-6 items-stretch mt-6">
        
        {/* Top navigation tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="bg-slate-100 border p-1 rounded-lg">
            <TabsTrigger value="All">All</TabsTrigger>
            <TabsTrigger value="FINISHED_GOODS">Finished Goods</TabsTrigger>
            <TabsTrigger value="RAW_MATERIAL">Raw Materials</TabsTrigger>
            <TabsTrigger value="CONSUMABLE">Consumables</TabsTrigger>
            <TabsTrigger value="PACKAGING">Packaging</TabsTrigger>
            <TabsTrigger value="SEMI_FINISHED_GOODS">Semi-Finished Goods</TabsTrigger>
          </TabsList>
        </Tabs>

        {/* Main Content Area */}
        <div className="flex-1 flex flex-col min-w-0 space-y-4">
          
          {/* Top Bar: Search & Actions */}
          <div className="flex flex-col space-y-4">
            <div className="flex items-center gap-4">
              <div className="relative flex-1">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-slate-400" />
                <input 
                  type="text" 
                  placeholder="Search products by SKU, Name, Brand, or Code..." 
                  className="w-full pl-10 pr-4 py-3 bg-white border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 shadow-sm"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
              </div>
              
              <div className="flex items-center gap-3 shrink-0">
                <select 
                  className="h-[46px] px-3 py-2 bg-white border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 shadow-sm text-slate-700 font-medium"
                  value={selectedCategory}
                  onChange={(e) => setSelectedCategory(e.target.value)}
                >
                  <option value="All">Category</option>
                  {availableCategories.map(c => <option key={c} value={c}>{c}</option>)}
                </select>
                
                <select 
                  className="h-[46px] px-3 py-2 bg-white border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 shadow-sm text-slate-700 font-medium"
                  value={selectedSubcategory}
                  onChange={(e) => setSelectedSubcategory(e.target.value)}
                >
                  <option value="All">Subcategory</option>
                  {availableBrands.map(b => <option key={b} value={b}>{b}</option>)}
                </select>
                <select 
                  className="h-[46px] px-3 py-2 bg-white border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 shadow-sm text-slate-700 font-medium"
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value as SortOption)}
                >
                  <option value="updated_desc">Recently Updated</option>
                  <option value="name_asc">Name (A-Z)</option>
                  <option value="name_desc">Name (Z-A)</option>
                  <option value="price_asc">Price (Low to High)</option>
                  <option value="price_desc">Price (High to Low)</option>
                  <option value="stock_asc">Stock (Lowest)</option>
                  <option value="stock_desc">Stock (Highest)</option>
                </select>
                
                <Button className="h-[46px] gap-2 bg-indigo-600 hover:bg-indigo-700" onClick={() => setIsAddDialogOpen(true)}>
                  <Plus className="h-4 w-4" /> Add Item
                </Button>
                
                <input 
                  type="file" 
                  accept=".csv" 
                  className="hidden" 
                  ref={fileInputRef} 
                  onChange={handleFileUpload} 
                />
                <Button 
                  variant="outline" 
                  className="h-[46px] gap-2 border-slate-200 text-slate-700 hover:bg-slate-50" 
                  onClick={() => fileInputRef.current?.click()}
                  disabled={isImporting}
                >
                  <Upload className="h-4 w-4" /> {isImporting ? "Importing..." : "Import CSV"}
                </Button>
              </div>
            </div>
            
            {/* Active Filters Bar */}
            <div className="flex items-center justify-between min-h-[32px]">
              <div className="flex flex-wrap items-center gap-2">
                <span className="text-sm text-slate-500 font-medium">Showing {filteredSkus.length} of {skus?.length || 0} Products</span>
                
                {activeUiFiltersCount > 0 && <span className="text-slate-300">|</span>}
                
                {activeTab !== "All" && (
                  <Badge variant="secondary" className="bg-white border text-slate-700 flex items-center gap-1 font-normal">
                    {activeTab.replace('_', ' ')} <X className="h-3 w-3 cursor-pointer hover:text-rose-500" onClick={() => setActiveTab("All")} />
                  </Badge>
                )}

                {selectedCategory !== "All" && (
                  <Badge variant="secondary" className="bg-white border text-slate-700 flex items-center gap-1 font-normal">
                    {selectedCategory} <X className="h-3 w-3 cursor-pointer hover:text-rose-500" onClick={() => setSelectedCategory("All")} />
                  </Badge>
                )}
                
                {selectedSubcategory !== "All" && (
                  <Badge variant="secondary" className="bg-white border text-slate-700 flex items-center gap-1 font-normal">
                    {selectedSubcategory} <X className="h-3 w-3 cursor-pointer hover:text-rose-500" onClick={() => setSelectedSubcategory("All")} />
                  </Badge>
                )}
                
                {activeUiFiltersCount > 0 && (
                  <button onClick={() => { setActiveTab("All"); setSelectedCategory("All"); setSelectedSubcategory("All") }} className="text-xs text-indigo-600 hover:underline ml-2">
                    Clear Filters
                  </button>
                )}
              </div>
            </div>
          </div>

          {/* Product List */}
          <Card className="border-slate-200 shadow-sm flex-1">
            <CardContent className="p-0">
              {isLoading ? (
                <div className="p-12 text-center text-slate-400">Loading Product Catalog...</div>
              ) : filteredSkus.length > 0 ? (
                <div className="overflow-x-auto">
                  <table className="w-full text-sm text-left">
                    <thead className="bg-slate-50/50 text-slate-500 border-b">
                      <tr>
                        <th className="px-4 py-3 font-medium">Item Identity</th>
                        <th className="px-4 py-3 font-medium">Type & Category</th>
                        <th className="px-4 py-3 font-medium text-right">UoM</th>
                        <th className="px-4 py-3 font-medium text-right w-48">Inventory Count</th>
                        <th className="px-4 py-3 font-medium text-center">Confidence</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100">
                      {filteredSkus.map(sku => {
                        const count = getInventoryCount(sku.id)
                        const confidenceScore = getInventoryConfidence(sku.id)
                        
                        return (
                          <tr 
                            key={sku.id} 
                            className="hover:bg-slate-50/50 transition-colors cursor-pointer group"
                            onClick={() => setSelectedSku(sku)}
                          >
                            <td className="px-4 py-4">
                              <div className="flex items-center gap-4">
                                <div className="h-12 w-12 rounded bg-slate-100 border flex items-center justify-center overflow-hidden flex-shrink-0">
                                  {sku.images && sku.images.length > 0 ? (
                                    <img src={sku.images[0].image_url} alt={sku.product?.product_name} className="h-full w-full object-cover" />
                                  ) : (
                                    <Package className="h-5 w-5 text-slate-300" />
                                  )}
                                </div>
                                <div>
                                  <div className="font-medium text-slate-900 line-clamp-1 max-w-[250px]" title={sku.product?.product_name}>
                                    {sku.product?.product_name || "Unknown Item"}
                                  </div>
                                  <div className="font-mono text-xs text-slate-500 mt-1">{sku.item_code}</div>
                                </div>
                              </div>
                            </td>
                            <td className="px-4 py-4">
                              <div className="flex flex-col gap-1.5">
                                <Badge variant="secondary" className="w-fit bg-slate-100 text-slate-600 font-normal">
                                  {sku.product?.item_type?.replace('_', ' ') || 'FINISHED GOODS'}
                                </Badge>
                                {sku.product?.item_type === 'FINISHED_GOODS' && (
                                  sku.has_bom ? (
                                    <Badge variant="outline" className="w-fit bg-emerald-50 text-emerald-700 border-emerald-200 font-normal flex items-center gap-1 text-[10px] px-1.5 py-0">
                                      ✓ BOM Configured
                                    </Badge>
                                  ) : (
                                    <Badge variant="outline" className="w-fit bg-rose-50 text-rose-700 border-rose-200 font-normal flex items-center gap-1 text-[10px] px-1.5 py-0">
                                      <AlertCircle className="h-3 w-3" /> Missing BOM
                                    </Badge>
                                  )
                                )}
                                {sku.product?.product_type && (
                                  <span className="text-xs text-slate-500">{sku.product.product_type}</span>
                                )}
                              </div>
                            </td>
                            <td className="px-4 py-4 text-right">
                              <span className="font-medium text-slate-900">{uoms?.find(u => u.id === (sku as any).uom_id)?.short_name || "-"}</span>
                            </td>
                            <td className="px-4 py-4 text-right">
                              <div className="flex justify-end">
                                <Badge variant="outline" className={`font-mono text-base px-3 py-1 border-2 ${count > 0 ? 'bg-indigo-50 text-indigo-700 border-indigo-200' : count < 0 ? 'bg-rose-50 text-rose-700 border-rose-200' : 'bg-slate-50 text-slate-600 border-slate-200'}`}>
                                  {formatQuantityValue(count, uoms?.find(u => u.id === (sku as any).uom_id)?.unit_type)} {uoms?.find(u => u.id === (sku as any).uom_id)?.short_name || "units"}
                                </Badge>
                              </div>
                            </td>
                            <td className="px-4 py-4 text-center">
                              <div className="flex items-center justify-center gap-1.5">
                                <div className={`h-2 w-2 rounded-full ${confidenceScore > 90 ? 'bg-emerald-500' : confidenceScore > 70 ? 'bg-amber-400' : 'bg-rose-500'}`}></div>
                                <span className={`text-xs font-medium ${confidenceScore > 90 ? 'text-emerald-700' : confidenceScore > 70 ? 'text-amber-700' : 'text-rose-700'}`}>{confidenceScore}%</span>
                              </div>
                            </td>
                          </tr>
                        )
                      })}
                    </tbody>
                  </table>
                </div>
              ) : (
                <div className="p-16 flex flex-col items-center justify-center text-slate-400 bg-slate-50/30">
                  <div className="h-16 w-16 bg-slate-100 rounded-full flex items-center justify-center mb-4 border">
                    <Search className="h-6 w-6 text-slate-300" />
                  </div>
                  <h3 className="text-lg font-medium text-slate-900">No products match your current filters.</h3>
                  <p className="text-sm mt-1 mb-6">Try removing some filters or searching differently.</p>
                  <button onClick={() => { setActiveTab("All"); setSelectedCategory("All"); setSelectedSubcategory("All") }} className="px-4 py-2 bg-white border border-slate-200 rounded-md text-sm font-medium hover:bg-slate-50 shadow-sm text-slate-700">
                    Clear All Filters
                  </button>
                </div>
              )}
            </CardContent>
          </Card>

        </div>
      </div>

      <ProductWorkspaceDialog 
        sku={selectedSku} 
        open={!!selectedSku} 
        onOpenChange={(open) => !open && setSelectedSku(null)} 
        inventoryCount={selectedSku ? getInventoryCount(selectedSku.id) : 0}
      />
      
      <InventoryItemFormDialog 
        open={isAddDialogOpen} 
        onOpenChange={setIsAddDialogOpen} 
      />
    </div>
  )
}
