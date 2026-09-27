const money = (n) =>
  '$' + Number(n).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })
export default function SummaryCards({summary}) {
    return(
        <div className="cards">
            <div className="stat income">
                <span className="label">Income</span>
                <span className="value">{money(summary.income)}</span>
            </div>
            <div className="stat expense">
                <span className="label">Expenses</span>
                <span className="value">{money(summary.expense)}</span>
            </div>
            <div className={'stat' + (summary.net >=0? 'net-pos' : 'net-neg')}>
                <span className="label">Net</span>
                <span className="value">{money(summary.net)}</span>
            </div>
        </div>
    )
}