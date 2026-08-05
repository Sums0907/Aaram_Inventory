import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { FileDown, CalendarCheck, CheckCircle2, FileSpreadsheet, BookOpen, Clock, BadgeCheck, FileText, AlertCircle } from "lucide-react"
import { useEffect, useState } from "react"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"

type MonthlyJournalLine = {
  Ledger: string;
  Debit: number;
  Credit: number;
}

type MonthlyJournals = {
  sales: MonthlyJournalLine[];
  credit_notes: MonthlyJournalLine[];
  settlements: MonthlyJournalLine[];
}

// Professional Journal Table Component
function FormalGeneralJournal({ 
  title, 
  journalId,
  dateRange,
  narration, 
  lines 
}: { 
  title: string, 
  journalId: string,
  dateRange: string,
  narration: string, 
  lines: MonthlyJournalLine[] 
}) {
  // Sort Debits first, Credits second
  const sortedLines = [...lines].sort((a, b) => {
    if (a.Debit > 0 && b.Debit === 0) return -1;
    if (a.Debit === 0 && b.Debit > 0) return 1;
    return 0;
  });

  const totalDebit = lines.reduce((sum, line) => sum + line.Debit, 0);
  const totalCredit = lines.reduce((sum, line) => sum + line.Credit, 0);
  const isBalanced = Math.abs(totalDebit - totalCredit) < 0.01;

  return (
    <Card className="border border-slate-300 shadow-md bg-white overflow-hidden font-sans rounded-none sm:rounded-sm">
      {/* Formal Header Section */}
      <div className="bg-slate-50 border-b border-slate-200 px-6 py-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <h3 className="text-xl font-bold text-slate-900 tracking-tight">{title}</h3>
            {isBalanced ? (
              <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 text-[10px] font-bold tracking-widest uppercase">
                <BadgeCheck className="h-3 w-3" /> Balanced
              </span>
            ) : (
              <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-red-100 text-red-800 text-[10px] font-bold tracking-widest uppercase">
                <AlertCircle className="h-3 w-3" /> Unbalanced
              </span>
            )}
          </div>
          <div className="flex items-center gap-4 text-xs font-medium text-slate-500 uppercase tracking-wider">
            <span className="flex items-center gap-1"><FileText className="h-3.5 w-3.5" /> ID: {journalId}</span>
            <span className="flex items-center gap-1"><Clock className="h-3.5 w-3.5" /> {dateRange}</span>
          </div>
        </div>
      </div>
      
      {/* Accounting Table */}
      <div className="px-6 py-6">
        <Table className="border-collapse w-full">
          <TableHeader>
            <TableRow className="border-b-2 border-slate-800 hover:bg-transparent">
              <TableHead className="text-slate-900 font-bold uppercase tracking-wider text-xs w-[60%] h-10 align-bottom pb-2">
                Account Titles and Explanation
              </TableHead>
              <TableHead className="text-slate-900 font-bold uppercase tracking-wider text-xs text-right w-[20%] h-10 align-bottom pb-2">
                Debit (₹)
              </TableHead>
              <TableHead className="text-slate-900 font-bold uppercase tracking-wider text-xs text-right w-[20%] h-10 align-bottom pb-2">
                Credit (₹)
              </TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {sortedLines.map((line, idx) => (
              <TableRow key={idx} className="border-none hover:bg-slate-50">
                <TableCell className={`py-2 align-top text-sm ${line.Credit > 0 ? "pl-12 text-slate-600" : "font-semibold text-slate-900"}`}>
                  {line.Ledger}
                </TableCell>
                <TableCell className="py-2 text-right align-top text-sm font-mono text-slate-800">
                  {line.Debit > 0 ? line.Debit.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) : ""}
                </TableCell>
                <TableCell className="py-2 text-right align-top text-sm font-mono text-slate-800">
                  {line.Credit > 0 ? line.Credit.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) : ""}
                </TableCell>
              </TableRow>
            ))}
            
            {/* Narration Row */}
            <TableRow className="border-none hover:bg-transparent">
              <TableCell colSpan={3} className="py-4 pl-12">
                <span className="text-xs text-slate-500 italic">({narration})</span>
              </TableCell>
            </TableRow>

            {/* Totals Row */}
            <TableRow className="hover:bg-transparent">
              <TableCell className="border-t border-slate-300 py-3 text-right uppercase tracking-widest text-xs font-bold text-slate-900">
                Totals
              </TableCell>
              <TableCell className="border-t border-b-4 border-slate-800 border-double py-3 text-right font-mono font-bold text-sm text-slate-900">
                {totalDebit.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              </TableCell>
              <TableCell className="border-t border-b-4 border-slate-800 border-double py-3 text-right font-mono font-bold text-sm text-slate-900">
                {totalCredit.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              </TableCell>
            </TableRow>
          </TableBody>
        </Table>
      </div>
    </Card>
  );
}

export function ExportsPage() {
  const [journals, setJournals] = useState<MonthlyJournals | null>(null)
  const [loading, setLoading] = useState(true)
  const TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0IiwidXNlcm5hbWUiOiJkZW1vIiwicm9sZSI6ImFkbWluIiwiZXhwIjoxODE3NDcyNjA2fQ.J4sb028IFN8h3OBlYq1RatBHZKs0SH6p8eGuKVXKp_c";

  // Derive the current month for display purposes (e.g. "April 2026")
  const currentMonth = "April 2026"; 

  useEffect(() => {
    async function fetchJournals() {
      try {
        const response = await fetch('http://localhost:8000/api/v1/accounting/export/json', {
          headers: { Authorization: `Bearer ${TOKEN}` }
        })
        const resData = await response.json()
        if (resData.success) {
          setJournals(resData.data)
        }
      } catch (err) {
        console.error("Failed to fetch journals", err)
      } finally {
        setLoading(false)
      }
    }
    fetchJournals()
  }, [])

  const downloadFile = async (endpoint: string, filename: string) => {
    const response = await fetch(`http://localhost:8000/api/v1/accounting/export/vyapar/${endpoint}`, {
      headers: { Authorization: `Bearer ${TOKEN}` }
    })
    
    if (response.ok) {
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = filename
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
    } else {
      alert("Failed to download CSV.")
    }
  }

  const downloadAll = async () => {
    await downloadFile('sales', 'Vyapar_Sales_Journal.csv');
    setTimeout(() => downloadFile('credit-notes', 'Vyapar_CreditNotes_Journal.csv'), 500);
    setTimeout(() => downloadFile('settlements', 'Vyapar_Settlements_Journal.csv'), 1000);
  }

  return (
    <div className="space-y-12 animate-in fade-in duration-700 pb-16 bg-slate-50 min-h-screen -m-6 p-6 sm:p-10">
      
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 border-b border-slate-200 pb-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-slate-900 font-serif">Month-End Accounting Close</h1>
          <p className="text-slate-500 mt-2 max-w-2xl text-lg">
            Review your automated, balanced journal entries below. Once verified, download the formal package for your external ledger.
          </p>
        </div>
        
        {/* Export Action Card */}
        <div className="bg-indigo-600 rounded-xl shadow-lg p-5 text-white max-w-sm w-full relative overflow-hidden">
          <div className="absolute top-0 right-0 p-4 opacity-10">
            <BookOpen className="w-32 h-32" />
          </div>
          <div className="relative z-10">
            <h3 className="font-semibold text-lg flex items-center gap-2">
              <FileDown className="h-5 w-5" /> Export to Vyapar
            </h3>
            <p className="text-indigo-100 text-sm mt-1 mb-4">
              Download the complete month-end package containing all balanced journals.
            </p>
            <Button 
              size="lg" 
              className="w-full bg-white text-indigo-700 hover:bg-indigo-50 font-bold shadow-sm"
              onClick={downloadAll}
            >
              Download CSV Package
            </Button>
          </div>
        </div>
      </div>

      {/* Formal Reports Section */}
      <div className="max-w-5xl mx-auto space-y-8">
        <div className="flex items-center gap-3">
          <div className="h-px bg-slate-300 flex-1" />
          <span className="uppercase tracking-widest text-slate-400 font-bold text-xs">Formal Journal Preview</span>
          <div className="h-px bg-slate-300 flex-1" />
        </div>

        {loading || !journals ? (
          <div className="text-center py-20">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600 mx-auto mb-4"></div>
            <p className="text-slate-500 font-medium">Compiling journals...</p>
          </div>
        ) : (
          <div className="space-y-10">
            
            <FormalGeneralJournal 
              title="Sales Summary Journal"
              journalId={`SJ-${currentMonth.replace(' ', '-').toUpperCase()}`}
              dateRange={`01 ${currentMonth} - 30 ${currentMonth}`}
              narration="To record aggregated tax invoices for the current period, recognizing gross revenue and tax liabilities."
              lines={journals.sales}
            />

            <FormalGeneralJournal 
              title="Credit Notes Summary Journal"
              journalId={`CNJ-${currentMonth.replace(' ', '-').toUpperCase()}`}
              dateRange={`01 ${currentMonth} - 30 ${currentMonth}`}
              narration="To record aggregated sales returns and cancellations, reducing accounts receivable and adjusting tax liabilities."
              lines={journals.credit_notes}
            />

            <FormalGeneralJournal 
              title="Settlements Summary Journal"
              journalId={`SET-${currentMonth.replace(' ', '-').toUpperCase()}`}
              dateRange={`01 ${currentMonth} - 30 ${currentMonth}`}
              narration="To record aggregated payment gateway deposits, merchant fees, and applicable input tax credits."
              lines={journals.settlements}
            />

          </div>
        )}
      </div>
    </div>
  )
}
