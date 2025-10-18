import styles from '../../../styles/Orders/store_dashboard/RecentOrdersWidget.module.css'

import { useEffect, useState } from 'react'
import clsx from 'clsx'

export default function RecentOrdersWidget({ storeId }) {
    const [orders, setOrders] = useState([])
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

            const params = new URLSearchParams({
                sort: 'newest',
                filters: JSON.stringify(filters),
            })

            const response = await fetch(`/api/orders/search/?${params.toString()}`)
            const data = await response.json()
            setOrders(data.orders)
            setLoading(false)
        }

        fetchOrders()

        return () => controller.abort()
    }, [storeId, refreshKey])

    const handleRefresh = () => {
        setRefreshKey(prev => prev + 1)
    }

    return (
        <div className={clsx('card', styles.cardCustom)}>
            <div className="card-header justify-content-between align-items-center d-flex">
                <h3 className={styles.infoCardHeaderTitle}>Recent Orders</h3>
                <button className="btn btn-sm btn-primary" onClick={handleRefresh}>Refresh</button>
            </div>
            <div className="card-body d-flex justify-content-center align-items-center flex-column">
                <div className="position-relative">
                    { loading && (
                        <div className="position-absolute top-0 start-0 w-100 h-100 d-flex justify-content-center align-items-center bg-white bg-opacity-75">
                            <div className="spinner-border text-primary" role="status">
                            <span className="visually-hidden">Loading...</span>
                            </div>
                        </div>
                    )}
                    <div className={clsx('table-responsive', styles.ordersTableContainer)}>
                    
                        <table className="table table-striped table-bordered">
                            <thead>
                                <tr>
                                    <th>Order ID</th>
                                    <th>Customer Username</th>
                                    <th>Customer Name</th>
                                    <th>Date</th>
                                    <th>Total</th>
                                    <th>Status</th>
                                    <th scope="col" className="text-center">
                                        <i className="bi bi-eye"></i>
                                    </th>
                                </tr>
                            </thead>
                            <tbody>
                                { orders.map(order => (
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
                                )) }
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
            <div className="card-footer d-flex justify-content-center">
                <a href="/order_dash" className="btn btn-sm btn-secondary">View All Orders</a>
            </div>
        </div>
    )
}