// @ts-nocheck
import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export const formatQuantityValue = (qty: number | string, unitType?: "INTEGER" | "DECIMAL" | string) => {
  const numQty = Number(qty);
  if (isNaN(numQty) || numQty === 0) return "0"
  
  if (!unitType || unitType === "INTEGER") {
    return Math.round(numQty).toString()
  }
  
  // DECIMAL type - strictly 2 decimal places (e.g. 14 -> 14.00, 14.5 -> 14.50)
  return numQty.toFixed(2)
}
