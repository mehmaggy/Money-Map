import { useEffect, useState } from 'react'
import { api } from './api'
import SummaryCards from './components/SummaryCards'
import SpendingByCategoryChart from './components/SpendingByCategoryChart'
import MonthlyTrendChart from './components/MonthlyTrendChart'
import InsightsPanel from './components/InsightsPanel'
import AddTransactionForm from './components/AddTransactionForm'
import ImportCsvCard from './components/ImportCsvCard'
import TransactionsTable from './components/TransactionsTable'
export default function App() {
  const [months, setMonths] = useState([])
  const [month, setMonth] = useState('')
  const [summary, setSummary] = useState(null)
  const [categoryData, setCategoryData] = useState([])
  const [trendData, setTrendData] = useState([])
  const [insights, setInsights] = useState([])
  const [transactions, setTransactions] = useState([])
  const [categories, setCategories] = useState([])

  //on first load, get the list of months that have data + category list.
  useEffect(() => {
    (async () => {
        const [ms, cats] = await Promise.all([api.months(), api.categories()])
        setCategories(cats)
        setMonths(ms)
        setMonth(ms[0] || '')   //default to the most recent match
    }) ().catch(console.error)
  }, [])

  //whenever the selected month changes, load all the data for it.
  useEffect(() => {
    if(!month) return
    (async () => {
        const [sum, cat, tr, ins, txns] = await Promise.all([
            api.summary(month), api.byCategory(month), api.trend(),
            api.insights(month), api.transactions(month)
        ])
        setSummary(sum); setCategoryData(cat); setTrendData(tr)
        setInsights(ins.iters || []); setTransactions(txns)
    })().catch(console.error)
  }, [month])

  // Called after add/ import/ delete so the screen refreshes.
  async function refreshAll() {
    const ms = await api.months()
    setMonths(ms)
    const m = ms.includes(month) ? month : (ms[0] || '')
    if( m === month){
        // month didn't change, so re-trigger the loaders manually
        const [sum, cat, tr, ins, txns] = await Promise.all([
            api.summary(m), api.byCategory(m), api.trend(), api.insights(m), api.transactions(m)
        ])
        setSummary(sum); setCategoryData(cat); setTrendData(tr)
        setInsights(ins.items || []); setTransactiosn(txns)
    } else {
        setMonth(m) // changing month triggers the effect above
    } 
}

return (
<div className="app">
      <header className="header">
        <div className="brand"><span className="logo">💰</span><h1>MoneyMap</h1></div>
        <p className="subtitle">Personal Finance Dashboard</p>
      </header>

      <div className="toolbar">
        <label>Month:&nbsp;
          <select value={month} onChange={e => setMonth(e.target.value)}>
            {months.length === 0 && <option value="">No data yet</option>}
            {months.map(m => <option key={m} value={m}>{m}</option>)}
          </select>
        </label>
        {months.length === 0 &&
          <span className="hint">Import <code>sample_transactions.csv</code> 
          below to get started.</span>}
      </div>

      {summary && <SummaryCards summary={summary} />}

      <div className="grid-2">
        <div className="card">
          <h3>Spending by Category</h3>
          <SpendingByCategoryChart data={categoryData} />
        </div>
        <div className="card">
          <h3>Monthly Trend</h3>
          <MonthlyTrendChart data={trendData} />
        </div>
      </div>

      <InsightsPanel insights={insights} />

      <div className="grid-2">
        <AddTransactionForm categories={categories} onAdded={refreshAll} />
        <ImportCsvCard onImported={refreshAll} />
      </div>

      <TransactionsTable transactions={transactions} onDeleted={refreshAll} />

      <footer>MoneyMap · React + Flask + SQLite + Recharts</footer>
    </div>
        )
} 

