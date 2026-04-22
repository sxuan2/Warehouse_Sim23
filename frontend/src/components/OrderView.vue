<template>
  <div class="flex flex-col gap-6 h-full">
    
    <div class="bg-[#0a0b0d] border border-[#1e293b] p-4 shrink-0">
      <div class="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <div class="text-[10px] text-indigo-400 font-bold uppercase tracking-widest">Fulfillment Flow Guide</div>
          <div class="text-[10px] text-slate-500 mt-1">
            Next action: Select a PENDING order to review, or complete a PROCESSING order by shipping.
          </div>
        </div>
        <div class="text-[10px] text-slate-500 uppercase tracking-widest font-bold">
          Pipeline: PENDING => PROCESSING => SHIPPED
        </div>
      </div>

      <div class="mt-4 grid grid-cols-1 md:grid-cols-3 gap-3">
        <div class="border border-amber-500/20 bg-amber-500/5 p-3">
          <div class="text-[9px] uppercase font-bold tracking-widest text-amber-400">1. Queue</div>
          <div class="text-lg font-bold text-white mt-1">{{ pendingOrdersCount }}</div>
          <div class="text-[10px] text-slate-500">PENDING orders</div>
        </div>
        <div class="border border-indigo-500/20 bg-indigo-500/5 p-3">
          <div class="text-[9px] uppercase font-bold tracking-widest text-indigo-400">2. Fulfillment</div>
          <div class="text-lg font-bold text-white mt-1">{{ processingOrdersCount }}</div>
          <div class="text-[10px] text-slate-500">PROCESSING orders</div>
        </div>
        <div class="border border-emerald-500/20 bg-emerald-500/5 p-3">
          <div class="text-[9px] uppercase font-bold tracking-widest text-emerald-400">3. Closed</div>
          <div class="text-lg font-bold text-white mt-1">{{ shippedOrdersCount }}</div>
          <div class="text-[10px] text-slate-500">SHIPPED orders</div>
        </div>
      </div>
    </div>

    <div v-if="orderStore.error" class="bg-rose-500/10 border border-rose-500/20 p-4 shrink-0 flex items-center justify-between">
      <div class="flex items-center gap-2">
        <AlertTriangleIcon class="text-rose-500" :size="16" />
        <span class="text-rose-500 text-[10px] font-bold uppercase tracking-widest">SYSTEM HALT: {{ orderStore.error }}</span>
      </div>
      <button @click="orderStore.error = null" class="text-rose-500 hover:text-white transition-colors">
        <XIcon :size="14" />
      </button>
    </div>

    <div v-if="selectedOrder" class="bg-[#0f1115] border border-[#1e293b] flex flex-col flex-1 min-h-0">
      <div class="bg-[#161b22] border-b border-[#1e293b] p-4 flex justify-between items-center shrink-0 shadow-lg">
        <div class="flex items-center gap-6">
          <button @click="selectedOrder = null" class="text-slate-400 hover:text-indigo-400 transition-colors bg-white/5 p-1 rounded">
            <ChevronLeftIcon :size="18" />
          </button>
          <div>
            <div class="text-[10px] text-slate-500 uppercase font-bold tracking-widest flex items-center gap-2">
              Order Review <span class="text-slate-700">|</span> 
              <span class="text-indigo-400">Ref: {{ selectedOrder.order_number }}</span>
              <span class="text-slate-700">|</span> 
              <span>Client: {{ selectedOrder.customer_name || 'UNKNOWN' }}</span>
            </div>
          </div>
        </div>
        
        <div class="flex items-center gap-2">
          <button 
            v-if="selectedOrder.status === 'PENDING'"
            @click="markAsProcessing"
            class="bg-indigo-600 hover:bg-indigo-500 text-white text-[10px] font-bold px-4 py-2 flex items-center gap-2 rounded shadow-sm transition-all"
          >
            <TruckIcon :size="14" /> Start Fulfillment
          </button>
          
          <button 
            v-if="selectedOrder.status === 'PROCESSING'"
            @click="handleShipOrder"
            :disabled="orderStore.isLoading"
            class="bg-[#0e7490] hover:bg-[#0891b2] disabled:bg-white/10 disabled:text-slate-500 text-white text-[10px] font-bold px-4 py-2 flex items-center gap-2 rounded shadow-sm transition-all"
          >
            <TruckIcon v-if="!orderStore.isLoading" :size="14" />
            <RefreshCcwIcon v-else class="animate-spin" :size="14" />
            {{ orderStore.isLoading ? 'Verifying Stock...' : 'Ship and Close Order' }}
          </button>
          
          <span v-if="selectedOrder.status === 'SHIPPED'" class="border border-emerald-500/20 text-emerald-500 text-[10px] font-bold px-4 py-2 rounded uppercase tracking-widest">
            Order Complete
          </span>
        </div>
      </div>

      <div class="bg-[#161b22] border-b border-[#1e293b] flex gap-1 px-4 pt-4 shrink-0">
        <button 
          v-for="tab in ['items', 'details']" 
          :key="tab"
          @click="activeSubTab = tab"
          :class="['px-4 py-2 text-[10px] uppercase tracking-widest font-bold transition-all border-x border-t rounded-t-sm', 
                   activeSubTab === tab ? 'bg-[#0e7490] text-white border-[#0e7490]' : 'bg-white/5 text-slate-500 border-[#1e293b] hover:bg-white/10']"
        >
          {{ tab === 'items' ? 'Order Line Items' : 'Shipping Details' }}
        </button>
      </div>

      <div class="p-6 overflow-y-auto flex-1">
        <div v-if="activeSubTab === 'items'" class="bg-white border border-slate-200 rounded-sm shadow-sm overflow-hidden animate-in fade-in zoom-in-95 duration-200">
          <div class="p-3 bg-slate-50 border-b border-slate-200 flex justify-between items-center">
            <h4 class="text-[10px] text-[#0e7490] uppercase font-bold tracking-widest">Requested Items</h4>
          </div>
          <table class="w-full text-left border-collapse">
            <thead class="bg-[#cbd5e1] text-[10px] text-slate-700 uppercase font-bold border-b border-slate-300">
              <tr>
                <th class="p-2 border-r border-slate-300 w-16">Quantity</th>
                <th class="p-2 border-r border-slate-300">SKU Code</th>
                <th class="p-2 border-r border-slate-300">Unit of Measure</th>
                <th class="p-2 text-right">Extended Total</th>
              </tr>
            </thead>
            <tbody class="text-[11px] text-slate-700">
              <tr v-for="item in selectedOrder.items" :key="item.id" class="border-b border-slate-200 even:bg-slate-50 hover:bg-indigo-50/50 transition-colors">
                <td class="p-2 border-r border-slate-200 font-bold">{{ item.qty }}</td>
                <td class="p-2 border-r border-slate-200 font-mono text-[#0e7490]">{{ item.sku_part_number }}</td>
                <td class="p-2 border-r border-slate-200">{{ item.uom || 'Unit' }}</td>
                <td class="p-2 text-right font-bold">${{ item.price || '0.00' }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <div v-if="activeSubTab === 'details'" class="bg-white border border-slate-200 rounded-sm p-6 shadow-sm animate-in fade-in duration-200 text-slate-800">
          <div class="grid grid-cols-2 md:grid-cols-4 gap-6">
            <div class="flex flex-col gap-1">
              <span class="text-[10px] text-slate-400 font-bold uppercase tracking-widest">Recipient</span>
              <span class="text-xs font-medium">{{ selectedOrder.recipient_name || 'N/A' }}</span>
            </div>
            <div class="flex flex-col gap-1">
              <span class="text-[10px] text-slate-400 font-bold uppercase tracking-widest">Destination City</span>
              <span class="text-xs font-medium">{{ selectedOrder.city || 'N/A' }}</span>
            </div>
            <div class="flex flex-col gap-1">
              <span class="text-[10px] text-slate-400 font-bold uppercase tracking-widest">Earliest Ship Date</span>
              <span class="text-xs font-medium">{{ selectedOrder.earliest_ship_date ? new Date(selectedOrder.earliest_ship_date).toLocaleDateString() : 'Immediate' }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-else class="bg-[#0a0b0d] border border-[#1e293b] flex flex-col flex-1 min-h-0">
      <div class="flex justify-between items-center p-4 border-b border-[#1e293b] shrink-0">
        <div class="text-xs font-bold text-white tracking-widest flex items-center gap-2 uppercase">
          <ArrowRightLeftIcon class="text-indigo-500" :size="16" />
          Outbound Manifests
        </div>
        <button 
          @click="orderStore.fetchOrders()"
          class="text-slate-500 hover:text-white transition-colors"
        >
          <RefreshCcwIcon :size="14" :class="{'animate-spin': orderStore.isLoading}" />
        </button>
      </div>

      <div class="overflow-y-auto flex-1">
        <table class="w-full text-left">
          <thead class="bg-[#161b22] text-[10px] text-slate-500 uppercase tracking-widest font-bold border-b border-[#1e293b] sticky top-0">
            <tr>
              <th class="p-4">Order ID</th>
              <th class="p-4">Client / Customer</th>
              <th class="p-4">Total Lines</th>
              <th class="p-4">Status</th>
              <th class="p-4 text-right">Actions</th>
            </tr>
          </thead>
          <tbody class="text-[12px] text-slate-400">
            <tr v-if="orderStore.orders.length === 0">
              <td colspan="5" class="p-20 text-center uppercase tracking-tighter opacity-30 italic">No Active Order Manifests</td>
            </tr>
            <tr 
              v-for="order in orderStore.orders" 
              :key="order.id" 
              @click="selectedOrder = order"
              class="border-b border-[#1e293b] hover:bg-white/[0.02] cursor-pointer group transition-colors"
            >
              <td class="p-4 font-mono font-bold text-white group-hover:text-indigo-400">{{ order.order_number }}</td>
              <td class="p-4 opacity-80">{{ order.customer_name || 'Default Client' }}</td>
              <td class="p-4 font-mono">{{ order.items.length }}</td>
              <td class="p-4">
                <span :class="[
                  'px-2 py-0.5 border text-[10px] font-bold',
                  order.status === 'PENDING' ? 'bg-amber-500/10 text-amber-400 border-amber-500/20' : 
                  order.status === 'PROCESSING' ? 'bg-indigo-500/10 text-indigo-400 border-indigo-500/20' :
                  'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                ]">
                  {{ order.status }}
               </span>
              </td>
              <td class="p-4 text-right">
                <ChevronRightIcon :size="14" class="inline opacity-20 group-hover:opacity-100 group-hover:translate-x-1 transition-all" />
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useOrderStore, type OutboundOrder } from '../store/order';
import { 
  ArrowRightLeftIcon, 
  TruckIcon, 
  ChevronLeftIcon, 
  ChevronRightIcon, 
  RefreshCcwIcon,
  AlertTriangleIcon,
  XIcon
} from 'lucide-vue-next';

// Store Integration
const orderStore = useOrderStore();

// Local State
const selectedOrder = ref<OutboundOrder | null>(null);
const activeSubTab = ref('items');

// Computed Properties for Flow Guide
const pendingOrdersCount = computed(() => orderStore.orders.filter(o => o.status === 'PENDING').length);
const processingOrdersCount = computed(() => orderStore.orders.filter(o => o.status === 'PROCESSING').length);
const shippedOrdersCount = computed(() => orderStore.orders.filter(o => o.status === 'SHIPPED').length);

// Lifecycle
onMounted(() => {
  orderStore.fetchOrders();
});

// Actions
const markAsProcessing = () => {
  if (selectedOrder.value) {
    // In a full implementation, this would call a PATCH /api/orders/:id endpoint
    // For this demonstration, we simulate local state change prior to actual shipping
    selectedOrder.value.status = 'PROCESSING';
  }
};

const handleShipOrder = async () => {
  if (!selectedOrder.value) return;
  
  try {
    // This triggers the Django backend to perform the atomic inventory deduction
    const updatedOrder = await orderStore.fulfillOrder(selectedOrder.value.id);
    
    // Update local selected view with the server response
    selectedOrder.value = updatedOrder;
  } catch (error) {
    // The Pinia store handles the error catching, the UI will display the banner
    console.error("Fulfillment failed due to inventory mismatch or lock error.", error);
  }
};
</script>