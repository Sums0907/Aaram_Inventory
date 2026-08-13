import { formatQuantityValue } from "@/lib/utils"
import { useState } from "react"
import { useTransformations } from "@/api/job-works"
import { useSKUs } from "@/api/masters"
import { useSuppliers } from "@/api/suppliers"
import { Button } from "@/components/ui/button"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Eye, ArrowRightLeft } from "lucide-react"

export function TransformationsPage() {
  const { data: transformationsData, isLoading } = useTransformations()
  const { data: skus } = useSKUs()
  const { data: suppliersData } = useSuppliers(0, 100)
  const transformations = transformationsData?.data || []

  const getSkuName = (id: string) => {
    const sku = skus?.find((s: any) => s.id === id)
    if (!sku) return id
    return `${sku.product?.product_name || "Unknown"} ${sku.item_code ? `(${sku.item_code})` : ""}`
  }

  const getSupplierName = (id?: string) => {
    if (!id) return "-"
    const supplier = suppliersData?.data?.find((s: any) => s.id === id)
    return supplier ? supplier.name : id
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Transformations</h1>
          <p className="text-sm text-slate-500">
            Audit log of all inventory conversions (Job Work, Manufacturing, Assembly).
          </p>
        </div>
        <div className="flex gap-2">
          {/* Action buttons could go here */}
        </div>
      </div>
      
      <div className="rounded-md border bg-white shadow-sm">
        <Table>
          <TableHeader>
            <TableRow className="bg-slate-50/50">
              <TableHead>Date</TableHead>
              <TableHead>Job Worker</TableHead>
              <TableHead>Transformation Reason</TableHead>
              <TableHead>Consumed</TableHead>
              <TableHead></TableHead>
              <TableHead>Produced</TableHead>
              <TableHead>Reference</TableHead>
              <TableHead className="w-[100px]"></TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading ? (
              <TableRow>
                <TableCell colSpan={8} className="text-center h-24 text-slate-500">
                  Loading transformations...
                </TableCell>
              </TableRow>
            ) : transformations.length === 0 ? (
              <TableRow>
                <TableCell colSpan={8} className="text-center h-24 text-slate-500">
                  No inventory transformations recorded yet.
                </TableCell>
              </TableRow>
            ) : (
              transformations.map((trans: any) => (
                <TableRow key={trans.id} className="hover:bg-slate-50">
                  <TableCell className="whitespace-nowrap">
                    {new Date(trans.created_on).toLocaleDateString()}
                  </TableCell>
                  <TableCell className="font-medium text-slate-900">
                    {getSupplierName(trans.job_worker_id)}
                  </TableCell>
                  <TableCell>
                    <span className="inline-flex items-center rounded-full bg-blue-50 px-2 py-1 text-xs font-medium text-blue-700 ring-1 ring-inset ring-blue-600/20">
                      {trans.transformation_reason.replace(/_/g, " ")}
                    </span>
                  </TableCell>
                  <TableCell>
                    <div className="text-sm">
                      <span className="font-semibold text-amber-600">-{formatQuantityValue(trans.quantity_consumed)}</span>
                      <span className="text-slate-500 ml-1 block text-xs">{getSkuName(trans.source_item_id)}</span>
                    </div>
                  </TableCell>
                  <TableCell>
                    <ArrowRightLeft className="h-4 w-4 text-slate-300" />
                  </TableCell>
                  <TableCell>
                    <div className="text-sm">
                      <span className="font-semibold text-green-600">+{formatQuantityValue(trans.quantity_produced)}</span>
                      <span className="text-slate-500 ml-1 block text-xs">{getSkuName(trans.destination_item_id)}</span>
                    </div>
                  </TableCell>
                  <TableCell className="text-slate-500 text-sm">
                    {trans.reference_document || "-"}
                  </TableCell>
                  <TableCell>
                    <Button variant="ghost" size="sm">
                      <Eye className="h-4 w-4 text-slate-400" />
                    </Button>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>
    </div>
  )
}
