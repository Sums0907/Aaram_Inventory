import React, { useState } from 'react';
import { useUnitsOfMeasure, useCreateUOM, useUpdateUOM, useActivateUOM, useDeactivateUOM } from '@/api/masters';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Label } from '@/components/ui/label';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger, DialogFooter } from '@/components/ui/dialog';
import { Plus, Edit } from 'lucide-react';

export default function UnitsOfMeasurePage() {
  const { data: uoms, isLoading } = useUnitsOfMeasure();
  const createUOM = useCreateUOM();
  const updateUOM = useUpdateUOM();
  const activateUOM = useActivateUOM();
  const deactivateUOM = useDeactivateUOM();

  const [open, setOpen] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [formData, setFormData] = useState<{
    unit_code: string;
    unit_name: string;
    short_name: string;
    description: string;
    unit_type: "INTEGER" | "DECIMAL";
  }>({
    unit_code: '',
    unit_name: '',
    short_name: '',
    description: '',
    unit_type: 'INTEGER'
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (editingId) {
      await updateUOM.mutateAsync({ id: editingId, data: formData });
    } else {
      await createUOM.mutateAsync(formData);
    }
    setOpen(false);
    setEditingId(null);
    setFormData({ unit_code: '', unit_name: '', short_name: '', description: '', unit_type: 'INTEGER' });
  };
  
  const handleEdit = (uom: any) => {
    setEditingId(uom.id);
    setFormData({
      unit_code: uom.unit_code,
      unit_name: uom.unit_name,
      short_name: uom.short_name,
      description: uom.description || '',
      unit_type: uom.unit_type || 'INTEGER'
    });
    setOpen(true);
  };
  
  const handleOpenChange = (isOpen: boolean) => {
    setOpen(isOpen);
    if (!isOpen) {
      setEditingId(null);
      setFormData({ unit_code: '', unit_name: '', short_name: '', description: '', unit_type: 'INTEGER' });
    }
  };

  const toggleStatus = async (id: string, currentStatus: string) => {
    if (currentStatus === 'ACTIVE') {
      await deactivateUOM.mutateAsync(id);
    } else {
      await activateUOM.mutateAsync(id);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">Units of Measure</h2>
          <p className="text-muted-foreground">Manage centralized inventory units</p>
        </div>
        <Dialog open={open} onOpenChange={handleOpenChange}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="mr-2 h-4 w-4" /> Add UOM
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>{editingId ? "Edit" : "Add"} Unit of Measure</DialogTitle>
            </DialogHeader>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <Label>Unit Code (e.g. m, kg)</Label>
                <Input required disabled={!!editingId} value={formData.unit_code} onChange={e => setFormData({ ...formData, unit_code: e.target.value })} />
              </div>
              <div className="space-y-2">
                <Label>Unit Name (e.g. Metre, Kilogram)</Label>
                <Input required value={formData.unit_name} onChange={e => setFormData({ ...formData, unit_name: e.target.value })} />
              </div>
              <div className="space-y-2">
                <Label>Short Name / Symbol (e.g. mtrs, kg)</Label>
                <Input required value={formData.short_name} onChange={e => setFormData({ ...formData, short_name: e.target.value })} />
              </div>
              
              <div className="space-y-2">
                <Label>Quantity Type</Label>
                <Select value={formData.unit_type} onValueChange={(v: "INTEGER" | "DECIMAL") => setFormData({...formData, unit_type: v})}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select type" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="INTEGER">Integer (e.g. Pieces, Pairs)</SelectItem>
                    <SelectItem value="DECIMAL">Decimal (e.g. Metres, Kgs)</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label>Description</Label>
                <Input value={formData.description} onChange={e => setFormData({ ...formData, description: e.target.value })} />
              </div>
              <DialogFooter>
                <Button type="submit" disabled={createUOM.isPending}>Save</Button>
              </DialogFooter>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Master Units</CardTitle>
          <CardDescription>All inventory units and their active status.</CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Code</TableHead>
                <TableHead>Name</TableHead>
                <TableHead>Symbol</TableHead>
                <TableHead>Type</TableHead>
                <TableHead>Status</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {isLoading ? (
                <TableRow><TableCell colSpan={5} className="text-center">Loading...</TableCell></TableRow>
              ) : uoms?.length === 0 ? (
                <TableRow><TableCell colSpan={5} className="text-center text-muted-foreground">No units found</TableCell></TableRow>
              ) : (
                uoms?.map(uom => (
                  <TableRow key={uom.id}>
                    <TableCell className="font-medium">{uom.unit_code}</TableCell>
                    <TableCell>{uom.unit_name}</TableCell>
                    <TableCell>{uom.short_name}</TableCell>
                    <TableCell><Badge variant="outline">{uom.unit_type}</Badge></TableCell>
                    <TableCell>
                      <Badge variant={uom.status === 'ACTIVE' ? 'default' : 'secondary'}>
                        {uom.status}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-right flex justify-end gap-2">
                      <Button variant="ghost" size="sm" onClick={() => handleEdit(uom)}>
                        Edit
                      </Button>
                      <Button variant="outline" size="sm" onClick={() => toggleStatus(uom.id, uom.status)}>
                        {uom.status === 'ACTIVE' ? 'Deactivate' : 'Activate'}
                      </Button>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}
