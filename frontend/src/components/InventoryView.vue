<template>
  <div class="grid grid-cols-3 gap-6">
    <div class="col-span-2 bg-[#0a0b0d] border border-[#1e293b] rounded-none overflow-hidden flex flex-col shadow-2xl">
      <div class="p-4 border-b border-[#1e293b] flex justify-between items-center bg-[#0d0f12]">
        <h3 class="font-bold text-white text-xs tracking-widest flex items-center gap-2 uppercase italic">
          <DatabaseIcon :size="14" class="text-indigo-500" />
          Inventory_Ledger
        </h3>
        <div class="flex items-center gap-4">
          <button 
            @click="isReceiveModalOpen = true"
            class="bg-indigo-600/10 hover:bg-indigo-600/20 text-indigo-400 border border-indigo-600/20 px-3 py-1 text-[9px] font-bold uppercase tracking-widest flex items-center gap-2 transition-all"
          >
            <PlusIcon :size="10" />
            Receive_Stock
          </button>
          <div class="flex items-center gap-2">
            <span class="w-1.5 h-1.5 bg-indigo-500 rounded-full animate-pulse shadow-[0_0_8px_rgba(99,102,241,0.8)]"></span>
            <span class="text-[9px] text-indigo-400 font-bold uppercase tracking-widest">Live_Sync</span>
          </div>
        </div>
      </div>

      <div class="overflow-x-auto min-h-[400px]">
        <div v-if="inventoryStore.isLoading" class="flex-1 flex flex-col items-center justify-center p-20 gap-4">
          <RefreshCcwIcon class="animate-spin text-indigo-500" :size="24" />
          <span class="text-[10px] text-indigo-400 font-bold uppercase tracking-widest">Awaiting_Backend_Data...</span>
        </div>
        
        <table v-else class="w-full text-left border-collapse">
          <thead class="bg-[#161b22] text-[9px] text-[#484f58] uppercase tracking-[0.2em] font-bold border-b border-[#1e293b]">
            <tr>
              <th class="px-6 py-4 font-serif italic text-white/30 lowercase">sku_hash</th>
              <th class="px-6 py-4 font-serif italic text-white/30 lowercase">loc_node</th>
              <th class="px-6 py-4 font-serif italic text-white/30 lowercase text-right">qty_val</th>
            </tr>
          </thead>
          <tbody class="text-[11px] font-mono text-[#8b949e]">
            <tr 
              v-for="item in inventoryStore.items" 
              :key="item.id" 
              class="border-b border-[#1e293b] hover:bg-white/[0.02] transition-colors group"
            >
              <td class="px-6 py-4 font-bold text-indigo-400/80 group-hover:text-white transition-colors">
                {{ item.sku_details.part_number }}
              </td>
              <td class="px-6 py-4">{{ item.location_details.name }}</td>
              <td class="px-6 py-4 text-right tabular-nums text-white/80">{{ item.qty.toFixed(2) }}</td>
            </tr>
            
            <tr v-if="inventoryStore.items.length === 0">
              <td colspan="3" class="px-6 py-20 text-center text-slate-700 italic border-none bg-black/20">
                <AlertTriangleIcon class="mx-auto mb-4 opacity-20" :size="32" />
                <div class="uppercase tracking-widest text-[10px] font-bold mb-1">[NULL_SET_RETURNED]</div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div class="bg-[#0a0b0d] border border-[#1e293b] p-6 flex flex-col shadow-2xl relative">
      <div class="flex justify-between items-center mb-8">
        <h3 class="font-bold text-white text-[10px] uppercase tracking-[0.2em]">Network_Load</h3>
        <div class="text-white/20 text-[9px] font-bold">DRF_API</div>
      </div>
      
      <div v-if="inventoryStore.error" class="bg-rose-500/10 border border-rose-500/20 p-4 mb-4">
        <span class="text-rose-500 text-[10px] font-bold uppercase tracking-widest">ERR: {{ inventoryStore.error }}</span>
      </div>

      <div class="space-y-4 mt-auto pt-10">
        <div class="flex justify-between items-end">
          <div class="text-[9px] text-slate-500 uppercase tracking-widest font-bold">Data Integrity</div>
          <div class="text-[9px] text-indigo-400 font-bold">100%</div>
        </div>
        <div class="w-full bg-[#1e293b] h-1">
          <div class="bg-indigo-500 w-full h-full"></div>
        </div>
        <p class="text-[9px] text-slate-600 leading-relaxed uppercase tracking-tighter">
          Environment: Django Postgres Prox
        </p>
      </div>
    </div>

    <div v-if="isReceiveModalOpen" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
      <div class="bg-[#0a0b0d] border border-indigo-500/30 w-full max-w-md p-8 shadow-2xl relative">
        <div class="text-white text-xs font-bold uppercase tracking-[0.2em] mb-6 flex items-center gap-2">
          <div class="w-1.5 h-4 bg-indigo-500"></div>
          Inbound stock receipt
        </div>
        
        <form @submit.prevent="handleReceiveStock" class="space-y-6">
          <div>
            <label class="block text-[9px] text-slate-500 uppercase font-bold mb-2 tracking-widest">Target SKU UUID</label>
            <input 
              v-model="inboundForm.skuId"
              type="text"
              required
              class="w-full bg-[#161b22] border border-[#1e293b] text-white p-3 text-xs focus:border-indigo-500 outline-none font-mono"
              placeholder="e.g. 550e8400-e29b-41d4-a716-446655440000"
            />
          </div>

          <div>
            <label class="block text-[9px] text-slate-500 uppercase font-bold mb-2 tracking-widest">Target Location UUID</label>
            <input 
              v-model="inboundForm.binId"
              type="text"
              required
              class="w-full bg-[#161b22] border border-[#1e293b] text-white p-3 text-xs focus:border-indigo-500 outline-none font-mono"
              placeholder="e.g. 123e4567-e89b-12d3-a456-426614174000"
            />
          </div>
          
          <div>
            <label class="block text-[9px] text-slate-500 uppercase font-bold mb-2 tracking-widest">Client UUID</label>
            <input 
              v-model="inboundForm.clientId"
              type="text"
              required
              class="w-full bg-[#161b22] border border-[#1e293b] text-white p-3 text-xs focus:border-indigo-500 outline-none font-mono"
            />
          </div>

          <div>
            <label class="block text-[9px] text-slate-500 uppercase font-bold mb-2 tracking-widest">Quantity</label>
            <input 
              v-model="inboundForm.qty"
              type="number"
              min="1"
              required
              class="w-full bg-[#161b22] border border-[#1e293b] text-white p-3 text-xs focus:border-indigo-500 outline-none"
            />
          </div>

          <div class="flex gap-4 pt-4">
            <button 
              type="button"
              @click="isReceiveModalOpen = false"
              class="flex-1 bg-white/5 hover:bg-white/10 text-white text-[10px] uppercase font-bold py-3 transition-colors"
            >
              Cancel
            </button>
            <button 
              type="submit"
              :disabled="inventoryStore.isLoading"
              class="flex-1 bg-indigo-600 hover:bg-indigo-500 disabled:bg-indigo-600/50 text-white text-[10px] uppercase font-bold py-3 transition-colors"
            >
              {{ inventoryStore.isLoading ? 'Processing...' : 'Confirm receipt' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue';
import { useInventoryStore } from '../store/inventory';
import { 
  DatabaseIcon, 
  PlusIcon, 
  RefreshCcwIcon, 
  AlertTriangleIcon 
} from 'lucide-vue-next';

// Store Integration
const inventoryStore = useInventoryStore();

// Local State
const isReceiveModalOpen = ref(false);
const inboundForm = reactive({
  skuId: '',
  binId: '',
  clientId: '',
  qty: 1
});

// Lifecycle hook: Fetch data when component mounts
onMounted(() => {
  inventoryStore.fetchInventory();
});

// Actions
const handleReceiveStock = async () => {
  try {
    await inventoryStore.receiveStock({
      skuId: inboundForm.skuId,
      binId: inboundForm.binId,
      clientId: inboundForm.clientId,
      qty: inboundForm.qty
    });
    // If successful, close modal and reset form
    isReceiveModalOpen.value = false;
    inboundForm.qty = 1;
  } catch (error) {
    // Error is handled and stored by Pinia, UI will display it automatically
    console.error("Receive stock failed:", error);
  }
};
</script>