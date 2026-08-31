import { createContext, useContext, useState, useEffect } from "react";
import type { ReactNode } from "react";

interface WarehouseContextType {
  selectedWarehouseId: string | null;
  setSelectedWarehouseId: (id: string | null) => void;
}

const WarehouseContext = createContext<WarehouseContextType | undefined>(undefined);

export function WarehouseProvider({ children }: { children: ReactNode }) {
  const [selectedWarehouseId, setSelectedWarehouseId] = useState<string | null>(null);

  // We persist this in localStorage so it remembers the user's choice across reloads.
  useEffect(() => {
    const savedWarehouseId = localStorage.getItem("aaram_selected_warehouse_id");
    if (savedWarehouseId) {
      setSelectedWarehouseId(savedWarehouseId);
    }
  }, []);

  const handleSetSelectedWarehouseId = (id: string | null) => {
    setSelectedWarehouseId(id);
    if (id) {
      localStorage.setItem("aaram_selected_warehouse_id", id);
    } else {
      localStorage.removeItem("aaram_selected_warehouse_id");
    }
  };

  return (
    <WarehouseContext.Provider 
      value={{ 
        selectedWarehouseId, 
        setSelectedWarehouseId: handleSetSelectedWarehouseId 
      }}
    >
      {children}
    </WarehouseContext.Provider>
  );
}

export function useWarehouse() {
  const context = useContext(WarehouseContext);
  if (context === undefined) {
    throw new Error("useWarehouse must be used within a WarehouseProvider");
  }
  return context;
}
