import { useEffect } from "react"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import * as z from "zod"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog"
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { useCreateCategory } from "@/api/masters"

const formSchema = z.object({
  category_name: z.string().min(1, "Category name is required"),
  category_code: z.string().optional(),
  item_type: z.string(),
  parent_id: z.string().optional(),
  attributes: z.string().optional(),
})

type FormValues = z.infer<typeof formSchema>

interface CategoryFormDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  defaultItemType?: string
  defaultParentId?: string
}

export function CategoryFormDialog({ open, onOpenChange, defaultItemType, defaultParentId }: CategoryFormDialogProps) {
  const form = useForm<FormValues>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      category_name: "",
      category_code: "",
      item_type: defaultItemType || "FINISHED_GOODS",
      parent_id: defaultParentId || "",
      attributes: "",
    },
  })

  const createMutation = useCreateCategory()

  useEffect(() => {
    if (open) {
      form.reset({
        category_name: "",
        category_code: "",
        item_type: defaultItemType || "FINISHED_GOODS",
        parent_id: defaultParentId || "",
        attributes: "",
      })
    }
  }, [open, defaultItemType, defaultParentId, form])

  const onSubmit = async (values: FormValues) => {
    try {
      await createMutation.mutateAsync({
        category_name: values.category_name,
        category_code: values.category_code || undefined,
        item_type: values.item_type,
        parent_id: values.parent_id || undefined,
        attributes: values.attributes ? values.attributes.split(",").map(s => s.trim()).filter(Boolean) : []
      })
      onOpenChange(false)
    } catch (error) {
      console.error("Failed to create category:", error)
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>
            {defaultParentId ? "Create Subcategory" : "Create Category"}
          </DialogTitle>
        </DialogHeader>

        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <FormField
              control={form.control}
              name="category_name"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Category Name *</FormLabel>
                  <FormControl>
                    <Input placeholder="e.g. Raw Cotton" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            
            <FormField
              control={form.control}
              name="category_code"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Category Code (Auto-generated if blank)</FormLabel>
                  <FormControl>
                    <Input placeholder="e.g. C-RAW-01" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="attributes"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Required Attributes (Comma separated)</FormLabel>
                  <FormControl>
                    <Input placeholder="e.g. Length, Breadth, Weight" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <DialogFooter className="mt-6">
              <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
                Cancel
              </Button>
              <Button type="submit" disabled={createMutation.isPending}>
                {createMutation.isPending ? "Creating..." : "Create Category"}
              </Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  )
}
