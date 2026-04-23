<template>
  <div class="flex flex-col h-full bg-wms-bg border border-wms-border animate-in fade-in zoom-in-95 duration-300">
    
    <div v-if="orderStore.error || localError" class="bg-rose-600 p-3 border-b border-rose-900 flex items-center justify-between z-30">
      <div class="flex items-center gap-3">
        <AlertCircle class="text-wms-text animate-pulse" :size="18" />
        <pre class="text-[10px] font-mono text-wms-text whitespace-pre-wrap">{{ orderStore.error || localError }}</pre>
      </div>
      <button @click="clearErrors" class="text-wms-text/50 hover:text-wms-text"><X :size="14" /></button>
    </div>

    <div class="p-4 border-b border-wms-border flex justify-between items-center bg-wms-header">
      <div class="flex items-center gap-4">
        <h2 class="text-wms-text text-xs font-bold uppercase tracking-[0.2em]">Create Outbound Order</h2>
        <div v-if="form.order_number" class="px-2 py-0.5 bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-[9px] font-mono">REF: {{ form.order_number }}</div>
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
        :class="['px-6 py-3 text-[9px] uppercase font-bold tracking-widest transition-all border-b-2', activeTab === tab.id ? 'border-indigo-500 text-indigo-400 bg-indigo-500/5' : 'border-transparent text-slate-500 hover:text-slate-300']">
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
            <label class="block text-[9px] text-slate-500 uppercase font-bold mb-2">Transaction ID (Auto)</label>
            <input v-model="form.transaction_id" type="text" readonly placeholder="Auto-generated on save" class="w-full bg-wms-surface/60 border border-wms-border text-slate-400 p-2 text-xs font-mono cursor-not-allowed">
          </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6 p-6 bg-white/5 border border-wms-border">
          <div>
            <label class="block text-[9px] text-slate-500 uppercase font-bold mb-2">Recipient Name</label>
            <input v-model="form.recipient_name" type="text" class="w-full bg-wms-surface border border-wms-border text-wms-text p-2 text-xs outline-none">
          </div>
          <div>
            <label class="block text-[9px] text-slate-500 uppercase font-bold mb-2">Company Name</label>
            <input v-model="form.company_name" type="text" class="w-full bg-wms-surface border border-wms-border text-wms-text p-2 text-xs outline-none">
          </div>
          <div>
            <label class="block text-[9px] text-slate-500 uppercase font-bold mb-2">Address 1</label>
            <input v-model="form.address1" type="text" class="w-full bg-wms-surface border border-wms-border text-wms-text p-2 text-xs outline-none">
          </div>
          <div>
            <label class="block text-[9px] text-slate-500 uppercase font-bold mb-2">Address 2</label>
            <input v-model="form.address2" type="text" class="w-full bg-wms-surface border border-wms-border text-wms-text p-2 text-xs outline-none">
          </div>
          <div>
            <label class="block text-[9px] text-slate-500 uppercase font-bold mb-2">City</label>
            <input v-model="form.city" type="text" class="w-full bg-wms-surface border border-wms-border text-wms-text p-2 text-xs outline-none">
          </div>
          <div>
            <label class="block text-[9px] text-slate-500 uppercase font-bold mb-2">State / Province</label>
            <select v-model="form.state" class="w-full bg-wms-surface border border-wms-border text-wms-text p-2 text-xs outline-none">
              <option value="">-- Choose --</option>
              <option v-for="r in regions" :key="`${r.country}-${r.code}`" :value="r.name">{{ r.name }}</option>
            </select>
          </div>
          <div>
            <label class="block text-[9px] text-slate-500 uppercase font-bold mb-2">Postal Code</label>
            <input v-model="form.postal_code" type="text" class="w-full bg-wms-surface border border-wms-border text-wms-text p-2 text-xs outline-none">
          </div>
          <div>
            <label class="block text-[9px] text-slate-500 uppercase font-bold mb-2">Country</label>
            <select v-model="form.country" class="w-full bg-wms-surface border border-wms-border text-wms-text p-2 text-xs outline-none">
              <option value="">-- Choose --</option>
              <option v-for="c in countries" :key="c.code" :value="c.name">{{ c.name }}</option>
            </select>
          </div>
          <div>
            <label class="block text-[9px] text-slate-500 uppercase font-bold mb-2">Earliest Ship Date</label>
            <input v-model="form.earliest_ship_date" type="datetime-local" class="w-full bg-wms-surface border border-wms-border text-wms-text p-2 text-xs outline-none">
          </div>
          <div>
            <label class="block text-[9px] text-slate-500 uppercase font-bold mb-2">Purchase Order</label>
            <input v-model="form.purchase_order" type="text" class="w-full bg-wms-surface border border-wms-border text-wms-text p-2 text-xs outline-none">
          </div>
          <div>
            <label class="block text-[9px] text-slate-500 uppercase font-bold mb-2">Created By</label>
            <select v-model="form.created_by" class="w-full bg-wms-surface border border-wms-border text-wms-text p-2 text-xs outline-none">
              <option value="">-- Choose --</option>
              <option v-for="u in users" :key="u.id" :value="u.display_name">{{ u.display_name }}</option>
            </select>
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

        <div class="space-y-3">
          <div
            v-for="(item, idx) in form.items"
            :key="idx"
            class="grid grid-cols-1 md:grid-cols-12 gap-3 p-4 bg-white/5 border border-wms-border items-end"
          >
            <div class="md:col-span-6">
              <label class="block text-[9px] text-slate-500 uppercase font-bold mb-2">SKU *</label>
              <select v-model="item.sku_id" class="w-full bg-wms-surface border border-wms-border text-wms-text p-2 text-xs outline-none">
                <option value="">-- Choose SKU --</option>
                <option v-for="sku in skus" :key="sku.id" :value="sku.id">
                  {{ sku.part_number }}
                </option>
              </select>
            </div>

            <div class="md:col-span-2">
              <label class="block text-[9px] text-slate-500 uppercase font-bold mb-2">Qty *</label>
              <input v-model.number="item.qty" type="number" min="1" class="w-full bg-wms-surface border border-wms-border text-wms-text p-2 text-xs font-mono outline-none">
            </div>

            <div class="md:col-span-2">
              <label class="block text-[9px] text-slate-500 uppercase font-bold mb-2">UOM</label>
              <input v-model="item.uom" type="text" placeholder="Each" class="w-full bg-wms-surface border border-wms-border text-wms-text p-2 text-xs font-mono outline-none">
            </div>

            <div class="md:col-span-1">
              <label class="block text-[9px] text-slate-500 uppercase font-bold mb-2">Price</label>
              <input v-model.number="item.price" type="number" min="0" step="0.01" class="w-full bg-wms-surface border border-wms-border text-wms-text p-2 text-xs font-mono outline-none">
            </div>

            <div class="md:col-span-1 flex justify-end">
              <button
                @click="removeItemLine(idx)"
                type="button"
                class="px-3 py-2 text-[9px] font-bold uppercase border border-rose-500/20 text-rose-400 hover:bg-rose-500/10 transition-colors"
                :disabled="form.items.length === 1"
              >
                Remove
              </button>
            </div>
          </div>

          <div v-if="form.items.length === 0" class="text-[10px] text-slate-500 italic border border-dashed border-wms-border p-4">
            No line items yet. Click + Add Line Item to continue.
          </div>
        </div>
      </div>

      <div v-if="activeTab === 'carrier'" class="space-y-6 max-w-6xl">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 p-6 bg-white/5 border border-wms-border">
          <div>
            <label class="block text-[9px] text-slate-500 uppercase font-bold mb-2">Carrier</label>
            <input v-model="form.carrier" type="text" class="w-full bg-wms-surface border border-wms-border text-wms-text p-2 text-xs outline-none">
          </div>
          <div>
            <label class="block text-[9px] text-slate-500 uppercase font-bold mb-2">SCAC</label>
            <input v-model="form.scac" type="text" class="w-full bg-wms-surface border border-wms-border text-wms-text p-2 text-xs outline-none">
          </div>
          <div>
            <label class="block text-[9px] text-slate-500 uppercase font-bold mb-2">Service</label>
            <input v-model="form.service" type="text" class="w-full bg-wms-surface border border-wms-border text-wms-text p-2 text-xs outline-none">
          </div>
          <div>
            <label class="block text-[9px] text-slate-500 uppercase font-bold mb-2">Billing Type</label>
            <input v-model="form.billing_type" type="text" class="w-full bg-wms-surface border border-wms-border text-wms-text p-2 text-xs outline-none">
          </div>
          <div>
            <label class="block text-[9px] text-slate-500 uppercase font-bold mb-2">Account Number</label>
            <input v-model="form.account_number" type="text" class="w-full bg-wms-surface border border-wms-border text-wms-text p-2 text-xs outline-none">
          </div>
          <div>
            <label class="block text-[9px] text-slate-500 uppercase font-bold mb-2">Account Zip</label>
            <input v-model="form.account_zip" type="text" class="w-full bg-wms-surface border border-wms-border text-wms-text p-2 text-xs outline-none">
          </div>
          <div>
            <label class="block text-[9px] text-slate-500 uppercase font-bold mb-2">Tracking Number</label>
            <input v-model="form.tracking_number" type="text" class="w-full bg-wms-surface border border-wms-border text-wms-text p-2 text-xs outline-none">
          </div>
          <div>
            <label class="block text-[9px] text-slate-500 uppercase font-bold mb-2">Load Number</label>
            <input v-model="form.load_number" type="text" class="w-full bg-wms-surface border border-wms-border text-wms-text p-2 text-xs outline-none">
          </div>
          <div>
            <label class="block text-[9px] text-slate-500 uppercase font-bold mb-2">BOL Number</label>
            <input v-model="form.bol_number" type="text" class="w-full bg-wms-surface border border-wms-border text-wms-text p-2 text-xs outline-none">
          </div>
          <div>
            <label class="block text-[9px] text-slate-500 uppercase font-bold mb-2">Trailer Number</label>
            <input v-model="form.trailer_number" type="text" class="w-full bg-wms-surface border border-wms-border text-wms-text p-2 text-xs outline-none">
          </div>
          <div>
            <label class="block text-[9px] text-slate-500 uppercase font-bold mb-2">Seal Number</label>
            <input v-model="form.seal_number" type="text" class="w-full bg-wms-surface border border-wms-border text-wms-text p-2 text-xs outline-none">
          </div>
          <div>
            <label class="block text-[9px] text-slate-500 uppercase font-bold mb-2">Door</label>
            <input v-model="form.door" type="text" class="w-full bg-wms-surface border border-wms-border text-wms-text p-2 text-xs outline-none">
          </div>
          <div>
            <label class="block text-[9px] text-slate-500 uppercase font-bold mb-2">Capacity Type</label>
            <input v-model="form.capacity_type" type="text" class="w-full bg-wms-surface border border-wms-border text-wms-text p-2 text-xs outline-none">
          </div>
          <div>
            <label class="block text-[9px] text-slate-500 uppercase font-bold mb-2">Pickup Date</label>
            <input v-model="form.pickup_date" type="datetime-local" class="w-full bg-wms-surface border border-wms-border text-wms-text p-2 text-xs outline-none">
          </div>
          <div>
            <label class="block text-[9px] text-slate-500 uppercase font-bold mb-2">Packaging UOM</label>
            <input v-model="form.packaging_uom" type="text" class="w-full bg-wms-surface border border-wms-border text-wms-text p-2 text-xs outline-none">
          </div>
          <div>
            <label class="block text-[9px] text-slate-500 uppercase font-bold mb-2">MU UOM</label>
            <input v-model="form.mu_uom" type="text" class="w-full bg-wms-surface border border-wms-border text-wms-text p-2 text-xs outline-none">
          </div>
        </div>

        <div class="grid grid-cols-2 md:grid-cols-4 gap-4 p-6 bg-white/5 border border-wms-border">
          <label class="flex items-center gap-2 text-[10px] text-slate-300 uppercase font-bold">
            <input v-model="form.require_return_receipt" type="checkbox" class="accent-indigo-500">
            Return Receipt
          </label>
          <label class="flex items-center gap-2 text-[10px] text-slate-300 uppercase font-bold">
            <input v-model="form.saturday_delivery" type="checkbox" class="accent-indigo-500">
            Saturday Delivery
          </label>
          <label class="flex items-center gap-2 text-[10px] text-slate-300 uppercase font-bold">
            <input v-model="form.residential_delivery" type="checkbox" class="accent-indigo-500">
            Residential Delivery
          </label>
          <label class="flex items-center gap-2 text-[10px] text-slate-300 uppercase font-bold">
            <input v-model="form.insurance" type="checkbox" class="accent-indigo-500">
            Insurance
          </label>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-4 gap-6 p-6 bg-white/5 border border-wms-border">
          <div>
            <label class="block text-[9px] text-slate-500 uppercase font-bold mb-2">Insurance Amount</label>
            <input v-model.number="form.insurance_amount" type="number" min="0" step="0.01" class="w-full bg-wms-surface border border-wms-border text-wms-text p-2 text-xs font-mono outline-none">
          </div>
          <div>
            <label class="block text-[9px] text-slate-500 uppercase font-bold mb-2">Total Packages</label>
            <input v-model.number="form.total_packages" type="number" min="0" class="w-full bg-wms-surface border border-wms-border text-wms-text p-2 text-xs font-mono outline-none">
          </div>
          <div>
            <label class="block text-[9px] text-slate-500 uppercase font-bold mb-2">Total Weight</label>
            <input v-model.number="form.total_weight" type="number" min="0" step="0.0001" class="w-full bg-wms-surface border border-wms-border text-wms-text p-2 text-xs font-mono outline-none">
          </div>
          <div>
            <label class="block text-[9px] text-slate-500 uppercase font-bold mb-2">Total Movable Units</label>
            <input v-model.number="form.total_movable_units" type="number" min="0" class="w-full bg-wms-surface border border-wms-border text-wms-text p-2 text-xs font-mono outline-none">
          </div>
          <div>
            <label class="block text-[9px] text-slate-500 uppercase font-bold mb-2">Total Volume</label>
            <input v-model.number="form.total_volume" type="number" min="0" step="0.0001" class="w-full bg-wms-surface border border-wms-border text-wms-text p-2 text-xs font-mono outline-none">
          </div>
        </div>

        <div class="grid grid-cols-1 gap-6 p-6 bg-white/5 border border-wms-border">
          <div>
            <label class="block text-[9px] text-slate-500 uppercase font-bold mb-2">Warehouse Instructions</label>
            <textarea v-model="form.warehouse_instructions" rows="3" class="w-full bg-wms-surface border border-wms-border text-wms-text p-2 text-xs outline-none"></textarea>
          </div>
          <div>
            <label class="block text-[9px] text-slate-500 uppercase font-bold mb-2">Carrier Instructions</label>
            <textarea v-model="form.carrier_instructions" rows="3" class="w-full bg-wms-surface border border-wms-border text-wms-text p-2 text-xs outline-none"></textarea>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, watch } from 'vue';
import { useOrderStore } from '../store/order';
// 【修复】使用安全的图标命名
import { AlertCircle, X } from 'lucide-vue-next';
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
const users = ref<any[]>([]);
const countries = ref<any[]>([]);
const regions = ref<any[]>([]);

type OrderLineItem = {
  sku_id: string;
  qty: number;
  price: number;
  weight: number;
  uom: string;
};

const form = reactive({
  order_number: '',
  transaction_id: '',
  client_id: '',
  warehouse_id: '',
  recipient_name: '',
  company_name: '',
  address1: '',
  address2: '',
  city: '',
  state: '',
  postal_code: '',
  country: '',
  earliest_ship_date: '',
  purchase_order: '',
  created_by: '',
  carrier: '',
  scac: '',
  service: '',
  billing_type: '',
  account_number: '',
  account_zip: '',
  tracking_number: '',
  warehouse_instructions: '',
  carrier_instructions: '',
  load_number: '',
  bol_number: '',
  trailer_number: '',
  seal_number: '',
  door: '',
  capacity_type: '',
  pickup_date: '',
  require_return_receipt: false,
  saturday_delivery: false,
  residential_delivery: false,
  insurance: false,
  insurance_amount: 0,
  total_packages: 0,
  packaging_uom: '',
  total_weight: 0,
  total_movable_units: 0,
  mu_uom: '',
  total_volume: 0,
  items: [{ sku_id: '', qty: 1, price: 0, weight: 0, uom: 'Each' }] as OrderLineItem[]
});

// 【核心修复】请求物料列表时的分页兼容
watch(() => form.client_id, async (newId) => {
  if (newId) {
    isUpdatingSkus.value = true;
    try {
      const res = await apiClient.get(`/warehouses/sku/?client_id=${newId}`);
      skus.value = Array.isArray(res.data) ? res.data : (res.data?.results || []);
      form.items = [{ sku_id: '', qty: 1, price: 0, weight: 0, uom: 'Each' }]
    } catch (e) {}
    isUpdatingSkus.value = false;
  }
});

watch(() => form.country, async (countryName) => {
  form.state = '';
  const matchedCountry = countries.value.find(c => c.name === countryName);
  if (!matchedCountry?.code) {
    regions.value = [];
    return;
  }

  try {
    const response = await apiClient.get(`/warehouses/regions/?country=${matchedCountry.code}`);
    regions.value = Array.isArray(response.data) ? response.data : [];
  } catch {
    regions.value = [];
  }
});

// 【核心修复】请求基础信息时的分页兼容
onMounted(async () => {
  try {
    const [cRes, wRes, uRes, countryRes] = await Promise.all([
      apiClient.get('/warehouses/client/'),
      apiClient.get('/warehouses/warehouse/'),
      apiClient.get('/warehouses/users/'),
      apiClient.get('/warehouses/countries/')
    ]);
    clients.value = Array.isArray(cRes.data) ? cRes.data : (cRes.data?.results || []);
    warehouses.value = Array.isArray(wRes.data) ? wRes.data : (wRes.data?.results || []);
    users.value = Array.isArray(uRes.data) ? uRes.data : [];
    countries.value = Array.isArray(countryRes.data) ? countryRes.data : [];
  } catch (e) {}
});

const addItemLine = () => form.items.push({ sku_id: '', qty: 1, price: 0, weight: 0, uom: 'Each' });
const removeItemLine = (idx: number) => form.items.splice(idx, 1);
const clearErrors = () => { orderStore.error = null; localError.value = null; };

const submitForm = async () => {
  if (!form.client_id || !form.order_number) {
    localError.value = "REQUIRED: Customer and Ref Number are mandatory.";
    activeTab.value = 'contact';
    return;
  }

  const invalidLine = form.items.some(item => !item.sku_id || Number(item.qty) <= 0);
  if (invalidLine) {
    localError.value = 'REQUIRED: Every line item needs a SKU and a quantity greater than 0.';
    activeTab.value = 'items';
    return;
  }

  try {
    const payload = {
      ...form,
      transaction_id: form.transaction_id?.trim() || undefined,
      items: form.items.map(item => ({
        sku_id: item.sku_id,
        qty: Number(item.qty),
        uom: item.uom || 'Each',
        price: Number(item.price) || 0,
      }))
    };

    await orderStore.createOrder(payload);
    emit('success');
  } catch (err) {}
};
</script>