import React from 'react'
import ReactDOM from 'react-dom/client'
import OrdersDashboard from './components/Orders/OrdersDashboard.jsx'
import RecentOrdersWidget from './components/Orders/store_dashboard/RecentOrdersWidget.jsx'
import StoreInfoWidget from './components/Orders/store_dashboard/StoreInfoWidget.jsx'

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

const storeDashboardStoreInfoContainer = document.getElementById('store-dashboard-store-info-widget-container')
if (storeDashboardStoreInfoContainer) {
    const storeId = storeDashboardStoreInfoContainer.dataset.storeId

    ReactDOM.createRoot(storeDashboardStoreInfoContainer).render(
        <React.StrictMode>
            <StoreInfoWidget storeId={storeId} />
        </React.StrictMode>
    )
}