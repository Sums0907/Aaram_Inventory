import { useState } from "react"
import { useSuppliers } from "@/api/suppliers"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { 
  Table, 
  TableBody, 
  TableCell, 
  TableHead, 
  TableHeader, 
  TableRow 
} from "@/components/ui/table"
import { Plus, Search, FileDown } from "lucide-react"
import { SupplierDialog } from "@/components/suppliers/SupplierDialog"
import { JobWorkerWorkspace } from "@/components/suppliers/JobWorkerWorkspace"

export function SuppliersPage() {
  const [search, setSearch] = useState("")
  const [dialogOpen, setDialogOpen] = useState(false)
  const [selectedSupplierId, setSelectedSupplierId] = useState<string | null>(null)
  const [jobWorkDialogOpen, setJobWorkDialogOpen] = useState(false)
  const [activeJobWorker, setActiveJobWorker] = useState<{id: string, name: string} | null>(null)

  const { data, isLoading } = useSuppliers(0, 100)
  
  const suppliers = data?.data || []
  
  const filteredSuppliers = suppliers.filter(s => 
    s?.name?.toLowerCase().includes(search.toLowerCase()) || 
    (s?.gstin && s.gstin.toLowerCase().includes(search.toLowerCase()))
  )

  const handleEdit = (id: string) => {
    setSelectedSupplierId(id)
    setDialogOpen(true)
  }

  const handleCreate = () => {
    setSelectedSupplierId(null)
    setDialogOpen(true)
  }

  const handleOpenJobWork = (id: string, name: string) => {
    setActiveJobWorker({ id, name })
    setJobWorkDialogOpen(true)
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Suppliers</h1>
          <p className="text-sm text-slate-500">
            Manage your network of vendors and suppliers.
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline">
            <FileDown className="mr-2 h-4 w-4" />
            Export
          </Button>
          <Button onClick={handleCreate} className="bg-indigo-600 hover:bg-indigo-700">
            <Plus className="mr-2 h-4 w-4" />
            Add Supplier
          </Button>
        </div>
      </div>

      <div className="flex items-center space-x-2">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-slate-400" />
          <Input
            placeholder="Search suppliers..."
            className="pl-9"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
      </div>

      <div className="rounded-md border bg-white">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Supplier Name</TableHead>
              <TableHead>GSTIN</TableHead>
              <TableHead>Contact</TableHead>
              <TableHead>Email</TableHead>
              <TableHead className="text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading ? (
              <TableRow>
                <TableCell colSpan={5} className="text-center h-24 text-slate-500">
                  Loading suppliers...
                </TableCell>
              </TableRow>
            ) : filteredSuppliers.length === 0 ? (
              <TableRow>
                <TableCell colSpan={5} className="text-center h-24 text-slate-500">
                  No suppliers found.
                </TableCell>
              </TableRow>
            ) : (
              filteredSuppliers.map((supplier) => (
                <TableRow key={supplier.id}>
                  <TableCell className="font-medium">{supplier.name}</TableCell>
                  <TableCell>{supplier.gstin || "-"}</TableCell>
                  <TableCell>{supplier.contact_number || "-"}</TableCell>
                  <TableCell>{supplier.email || "-"}</TableCell>
                  <TableCell className="text-right">
                    {supplier.is_job_worker && (
                      <Button 
                        variant="ghost" 
                        size="sm"
                        onClick={() => handleOpenJobWork(supplier.id, supplier.name)}
                        className="text-indigo-600 hover:text-indigo-700 hover:bg-indigo-50 mr-2"
                      >
                        Job Work
                      </Button>
                    )}
                    <Button 
                      variant="ghost" 
                      size="sm"
                      onClick={() => handleEdit(supplier.id)}
                    >
                      Edit
                    </Button>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>

      <SupplierDialog 
        open={dialogOpen} 
        onOpenChange={setDialogOpen}
        supplierId={selectedSupplierId}
      />

      {activeJobWorker && (
        <JobWorkerWorkspace 
          open={jobWorkDialogOpen}
          onOpenChange={setJobWorkDialogOpen}
          supplierId={activeJobWorker.id}
          supplierName={activeJobWorker.name}
        />
      )}
    </div>
  )
}
