import { defineStore } from 'pinia';
import apiClient from '../api/client';

export interface OrderItem {
    id: string;
    sku_part_number: string;
    qty: number;
}

export interface OutboundOrder {
    id: string;
    order_number: string;
    status: string;
    customer_name: string | null;
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
                await this.fetchOrders(); // Automatically refresh orders to reflect SHIPPED status
                return response.data;
            } catch (err: any) {
                this.error = err.response?.data?.error || err.message;
                throw err; // Rethrow to allow UI components to handle business logic failures
            } finally {
                this.isLoading = false;
            }
        }
    }
});