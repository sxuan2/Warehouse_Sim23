import { defineStore } from 'pinia';
import apiClient from '../api/client';

export interface OrderItem {
    id?: string;
    sku_part_number?: string;
    sku_id?: string;
    qty: number;
    uom: string | null;
    price: string | number | null;
}

export interface OutboundOrder {
    id?: string;
    order_number: string;
    transaction_id?: string | null;
    status: string;
    client_name: string | null;
    warehouse_name?: string | null;
    company_name?: string | null;
    recipient_name: string | null;
    address1?: string | null;
    address2?: string | null;
    state?: string | null;
    postal_code?: string | null;
    country?: string | null;
    city: string | null;
    earliest_ship_date: string | null;
    purchase_order?: string | null;
    created_by?: string | null;
    carrier?: string | null;
    scac?: string | null;
    service?: string | null;
    billing_type?: string | null;
    account_number?: string | null;
    account_zip?: string | null;
    tracking_number?: string | null;
    load_number?: string | null;
    bol_number?: string | null;
    trailer_number?: string | null;
    seal_number?: string | null;
    door?: string | null;
    capacity_type?: string | null;
    pickup_date?: string | null;
    created_at?: string | null;
    require_return_receipt?: boolean;
    saturday_delivery?: boolean;
    residential_delivery?: boolean;
    insurance?: boolean;
    insurance_amount?: string | number | null;
    total_packages?: number | null;
    packaging_uom?: string | null;
    total_weight?: string | number | null;
    total_movable_units?: number | null;
    mu_uom?: string | null;
    total_volume?: string | number | null;
    warehouse_instructions?: string | null;
    carrier_instructions?: string | null;
    updated_at?: string | null;
    items: OrderItem[];
}

export const useOrderStore = defineStore('order', {
    state: () => ({
        orders: [] as OutboundOrder[],
        isLoading: false,
        error: null as string | null,
    }),
    
    actions: {
        async fetchOrders() {
            this.isLoading = true;
            this.error = null;
            try {
                const response = await apiClient.get('/warehouses/orders/');
                // 【核心修复】兼容 Django 分页返回的 { results: [] } 格式
                if (Array.isArray(response.data)) {
                    this.orders = response.data;
                } else if (response.data && Array.isArray(response.data.results)) {
                    this.orders = response.data.results;
                } else {
                    this.orders = [];
                }
            } catch (err: any) {
                this.error = err.response?.data?.error || err.message;
                this.orders = [];
            } finally {
                this.isLoading = false;
            }
        },

        async fulfillOrder(orderId: string) {
            this.isLoading = true;
            this.error = null;
            try {
                const response = await apiClient.post(`/warehouses/orders/${orderId}/fulfill/`);
                const index = this.orders.findIndex(o => o.transaction_id === orderId || o.id === orderId);
                if (index !== -1) {
                    this.orders[index] = response.data;
                }
                return response.data;
            } catch (err: any) {
                this.error = err.response?.data?.error || err.message;
                throw err;
            } finally {
                this.isLoading = false;
            }
        },

        async revertOrderToPending(orderId: string) {
            this.isLoading = true;
            this.error = null;
            try {
                const response = await apiClient.post(`/warehouses/orders/${orderId}/revert-pending/`);
                const index = this.orders.findIndex(o => o.transaction_id === orderId || o.id === orderId);
                if (index !== -1) {
                    this.orders[index] = response.data;
                }
                return response.data;
            } catch (err: any) {
                this.error = err.response?.data?.error || err.message;
                throw err;
            } finally {
                this.isLoading = false;
            }
        },

        async shipOrder(orderId: string) {
            this.isLoading = true;
            this.error = null;
            try {
                const response = await apiClient.post(`/warehouses/orders/${orderId}/ship/`);
                const index = this.orders.findIndex(o => o.transaction_id === orderId || o.id === orderId);
                if (index !== -1) {
                    this.orders[index] = response.data;
                }
                return response.data;
            } catch (err: any) {
                this.error = err.response?.data?.error || err.message;
                throw err;
            } finally {
                this.isLoading = false;
            }
        },

        async createOrder(payload: any) {
            this.isLoading = true;
            this.error = null;
            try {
                const response = await apiClient.post('/warehouses/orders/', payload);
                if (!Array.isArray(this.orders)) this.orders = [];
                this.orders.unshift(response.data);
                return response.data;
            } catch (err: any) {
                this.error = err.response?.data ? JSON.stringify(err.response.data) : err.message;
                throw err;
            } finally {
                this.isLoading = false;
            }
        }
    }
});