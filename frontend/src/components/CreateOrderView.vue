<template>
  <div class="flex flex-col h-full bg-wms-bg border border-wms-border animate-in fade-in zoom-in-95 duration-300">
    
    <div v-if="orderStore.error || localError" class="bg-rose-600 p-3 border-b border-rose-900 flex items-center justify-between z-30">
      <div class="flex items-center gap-3">
        <AlertTriangleIcon class="text-wms-text animate-pulse" :size="18" />
        <pre class="text-[10px] font-mono text-wms-text whitespace-pre-wrap">{{ orderStore.error || localError }}</pre>
      </div>
      <button @click="clearErrors" class="text-wms-text/50 hover:text-wms-text"><XIcon :size="14" /></button>
    </div>

    <div class="p-4 border-b border-wms-border flex justify-between items-center bg-wms-header">
      <div class="flex items-center gap-4">
        <h2 class="text-wms-text text-xs font-bold uppercase tracking-[0.2em]">Create Outbound Order</h2>
        <div v-if="form.order_number" class="px-2 py-0.5 bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-[9px] font-mono">
          REF: {{ form.order_number }}
        </div>
      </div>
      <div class="flex gap-3">
        <button @click="$emit('cancel')" class="px-4 py-1.5 text-[10px] font-bold text-slate-400 hover:text-wms-text border border-wms-border uppercase">Cancel</button>
        <button @click="submitForm" :disabled="orderStore.isLoading" class="px-6 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-wms-text text-[10px] font-bold uppercase shadow-lg">
          {{ orderStore.isLoading ? 'Committing...' : 'Save & Close Order' }}
        </button>
      </div>
    </div>

    <div class="flex border-b border-wms-border px-4 bg-wms-header">
      <button v-for="tab in tabs" :key="tab.id" @click="activeTab = tab.id"
        :class="['px-6 py-3 text-[9px] uppercase font-bold tracking-widest transition-all border-b-2', 
                 activeTab === tab.id ? 'border-indigo-500 text-indigo-400 bg-indigo-500/5' : 'border-transparent text-slate-500 hover:text-slate-300']">
        {{ tab.label }}
      </button>
    </div>

    <div class="flex-1 overflow-y-auto p-8 custom-scrollbar">
      
      <div v-if="activeTab === 'contact'" class="space-y-10 max-w-6xl">
        <div class="grid grid-cols-1 md:grid-cols-4 gap-6 p-6 bg-white/5 border border-wms-border">
          <div>
            <label class="block text-[9px] text-slate-500 uppercase font-bold mb-2">Customer *</label>
            <select v-model="form.client_id" class="w-full bg-wms-surface border border-wms-border text-wms-text p-2 text-xs outline-none">
              <option value="">-- Choose --</option>
              <option v-for="c in clients" :key="c.id" :value="c.id">{{ c.name }}</option>
            </select>
          </div>
          <div>
            <label class="block text-[9px] text-slate-500 uppercase font-bold mb-2">Warehouse *</label>
            <select v-model="form.warehouse_id" class="w-full bg-wms-surface border border-wms-border text-wms-text p-2 text-xs outline-none">
              <option v-for="w in warehouses" :key="w.id" :value="w.id">{{ w.name }}</option>
            </select>
          </div>
          <div>
            <label class="block text-[9px] text-slate-500 uppercase font-bold mb-2">Ref Number *</label>
            <input v-model="form.order_number" type="text" class="w-full bg-wms-surface border border-wms-border text-wms-text p-2 text-xs font-mono">
          </div>
          <div>
            <label class="block text-[9px] text-slate-500 uppercase font-bold mb-2">Transaction ID *</label>
            <input v-model="form.transaction_id" type="text" class="w-full bg-wms-surface border border-wms-border text-wms-text p-2 text-xs font-mono">
          </div>
        </div>

        <div class="space-y-6">
          <h4 class="text-[10px] text-indigo-400 font-bold uppercase tracking-widest border-b border-wms-border pb-2">Shipping Destination</h4>
          <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div>
              <label class="block text-[9px] text-slate-500 uppercase font-bold mb-2">Recipient Name</label>
              <input v-model="form.recipient_name" type="text" class="w-full bg-wms-surface border border-wms-border text-wms-text p-2 text-xs outline-none">
            </div>
            <div>
              <label class="block text-[9px] text-slate-500 uppercase font-bold mb-2">Company Name</label>
              <input v-model="form.company_name" type="text" class="w-full bg-wms-surface border border-wms-border text-wms-text p-2 text-xs outline-none">
            </div>
            <div>
              <label class="block text-[9px] text-slate-500 uppercase font-bold mb-2">Address 1 *</label>
              <input v-model="form.address1" type="text" class="w-full bg-wms-surface border border-wms-border text-wms-text p-2 text-xs outline-none">
            </div>
            <div>
              <label class="block text-[9px] text-slate-500 uppercase font-bold mb-2">City/Township *</label>
              <input v-model="form.city" type="text" class="w-full bg-wms-surface border border-wms-border text-wms-text p-2 text-xs outline-none">
            </div>
            <div>
              <label class="block text-[9px] text-slate-500 uppercase font-bold mb-2">State/Province *</label>
              <input v-model="form.state" type="text" class="w-full bg-wms-surface border border-wms-border text-wms-text p-2 text-xs outline-none">
            </div>
            <div>
              <label class="block text-[9px] text-slate-500 uppercase font-bold mb-2">Postal Code *</label>
              <input v-model="form.postal_code" type="text" class="w-full bg-wms-surface border border-wms-border text-wms-text p-2 text-xs outline-none">
            </div>
          </div>
        </div>
      </div>

      <div v-if="activeTab === 'items'" class="space-y-6">
        <div class="flex justify-between items-center">
          <div class="flex items-center gap-4">
            <h4 class="text-[10px] text-indigo-400 font-bold uppercase tracking-widest italic">Order Line Items</h4>
            <span v-if="isUpdatingSkus" class="text-[9px] text-amber-500 animate-pulse font-bold tracking-tighter">Syncing Catalog...</span>
          </div>
          <button @click="addItemLine" :disabled="!form.client_id" class="bg-indigo-600 hover:bg-indigo-500 disabled:opacity-20 text-wms-text px-3 py-1 text-[9px] font-bold uppercase rounded-sm">+ Add Line Item</button>
        </div>

        <div v-if="!form.client_id" class="p-20 text-center border-2 border-dashed border-wms-border rounded text-slate-600 uppercase text-[10px] font-bold tracking-widest">
           Please select a Customer in the "Contact Details" tab first.
        </div>
        
        <div v-else class="bg-white rounded-sm overflow-hidden border border-slate-200 shadow-xl">
          <table class="w-full text-left">
            <thead class="bg-[#cbd5e1] text-[9px] text-slate-700 uppercase font-bold border-b border-slate-300">
              <tr>
                <th class="p-3">SKU *</th>
                <th class="p-3">Qty *</th>
                <th class="p-3">Price</th>
                <th class="p-3">Weight (lbs)</th>
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
                  <input v-model.number="line.qty" type="number" min="1" class="w-24 border border-slate-300 p-1.5 outline-none">
                </td>
                <td class="p-3 font-mono text-slate-500 italic">
                  <input v-model.number="line.price" type="number" step="0.01" class="w-24 border border-slate-300 p-1.5 outline-none">
                </td>
                <td class="p-3">
                   <input v-model.number="line.weight" type="number" step="0.01" class="w-24 border border-slate-300 p-1.5 outline-none">
                </td>
                <td class="p-3">
                  <button @click="removeItemLine(index)" class="text-rose-500 font-black">X</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div v-if="activeTab === 'carrier'" class="grid grid-cols-1 md:grid-cols-2 gap-10 max-w-5xl">
         <div class="space-y-6">
            <h4 class="text-[10px] text-indigo-400 font-bold uppercase tracking-widest border-b border-wms-border pb-2">Carrier Information</h4>
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-[9px] text-slate-500 uppercase font-bold mb-2">Carrier Name</label>
                <input v-model="form.carrier" type="text" class="w-full bg-wms-surface border border-wms-border text-wms-text p-2 text-xs outline-none">
              </div>
              <div>
                <label class="block text-[9px] text-slate-500 uppercase font-bold mb-2">SCAC</label>
                <input v-model="form.scac" type="text" class="w-full bg-wms-surface border border-wms-border text-wms-text p-2 text-xs outline-none">
              </div>
            </div>
            <div>
              <label class="block text-[9px] text-slate-500 uppercase font-bold mb-2">Tracking Number</label>
              <input v-model="form.tracking_number" type="text" class="w-full bg-wms-surface border border-wms-border text-wms-text p-2 text-xs outline-none">
            </div>
         </div>

         <div class="space-y-6">
            <h4 class="text-[10px] text-indigo-400 font-bold uppercase tracking-widest border-b border-wms-border pb-2">Routing Details</h4>
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-[9px] text-slate-500 uppercase font-bold mb-2">BOL Number</label>
                <input v-model="form.bol_number" type="text" class="w-full bg-wms-surface border border-wms-border text-wms-text p-2 text-xs outline-none font-mono">
              </div>
              <div>
                <label class="block text-[9px] text-slate-500 uppercase font-bold mb-2">Door / Dock</label>
                <input v-model="form.door" type="text" class="w-full bg-wms-surface border border-wms-border text-wms-text p-2 text-xs outline-none">
              </div>
            </div>
            <div>
              <label class="block text-[9px] text-slate-500 uppercase font-bold mb-2">Pickup Date/Time</label>
              <input v-model="form.pickup_date" type="datetime-local" class="w-full bg-wms-surface border border-wms-border text-wms-text p-2 text-xs outline-none">
            </div>
         </div>
      </div>

    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, watch } from 'vue';
import { useOrderStore } from '../store/order';
import { AlertTriangleIcon, XIcon } from 'lucide-vue-next';
import apiClient from '../api/client';

const emit = defineEmits(['cancel', 'success']);
const orderStore = useOrderStore();
const localError = ref<string | null>(null);
const isUpdatingSkus = ref(false);

const tabs = [
  { id: 'contact', label: 'Order Contact Details' },
  { id: 'items', label: 'Order Line Items' },
  { id: 'carrier', label: 'Carrier and Routing' }
];
const activeTab = ref('contact');

const clients = ref<any[]>([]);
const warehouses = ref<any[]>([]);
const skus = ref<any[]>([]);

const form = reactive({
  order_number: '',
  transaction_id: '',
  client_id: '',
  warehouse_id: '',
  recipient_name: '',
  company_name: '',
  address1: '',
  city: '',
  state: '',
  postal_code: '',
  carrier: '',
  bol_number: '',
  items: [{ sku_id: '', qty: 1, price: 0, weight: 0 }]
});

// 监听客户变化，自动清空并过滤物料 [Cite: 之前 turns 的逻辑]
watch(() => form.client_id, async (newId) => {
  if (newId) {
    isUpdatingSkus.value = true;
    const res = await apiClient.get(`/warehouses/sku/?client_id=${newId}`);
    skus.value = res.data;
    form.items = [{ sku_id: '', qty: 1, price: 0, weight: 0 }];
    isUpdatingSkus.value = false;
  }
});

onMounted(async () => {
  const [cRes, wRes] = await Promise.all([
    apiClient.get('/warehouses/client/'),
    apiClient.get('/warehouses/warehouse/')
  ]);
  clients.value = cRes.data;
  warehouses.value = wRes.data;
});

const addItemLine = () => form.items.push({ sku_id: '', qty: 1, price: 0, weight: 0 });
const removeItemLine = (idx: number) => form.items.splice(idx, 1);
const clearErrors = () => { orderStore.error = null; localError.value = null; };

const submitForm = async () => {
  if (!form.client_id || !form.order_number || !form.transaction_id) {
    localError.value = "REQUIRED: Customer, Ref Number, and Transaction ID are mandatory.";
    activeTab.value = 'contact';
    return;
  }
  try {
    await orderStore.createOrder(form);
    emit('success');
  } catch (err) {}
};
</script>