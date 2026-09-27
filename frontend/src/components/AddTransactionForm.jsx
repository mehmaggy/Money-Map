import { useState } from 'react'
import { api } from '../api'

const today = () => new Date().toISOString().slice(0, 10)

export default function AddTransactionForm({ categories, onAdded }) {
  const [date, setDate] = useState(today())
  const [description, setDescription] = useState('')
  const [amount, setAmount] = useState('')
  const [type, setType] = useState('expense')
  const [categoryId, setCategoryId] = useState('')   // '' = auto-detect
  const [msg, setMsg] = useState('')

  async function submit() {
    if (!amount) { setMsg('Please enter an amount.'); return }
    await api.addTransaction({
      txn_date: date,
      description,
      amount: Number(amount),
      type,
      category_id: categoryId ? Number(categoryId) : null
    })
    setMsg('Added! ✅')
    setDescription(''); setAmount('')
    onAdded()
    setTimeout(() => setMsg(''), 1500)
  }

  return (
    <div className="card">
      <h3>Add a Transaction</h3>
      <div className="form">
        <label>Date<input type="date" value={date} onChange={e => setDate(e.target.value)} /></label>
        <label>Description
          <input type="text" placeholder="e.g. Starbucks Coffee"
                 value={description} onChange={e => setDescription(e.target.value)} />
        </label>
        <div className="form-row">
          <label>Amount
            <input type="number" step="0.01" min="0" placeholder="12.50"
                   value={amount} onChange={e => setAmount(e.target.value)} />
          </label>
          <label>Type
            <select value={type} onChange={e => setType(e.target.value)}>
              <option value="expense">Expense</option>
              <option value="income">Income</option>
            </select>
          </label>
        </div>
        <label>Category
          <select value={categoryId} onChange={e => setCategoryId(e.target.value)}>
            <option value="">Auto-detect</option>
            {categories.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
          </select>
        </label>
        <button className="primary" onClick={submit}>Add</button>
        <span className="msg">{msg}</span>
      </div>
    </div>
  )
}