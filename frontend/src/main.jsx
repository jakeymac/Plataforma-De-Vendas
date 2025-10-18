import React from 'react'
import ReactDOM from 'react-dom/client'
import OrdersDashboard from './components/Orders/OrdersDashboard.jsx'
import RecentOrdersWidget from './components/Orders/store_dashboard/RecentOrdersWidget.jsx'

const ordersDashboardMainContainer = document.getElementById('orders-dashboard-main-container')
if (ordersDashboardMainContainer) {
    const storeId = ordersDashboardMainContainer.dataset.storeId

  ReactDOM.createRoot(ordersDashboardMainContainer).render(
    <React.StrictMode>
      <OrdersDashboard storeId={storeId} />
    </React.StrictMode>
  )
}

const storeDashboardRecentOrdersContainer = document.getElementById('store-dashboard-recent-orders-widget-container')
if (storeDashboardRecentOrdersContainer) {
    const storeId = storeDashboardRecentOrdersContainer.dataset.storeId

    ReactDOM.createRoot(storeDashboardRecentOrdersContainer).render(
        <React.StrictMode>
            <RecentOrdersWidget storeId={storeId} />
        </React.StrictMode>
    )
}