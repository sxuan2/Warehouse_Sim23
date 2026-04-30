<template>
  <div class="flex flex-col gap-6 h-full animate-in fade-in duration-500">
    <div class="bg-wms-bg border border-wms-border p-4 shrink-0 flex flex-col md:flex-row gap-6 justify-between">
      <div>
        <div class="text-[10px] text-indigo-400 font-bold uppercase tracking-widest">Inventory Flow Overview</div>
        <div class="text-[10px] text-slate-500 mt-1">
          Lifecycle: RECEIVE => STORE => FULFILL. Snapshot shows current on-hand inventory.
        </div>
      </div>
      <div class="flex gap-4">
        <div class="border border-indigo-500/20 bg-indigo-500/5 px-4 py-3 min-w-[120px]">
          <div class="text-[9px] uppercase font-bold tracking-widest text-indigo-400">Total SKUs</div>
          <div class="text-lg font-bold text-wms-text mt-1 font-mono">{{ inventoryStore.items.length }}</div>
          <div class="text-[10px] text-slate-500 mt-1">Tracked sku lines</div>
        </div>
        <div class="border border-emerald-500/20 bg-emerald-500/5 px-4 py-3 min-w-[120px]">
          <div class="text-[9px] uppercase font-bold tracking-widest text-emerald-400">Active Clients</div>
          <div class="text-lg font-bold text-wms-text mt-1 font-mono">{{ clients.length }}</div>
          <div class="text-[10px] text-slate-500 mt-1">Owners in inventory</div>
        </div>
      </div>
    </div>

    <div class="bg-wms-bg border border-wms-border flex flex-col shadow-2xl relative overflow-hidden flex-1 min-h-0">
      
      <div class="p-4 border-b border-wms-border flex justify-between items-center bg-wms-header">
        <div class="flex items-center gap-6">
          <h3 class="font-bold text-wms-text text-xs tracking-widest flex items-center gap-2 uppercase">
            <DatabaseIcon :size="14" class="text-indigo-500" />
            Inventory_Ledger
          </h3>
          
          <div class="flex items-center gap-3 border-l border-wms-border pl-6">
            <span class="text-[9px] text-slate-500 uppercase font-bold tracking-tighter">View By Customer:</span>
            <select 
              v-model="selectedClientId" 
              class="bg-wms-header border border-wms-border text-indigo-400 text-[10px] px-3 py-1 outline-none focus:border-indigo-500 transition-colors cursor-pointer uppercase font-bold"
            >
              <option value="">-- All Customer Inventory --</option>
              <option v-for="c in clients" :key="c.id" :value="c.id">{{ c.name }}</option>
            </select>
          </div>
        </div>

        <div class="flex items-center gap-4">
          <button 
            @click="isReceiveModalOpen = true"
            class="bg-indigo-600/10 hover:bg-indigo-600/20 text-indigo-400 border border-indigo-600/20 px-4 py-1.5 text-[9px] font-bold uppercase tracking-widest flex items-center gap-2 transition-all active:scale-95"
          >
            <PlusIcon :size="12" />
            Receive_Stock
          </button>
          </div>
      </div>

      <div class="overflow-x-auto min-h-[550px] custom-scrollbar">
        <div v-if="inventoryStore.isLoading" class="flex-1 flex flex-col items-center justify-center p-20 gap-4">
          <RefreshCcwIcon class="animate-spin text-indigo-500" :size="24" />
          <span class="text-[10px] text-indigo-400 font-bold uppercase tracking-widest">Syncing Ledger...</span>
        </div>
        
        <table v-else class="w-full text-left border-collapse">
          <thead class="bg-wms-header text-[9px] text-slate-500 uppercase tracking-[0.2em] font-bold border-b border-wms-border">
            <tr>
              <th class="px-6 py-4">Customer Entity</th>
              <th class="px-6 py-4">SKU Hash</th>
              <th class="px-6 py-4">Location Node</th>
              <th class="px-6 py-4">Lot Number</th>
              <th class="px-6 py-4 text-right">Quantity</th>
            </tr>
          </thead>
          <tbody class="text-[11px] font-mono text-[#8b949e]">
            <tr 
              v-for="item in filteredInventory" 
              :key="item.id" 
              class="border-b border-wms-border hover:bg-white/[0.02] transition-colors group"
            >
              <td class="px-6 py-4 font-bold text-slate-500 uppercase tracking-tighter">
                {{ item.client_name }}
              </td>
              <td class="px-6 py-4 font-bold text-indigo-400/80 group-hover:text-wms-text transition-colors">
                {{ item.sku_details.part_number }}
              </td>
              <td class="px-6 py-4">{{ item.location_details.name }}</td>
              <td class="px-6 py-4 text-[#58a6ff]/40 italic">{{ item.lot_number || '---' }}</td>
              <td class="px-6 py-4 text-right tabular-nums text-wms-text font-bold">{{ item.qty.toFixed(2) }}</td>
            </tr>
            
            <tr v-if="filteredInventory.length === 0">
              <td colspan="5" class="px-6 py-32 text-center text-slate-700 italic border-none bg-black/10">
                <div class="flex flex-col items-center gap-4">
                  <DatabaseZapIcon class="opacity-10" :size="48" />
                  <div class="uppercase tracking-widest text-[10px] font-bold">[EMPTY_SET_FOR_SELECTED_CLIENT]</div>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div v-if="inventoryStore.error" class="bg-rose-500/10 border border-rose-500/20 p-4 shrink-0 flex items-center justify-between">
      <div class="flex items-center gap-2">
        <AlertTriangleIcon class="text-rose-500" :size="12" />
        <span class="text-rose-500 text-[10px] font-bold uppercase tracking-widest">Protocol_Error: {{ inventoryStore.error }}</span>
      </div>
    </div>

    <div v-if="isReceiveModalOpen" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/90 backdrop-blur-md animate-in fade-in duration-300">
      <div class="bg-wms-bg border border-indigo-500/30 w-full max-w-md p-8 shadow-[0_0_50px_rgba(99,102,241,0.2)] relative">
        <div class="text-wms-text text-xs font-bold uppercase tracking-[0.2em] mb-8 flex items-center gap-3">
          <div class="w-1 h-5 bg-indigo-500"></div>
          Inbound stock receipt (Blind)
        </div>
        
        <form @submit.prevent="handleReceiveStock" class="space-y-6">
          <div>
            <label class="block text-[9px] text-slate-500 uppercase font-bold mb-2 tracking-widest">Client / Owner *</label>
            <select v-model="inboundForm.clientId" required class="w-full bg-wms-header border border-wms-border text-wms-text p-3 text-xs focus:border-indigo-500 outline-none transition-colors">
              <option value="" disabled>-- Select Owner --</option>
              <option v-for="c in clients" :key="c.id" :value="c.id">{{ c.name }}</option>
            </select>
          </div>

          <div>
            <label class="block text-[9px] text-slate-500 uppercase font-bold mb-2 tracking-widest">Target SKU *</label>
            <select v-model="inboundForm.skuId" required class="w-full bg-wms-header border border-wms-border text-wms-text p-3 text-xs focus:border-indigo-500 outline-none transition-colors">
              <option value="" disabled>-- Select SKU --</option>
              <option v-for="sku in dicts.skus" :key="sku.id" :value="sku.id">{{ sku.part_number }} ({{ sku.client_name }})</option>
            </select>
          </div>

          <div>
            <label class="block text-[9px] text-slate-500 uppercase font-bold mb-2 tracking-widest">Storage Bin *</label>
            <select v-model="inboundForm.binId" required class="w-full bg-wms-header border border-wms-border text-wms-text p-3 text-xs focus:border-indigo-500 outline-none transition-colors">
              <option value="" disabled>-- Select Location --</option>
              <option v-for="loc in dicts.locations" :key="loc.id" :value="loc.id">{{ loc.name }} ({{ loc.warehouse_name }})</option>
            </select>
          </div>

          <div>
            <label class="block text-[9px] text-slate-500 uppercase font-bold mb-2 tracking-widest">Quantity *</label>
            <input v-model="inboundForm.qty" type="number" min="1" required class="w-full bg-wms-header border border-wms-border text-wms-text p-3 text-xs focus:border-indigo-500 outline-none font-mono"/>
          </div>

          <div class="flex gap-4 pt-6">
            <button type="button" @click="isReceiveModalOpen = false" class="flex-1 bg-white/5 hover:bg-white/10 text-wms-text text-[10px] uppercase font-bold py-3 transition-colors tracking-widest">Cancel</button>
            <button type="submit" :disabled="inventoryStore.isLoading" class="flex-1 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-30 text-wms-text text-[10px] uppercase font-bold py-3 transition-colors tracking-widest shadow-lg shadow-indigo-600/20">
              {{ inventoryStore.isLoading ? 'Processing...' : 'Confirm Receipt' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineOptions({ name: 'InventoryView' });
import { ref, reactive, onMounted, computed } from 'vue';
import { useInventoryStore } from '../store/inventory';
import apiClient from '../api/client';
import { 
  DatabaseIcon, PlusIcon, RefreshCcwIcon, 
  AlertTriangleIcon, DatabaseZapIcon 
} from 'lucide-vue-next';

const inventoryStore = useInventoryStore();

const selectedClientId = ref(''); 
const clients = ref<any[]>([]);
const dicts = reactive({
  skus: [] as any[],
  locations: [] as any[]
});

const filteredInventory = computed(() => {
  if (!selectedClientId.value) return inventoryStore.items;
  return inventoryStore.items.filter(item => item.client === selectedClientId.value);
});

const isReceiveModalOpen = ref(false);
const inboundForm = reactive({
  skuId: '',
  binId: '',
  clientId: '',
  qty: 1
});

onMounted(async () => {
  inventoryStore.fetchInventory();
  
  try {
    const [cRes, sRes, lRes] = await Promise.all([
      apiClient.get('/warehouses/client/'),
      apiClient.get('/warehouses/sku/'),
      apiClient.get('/warehouses/location/')
    ]);
    clients.value = cRes.data;
    dicts.skus = sRes.data;
    dicts.locations = lRes.data;
  } catch (error) {
    console.error("Failed to load metrics and dictionaries:", error);
  }
});

const handleReceiveStock = async () => {
  try {
    await inventoryStore.receiveStock({
      skuId: inboundForm.skuId,
      binId: inboundForm.binId,
      clientId: inboundForm.clientId,
      qty: inboundForm.qty
    });
    isReceiveModalOpen.value = false;
    inboundForm.qty = 1;
    inboundForm.skuId = '';
  } catch (error) {
    console.error("Receive operation failed:", error);
  }
};
</script>

<style scoped>
.custom-scrollbar::-webkit-scrollbar { width: 4px; }
.custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: #1e293b; border-radius: 4px; }
.custom-scrollbar:hover::-webkit-scrollbar-thumb { background: #334155; }
</style>