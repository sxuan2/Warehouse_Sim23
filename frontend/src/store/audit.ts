import { defineStore } from 'pinia';
import apiClient from '../api/client';

export interface AuditTransaction {
    id: string;
    type: string;
    sku_part_number: string;
    client_name: string;
    change_qty: number;
    from_bin_name: string | null;
    to_bin_name: string | null;
    reference_id: string | null;
    reason: string | null;
    timestamp: string;
}

export const useAuditStore = defineStore('audit', {
    state: () => ({
        transactions: [] as AuditTransaction[],
        isLoading: false,
        error: null as string | null,
    }),
    
    actions: {
        async fetchTransactions() {
            this.isLoading = true;
            this.error = null;
            try {
                const response = await apiClient.get('/warehouses/transactions/');
                this.transactions = response.data;
            } catch (err: any) {
                this.error = err.response?.data?.error || err.message;
            } finally {
                this.isLoading = false;
            }
        }
    }
});