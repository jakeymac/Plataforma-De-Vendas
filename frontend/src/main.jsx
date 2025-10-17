import React from 'react'
import ReactDOM from 'react-dom/client'
import OrdersDashboard from './components/Orders/OrdersDashboard.jsx'

const rootEl = document.getElementById('orders-dashboard-main-container')
if (rootEl) {
    const storeId = rootEl.dataset.storeId

  ReactDOM.createRoot(rootEl).render(
    <React.StrictMode>
      <OrdersDashboard storeId={storeId} />
    </React.StrictMode>
  )
}