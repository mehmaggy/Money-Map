import { api } from '../api'

const money = (n) => '$' + Number(n).toFixed(2)

export default function TransactionsTable({ transactions, onDeleted }) {
  async function remove(id) {
    await api.deleteTransaction(id)
    onDeleted()
  }
  return (
    <div className="card">
      <h3>Transactions</h3>
      {transactions.length === 0
        ? <p className="empty">No transactions for this month.</p>
        : (
          <table className="table">
            <thead>
              <tr><th>Date</th><th>Description</th><th>Category</th><th>Type</th><th className="right">Amount</th><th></th></tr>
            </thead>
            <tbody>
              {transactions.map(t => (
                <tr key={t.id}>
                  <td>{t.txn_date}</td>
                  <td>{t.description}</td>
                  <td><span className="badge">{t.category || 'Other'}</span></td>
                  <td className={t.type === 'income' ? 'green' : 'red'}>{t.type}</td>
                  <td className="right">{money(t.amount)}</td>
                  <td><button className="link" onClick={() => remove(t.id)}>delete</button></td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
    </div>
  )
}