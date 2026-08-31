import { useEffect } from "react";
import { useGetWarehouses } from "@/api/warehouses";
import { useWarehouse } from "@/contexts/WarehouseContext";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { MapPin, Loader2 } from "lucide-react";

export function WarehouseSelector() {
  const { data: warehouses, isLoading, error } = useGetWarehouses();
  const { selectedWarehouseId, setSelectedWarehouseId } = useWarehouse();

  useEffect(() => {
    // Auto-select the first warehouse if none is selected and data is available
    if (warehouses && warehouses.length > 0 && !selectedWarehouseId) {
      setSelectedWarehouseId(warehouses[0].id);
    }
  }, [warehouses, selectedWarehouseId, setSelectedWarehouseId]);

  if (isLoading) {
    return (
      <div className="flex items-center gap-2 px-3 py-2 text-sm text-slate-400">
        <Loader2 className="h-4 w-4 animate-spin" />
        <span>Loading...</span>
      </div>
    );
  }

  if (error || !warehouses || warehouses.length === 0) {
    return (
      <div className="flex items-center gap-2 px-3 py-2 text-sm text-amber-500">
        <MapPin className="h-4 w-4" />
        <span>No Warehouses Found</span>
      </div>
    );
  }

  return (
    <div className="flex items-center gap-2">
      <Select
        value={selectedWarehouseId || ""}
        onValueChange={(val) => setSelectedWarehouseId(val)}
      >
        <SelectTrigger className="w-[200px] bg-slate-900 border-slate-700 text-slate-200 h-9">
          <div className="flex items-center gap-2">
            <MapPin className="h-4 w-4 text-slate-400" />
            <SelectValue placeholder="Select Warehouse" />
          </div>
        </SelectTrigger>
        <SelectContent>
          {warehouses.map((w) => (
            <SelectItem key={w.id} value={w.id}>
              {w.warehouse_name}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  );
}
