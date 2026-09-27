import { useState } from 'react'
import { api } from '../api'

export default function ImportCsvCard({ onImported }) {
  const [file, setFile] = useState(null)
  const [msg, setMsg] = useState('')

  async function upload() {
    if (!file) { setMsg('Choose a .csv file first.'); return }
    setMsg('Uploading…')
    const result = await api.importCsv(file)
    if (result.error) { setMsg('Error: ' + result.error); return }
    let text = `Imported ${result.imported} transaction(s).`
    if (result.errors && result.errors.length) text += ` Skipped ${result.errors.length}.`
    setMsg(text)
    onImported()
  }

  return (
    <div className="card">
      <h3>Import Bank CSV</h3>
      <p className="hint">Columns: <code>date, description, amount</code> (negative = money spent).</p>
      <div className="form">
        <input type="file" accept=".csv" onChange={e => setFile(e.target.files[0])} />
        <button className="primary" onClick={upload}>Upload &amp; import</button>
        <span className="msg">{msg}</span>
      </div>
    </div>
  )
}