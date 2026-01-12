import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { withdrawalAPI } from '../api'
import { format } from 'date-fns'
import toast from 'react-hot-toast'

export default function Withdrawals() {
  const [statusFilter, setStatusFilter] = useState('pending')
  const queryClient = useQueryClient()

  const { data: withdrawals, isLoading } = useQuery({
    queryKey: ['withdrawals', statusFilter],
    queryFn: async () => {
      const response = await withdrawalAPI.getAll(statusFilter)
      return response.data
    },
  })

  const approveMutation = useMutation({
    mutationFn: ({ withdrawal_id, payment_reference }) =>
      withdrawalAPI.approve(withdrawal_id, { payment_reference }),
    onSuccess: () => {
      toast.success('Withdrawal approved')
      queryClient.invalidateQueries(['withdrawals'])
    },
  })

  const rejectMutation = useMutation({
    mutationFn: ({ withdrawal_id, rejection_reason }) =>
      withdrawalAPI.reject(withdrawal_id, { rejection_reason }),
    onSuccess: () => {
      toast.success('Withdrawal rejected')
      queryClient.invalidateQueries(['withdrawals'])
    },
  })

  const markPaidMutation = useMutation({
    mutationFn: ({ withdrawal_id, payment_reference }) =>
      withdrawalAPI.markPaid(withdrawal_id, { payment_reference }),
    onSuccess: () => {
      toast.success('Withdrawal marked as paid')
      queryClient.invalidateQueries(['withdrawals'])
    },
  })

  const handleApprove = (withdrawal_id) => {
    const reference = prompt('Enter payment reference (optional):')
    approveMutation.mutate({ withdrawal_id, payment_reference: reference })
  }

  const handleReject = (withdrawal_id) => {
    const reason = prompt('Enter rejection reason:')
    if (reason) {
      rejectMutation.mutate({ withdrawal_id, rejection_reason: reason })
    }
  }

  const handleMarkPaid = (withdrawal_id) => {
    const reference = prompt('Enter payment reference:')
    if (reference) {
      markPaidMutation.mutate({ withdrawal_id, payment_reference: reference })
    }
  }

  return (
    <div>
      <h1 className="text-3xl font-bold text-gray-900 mb-6">Withdrawal Management</h1>

      {/* Status Filter */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <div className="flex gap-4">
          {['pending', 'approved', 'paid', 'rejected'].map((status) => (
            <button
              key={status}
              onClick={() => setStatusFilter(status)}
              className={`px-6 py-2 rounded-lg font-medium transition ${
                statusFilter === status
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {status.charAt(0).toUpperCase() + status.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {/* Withdrawals Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">ID</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">User ID</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Amount</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Method</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Details</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Requested</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {isLoading ? (
              <tr>
                <td colSpan="7" className="px-6 py-4 text-center">Loading...</td>
              </tr>
            ) : !withdrawals || withdrawals.length === 0 ? (
              <tr>
                <td colSpan="7" className="px-6 py-4 text-center text-gray-500">
                  No {statusFilter} withdrawals
                </td>
              </tr>
            ) : (
              withdrawals.map((withdrawal) => (
                <tr key={withdrawal.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 text-sm font-medium text-gray-900">
                    {withdrawal.withdrawal_id}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-900">{withdrawal.user_id}</td>
                  <td className="px-6 py-4 text-sm font-bold text-gray-900">
                    ₹{parseFloat(withdrawal.amount).toFixed(2)}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-900">
                    {withdrawal.withdrawal_method.toUpperCase()}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-900">
                    {withdrawal.upi_id || withdrawal.bank_account || 'N/A'}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500">
                    {format(new Date(withdrawal.requested_at), 'dd MMM yyyy HH:mm')}
                  </td>
                  <td className="px-6 py-4 text-sm">
                    {withdrawal.status === 'pending' && (
                      <div className="flex gap-2">
                        <button
                          onClick={() => handleApprove(withdrawal.withdrawal_id)}
                          className="px-3 py-1 bg-green-600 text-white rounded hover:bg-green-700"
                        >
                          Approve
                        </button>
                        <button
                          onClick={() => handleReject(withdrawal.withdrawal_id)}
                          className="px-3 py-1 bg-red-600 text-white rounded hover:bg-red-700"
                        >
                          Reject
                        </button>
                      </div>
                    )}
                    {withdrawal.status === 'approved' && (
                      <button
                        onClick={() => handleMarkPaid(withdrawal.withdrawal_id)}
                        className="px-3 py-1 bg-blue-600 text-white rounded hover:bg-blue-700"
                      >
                        Mark Paid
                      </button>
                    )}
                    {(withdrawal.status === 'paid' || withdrawal.status === 'rejected') && (
                      <span className={`px-3 py-1 rounded text-xs ${
                        withdrawal.status === 'paid'
                          ? 'bg-green-100 text-green-800'
                          : 'bg-red-100 text-red-800'
                      }`}>
                        {withdrawal.status}
                      </span>
                    )}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}
