<template>
  <div class="space-y-6 animate-in fade-in duration-300 h-full overflow-y-auto">
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 shrink-0">
      <div class="bg-wms-bg border border-[#1e293b] p-5 flex flex-col relative overflow-hidden group hover:border-indigo-500/30 transition-colors">
        <div class="absolute right-[-10px] top-[-10px] text-[#1e293b] opacity-10 group-hover:text-indigo-500 group-hover:opacity-10 transition-all">
          <Box :size="70" />
        </div>
        <div class="text-[9px] text-slate-600 uppercase tracking-[0.2em] mb-1 font-bold">Total Stock Units</div>
        <div class="text-2xl font-bold text-wms-text tracking-tighter">{{ totalStockUnits }}</div>
        <div class="text-[9px] mt-2 font-bold tracking-[0.1em] flex items-center gap-1 uppercase text-slate-500">Across all active bins</div>
      </div>

      <div class="bg-wms-bg border border-[#1e293b] p-5 flex flex-col relative overflow-hidden group hover:border-indigo-500/30 transition-colors">
        <div class="absolute right-[-10px] top-[-10px] text-[#1e293b] opacity-10 group-hover:text-indigo-500 group-hover:opacity-10 transition-all">
          <ArrowRightLeft :size="70" />
        </div>
        <div class="text-[9px] text-slate-600 uppercase tracking-[0.2em] mb-1 font-bold">Total Orders (System)</div>
        <div class="text-2xl font-bold text-wms-text tracking-tighter">{{ totalOrdersCount }}</div>
        <div class="text-[9px] mt-2 font-bold tracking-[0.1em] flex items-center gap-1 uppercase text-slate-500">Historical & Active</div>
      </div>

      <div class="bg-wms-bg border border-[#1e293b] p-5 flex flex-col relative overflow-hidden group hover:border-emerald-500/30 transition-colors">
        <div class="absolute right-[-10px] top-[-10px] text-[#1e293b] opacity-10 group-hover:text-emerald-500 group-hover:opacity-10 transition-all">
          <Truck :size="70" />
        </div>
        <div class="text-[9px] text-slate-600 uppercase tracking-[0.2em] mb-1 font-bold">Successfully Shipped</div>
        <div class="text-2xl font-bold text-wms-text tracking-tighter">{{ shippedOrdersCount }}</div>
        <div class="text-[9px] mt-2 font-bold tracking-[0.1em] flex items-center gap-1 uppercase text-emerald-500">Fulfillment Complete</div>
      </div>

      <div class="bg-wms-bg border border-amber-500/20 p-5 flex flex-col relative overflow-hidden group hover:border-amber-500/50 transition-colors">
        <div class="absolute right-[-10px] top-[-10px] text-[#1e293b] opacity-10 group-hover:text-amber-500 group-hover:opacity-10 transition-all">
          <AlertCircle :size="70" />
        </div>
        <div class="text-[9px] text-amber-500/70 uppercase tracking-[0.2em] mb-1 font-bold">Pending Fulfillment</div>
        <div class="text-2xl font-bold text-amber-400 tracking-tighter">{{ pendingOrdersCount }}</div>
        <div class="text-[9px] mt-2 font-bold tracking-[0.1em] flex items-center gap-1 uppercase text-amber-500/50">Requires Action</div>
      </div>
    </div>

    <div class="grid grid-cols-1 gap-6">
      <div class="bg-wms-bg border border-[#1e293b] p-6 flex flex-col h-[350px]">
        <h3 class="text-xs font-bold text-wms-text uppercase tracking-widest mb-6 flex items-center gap-2">
          <Activity :size="14" class="text-indigo-400" /> Recent Order Activity
        </h3>
        
        <div v-if="orderStore.isLoading" class="flex-1 flex flex-col items-center justify-center gap-4">
          <RefreshCcw class="animate-spin text-indigo-500 opacity-50" :size="20" />
          <span class="text-[9px] text-slate-500 uppercase tracking-widest font-bold">Syncing ledgers...</span>
        </div>

        <div v-else-if="recentOrders.length === 0" class="flex-1 flex flex-col items-center justify-center text-slate-600 italic">
          <span class="text-[10px] uppercase tracking-widest font-bold">No recent order activity</span>
        </div>

        <div v-else class="overflow-y-auto pr-2">
          <table class="w-full text-left border-collapse">
            <thead class="sticky top-0 z-10 bg-wms-bg border-b border-wms-border text-[9px] uppercase tracking-[0.2em] font-bold text-slate-500">
              <tr>
                <th class="px-3 py-3 w-6"></th>
                <th class="px-3 py-3">Transaction ID</th>
                <th class="px-3 py-3">Customer</th>
                <th class="px-3 py-3">Warehouse</th>
                <th class="px-3 py-3">Created Time</th>
                <th class="px-3 py-3">Pickup Date</th>
                <th class="px-3 py-3">Status</th>
              </tr>
            </thead>
            <tbody class="text-[11px]">
              <tr
                v-for="order in recentOrders"
                :key="order.id"
                class="border-b border-white/[0.05] hover:bg-white/[0.05] transition-colors"
              >
                <td class="px-3 py-3">
                  <div :class="['w-2 h-2 rounded-full shadow-[0_0_8px_currentColor]', order.status === 'SHIPPED' ? 'bg-emerald-500 text-emerald-500' : order.status === 'COMPLETE' ? 'bg-indigo-500 text-indigo-500' : 'bg-amber-500 text-amber-500']"></div>
                </td>
                <td class="px-3 py-3 font-mono font-bold text-wms-text whitespace-nowrap">
                  {{ order.transaction_id || order.order_number }}
                </td>
                <td class="px-3 py-3 text-wms-text whitespace-nowrap">{{ order.client_name || 'N/A' }}</td>
                <td class="px-3 py-3 text-slate-400 whitespace-nowrap">{{ order.warehouse_name || 'N/A' }}</td>
                <td class="px-3 py-3 text-slate-400 font-mono whitespace-nowrap">
                  {{ order.created_at ? new Date(order.created_at).toLocaleString() : 'N/A' }}
                </td>
                <td class="px-3 py-3 text-slate-400 font-mono whitespace-nowrap">
                  {{ order.pickup_date ? new Date(order.pickup_date).toLocaleString() : 'N/A' }}
                </td>
                <td class="px-3 py-3">
                  <span :class="['px-2 py-0.5 border text-[9px] font-bold uppercase tracking-widest rounded-sm', order.status === 'SHIPPED' ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' : order.status === 'COMPLETE' ? 'bg-indigo-500/10 text-indigo-400 border-indigo-500/20' : 'bg-amber-500/10 text-amber-400 border-amber-500/20']">
                    {{ order.status }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div class="bg-wms-bg border border-[#1e293b] p-6 flex flex-col h-[350px]">
        <h3 class="text-xs font-bold text-wms-text uppercase tracking-widest mb-6 flex items-center gap-2">
          <Activity :size="14" class="text-indigo-400" /> Recent Receipt Activity
        </h3>

        <div v-if="receiptStore.isLoading" class="flex-1 flex flex-col items-center justify-center gap-4">
          <RefreshCcw class="animate-spin text-indigo-500 opacity-50" :size="20" />
          <span class="text-[9px] text-slate-500 uppercase tracking-widest font-bold">Syncing ledgers...</span>
        </div>

        <div v-else-if="recentReceipts.length === 0" class="flex-1 flex flex-col items-center justify-center text-slate-600 italic">
          <span class="text-[10px] uppercase tracking-widest font-bold">No recent receipt activity</span>
        </div>

        <div v-else class="overflow-y-auto pr-2">
          <table class="w-full text-left border-collapse">
            <thead class="sticky top-0 z-10 bg-wms-bg border-b border-wms-border text-[9px] uppercase tracking-[0.2em] font-bold text-slate-500">
              <tr>
                <th class="px-3 py-3 w-6"></th>
                <th class="px-3 py-3">Transaction ID</th>
                <th class="px-3 py-3">Customer</th>
                <th class="px-3 py-3">Warehouse</th>
                <th class="px-3 py-3">Created Time</th>
                <th class="px-3 py-3">Status</th>
              </tr>
            </thead>
            <tbody class="text-[11px]">
              <tr
                v-for="receipt in recentReceipts"
                :key="receipt.id || receipt.transaction_id"
                class="border-b border-white/[0.05] hover:bg-white/[0.05] transition-colors"
              >
                <td class="px-3 py-3">
                  <div :class="['w-2 h-2 rounded-full shadow-[0_0_8px_currentColor]', receipt.status === 'RECEIVED' ? 'bg-emerald-500 text-emerald-500' : receipt.status === 'COMPLETE' ? 'bg-indigo-500 text-indigo-500' : 'bg-amber-500 text-amber-500']"></div>
                </td>
                <td class="px-3 py-3 font-mono font-bold text-wms-text whitespace-nowrap">{{ receipt.transaction_id }}</td>
                <td class="px-3 py-3 text-wms-text whitespace-nowrap">{{ receipt.client_name || 'N/A' }}</td>
                <td class="px-3 py-3 text-slate-400 whitespace-nowrap">{{ receipt.warehouse_name || 'N/A' }}</td>
                <td class="px-3 py-3 text-slate-400 font-mono whitespace-nowrap">
                  {{ receipt.created_at ? new Date(receipt.created_at).toLocaleString() : 'N/A' }}
                </td>
                <td class="px-3 py-3">
                  <span :class="['px-2 py-0.5 border text-[9px] font-bold uppercase tracking-widest rounded-sm', receipt.status === 'RECEIVED' ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' : receipt.status === 'COMPLETE' ? 'bg-indigo-500/10 text-indigo-400 border-indigo-500/20' : 'bg-amber-500/10 text-amber-400 border-amber-500/20']">
                    {{ receipt.status }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue';
import { useOrderStore } from '../store/order';
import { useInventoryStore } from '../store/inventory';
import { useReceiptStore } from '../store/receipt';
// 【核心修复】移除所有容易失效的 Icon 后缀
import { 
  Box, 
  ArrowRightLeft, 
  Truck, 
  AlertCircle,
  Activity,
  RefreshCcw
} from 'lucide-vue-next';

const orderStore = useOrderStore();
const inventoryStore = useInventoryStore();
const receiptStore = useReceiptStore();

onMounted(() => {
  orderStore.fetchOrders();
  inventoryStore.fetchInventory();
  receiptStore.fetchReceipts();
});

// 【核心修复】增加数组类型检查，防止 reduce/filter 崩溃
const totalStockUnits = computed(() => {
  const items = inventoryStore.items;
  return Array.isArray(items) ? items.reduce((sum, item) => sum + item.qty, 0) : 0;
});

const totalOrdersCount = computed(() => {
  return Array.isArray(orderStore.orders) ? orderStore.orders.length : 0;
});

const shippedOrdersCount = computed(() => {
  const orders = orderStore.orders;
  return Array.isArray(orders) ? orders.filter(o => o.status === 'SHIPPED').length : 0;
});

const pendingOrdersCount = computed(() => {
  const orders = orderStore.orders;
  return Array.isArray(orders) ? orders.filter(o => o.status === 'PENDING').length : 0;
});

const recentOrders = computed(() => {
  const orders = orderStore.orders;
  return Array.isArray(orders) ? [...orders].slice(0, 10) : [];
});

const recentReceipts = computed(() => {
  const receipts = receiptStore.receipts;
  return Array.isArray(receipts) ? [...receipts].slice(0, 10) : [];
});
</script>
