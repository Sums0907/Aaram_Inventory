import { Search, X, Lock } from "lucide-react"
import { Badge } from "@/components/ui/badge"
import { Checkbox } from "@/components/ui/checkbox"
import { Label } from "@/components/ui/label"
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"
import { Slider } from "@/components/ui/slider"
import { Separator } from "@/components/ui/separator"
import { ScrollArea } from "@/components/ui/scroll-area"

export interface ProductFilters {
  itemTypes: string[]
  categories: string[]
  brands: string[]
  stockStatus: string
  priceRange: [number, number]
  productStatus: string
}

export const DEFAULT_FILTERS: ProductFilters = {
  itemTypes: [],
  categories: [],
  brands: [],
  stockStatus: "All Products",
  priceRange: [0, 10000],
  productStatus: "Active",
}

interface ProductFiltersSidebarProps {
  filters: ProductFilters
  setFilters: (filters: ProductFilters) => void
  availableCategories: string[]
  availableBrands: string[]
}

export function ProductFiltersSidebar({
  filters,
  setFilters,
  availableCategories,
  availableBrands
}: ProductFiltersSidebarProps) {
  
  const handleItemTypeChange = (itemType: string, checked: boolean) => {
    const newItemTypes = checked 
      ? [...filters.itemTypes, itemType]
      : filters.itemTypes.filter(t => t !== itemType)
    setFilters({ ...filters, itemTypes: newItemTypes })
  }

  const handleCategoryChange = (category: string, checked: boolean) => {
    const newCategories = checked 
      ? [...filters.categories, category]
      : filters.categories.filter(c => c !== category)
    setFilters({ ...filters, categories: newCategories })
  }

  const handleBrandChange = (brand: string, checked: boolean) => {
    const newBrands = checked
      ? [...filters.brands, brand]
      : filters.brands.filter(b => b !== brand)
    setFilters({ ...filters, brands: newBrands })
  }

  const clearFilters = () => {
    setFilters(DEFAULT_FILTERS)
  }

  return (
    <div className="w-64 flex-shrink-0 flex flex-col bg-white border border-slate-200 rounded-lg shadow-sm h-fit">
      <div className="p-4 border-b flex items-center justify-between bg-slate-50/50 rounded-t-lg">
        <h3 className="font-semibold text-slate-900">Filters</h3>
        <button 
          onClick={clearFilters}
          className="text-xs text-indigo-600 font-medium hover:text-indigo-800 transition-colors"
        >
          Clear All
        </button>
      </div>

      <ScrollArea className="h-[calc(100vh-280px)] min-h-[400px]">
        <div className="p-4 space-y-6">
          
          {/* 0. ITEM TYPE */}
          <div className="space-y-3">
            <h4 className="text-sm font-medium text-slate-900">Item Type</h4>
            <div className="space-y-2">
              {["FINISHED_GOODS", "RAW_MATERIAL", "CONSUMABLE", "PACKAGING_MATERIAL", "ASSET"].map(type => (
                <div key={type} className="flex items-center space-x-2">
                  <Checkbox 
                    id={`type-${type}`} 
                    checked={filters.itemTypes.includes(type)}
                    onCheckedChange={(c) => handleItemTypeChange(type, c as boolean)}
                  />
                  <Label htmlFor={`type-${type}`} className="text-sm font-normal text-slate-700 cursor-pointer">
                    {type.replace('_', ' ')}
                  </Label>
                </div>
              ))}
            </div>
          </div>

          <Separator />

          {/* 1. STOCK STATUS */}
          <div className="space-y-3">
            <h4 className="text-sm font-medium text-slate-900">Stock Status</h4>
            <RadioGroup 
              value={filters.stockStatus} 
              onValueChange={(val) => setFilters({ ...filters, stockStatus: val })}
              className="space-y-1"
            >
              {["All Products", "In Stock", "Low Stock", "Out of Stock", "Negative Stock"].map((status) => (
                <div key={status} className="flex items-center space-x-2">
                  <RadioGroupItem value={status} id={`stock-${status}`} />
                  <Label htmlFor={`stock-${status}`} className="text-sm font-normal text-slate-700 cursor-pointer">
                    {status}
                  </Label>
                </div>
              ))}
            </RadioGroup>
          </div>

          <Separator />

          {/* 2. PRODUCT STATUS */}
          <div className="space-y-3">
            <h4 className="text-sm font-medium text-slate-900">Product Status</h4>
            <RadioGroup 
              value={filters.productStatus} 
              onValueChange={(val) => setFilters({ ...filters, productStatus: val })}
              className="space-y-1"
            >
              {["Active", "Hidden", "Archived"].map((status) => (
                <div key={status} className="flex items-center space-x-2">
                  <RadioGroupItem value={status} id={`pstatus-${status}`} />
                  <Label htmlFor={`pstatus-${status}`} className="text-sm font-normal text-slate-700 cursor-pointer">
                    {status}
                  </Label>
                </div>
              ))}
            </RadioGroup>
          </div>

          <Separator />

          {/* 3. PRICE RANGE */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h4 className="text-sm font-medium text-slate-900">Selling Price</h4>
              <span className="text-xs text-slate-500 font-mono">
                ₹{filters.priceRange[0]} - ₹{filters.priceRange[1]}
              </span>
            </div>
            <Slider
              defaultValue={[0, 10000]}
              max={10000}
              step={100}
              value={filters.priceRange}
              onValueChange={(val) => setFilters({ ...filters, priceRange: val as [number, number] })}
              className="mt-2"
            />
          </div>

          <Separator />

          {/* 4. BRAND */}
          <div className="space-y-3">
            <h4 className="text-sm font-medium text-slate-900">Brand</h4>
            <div className="space-y-2">
              {availableBrands.map(brand => (
                <div key={brand} className="flex items-center space-x-2">
                  <Checkbox 
                    id={`brand-${brand}`} 
                    checked={filters.brands.includes(brand)}
                    onCheckedChange={(c) => handleBrandChange(brand, c as boolean)}
                  />
                  <Label htmlFor={`brand-${brand}`} className="text-sm font-normal text-slate-700 cursor-pointer">
                    {brand}
                  </Label>
                </div>
              ))}
            </div>
          </div>

          <Separator />

          {/* 5. CATEGORY */}
          <div className="space-y-3">
            <h4 className="text-sm font-medium text-slate-900">Category</h4>
            <div className="space-y-2">
              {availableCategories.map(category => (
                <div key={category} className="flex items-center space-x-2">
                  <Checkbox 
                    id={`cat-${category}`} 
                    checked={filters.categories.includes(category)}
                    onCheckedChange={(c) => handleCategoryChange(category, c as boolean)}
                  />
                  <Label htmlFor={`cat-${category}`} className="text-sm font-normal text-slate-700 cursor-pointer">
                    {category}
                  </Label>
                </div>
              ))}
            </div>
          </div>

          <Separator />

          {/* COMING SOON FILTERS */}
          <div className="space-y-4 opacity-50 pointer-events-none">
            <div className="flex items-center justify-between">
              <h4 className="text-sm font-medium text-slate-500">Product Attributes</h4>
              <Badge variant="outline" className="text-[10px] bg-slate-100 uppercase">Coming Soon</Badge>
            </div>
            <div className="space-y-2">
              {["Fabric", "Colour", "Pattern", "Size"].map(f => (
                <div key={f} className="flex items-center space-x-2">
                  <Lock className="h-3 w-3 text-slate-400" />
                  <Label className="text-sm font-normal text-slate-500">{f}</Label>
                </div>
              ))}
            </div>
          </div>

        </div>
      </ScrollArea>
    </div>
  )
}
