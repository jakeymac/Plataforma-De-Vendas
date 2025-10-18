import styles from '../../styles/Orders/OrdersDashboard.module.css'

import { useEffect, useState } from 'react'
import clsx from 'clsx'

export default function OrdersDashboard({ storeId }) {
  const [orders, setOrders] = useState([])
  const [search, setSearch] = useState('')
  const [searchInput, setSearchInput] = useState('')
  const [filter, setFilter] = useState('')
  const [sort, setSort] = useState('newest')
  const [page, setPage] = useState(1)
  const [total, setTotal] = useState(0)
  const [pageCount, setPageCount] = useState(1)
  const [loading, setLoading] = useState(false)
  const [refreshKey, setRefreshKey] = useState(0)

  useEffect(() => {
    

    const controller = new AbortController()

    const fetchOrders = async () => {
      setLoading(true)

      const filters = {}

      if (storeId) {
        filters.store = storeId
      }

      if (filter) {
        filters.status = filter
      }

      const params = new URLSearchParams({
        page: page,
        search: search || '',
        sort: sort || 'newest',
        filters: JSON.stringify(filters),
      }) 

      const response = await fetch(`/api/orders/search/?${params.toString()}`, { signal: controller.signal })
      const data = await response.json()
      setOrders(data.orders)
      setTotal(data.order_count)
      setPageCount(data.page_count)
      setLoading(false)

    }
    fetchOrders()

    return () => controller.abort()
  }, [page, search, filter, sort, storeId, refreshKey])

  const handleSearch = (e) => {
    setSearch(searchInput)
    setPage(1)
  }

  const handleClearSearch = () => {
    setSearchInput('')
    setPage(1)
  }

  const handleRefresh = () => {
    setPage(1)
    setSearchInput('')
    setFilter('')
    setSort('newest')
    setRefreshKey(prev => prev + 1)
  }

  return (
    <div className={clsx('card', styles.cardCustom)}>
      <div className="card-header">
        <div className="d-flex align-items-center justify-content-between mb-3">
          <div className="flex-grow-1 text-center">
            <h3 className="mb-0">Order Dashboard</h3>
          </div>
          <div className="ms-3">
            <button className="btn btn-sm btn-primary" id="refresh-button" onClick={handleRefresh}>Refresh</button>
          </div>
        </div>
        <div className="d-flex flex-wrap justify-content-center gap-2">
          <div className="d-flex" style={{ maxWidth: "500px" }}>
            <div className="position-relative flex-grow-1 me-2">
              <input type="text" className="form-control pe-5" value={searchInput} onChange={(e) => setSearchInput(e.target.value)} placeholder="Search orders..." /> {searchInput && (
                <button
                  className="btn btn-sm position-absolute top-50 end-0 translate-middle-y me-2 d-none"
                  onClick={handleClearSearch}
                  style={{ border: 'none', background: 'transparent '}}>
                    <i className="bi bi-x-circle text-muted"></i>
                  </button>
              )}
            </div>
            <button className="btn btn-primary" onClick={handleSearch}>Search</button>
          </div>
          <div className="input-group" style={{ maxWidth: '220px' }}>
            <label className="input-group-text">Filter</label>
            <select 
              className="form-select" 
              value={filter} 
              onChange={(e) => {
                setFilter(e.target.value)
                setPage(1)
              }}
            >
              <option value="">All</option>
              <option value="PENDING">Pending</option>
              <option value="IN_PROGRESS">In Progress</option>
              <option value="DONE">Done</option>
            </select>
          </div>
          <div className="input-group" style={{ maxWidth: '250px' }}>
            <label className="input-group-text">Sort By</label>
            <select className="form-select" value={sort} onChange={(e) => {
              setSort(e.target.value)
              setPage(1)
            }}>
              <option value="newest">Date (Newest)</option>
              <option value="oldest">Date (Oldest)</option>
              <option value="highest_total">Total (High to Low)</option>
              <option value="lowest_total">Total (Low to High)</option>
            </select>
          </div>
        </div>
      </div>
        <div className="card-body">
          <div className="position-relative">
            { loading && (
              <div className="position-absolute top-0 start-0 w-100 h-100 d-flex justify-content-center align-items-center bg-white bg-opacity-75">
                <div className="spinner-border text-primary" role="status">
                  <span className="visually-hidden">Loading...</span>
                </div>
              </div>
            )}
            <div className={clsx('table-responsive', styles.ordersTableContainer)}>
              <table className="table table-striped table-bordered mb-0">
                <thead className="table-light">
                  <tr>
                    <th>Order ID</th>
                    <th>Customer Username</th>
                    <th>Customer Name</th>
                    <th>Date</th>
                    <th>Total</th>
                    <th>Status</th>
                    <th className="text-center">
                      <i className="bi bi-eye"></i>
                    </th>
                  </tr>
                </thead>
                <tbody>
                  { orders.length === 0 ? (
                    <tr>
                      <td colSpan="7" className="text-center">No orders found</td>
                    </tr>
                  ) : (
                    orders.map((order) => (
                      <tr key={order.id}>
                        <td>{order.id}</td>
                        <td>{order.user_username}</td>
                        <td>{order.user_first_name} {order.user_last_name}</td>
                        <td>{new Date(order.created_at).toLocaleDateString()}</td>
                        <td>${order.total}</td>
                        <td>{order.status}</td>
                        <td className="text-center">
                          <a href={`/orders/${order.id}/`} className="btn btn-primary btn-sm">View</a>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>
        <div className="card-footer d-flex flex-column flex-md-row justify-content-center align-items-center gap-3">
          <div className="d-flex flex-wrap justify-content-center align-items-center gap-3">
            <span className="fw-semibold">Total: {total}</span>
          </div>
          <div className="d-flex justify-content-center align-items-center gap-2">
            <button 
              className="btn btn-outline-secondary btn-sm"
              disabled={page <= 1}
              onClick={() => setPage(page - 1)}
            >
              <i className="bi bi-chevron-left"></i> Prev
            </button>
            <span className="fw-semibold">Page {page}</span>
            <button 
              className="btn btn-outline-secondary btn-sm"
              disabled={page >= pageCount}
              onClick={() => setPage(page + 1)}
            >
              Next <i className="bi bi-chevron-right"></i>
            </button>
          </div>
        </div>
    </div>
  )
}