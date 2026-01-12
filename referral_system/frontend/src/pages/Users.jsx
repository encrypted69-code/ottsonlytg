// Users Page
import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { dashboardAPI } from '../api'
import { format } from 'date-fns'

export default function Users() {
  const [filters, setFilters] = useState({
    search: '',
    user_type: '',
    is_buyer: null,
    is_suspicious: null,
    page: 1,
    limit: 50,
  })

  const { data, isLoading } = useQuery({
    queryKey: ['users', filters],
    queryFn: async () => {
      const response = await dashboardAPI.getUsers(filters)
      return response.data
    },
  })

  return (
    <div>
      <h1 className="text-3xl font-bold text-gray-900 mb-6">User Management</h1>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <input
            type="text"
            placeholder="Search users..."
            value={filters.search}
            onChange={(e) => setFilters({ ...filters, search: e.target.value, page: 1 })}
            className="px-4 py-2 border border-gray-300 rounded-lg"
          />
          <select
            value={filters.user_type}
            onChange={(e) => setFilters({ ...filters, user_type: e.target.value, page: 1 })}
            className="px-4 py-2 border border-gray-300 rounded-lg"
          >
            <option value="">All Types</option>
            <option value="customer">Customer</option>
            <option value="referrer">Referrer</option>
            <option value="admin">Admin</option>
          </select>
          <select
            value={filters.is_buyer === null ? '' : filters.is_buyer}
            onChange={(e) => setFilters({ ...filters, is_buyer: e.target.value === '' ? null : e.target.value === 'true', page: 1 })}
            className="px-4 py-2 border border-gray-300 rounded-lg"
          >
            <option value="">All Users</option>
            <option value="true">Buyers Only</option>
            <option value="false">Non-Buyers</option>
          </select>
          <select
            value={filters.is_suspicious === null ? '' : filters.is_suspicious}
            onChange={(e) => setFilters({ ...filters, is_suspicious: e.target.value === '' ? null : e.target.value === 'true', page: 1 })}
            className="px-4 py-2 border border-gray-300 rounded-lg"
          >
            <option value="">All Status</option>
            <option value="true">Suspicious</option>
            <option value="false">Clean</option>
          </select>
        </div>
      </div>

      {/* Users Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">User</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Telegram ID</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Orders</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Total Spent</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Join Date</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {isLoading ? (
              <tr>
                <td colSpan="7" className="px-6 py-4 text-center">Loading...</td>
              </tr>
            ) : data?.data?.length === 0 ? (
              <tr>
                <td colSpan="7" className="px-6 py-4 text-center text-gray-500">No users found</td>
              </tr>
            ) : (
              data?.data?.map((user) => (
                <tr key={user.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4">
                    <div>
                      <div className="font-medium text-gray-900">{user.first_name} {user.last_name}</div>
                      <div className="text-sm text-gray-500">@{user.username || 'N/A'}</div>
                    </div>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-900">{user.telegram_id}</td>
                  <td className="px-6 py-4">
                    <span className={`px-2 py-1 text-xs rounded-full ${
                      user.user_type === 'admin' ? 'bg-purple-100 text-purple-800' :
                      user.user_type === 'referrer' ? 'bg-blue-100 text-blue-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {user.user_type}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-900">{user.total_orders}</td>
                  <td className="px-6 py-4 text-sm text-gray-900">₹{parseFloat(user.total_spent).toFixed(2)}</td>
                  <td className="px-6 py-4 text-sm text-gray-500">
                    {format(new Date(user.join_date), 'dd MMM yyyy')}
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex gap-2">
                      {user.is_suspicious && (
                        <span className="px-2 py-1 text-xs rounded-full bg-red-100 text-red-800">
                          Suspicious
                        </span>
                      )}
                      {user.is_blocked && (
                        <span className="px-2 py-1 text-xs rounded-full bg-red-100 text-red-800">
                          Blocked
                        </span>
                      )}
                      {!user.is_suspicious && !user.is_blocked && (
                        <span className="px-2 py-1 text-xs rounded-full bg-green-100 text-green-800">
                          Active
                        </span>
                      )}
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>

        {/* Pagination */}
        {data && data.pages > 1 && (
          <div className="px-6 py-4 border-t border-gray-200 flex items-center justify-between">
            <div className="text-sm text-gray-700">
              Showing page {data.page} of {data.pages} ({data.total} total users)
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => setFilters({ ...filters, page: filters.page - 1 })}
                disabled={filters.page === 1}
                className="px-4 py-2 border border-gray-300 rounded-lg disabled:opacity-50"
              >
                Previous
              </button>
              <button
                onClick={() => setFilters({ ...filters, page: filters.page + 1 })}
                disabled={filters.page === data.pages}
                className="px-4 py-2 border border-gray-300 rounded-lg disabled:opacity-50"
              >
                Next
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
