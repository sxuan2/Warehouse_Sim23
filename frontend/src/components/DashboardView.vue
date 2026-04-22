<template>
  <div class="space-y-6 animate-in fade-in duration-300 h-full overflow-y-auto">
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 shrink-0">
      <div class="bg-wms-bg border border-[#1e293b] p-5 flex flex-col relative overflow-hidden group hover:border-indigo-500/30 transition-colors">
        <div class="absolute right-[-10px] top-[-10px] text-[#1e293b] opacity-10 group-hover:text-indigo-500 group-hover:opacity-10 transition-all">
          <BoxIcon :size="70" />
        </div>
        <div class="text-[9px] text-slate-600 uppercase tracking-[0.2em] mb-1 font-bold">Total Stock Units</div>
        <div class="text-2xl font-bold text-wms-text tracking-tighter">
          {{ totalStockUnits }}
        </div>
        <div class="text-[9px] mt-2 font-bold tracking-[0.1em] flex items-center gap-1 uppercase text-slate-500">
          Across all active bins
        </div>
      </div>

      <div class="bg-wms-bg border border-[#1e293b] p-5 flex flex-col relative overflow-hidden group hover:border-indigo-500/30 transition-colors">
        <div class="absolute right-[-10px] top-[-10px] text-[#1e293b] opacity-10 group-hover:text-indigo-500 group-hover:opacity-10 transition-all">
          <ArrowRightLeftIcon :size="70" />
        </div>
        <div class="text-[9px] text-slate-600 uppercase tracking-[0.2em] mb-1 font-bold">Total Orders (System)</div>
        <div class="text-2xl font-bold text-wms-text tracking-tighter">
          {{ totalOrdersCount }}
        </div>
        <div class="text-[9px] mt-2 font-bold tracking-[0.1em] flex items-center gap-1 uppercase text-slate-500">
          Historical & Active
        </div>
      </div>

      <div class="bg-wms-bg border border-[#1e293b] p-5 flex flex-col relative overflow-hidden group hover:border-emerald-500/30 transition-colors">
        <div class="absolute right-[-10px] top-[-10px] text-[#1e293b] opacity-10 group-hover:text-emerald-500 group-hover:opacity-10 transition-all">
          <TruckIcon :size="70" />
        </div>
        <div class="text-[9px] text-slate-600 uppercase tracking-[0.2em] mb-1 font-bold">Successfully Shipped</div>
        <div class="text-2xl font-bold text-wms-text tracking-tighter">
          {{ shippedOrdersCount }}
        </div>
        <div class="text-[9px] mt-2 font-bold tracking-[0.1em] flex items-center gap-1 uppercase text-emerald-500">
          Fulfillment Complete
        </div>
      </div>

      <div class="bg-wms-bg border border-amber-500/20 p-5 flex flex-col relative overflow-hidden group hover:border-amber-500/50 transition-colors">
        <div class="absolute right-[-10px] top-[-10px] text-[#1e293b] opacity-10 group-hover:text-amber-500 group-hover:opacity-10 transition-all">
          <AlertTriangleIcon :size="70" />
        </div>
        <div class="text-[9px] text-amber-500/70 uppercase tracking-[0.2em] mb-1 font-bold">Pending Fulfillment</div>
        <div class="text-2xl font-bold text-amber-400 tracking-tighter">
          {{ pendingOrdersCount }}
        </div>
        <div class="text-[9px] mt-2 font-bold tracking-[0.1em] flex items-center gap-1 uppercase text-amber-500/50">
          Requires Action
        </div>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div class="col-span-2 bg-wms-bg border border-[#1e293b] p-6 flex flex-col h-[350px]">
        <h3 class="text-xs font-bold text-wms-text uppercase tracking-widest mb-6 flex items-center gap-2">
          <ActivityIcon :size="14" class="text-indigo-400" />
          Recent Order Activity
        </h3>
        
        <div v-if="orderStore.isLoading" class="flex-1 flex flex-col items-center justify-center gap-4">
          <RefreshCcwIcon class="animate-spin text-indigo-500 opacity-50" :size="20" />
          <span class="text-[9px] text-slate-500 uppercase tracking-widest font-bold">Syncing ledgers...</span>
        </div>

        <div v-else-if="recentOrders.length === 0" class="flex-1 flex flex-col items-center justify-center text-slate-600 italic">
          <span class="text-[10px] uppercase tracking-widest font-bold">No recent order activity</span>
        </div>

        <div v-else class="space-y-4 overflow-y-auto pr-2">
          <div 
            v-for="order in recentOrders" 
            :key="order.id" 
            class="flex items-center gap-4 text-[11px] p-3 bg-white/[0.02] border border-white/[0.05] group hover:bg-white/[0.05] transition-colors"
          >
            <div :class="[
              'w-2 h-2 rounded-full shadow-[0_0_8px_currentColor]',
              order.status === 'SHIPPED' ? 'bg-emerald-500 text-emerald-500' :
              order.status === 'PROCESSING' ? 'bg-indigo-500 text-indigo-500' :
              'bg-amber-500 text-amber-500'
            ]"></div>
            <span class="text-slate-500 w-24 font-mono font-bold">{{ order.order_number }}</span>
            <span class="text-wms-text flex-1 truncate">{{ order.customer_name || 'N/A' }}</span>
            <span class="text-slate-500 font-mono">{{ order.items.length }} line(s)</span>
            <span :class="[
              'px-2 py-0.5 border text-[9px] font-bold uppercase tracking-widest rounded-sm',
              order.status === 'SHIPPED' ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' :
              order.status === 'PROCESSING' ? 'bg-indigo-500/10 text-indigo-400 border-indigo-500/20' :
              'bg-amber-500/10 text-amber-400 border-amber-500/20'
            ]">
              {{ order.status }}
            </span>
          </div>
        </div>
      </div>

      <div class="bg-wms-bg border border-[#1e293b] p-6 flex flex-col items-center justify-center h-[350px]">
        <div class="text-[10px] text-slate-500 uppercase font-bold mb-6 tracking-widest w-full text-left">System Health</div>
        <div class="relative w-40 h-40 flex items-center justify-center mb-6">
          <svg class="absolute w-full h-full -rotate-90">
            <circle cx="80" cy="80" r="70" fill="transparent" stroke="#1e293b" stroke-width="4" />
            <circle cx="80" cy="80" r="70" fill="transparent" stroke="#10b981" stroke-width="4" stroke-dasharray="440" stroke-dashoffset="0" class="transition-all duration-1000" />
          </svg>
          <div class="text-center">
            <div class="text-3xl font-bold text-wms-text tracking-tighter">100%</div>
            <div class="text-[9px] text-emerald-500 uppercase font-bold tracking-widest mt-1">Operational</div>
          </div>
        </div>
        <div class="w-full space-y-3 pt-4 border-t border-[#1e293b]">
           <div class="flex justify-between items-center">
             <span class="text-[9px] text-slate-500 uppercase font-bold tracking-widest">Postgres DB</span>
             <span class="text-[9px] text-emerald-400 font-bold uppercase">Online</span>
           </div>
           <div class="flex justify-between items-center">
             <span class="text-[9px] text-slate-500 uppercase font-bold tracking-widest">API Latency</span>
             <span class="text-[9px] text-wms-text font-mono font-bold">&lt; 50ms</span>
           </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue';
import { useOrderStore } from '../store/order';
import { useInventoryStore } from '../store/inventory';
import { 
  BoxIcon, 
  ArrowRightLeftIcon, 
  TruckIcon, 
  AlertTriangleIcon,
  ActivityIcon,
  RefreshCcwIcon
} from 'lucide-vue-next';

// Connect to our existing Pinia stores!
const orderStore = useOrderStore();
const inventoryStore = useInventoryStore();

// Fetch data when dashboard loads
onMounted(() => {
  orderStore.fetchOrders();
  inventoryStore.fetchInventory();
});

// Computed properties for Dashboard Metrics
const totalStockUnits = computed(() => {
  return inventoryStore.items.reduce((sum, item) => sum + item.qty, 0);
});

const totalOrdersCount = computed(() => orderStore.orders.length);

const shippedOrdersCount = computed(() => {
  return orderStore.orders.filter(o => o.status === 'SHIPPED').length;
});

const pendingOrdersCount = computed(() => {
  return orderStore.orders.filter(o => o.status === 'PENDING').length;
});

// Get the 5 most recently created/updated orders (simulated by taking the first 5)
const recentOrders = computed(() => {
  return [...orderStore.orders].slice(0, 5);
});
</script>