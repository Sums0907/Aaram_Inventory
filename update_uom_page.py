import re

with open('frontend/src/pages/inventory/UnitsOfMeasurePage.tsx', 'r') as f:
    content = f.read()

# Add Select imports
content = content.replace("import { Input } from '@/components/ui/input';", "import { Input } from '@/components/ui/input';\nimport { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';")

# Add unit_type to formData state
content = content.replace("unit_code: '',", "unit_code: '',\n    unit_type: 'INTEGER',")
content = content.replace("{ unit_code: '', unit_name: '', short_name: '', description: '' }", "{ unit_code: '', unit_name: '', short_name: '', description: '', unit_type: 'INTEGER' }")

# Add editing state
content = content.replace("const [open, setOpen] = useState(false);", "const [open, setOpen] = useState(false);\n  const [editingId, setEditingId] = useState<string | null>(null);")

# Update handleSubmit
submit_replacement = """
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
"""
content = re.sub(r'const handleSubmit = async \(e: React\.FormEvent\) => \{.*?\};', submit_replacement.strip(), content, flags=re.DOTALL)

# Update Dialog Trigger
content = content.replace('onOpenChange={setOpen}', 'onOpenChange={handleOpenChange}')
content = content.replace('<DialogTitle>Add Unit of Measure</DialogTitle>', '<DialogTitle>{editingId ? "Edit" : "Add"} Unit of Measure</DialogTitle>')

# Update Form
form_field = """
              <div className="space-y-2">
                <Label>Quantity Type</Label>
                <Select value={formData.unit_type} onValueChange={(v) => setFormData({...formData, unit_type: v})}>
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
"""
content = content.replace('<div className="space-y-2">\n                <Label>Description</Label>', form_field + '                <Label>Description</Label>')

# Make unit_code disabled if editing
content = content.replace('<Input required value={formData.unit_code}', '<Input required disabled={!!editingId} value={formData.unit_code}')

# Update Table Headers
content = content.replace('<TableHead>Symbol</TableHead>', '<TableHead>Symbol</TableHead>\n                <TableHead>Type</TableHead>')

# Update Table Body
content = content.replace('<TableCell>{uom.short_name}</TableCell>', '<TableCell>{uom.short_name}</TableCell>\n                    <TableCell><Badge variant="outline">{uom.unit_type}</Badge></TableCell>')

# Update Table Actions
action_replacement = """
                    <TableCell className="text-right flex justify-end gap-2">
                      <Button variant="ghost" size="sm" onClick={() => handleEdit(uom)}>
                        Edit
                      </Button>
                      <Button variant="outline" size="sm" onClick={() => toggleStatus(uom.id, uom.status)}>
                        {uom.status === 'ACTIVE' ? 'Deactivate' : 'Activate'}
                      </Button>
                    </TableCell>
"""
content = re.sub(r'<TableCell className="text-right">.*?<\/TableCell>', action_replacement.strip(), content, flags=re.DOTALL)

with open('frontend/src/pages/inventory/UnitsOfMeasurePage.tsx', 'w') as f:
    f.write(content)

