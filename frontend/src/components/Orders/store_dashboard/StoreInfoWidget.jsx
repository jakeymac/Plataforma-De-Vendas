import styles from '../../../styles/Orders/store_dashboard/StoreInfoWidget.module.css'


import { use, useEffect, useState } from 'react'
import clsx from 'clsx'


export default function StoreInfoWidget({ storeId }) {
    const [storeData, setStoreData] = useState(null)
    const [storeDataForm, setStoreDataForm] = useState(null)
    const [loading, setLoading] = useState(true)
    const [isEditing, setIsEditing] = useState(false)
    const [errors, setErrors] = useState({})
    const [saving, setSaving] = useState(false)

    

    useEffect(() => {
        const fetchStoreData = async () => {
            setLoading(true)
            const response = await fetch(`/api/stores/${storeId}/`)
            const data = await response.json()
            setStoreData(data)
            setStoreDataForm(data)
            setLoading(false)
        }
        if (!storeData) {
            fetchStoreData()
        }
    }, [storeId])

    const handleEditClick = () => {
        setIsEditing(true)
    }

    const handleInputChange = (field, value) => {
        setStoreDataForm({
            ...storeDataForm,
            [field]: value,
        })
        setErrors({
            ...errors,
            [field]: null,
        })
    }

    const handleSave = async () => {
        setSaving(true)
        setErrors({})
        const response = await fetch(`/api/stores/update/`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken,
            },
            credentials: 'include',
            body: JSON.stringify(storeDataForm),
        })

        if (response.ok) {
            const data = await response.json()
            setStoreData(data)
            setStoreDataForm(data)
            setIsEditing(false)
        } else if (response.status === 400) {
            const errorData = await response.json()
            setErrors(errorData)
        }
        setSaving(false)
    }

    const handleCancel = () => {
        setIsEditing(false)
        setStoreDataForm(storeData)
        setErrors({})
    }



    return (
        <div className={clsx('card', styles.cardCustom)}>
            <div className="card-header info-card-header justify-content-between align-items-center d-flex">
                <h3>General Information</h3>
                {!isEditing && (
                    <button className="btn btn-sm btn-primary" onClick={handleEditClick}>
                        Edit Information
                    </button>
                )}
            </div>
            <div className="card-body">
                { loading ? (
                    <div className="text-center py-4">
                        <div className="spinner-border text-primary" role="status">
                            <span className="visually-hidden">Loading...</span>
                        </div>
                    </div>
                ) : isEditing ? (
                        <>
                            <div className="mb-2">
                                <label className="form-label fw-semibold">Store Name:</label>
                                <input 
                                    type="text" 
                                    className={`form-control ${errors.store_name ? 'is-invalid' : ''}`} 
                                    value={storeDataForm.store_name} 
                                    onChange={(e) => handleInputChange('store_name', e.target.value)} 
                                />
                                {errors.store_name && (
                                    <div className="invalid-feedback">
                                        {errors.store_name}
                                    </div>
                                )}
                            </div>
                            <div className="mb-2">
                                <label className="form-label fw-semibold">Contact Email:</label>
                                <input 
                                    type="email"
                                    className={`form-control ${errors.contact_email ? 'is-invalid' : ''}`}
                                    value={storeDataForm.contact_email || ''}
                                    onChange={(e) => handleInputChange('contact_email', e.target.value)}
                                />
                                {errors.contact_email && (
                                    <div className="invalid-feedback">
                                        {errors.contact_email}
                                    </div>
                                )}
                            </div>
                            <div className="mb-2">
                                <label className="form-label fw-semibold">Store URL:</label>
                                <input 
                                    type="text" 
                                    className={`form-control ${errors.store_url ? 'is-invalid' : ''}`} 
                                    value={storeDataForm.store_url} 
                                    onChange={(e) => handleInputChange('store_url', e.target.value)} 
                                />
                                {errors.store_url && (
                                    <div className="invalid-feedback">
                                        {errors.store_url}
                                    </div>
                                )}
                            </div>
                            <div className="mb-2">
                                <label className="form-label fw-semibold">Description:</label>
                                <textarea 
                                    className={`form-control ${errors.description ? 'is-invalid' : ''}`} 
                                    value={storeDataForm.description || ''} 
                                    onChange={(e) => handleInputChange('description', e.target.value)} 
                                />
                                {errors.description && (
                                    <div className="invalid-feedback">
                                        {errors.description}
                                    </div>
                                )}
                            </div>
                            <button className="btn btn-sm btn-primary me-2" onClick={handleSave} disabled={saving}>
                                { saving ? 'Saving...' : 'Save Changes' }
                            </button>
                            <button className="btn btn-sm btn-secondary" onClick={handleCancel} disabled={saving}>
                                Cancel
                            </button>
                        </> 
                ) : (
                    <>
                        <p><strong>Store Name:</strong> { storeData.store_name }</p>
                        <p><strong>Contact Email:</strong> 
                            { storeData.contact_email ? (
                                <>{ storeData.contact_email }</>
                            ) : (
                                <> No contact email provided.</>
                            )}
                        </p>
                        <p><strong>Store URL:</strong> { storeData.store_url }</p>
                        <p><strong>Description:</strong> 
                            { storeData.description ? (
                                <> { storeData.description }</>
                            ) : (
                                <> No description provided.</>
                            )}
                        </p>
                    </>
                )}
            </div>
        </div>
    )


}

/* 

<div class="card" id="general-info-card">
                    <div class="card-header info-card-header justify-content-between align-items-center d-flex">
                        <h3>General Information</h3>
                        <button class="btn btn-sm btn-primary">Edit Information</button>
                    </div>
                    <div class="card-body">
                        <p><strong>Store Name:</strong> {{ store.store_name }}</p>
                        <p><strong>Contact Email:</strong> {{ store.contact_email }}</p>
                        <p><strong>Store URL:</strong> {{ store.store_url }}</p>
                        <p><strong>Description:</strong> {{ store.description }}</p>
                    </div>
                </div>*/