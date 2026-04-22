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
    client_id: string;
    warehouse_id: string;
    items: ReceiptItem[];
}

export const useReceiptStore = defineStore('receipt', () => {
    const receipts = ref<Receipt[]>([]);
    const isLoading = ref(false);
    const error = ref<string | null>(null);

    async function fetchReceipts() {
        isLoading.value = true;
        try {
            const response = await apiClient.get('/warehouses/receipts/');
            receipts.value = response.data;
        } catch (err: any) {
            error.value = err.message;
        } finally {
            isLoading.value = false;
        }
    }

    // [CRITICAL FIX] 显式定义并确保它在返回对象中
    async function createReceipt(payload: any) {
        isLoading.value = true;
        error.value = null;
        console.log(">>> STORE_LOG: Executing createReceipt with payload", payload);
        
        try {
            const response = await apiClient.post('/warehouses/receipts/', payload);
            receipts.value.unshift(response.data);
            return response.data;
        } catch (err: any) {
            error.value = err.response?.data ? JSON.stringify(err.response.data) : err.message;
            throw err;
        } finally {
            isLoading.value = false;
        }
    }

    // 必须在这里返回，组件才能调用到
    return { 
        receipts, 
        isLoading, 
        error, 
        fetchReceipts, 
        createReceipt 
    };
});