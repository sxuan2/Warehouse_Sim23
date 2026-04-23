import { defineStore } from 'pinia';
import { ref } from 'vue';
import apiClient from '../api/client';

export interface ReceiptItem {
    id?: string;
    sku_id: string;
    sku_part_number?: string;
    qty: number;
    lot_number: string | null;
    putaway_location_id: string | null;
}

export interface Receipt {
    id?: string;
    transaction_id: string;
    status: string;
    client_name?: string;
    warehouse_name?: string;
    reference_number?: string | null;
    created_at?: string;
    arrival_date?: string | null;
    client_id: string;
    warehouse_id: string;
    items: ReceiptItem[];
}

export const useReceiptStore = defineStore('receipt', () => {
    // 显式初始化为空数组
    const receipts = ref<Receipt[]>([]);
    const isLoading = ref(false);
    const error = ref<string | null>(null);

    async function fetchReceipts() {
        isLoading.value = true;
        try {
            const response = await apiClient.get('/warehouses/receipts/');
            // 核心修复：防御性赋值
            receipts.value = response.data || [];
        } catch (err: any) {
            error.value = err.message;
            receipts.value = [];
        } finally {
            isLoading.value = false;
        }
    }

    async function createReceipt(payload: any) {
        isLoading.value = true;
        error.value = null;
        console.log(">>> STORE_LOG: Executing createReceipt with payload", payload);
        
        try {
            const response = await apiClient.post('/warehouses/receipts/', payload);
            if (!Array.isArray(receipts.value)) receipts.value = [];
            receipts.value.unshift(response.data);
            return response.data;
        } catch (err: any) {
            error.value = err.response?.data ? JSON.stringify(err.response.data) : err.message;
            throw err;
        } finally {
            isLoading.value = false;
        }
    }

    async function updateReceiptStatus(receiptKey: string, status: 'OPEN' | 'COMPLETE' | 'RECEIVED') {
        isLoading.value = true;
        error.value = null;
        try {
            const response = await apiClient.post(`/warehouses/receipts/${receiptKey}/status/`, { status });
            const updated = response.data;
            const index = receipts.value.findIndex(r => r.transaction_id === receiptKey || r.id === receiptKey);
            if (index !== -1) {
                receipts.value[index] = updated;
            } else {
                receipts.value.unshift(updated);
            }
            return updated;
        } catch (err: any) {
            error.value = err.response?.data ? JSON.stringify(err.response.data) : err.message;
            throw err;
        } finally {
            isLoading.value = false;
        }
    }

    return { 
        receipts, 
        isLoading, 
        error, 
        fetchReceipts, 
        createReceipt,
        updateReceiptStatus
    };
});