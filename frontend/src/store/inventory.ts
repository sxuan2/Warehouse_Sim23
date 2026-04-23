import { defineStore } from 'pinia';
import apiClient from '../api/client';

export interface InventoryItem {
    id: string;
    sku: string;
    sku_details: {
        part_number: string;
        description: string;
    };
    bin: string;
    location_details: {
        name: string;
    };
    client: string;
    client_name: string;
    qty: number;
    lot_number: string | null;
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
                // 【核心修复】兼容 Django 分页返回的 { results: [] } 格式
                if (Array.isArray(response.data)) {
                    this.items = response.data;
                } else if (response.data && Array.isArray(response.data.results)) {
                    this.items = response.data.results;
                } else {
                    this.items = [];
                }
            } catch (err: any) {
                this.error = err.response?.data?.error || err.message;
                this.items = [];
            } finally {
                this.isLoading = false;
            }
        },
        
        async receiveStock(payload: ReceiveStockPayload) {
            this.isLoading = true;
            this.error = null;
            try {
                const response = await apiClient.post('/warehouses/inventory/receive/', payload);
                await this.fetchInventory();
                return response.data;
            } catch (err: any) {
                this.error = err.response?.data?.error || err.message;
                throw err;
            } finally {
                this.isLoading = false;
            }
        }
    }
});