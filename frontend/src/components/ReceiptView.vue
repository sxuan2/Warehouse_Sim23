<template>
  <div class="flex flex-col gap-6 h-full">
    
    <div class="bg-wms-bg border border-wms-border p-4 shrink-0 flex flex-col md:flex-row gap-6 justify-between">
      <div>
        <div class="text-[10px] text-indigo-400 font-bold uppercase tracking-widest">Inbound Flow Overview</div>
        <div class="text-[10px] text-slate-500 mt-1">
          Lifecycle: OPEN => COMPLETE => RECEIVED. Inventory updates at RECEIVED.
        </div>
      </div>
      <div class="flex gap-4">
        <div class="border border-amber-500/20 bg-amber-500/5 px-4 py-3 min-w-[120px]">
          <div class="text-[9px] uppercase font-bold tracking-widest text-amber-400">Open</div>
          <div class="text-lg font-bold text-wms-text mt-1">{{ openCount }}</div>
          <div class="text-[10px] text-slate-500 mt-1">OPEN receipts</div>
        </div>
        <div class="border border-indigo-500/20 bg-indigo-500/5 px-4 py-3 min-w-[120px]">
          <div class="text-[9px] uppercase font-bold tracking-widest text-indigo-400">Complete</div>
          <div class="text-lg font-bold text-wms-text mt-1">{{ completeCount }}</div>
          <div class="text-[10px] text-slate-500 mt-1">COMPLETE receipts</div>
        </div>
        <div class="border border-emerald-500/20 bg-emerald-500/5 px-4 py-3 min-w-[120px]">
          <div class="text-[9px] uppercase font-bold tracking-widest text-emerald-400">Received</div>
          <div class="text-lg font-bold text-wms-text mt-1">{{ receivedCount }}</div>
          <div class="text-[10px] text-slate-500 mt-1">RECEIVED receipts</div>
        </div>
      </div>
    </div>

    <div v-if="receiptStore.error" class="bg-rose-500/10 border border-rose-500/20 p-4 shrink-0 flex items-center justify-between">
      <span class="text-rose-500 text-[10px] font-bold uppercase tracking-widest">ERROR: {{ receiptStore.error }}</span>
      <button @click="receiptStore.error = null" class="text-rose-500 hover:text-wms-text"><XIcon :size="14" /></button>
    </div>

    <div v-if="selectedReceipt" class="bg-wms-surface border border-wms-border flex flex-col flex-1 min-h-0 animate-in fade-in duration-200">
      <div class="bg-wms-header border-b border-wms-border p-4 flex justify-between items-center shrink-0 shadow-lg">
        <div class="flex items-center gap-6">
          <button @click="selectedReceipt = null" class="text-slate-400 hover:text-indigo-400 transition-colors bg-white/5 p-1 rounded">
            <ChevronLeftIcon :size="18" />
          </button>
          <div class="flex items-center gap-3">
            <span :class="[
              'px-2 py-0.5 border text-[10px] font-bold tracking-widest rounded-sm',
              selectedReceipt.status === 'RECEIVED' ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' :
              selectedReceipt.status === 'COMPLETE' ? 'bg-indigo-500/10 text-indigo-400 border-indigo-500/20' : 
              selectedReceipt.status === 'OPEN' ? 'bg-amber-500/10 text-amber-400 border-amber-500/20' :
              'bg-slate-500/10 text-slate-400 border-slate-500/20'
            ]">
              {{ selectedReceipt.status }}
            </span>
            <span class="text-[10px] text-slate-500 uppercase font-bold tracking-widest">
              Ref: <span class="text-indigo-400">{{ selectedReceipt.transaction_id }}</span>
            </span>
          </div>
        </div>

        <div class="flex items-center gap-2">
          <button
            v-if="selectedReceipt.status === 'OPEN'"
            @click="setStatus('COMPLETE')"
            :disabled="receiptStore.isLoading"
            class="bg-indigo-600 hover:bg-indigo-500 disabled:opacity-30 text-wms-text text-[10px] font-bold px-4 py-2 rounded uppercase tracking-widest"
          >
            Mark COMPLETE
          </button>

          <button
            v-if="selectedReceipt.status === 'COMPLETE'"
            @click="setStatus('RECEIVED')"
            :disabled="receiptStore.isLoading"
            class="bg-emerald-600 hover:bg-emerald-500 disabled:opacity-30 text-wms-text text-[10px] font-bold px-4 py-2 rounded uppercase tracking-widest"
          >
            Mark RECEIVED
          </button>

          <button
            v-if="selectedReceipt.status === 'COMPLETE'"
            @click="setStatus('OPEN')"
            :disabled="receiptStore.isLoading"
            class="bg-amber-600/20 hover:bg-amber-600/30 disabled:opacity-30 text-amber-300 text-[10px] font-bold px-4 py-2 rounded uppercase tracking-widest border border-amber-500/30"
          >
            Revert OPEN
          </button>

          <button
            v-if="selectedReceipt.status === 'RECEIVED'"
            @click="setStatus('COMPLETE')"
            :disabled="receiptStore.isLoading"
            class="bg-amber-600/20 hover:bg-amber-600/30 disabled:opacity-30 text-amber-300 text-[10px] font-bold px-4 py-2 rounded uppercase tracking-widest border border-amber-500/30"
          >
            Revert COMPLETE
          </button>
        </div>
      </div>

      <div class="bg-wms-header border-b border-wms-border flex gap-1 px-4 pt-4 shrink-0">
        <button 
          v-for="tab in ['items', 'general']" 
          :key="tab"
          @click="activeSubTab = tab"
          :class="['px-4 py-2 text-[10px] uppercase tracking-widest font-bold transition-all border-x border-t rounded-t-sm', 
                   activeSubTab === tab ? 'bg-[#0e7490] text-wms-text border-[#0e7490]' : 'bg-white/5 text-slate-500 border-wms-border hover:bg-white/10']"
        >
          {{ tab === 'items' ? 'Receipt Items' : 'General Info' }}
        </button>
      </div>

      <div class="p-6 overflow-y-auto flex-1">
        <div v-if="activeSubTab === 'items'" class="bg-white border border-slate-200 rounded-sm shadow-sm overflow-hidden text-slate-800">
          <table class="w-full text-left border-collapse">
            <thead class="bg-[#cbd5e1] text-[9px] text-slate-700 uppercase font-bold border-b border-slate-300">
              <tr>
                <th class="p-3 border-r border-slate-300">SKU Code</th>
                <th class="p-3 border-r border-slate-300">Qty (Pallet)</th>
                <th class="p-3 border-r border-slate-300">Weight (lbs)</th>
                <th class="p-3 border-r border-slate-300">Lot Number</th>
                <th class="p-3 border-r border-slate-300">MU Label</th>
                <th class="p-3">Putaway Location</th>
              </tr>
            </thead>
            <tbody class="text-[11px]">
              <tr v-for="item in selectedReceipt.items" :key="item.id" class="border-b border-slate-200 even:bg-slate-50 hover:bg-indigo-50/50">
                <td class="p-3 border-r border-slate-200 font-mono text-[#0e7490] font-bold">{{ item.sku_part_number }}</td>
                <td class="p-3 border-r border-slate-200 font-bold">{{ item.qty }}</td>
                <td class="p-3 border-r border-slate-200">{{ item.weight_lbs || '--' }}</td>
                <td class="p-3 border-r border-slate-200 font-mono text-slate-500">{{ item.lot_number || 'N/A' }}</td>
                <td class="p-3 border-r border-slate-200">{{ item.mu_label || 'N/A' }}</td>
                <td class="p-3 font-mono text-slate-600">{{ item.putaway_location_name || 'Pending' }}</td>
              </tr>
              <tr v-if="selectedReceipt.items.length === 0">
                <td colspan="6" class="p-8 text-center text-slate-400 italic">No items attached to this receipt.</td>
              </tr>
            </tbody>
          </table>
        </div>

        <div v-if="activeSubTab === 'general'" class="grid grid-cols-2 md:grid-cols-3 gap-6 bg-white border border-slate-200 rounded-sm p-6 shadow-sm text-slate-800">
          <div class="flex flex-col gap-1">
            <span class="text-[9px] text-slate-400 font-bold uppercase tracking-widest">Client</span>
            <span class="text-xs font-bold">{{ selectedReceipt.client_name }}</span>
          </div>
          <div class="flex flex-col gap-1">
            <span class="text-[9px] text-slate-400 font-bold uppercase tracking-widest">Warehouse</span>
            <span class="text-xs font-bold">{{ selectedReceipt.warehouse_name }}</span>
          </div>
          <div class="flex flex-col gap-1">
            <span class="text-[9px] text-slate-400 font-bold uppercase tracking-widest">PO Number</span>
            <span class="text-xs font-bold">{{ selectedReceipt.purchase_order_number || 'N/A' }}</span>
          </div>
          <div class="flex flex-col gap-1">
            <span class="text-[9px] text-slate-400 font-bold uppercase tracking-widest">Trailer/Pro</span>
            <span class="text-xs font-bold">{{ selectedReceipt.trailer_pro_number || 'N/A' }}</span>
          </div>
          <div class="flex flex-col gap-1">
            <span class="text-[9px] text-slate-400 font-bold uppercase tracking-widest">Arrival Date</span>
            <span class="text-xs font-bold">{{ selectedReceipt.arrival_date ? new Date(selectedReceipt.arrival_date).toLocaleString() : 'Pending' }}</span>
          </div>
        </div>
      </div>
    </div>

    <div v-else class="bg-wms-bg border border-wms-border flex flex-col flex-1 min-h-0 animate-in fade-in duration-200">
      <div class="flex justify-between items-center p-4 border-b border-wms-border shrink-0">
        <div class="text-xs font-bold text-wms-text tracking-widest flex items-center gap-2 uppercase">
          <FileDownIcon class="text-indigo-500" :size="16" />
          Receipt List
        </div>
        <button @click="receiptStore.fetchReceipts()" class="text-slate-500 hover:text-wms-text transition-colors">
          <RefreshCcwIcon :size="14" :class="{'animate-spin': receiptStore.isLoading}" />
        </button>
      </div>

      <div class="overflow-y-auto flex-1">
        <table class="w-full text-left">
          <thead class="bg-wms-header text-[10px] text-slate-500 uppercase tracking-widest font-bold border-b border-wms-border sticky top-0 z-10">
            <tr>
              <th class="p-4">Status</th>
              <th class="p-4">Trans. ID</th>
              <th class="p-4">Reference</th>
              <th class="p-4">Creation Date</th>
              <th class="p-4">Customer</th>
              <th class="p-4">Warehouse</th>
            </tr>
          </thead>
          <tbody class="text-[11px] text-slate-400">
            <tr v-if="receiptStore.isLoading && receiptStore.receipts.length === 0">
              <td colspan="6" class="p-20 text-center uppercase tracking-widest opacity-50 italic">Loading ledger...</td>
            </tr>
            <tr v-if="!receiptStore.isLoading && receiptStore.receipts.length === 0">
              <td colspan="6" class="p-20 text-center uppercase tracking-widest opacity-30 italic">No Receipts Found</td>
            </tr>
            <tr 
              v-for="receipt in receiptStore.receipts" 
              :key="receipt.id" 
              @click="selectedReceipt = receipt"
              class="border-b border-wms-border hover:bg-white/[0.02] cursor-pointer group transition-colors"
            >
              <td class="p-4">
                <span :class="[
                  'px-2 py-0.5 border text-[9px] font-bold tracking-widest rounded-sm',
                  receipt.status === 'RECEIVED' ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' :
                  receipt.status === 'COMPLETE' ? 'bg-indigo-500/10 text-indigo-400 border-indigo-500/20' : 
                  receipt.status === 'OPEN' ? 'bg-amber-500/10 text-amber-400 border-amber-500/20' :
                  'bg-slate-500/10 text-slate-400 border-slate-500/20'
                ]">
                  {{ receipt.status }}
                </span>
              </td>
              <td class="p-4 font-mono font-bold text-wms-text group-hover:text-indigo-400">{{ receipt.transaction_id }}</td>
              <td class="p-4">{{ receipt.reference_number || '--' }}</td>
              <td class="p-4">{{ new Date(receipt.created_at).toLocaleString() }}</td>
              <td class="p-4 text-wms-text opacity-90">{{ receipt.client_name }}</td>
              <td class="p-4 opacity-80">{{ receipt.warehouse_name }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useReceiptStore, type Receipt } from '../store/receipt';
import { 
  FileDownIcon, 
  ChevronLeftIcon, 
  RefreshCcwIcon,
  XIcon
} from 'lucide-vue-next';

const receiptStore = useReceiptStore();
const selectedReceipt = ref<Receipt | null>(null);
const activeSubTab = ref('items');

const openCount = computed(() => receiptStore.receipts.filter(r => r.status === 'OPEN').length);
const completeCount = computed(() => receiptStore.receipts.filter(r => r.status === 'COMPLETE').length);
const receivedCount = computed(() => receiptStore.receipts.filter(r => r.status === 'RECEIVED').length);

const setStatus = async (status: 'OPEN' | 'COMPLETE' | 'RECEIVED') => {
  const key = selectedReceipt.value?.transaction_id || selectedReceipt.value?.id;
  if (!key) return;
  try {
    const updated = await receiptStore.updateReceiptStatus(key, status);
    selectedReceipt.value = updated;
  } catch (e) {
    // error handled in store
  }
};

onMounted(() => {
  receiptStore.fetchReceipts();
});
</script>