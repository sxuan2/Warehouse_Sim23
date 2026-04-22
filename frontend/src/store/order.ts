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
    status: string;
    customer_name: string | null;
    recipient_name: string | null;
    city: string | null;
    earliest_ship_date: string | null;
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
                this.orders = response.data;
            } catch (err: any) {
                this.error = err.response?.data?.error || err.message;
            } finally {
                this.isLoading = false;
            }
        },

        async fulfillOrder(orderId: string) {
            this.isLoading = true;
            this.error = null;
            try {
                const response = await apiClient.post(`/warehouses/orders/${orderId}/fulfill/`);
                const index = this.orders.findIndex(o => o.id === orderId);
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