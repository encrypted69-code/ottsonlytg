import { useQuery } from '@tanstack/react-query'
import { dashboardAPI } from '../api'
import { Users, ShoppingCart, TrendingUp, DollarSign, AlertCircle, Wallet } from 'lucide-react'

function StatCard({ title, value, icon: Icon, color, subtitle }) {
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-gray-600 mb-1">{title}</p>
          <h3 className="text-2xl font-bold text-gray-900">{value}</h3>
          {subtitle && <p className="text-xs text-gray-500 mt-1">{subtitle}</p>}
        </div>
        <div className={`p-3 rounded-full ${color}`}>
          <Icon className="text-white" size={24} />
        </div>
      </div>
    </div>
  )
}

export default function Dashboard() {
  const { data: stats, isLoading } = useQuery({
    queryKey: ['dashboard-stats'],
    queryFn: async () => {
      const response = await dashboardAPI.getStats()
      return response.data
    },
    refetchInterval: 30000, // Refresh every 30 seconds
  })

  const { data: kpi } = useQuery({
    queryKey: ['dashboard-kpi'],
    queryFn: async () => {
      const response = await dashboardAPI.getKPI(30)
      return response.data
    },
  })

  const { data: payments } = useQuery({
    queryKey: ['payment-monitoring'],
    queryFn: async () => {
      const response = await dashboardAPI.getPaymentMonitoring(7)
      return response.data
    },
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600">Welcome to OTT Referral System Admin Panel</p>
      </div>

      {/* Today's Stats */}
      <div className="mb-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Today's Performance</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <StatCard
            title="New Users"
            value={stats?.new_users_today || 0}
            icon={Users}
            color="bg-blue-500"
          />
          <StatCard
            title="Buyers Today"
            value={stats?.buyers_today || 0}
            icon={ShoppingCart}
            color="bg-green-500"
          />
          <StatCard
            title="Revenue Today"
            value={`₹${stats?.revenue_today?.toFixed(2) || 0}`}
            icon={DollarSign}
            color="bg-purple-500"
          />
          <StatCard
            title="Net Profit"
            value={`₹${stats?.net_profit_today?.toFixed(2) || 0}`}
            icon={TrendingUp}
            color="bg-orange-500"
          />
        </div>
      </div>

      {/* Overall Stats */}
      <div className="mb-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Overall Statistics</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <StatCard
            title="Total Users"
            value={stats?.total_users || 0}
            icon={Users}
            color="bg-blue-600"
            subtitle={`${stats?.total_buyers || 0} buyers`}
          />
          <StatCard
            title="Total Revenue"
            value={`₹${stats?.total_revenue?.toFixed(2) || 0}`}
            icon={DollarSign}
            color="bg-green-600"
          />
          <StatCard
            title="Pending Withdrawals"
            value={stats?.pending_withdrawals || 0}
            icon={Wallet}
            color="bg-yellow-500"
            subtitle={`₹${stats?.pending_withdrawal_amount?.toFixed(2) || 0}`}
          />
        </div>
      </div>

      {/* KPI Metrics */}
      {kpi && (
        <div className="mb-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Key Performance Indicators (30 Days)</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="bg-white rounded-lg shadow p-6">
              <p className="text-sm text-gray-600 mb-1">Conversion Rate</p>
              <h3 className="text-2xl font-bold text-gray-900">{kpi.conversion_rate}%</h3>
            </div>
            <div className="bg-white rounded-lg shadow p-6">
              <p className="text-sm text-gray-600 mb-1">Referral Sales</p>
              <h3 className="text-2xl font-bold text-gray-900">{kpi.referral_sales_percent}%</h3>
            </div>
            <div className="bg-white rounded-lg shadow p-6">
              <p className="text-sm text-gray-600 mb-1">Daily Profit Average</p>
              <h3 className="text-2xl font-bold text-gray-900">₹{kpi.net_profit_per_day?.toFixed(2)}</h3>
            </div>
            <div className="bg-white rounded-lg shadow p-6">
              <p className="text-sm text-gray-600 mb-1">Total Sales</p>
              <h3 className="text-2xl font-bold text-gray-900">{kpi.total_sales}</h3>
            </div>
          </div>
        </div>
      )}

      {/* Payment Monitoring */}
      {payments && (
        <div>
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Payment Monitoring (7 Days)</h2>
          <div className="bg-white rounded-lg shadow p-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6">
              <div>
                <p className="text-sm text-gray-600 mb-1">QR Generated</p>
                <p className="text-2xl font-bold text-gray-900">{payments.qr_generated_count}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600 mb-1">Successful</p>
                <p className="text-2xl font-bold text-green-600">{payments.payment_success_count}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600 mb-1">Failed</p>
                <p className="text-2xl font-bold text-red-600">{payments.payment_failed_count}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600 mb-1">Drop-offs</p>
                <p className="text-2xl font-bold text-yellow-600">{payments.payment_dropoff_count}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600 mb-1">Conversion</p>
                <p className="text-2xl font-bold text-blue-600">{payments.conversion_rate}%</p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
