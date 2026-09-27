import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from 'recharts'

const COLORS = ['#6366f1', '#22c55e', '#f59e0b', '#ef4444', '#06b6d4', '#a855f7', '#94a3b8']

export default function SpendingByCategoryChart({ data }) {
    if(!data || data.length === 0) {
        return<p className="empty">No expenses recorded for this month. </p>
    }
    return(
        <ResponsiveContainer width = "100%" height = {300}>
            <PieChart>
                <Pie data={data} dataKey="total" nameKey="category"
                    cx="50%" cy="50%" outerRadius={100} label={(e) => e.category}>
                    {data.map((entry, i) => <Cell key={i} fill={COLORS[i%COLORS.length]} />)}
                </Pie>
                <Tooltip formatter={(v) => '$' + Number(v).toFixed(2)} />
                <Legend />
            </PieChart>
        </ResponsiveContainer>
    )
}