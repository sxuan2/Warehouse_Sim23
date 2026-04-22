import { defineStore } from 'pinia';
import apiClient from '../api/client';

export interface Sku {
    id: string;
    part_number: string;
    description: string | null;
}

export interface Location {
    id: string;
    name: string;
    warehouse_name: string;
}

export interface InventoryItem {
    id: string;
    sku_details: Sku;
    location_details: Location;
    qty: number;
}

export interface ReceiveStockPayload {
    skuId: string;
    binId: string;
    qty: number;
    clientId: string;
}

export const useInventoryStore = defineStore('inventory', {
    state: () => ({
        items: [] as InventoryItem[],
        isLoading: false,
        error: null as string | null,
    }),
    
    actions: {
        async fetchInventory() {
            this.isLoading = true;
            this.error = null;
            try {
                const response = await apiClient.get('/warehouses/inventory/');
                this.items = response.data;
            } catch (err: any) {
                this.error = err.response?.data?.error || err.message;
            } finally {
                this.isLoading = false;
            }
        },
        
        async receiveStock(payload: ReceiveStockPayload) {
            this.isLoading = true;
            this.error = null;
            try {
                const response = await apiClient.post('/warehouses/inventory/receive/', payload);
                await this.fetchInventory(); // Automatically refresh the inventory list
                return response.data;
            } catch (err: any) {
                this.error = err.response?.data?.error || err.message;
                throw err; // Rethrow to allow UI components to show alert dialogs
            } finally {
                this.isLoading = false;
            }
        }
    }
});