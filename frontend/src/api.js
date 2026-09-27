// All backend calls live here in one place.
const BASE = '/api'

async function getJson(path) {
    const res =await fetch(BASE + path)
    if (!res.ok) throw new Error('Request failed:' + path)
        return res.json()
}

export const api = {
    months:        ()      => getJson('/months'),
    categories:    ()      => getJson('/categories'),
    summary:       (month) => getJson(`/summary?month=${month}`),
  byCategory:    (month) => getJson(`/by-category?month=${month}`),
  trend:         ()      => getJson('/trend'),
  insights:      (month) => getJson(`/insights?month=${month}`),
  transactions:  (month) => getJson(`/transactions?month=${month}`),
    addTransaction: (body) =>
        fetch(BASE + '/transactions', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(body)
        }).then(r => r.json()),

    deleteTransaction: (id) =>
        fetch('${BASE}/transactions/${id}', {method:'DELETE'}).then(r => r.json()),

    importCsv: (file) => {
        const fd=new FormData()
        fd.append('file', file)
        return fetch(BASE + '/import', {method: 'POST', body:fd}).then(r => r.json())
    }
}