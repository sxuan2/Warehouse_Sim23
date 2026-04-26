<template>
  <div class="flex flex-col h-full bg-wms-bg border border-wms-border animate-in fade-in zoom-in-95 duration-300">
    
    <div v-if="receiptStore.error || localError" class="bg-rose-600 p-4 border-b border-rose-900 flex items-center justify-between shadow-2xl z-30">
      <div class="flex items-center gap-3">
        <AlertTriangleIcon class="text-wms-text animate-pulse" :size="20" />
        <pre class="text-[11px] font-mono text-wms-text whitespace-pre-wrap">{{ receiptStore.error || localError }}</pre>
      </div>
      <button @click="clearErrors" class="bg-black/20 hover:bg-black/40 p-2 text-wms-text"><XIcon :size="16" /></button>
    </div>

    <div class="p-4 border-b border-wms-border flex justify-between items-center bg-wms-header">
      <h2 class="text-wms-text text-xs font-bold uppercase tracking-[0.2em]">Create New Inbound Receipt</h2>
      <div class="flex gap-3">
        <button @click="$emit('cancel')" class="px-4 py-1.5 text-[10px] font-bold text-slate-400 hover:text-wms-text border border-wms-border uppercase">Cancel</button>
        <button @click="submitForm" :disabled="receiptStore.isLoading || isUpdatingSkus" class="px-6 py-1.5 bg-[#0e7490] hover:bg-[#0891b2] text-wms-text text-[10px] font-bold uppercase shadow-lg disabled:opacity-20">
          {{ receiptStore.isLoading ? 'Saving...' : 'Save Receipt' }}
        </button>
      </div>
    </div>

    <div class="flex border-b border-wms-border px-4 bg-wms-header">
      <button v-for="tab in tabs" :key="tab.id" @click="activeTab = tab.id"
        :class="['px-6 py-3 text-[9px] uppercase font-bold tracking-widest transition-all border-b-2', 
                 activeTab === tab.id ? 'border-indigo-500 text-indigo-400' : 'border-transparent text-slate-500 hover:text-slate-300']">
        {{ tab.label }}
      </button>
    </div>

    <div class="flex-1 overflow-y-auto p-8 custom-scrollbar">
      <div v-if="activeTab === 'basics'" class="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-4xl">
        <div class="space-y-6">
          <div>
            <label class="block text-[9px] text-slate-500 uppercase font-bold mb-2">Customer (Required first) *</label>
            <select v-model="form.client_id" class="w-full bg-wms-surface border border-wms-border text-wms-text p-2.5 text-xs outline-none focus:border-indigo-500">
              <option value="">-- Select Customer to Unlock SKUs --</option>
              <option v-for="c in clients" :key="c.id" :value="c.id">{{ c.name }}</option>
            </select>
          </div>
          <div>
            <label class="block text-[9px] text-slate-500 uppercase font-bold mb-2">Warehouse *</label>
            <select v-model="form.warehouse_id" class="w-full bg-wms-surface border border-wms-border text-wms-text p-2.5 text-xs outline-none focus:border-indigo-500">
              <option value="">-- Select Warehouse --</option>
              <option v-for="w in warehouses" :key="w.id" :value="w.id">{{ w.name }}</option>
            </select>
          </div>
        </div>
        <div class="space-y-6">
          <div>
            <label class="block text-[9px] text-slate-500 uppercase font-bold mb-2">Transaction ID (Auto)</label>
            <input v-model="form.transaction_id" type="text" readonly placeholder="Auto-generated on save" class="w-full bg-wms-surface/60 border border-wms-border text-slate-400 p-2.5 text-xs outline-none font-mono cursor-not-allowed">
          </div>
          <div>
            <label class="block text-[9px] text-slate-500 uppercase font-bold mb-2">Reference Number</label>
            <input v-model="form.reference_number" type="text" placeholder="Optional reference" class="w-full bg-wms-surface border border-wms-border text-wms-text p-2.5 text-xs outline-none focus:border-indigo-500 font-mono">
          </div>
        </div>
      </div>

      <div v-if="activeTab === 'items'" class="space-y-4">
        <div class="flex justify-between items-center mb-4">
          <div class="flex items-center gap-4">
            <h4 class="text-[10px] text-indigo-400 font-bold uppercase tracking-widest italic">Receipt Line Items</h4>
            <span v-if="isUpdatingSkus" class="text-[9px] text-amber-500 animate-pulse font-bold">Refetching Client SKUs...</span>
          </div>
          <button @click="addItemLine" :disabled="!form.client_id" class="bg-indigo-600 hover:bg-indigo-500 disabled:opacity-20 text-wms-text px-3 py-1 text-[9px] font-bold uppercase rounded-sm">+ Add Line Item</button>
        </div>
        
        <div v-if="!form.client_id" class="p-20 text-center border-2 border-dashed border-wms-border rounded text-slate-600 uppercase text-[10px] font-bold tracking-widest">
           Please select a Customer in the "Basic Info" tab to see available SKUs.
        </div>

        <div v-else class="bg-white rounded-sm overflow-hidden border border-slate-200 shadow-xl">
          <table class="w-full text-left">
            <thead class="bg-[#cbd5e1] text-[9px] text-slate-700 uppercase font-bold border-b border-slate-300">
              <tr>
                <th class="p-3">SKU *</th>
                <th class="p-3">Qty *</th>
                <th class="p-3">Lot Number</th>
                <th class="p-3">Putaway Bin</th>
                <th class="p-3"></th>
              </tr>
            </thead>
            <tbody class="text-[11px] text-slate-800 font-medium">
              <tr v-for="(line, index) in form.items" :key="index" class="border-b border-slate-200 even:bg-slate-50">
                <td class="p-3">
                  <select v-model="line.sku_id" class="w-full border border-slate-300 p-1.5 outline-none focus:border-indigo-500">
                    <option value="">-- Choose Item --</option>
                    <option v-for="s in skus" :key="s.id" :value="s.id">{{ s.part_number }}</option>
                  </select>
                </td>
                <td class="p-3">
                  <input v-model.number="line.qty" type="number" class="w-24 border border-slate-300 p-1.5 outline-none">
                </td>
                <td class="p-3">
                  <input v-model="line.lot_number" type="text" class="w-full border border-slate-300 p-1.5 outline-none font-mono">
                </td>
                <td class="p-3">
                  <select v-model="line.putaway_location_id" class="w-full border border-slate-300 p-1.5 outline-none">
                    <option value="">-- Unspecified --</option>
                    <option v-for="l in locations" :key="l.id" :value="l.id">{{ l.name }}</option>
                  </select>
                </td>
                <td class="p-3">
                  <button @click="removeItemLine(index)" class="text-rose-500 font-black">X</button>
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
import { ref, reactive, onMounted, watch } from 'vue';
import { useReceiptStore } from '../store/receipt';
import { AlertTriangleIcon, XIcon } from 'lucide-vue-next';
import apiClient from '../api/client';

const emit = defineEmits(['cancel', 'success']);
const receiptStore = useReceiptStore();
const localError = ref<string | null>(null);
const isUpdatingSkus = ref(false);

const tabs = [{ id: 'basics', label: 'Basic Info' }, { id: 'items', label: 'Receipt Line Items' }];
const activeTab = ref('basics');

const clients = ref<any[]>([]);
const warehouses = ref<any[]>([]);
const skus = ref<any[]>([]);
const locations = ref<any[]>([]);

const form = reactive({
  transaction_id: '',
  reference_number: '',
  client_id: '',
  warehouse_id: '',
  items: [{ sku_id: '', qty: 1, lot_number: '', putaway_location_id: '' }]
});

// [CRITICAL] Watcher to update SKU list whenever client changes
watch(() => form.client_id, async (newClientId) => {
  if (newClientId) {
    await fetchSkusByClient(newClientId);
    // Optional: Clear existing items if the client changes to prevent cross-contamination
    form.items = [{ sku_id: '', qty: 1, lot_number: '', putaway_location_id: '' }];
  } else {
    skus.value = [];
  }
});

const fetchSkusByClient = async (clientId: string) => {
  isUpdatingSkus.value = true;
  try {
    const res = await apiClient.get(`/warehouses/sku/?client_id=${clientId}`);
    skus.value = res.data;
  } catch (err) {
    localError.value = "Failed to fetch SKUs for the selected client.";
  } finally {
    isUpdatingSkus.value = false;
  }
};

onMounted(async () => {
  try {
    const [cRes, wRes, lRes] = await Promise.all([
      apiClient.get('/warehouses/client/'),
      apiClient.get('/warehouses/warehouse/'),
      apiClient.get('/warehouses/location/')
    ]);
    clients.value = cRes.data;
    warehouses.value = wRes.data;
    locations.value = lRes.data;
  } catch (err) {
    localError.value = "CRITICAL: Database link offline.";
  }
});

const addItemLine = () => form.items.push({ sku_id: '', qty: 1, lot_number: '', putaway_location_id: '' });
const removeItemLine = (idx: number) => form.items.splice(idx, 1);
const clearErrors = () => { receiptStore.error = null; localError.value = null; };

const submitForm = async () => {
  clearErrors();
  if (!form.client_id || !form.warehouse_id) {
    activeTab.value = 'basics';
    localError.value = "VALIDATION: Client and Warehouse are required.";
    return;
  }
  const payload = JSON.parse(JSON.stringify(form));
  if (!payload.transaction_id?.trim()) {
    delete payload.transaction_id;
  }
  payload.items.forEach((item: any) => { if (item.putaway_location_id === '') item.putaway_location_id = null; });
  try {
    await receiptStore.createReceipt(payload);
    emit('success');
  } catch (err) {}
};
</script>