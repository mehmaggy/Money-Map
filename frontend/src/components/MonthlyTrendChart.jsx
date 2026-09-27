import {LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer} from 'recharts'

export default function MonthlyTrendChart({data}) {
    if(!data || data.length === 0) {
        return <p className="empty">Not enough data yet for a trend.</p>
    }
    return (
        <ResponsiveContainer width="100%" height ={300}>
            <LineChart data ={data} margin = {{ top: 10, right: 20, bottom: 0, left: 0}}>
                <CartesianGrid strokeDasharray = "3 3" />
                <XAxis dataKey = "month" />
                <YAxis />
                <Tooltip formatter={(v) => "$" + Number(v).toFixed(2)} />
                <Legend />
                <Line type="monocome" dataKey="income" stroke="A22c55e" strokeWidth={2} />     
                <Line type="monocome" dataKey="expense" stroke="Aef4444" strokeWidth={2} />     
            </LineChart>
        </ResponsiveContainer>
    )
}