export default function InsightsPanel({ insights }) {
  if (!insights || insights.length === 0) return null
  return (
    <div className="card insights">
      <h3>💡 Insights</h3>
      <ul>
        {insights.map((text, i) => <li key={i}>{text}</li>)}
      </ul>
    </div>
  )
}