<!-- src/components/master_data/SkuTab.vue -->
<template>
  <div class="h-full flex flex-col space-y-4 animate-in fade-in duration-300">
    <!-- Header / Action Bar -->
    <div class="flex justify-between items-center bg-wms-bg border border-wms-border p-4 shrink-0 shadow-sm">
      <h3 class="text-[11px] font-bold text-wms-text uppercase tracking-widest flex items-center gap-2">
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-indigo-500"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path><polyline points="3.27 6.96 12 12.01 20.73 6.96"></polyline><line x1="12" y1="22.08" x2="12" y2="12"></line></svg>
        Product Master (SKU)
      </h3>
      <div class="flex gap-3">
        <button @click="fetchSkus" class="px-4 py-1.5 border border-indigo-500/30 text-indigo-400 hover:bg-indigo-500/10 text-[10px] font-bold uppercase tracking-widest transition-colors flex items-center gap-2">
           <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" :class="{'animate-spin': isLoading}"><polyline points="23 4 23 10 17 10"></polyline><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"></path></svg>
           Refresh Data
        </button>
        <button @click="openModal()" class="px-4 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-wms-text text-[10px] font-bold uppercase tracking-widest shadow-lg transition-colors">
          + New SKU
        </button>
      </div>
    </div>

    <!-- Error Banner -->
    <div v-if="error" class="bg-rose-500/10 border border-rose-500/20 p-3 text-rose-400 text-[10px] font-bold uppercase tracking-widest flex justify-between items-center z-10">
      <span class="flex items-center gap-2">
        <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>
        {{ error }}
      </span>
      <button @click="error = null" class="underline hover:text-white">Dismiss</button>
    </div>

    <!-- Data Table -->
    <div class="flex-1 overflow-y-auto border border-wms-border bg-wms-bg relative custom-scrollbar">
      <div v-if="isLoading" class="absolute inset-0 flex items-center justify-center bg-wms-bg/50 backdrop-blur-sm z-10">
        <span class="text-indigo-400 text-[10px] uppercase font-bold tracking-widest animate-pulse">Loading Catalog...</span>
      </div>
      
      <table class="w-full text-left border-collapse whitespace-nowrap">
        <thead class="bg-wms-header text-[9px] text-slate-500 uppercase tracking-[0.2em] font-bold sticky top-0 z-10 shadow-sm border-b border-wms-border">
          <tr>
            <th class="px-4 py-3 border-r border-wms-border/50 text-center w-10">Status</th>
            <th class="px-4 py-3 border-r border-wms-border/50">Client / Owner</th>
            <th class="px-4 py-3 border-r border-wms-border/50">Part Number (Code)</th>
            <th class="px-4 py-3 border-r border-wms-border/50">Product Name</th>
            <th class="px-4 py-3 border-r border-wms-border/50 text-center">Tracking</th>
            <th class="px-4 py-3 border-r border-wms-border/50 text-right">UOM</th>
            <th class="px-4 py-3 text-right">Actions</th>
          </tr>
        </thead>
        <tbody class="text-[11px] text-slate-300 font-medium">
          <tr v-if="skus.length === 0 && !isLoading">
            <td colspan="7" class="px-4 py-12 text-center text-slate-600 italic uppercase tracking-widest text-[10px]">No products in master catalog.</td>
          </tr>
          <tr v-for="sku in skus" :key="sku.id" class="border-b border-wms-border/30 hover:bg-white/[0.02] transition-colors">
            <td class="px-4 py-3 border-r border-wms-border/50 text-center">
              <div class="w-2.5 h-2.5 rounded-full mx-auto" :class="sku.is_active ? 'bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]' : 'bg-slate-600'"></div>
            </td>
            <!-- 使用 Serializer 传来的客户名称翻译 -->
            <td class="px-4 py-3 border-r border-wms-border/50 font-bold text-slate-200">{{ sku.client_name || getClientName(sku.client) }}</td>
            <td class="px-4 py-3 border-r border-wms-border/50 font-mono text-indigo-400 font-bold">{{ sku.part_number }}</td>
            <td class="px-4 py-3 border-r border-wms-border/50">{{ sku.name }}</td>
            <td class="px-4 py-3 border-r border-wms-border/50 text-center">
              <span v-if="sku.track_by !== 'NONE'" class="px-2 py-0.5 border border-indigo-500/30 bg-indigo-500/10 text-indigo-300 text-[9px] uppercase tracking-widest rounded-sm">{{ sku.track_by }}</span>
              <span v-else class="text-slate-500 text-[9px] uppercase tracking-widest">--</span>
            </td>
            <td class="px-4 py-3 border-r border-wms-border/50 text-right font-mono text-slate-400">{{ sku.uom }}</td>
            <td class="px-4 py-3 text-right space-x-4">
              <button @click="openModal(sku)" class="text-indigo-400 hover:text-indigo-300 uppercase text-[9px] font-bold tracking-widest transition-colors">Edit</button>
              <button @click="deleteSku(sku.id)" class="text-rose-500 hover:text-rose-400 uppercase text-[9px] font-bold tracking-widest transition-colors">Delete</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Create / Edit Modal -->
    <div v-if="isModalOpen" class="fixed inset-0 z-[100] flex items-center justify-center bg-black/80 backdrop-blur-sm animate-in fade-in duration-200 p-4">
      <div class="bg-wms-bg border border-wms-border w-full max-w-5xl shadow-2xl flex flex-col max-h-[90vh]">
        
        <div class="p-5 border-b border-wms-border bg-wms-header flex justify-between items-center shrink-0">
          <h4 class="text-wms-text text-xs font-bold uppercase tracking-[0.2em] flex items-center gap-3">
            <div class="w-1 h-5 bg-indigo-500"></div>
            {{ isEditing ? 'Edit Master SKU' : 'Register New SKU' }}
          </h4>
          <div class="flex items-center gap-4">
            <label class="flex items-center gap-2 cursor-pointer group">
              <span class="text-[10px] uppercase font-bold tracking-widest" :class="form.is_active ? 'text-emerald-400' : 'text-slate-500'">{{ form.is_active ? 'Active' : 'Inactive' }}</span>
              <div class="w-10 h-5 bg-slate-700 rounded-full relative transition-colors duration-300" :class="{'bg-emerald-500/30 border border-emerald-500/50': form.is_active}">
                <div class="absolute top-0.5 left-0.5 w-4 h-4 bg-slate-400 rounded-full transition-transform duration-300" :class="{'translate-x-5 bg-emerald-400': form.is_active}"></div>
              </div>
              <input type="checkbox" v-model="form.is_active" class="hidden">
            </label>
            <button @click="isModalOpen = false" class="text-slate-500 hover:text-wms-text transition-colors">
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
            </button>
          </div>
        </div>
        
        <form @submit.prevent="saveSku" class="overflow-y-auto custom-scrollbar flex-1 p-6 space-y-8">
          
          <!-- Section 1: Identity & Ownership -->
          <div>
            <h5 class="text-[10px] text-indigo-400 uppercase tracking-widest font-bold border-b border-wms-border pb-2 mb-4">1. Identity & Ownership</h5>
            <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div class="col-span-1 md:col-span-2">
                <label class="block text-[9px] text-slate-500 uppercase font-bold mb-2 tracking-widest">Client / Owner *</label>
                <select v-model="form.client" required :disabled="isEditing" class="w-full bg-wms-surface border border-wms-border text-wms-text p-2.5 text-xs outline-none focus:border-indigo-500 transition-colors disabled:opacity-50">
                  <option value="">-- Select Client --</option>
                  <option v-for="client in dropdowns.clients" :key="client.id" :value="client.id">{{ client.name }}</option>
                </select>
                <p v-if="isEditing" class="text-rose-400 text-[8px] mt-1 uppercase tracking-widest">Client cannot be changed after creation.</p>
              </div>
              <div class="col-span-1 md:col-span-2">
                <label class="block text-[9px] text-slate-500 uppercase font-bold mb-2 tracking-widest">Part Number (SKU Code) *</label>
                <input v-model="form.part_number" type="text" required :disabled="isEditing" class="w-full bg-wms-surface border border-wms-border text-wms-text p-2.5 text-xs outline-none focus:border-indigo-500 font-mono transition-colors disabled:opacity-50">
              </div>
              <div class="col-span-1 md:col-span-3">
                <label class="block text-[9px] text-slate-500 uppercase font-bold mb-2 tracking-widest">Product Name *</label>
                <input v-model="form.name" type="text" required class="w-full bg-wms-surface border border-wms-border text-wms-text p-2.5 text-xs outline-none focus:border-indigo-500 transition-colors">
              </div>
              <div class="col-span-1">
                <label class="block text-[9px] text-slate-500 uppercase font-bold mb-2 tracking-widest">Primary Barcode</label>
                <input v-model="form.barcode" type="text" class="w-full bg-wms-surface border border-wms-border text-wms-text p-2.5 text-xs outline-none focus:border-indigo-500 font-mono transition-colors">
              </div>
            </div>
          </div>

          <!-- Section 2: Physical Dimensions -->
          <div>
            <h5 class="text-[10px] text-indigo-400 uppercase tracking-widest font-bold border-b border-wms-border pb-2 mb-4">2. Physical Dimensions (Metric)</h5>
            <div class="grid grid-cols-2 md:grid-cols-5 gap-4">
              <div class="col-span-1">
                <label class="block text-[9px] text-slate-500 uppercase font-bold mb-2 tracking-widest">Length (mm)</label>
                <input v-model="form.length" type="number" step="0.01" min="0" class="w-full bg-wms-surface border border-wms-border text-wms-text p-2.5 text-xs outline-none focus:border-indigo-500 font-mono transition-colors">
              </div>
              <div class="col-span-1">
                <label class="block text-[9px] text-slate-500 uppercase font-bold mb-2 tracking-widest">Width (mm)</label>
                <input v-model="form.width" type="number" step="0.01" min="0" class="w-full bg-wms-surface border border-wms-border text-wms-text p-2.5 text-xs outline-none focus:border-indigo-500 font-mono transition-colors">
              </div>
              <div class="col-span-1">
                <label class="block text-[9px] text-slate-500 uppercase font-bold mb-2 tracking-widest">Height (mm)</label>
                <input v-model="form.height" type="number" step="0.01" min="0" class="w-full bg-wms-surface border border-wms-border text-wms-text p-2.5 text-xs outline-none focus:border-indigo-500 font-mono transition-colors">
              </div>
              <div class="col-span-1">
                <label class="block text-[9px] text-emerald-500 uppercase font-bold mb-2 tracking-widest">Est. Volume (mm³)</label>
                <!-- Vue实时计算体积，只读显示 -->
                <input :value="calculatedVolume" type="text" disabled class="w-full bg-wms-surface/50 border border-emerald-500/30 text-emerald-400 p-2.5 text-xs outline-none font-mono opacity-80 cursor-not-allowed">
              </div>
              <div class="col-span-1">
                <label class="block text-[9px] text-slate-500 uppercase font-bold mb-2 tracking-widest">Gross Weight (kg)</label>
                <input v-model="form.weight" type="number" step="0.001" min="0" class="w-full bg-wms-surface border border-wms-border text-wms-text p-2.5 text-xs outline-none focus:border-indigo-500 font-mono transition-colors">
              </div>
            </div>
          </div>

          <!-- Section 3: Inventory Policy & Traceability -->
          <div>
            <h5 class="text-[10px] text-indigo-400 uppercase tracking-widest font-bold border-b border-wms-border pb-2 mb-4">3. Inventory Policy & Traceability</h5>
            <div class="grid grid-cols-1 md:grid-cols-4 gap-4 items-start">
              <div class="col-span-1">
                <label class="block text-[9px] text-slate-500 uppercase font-bold mb-2 tracking-widest">Tracking Method</label>
                <select v-model="form.track_by" class="w-full bg-wms-surface border border-wms-border text-wms-text p-2.5 text-xs outline-none focus:border-indigo-500 transition-colors">
                  <option value="NONE">No Tracking</option>
                  <option value="BATCH">Batch / Lot Tracking</option>
                  <option value="SERIAL">Serial Number Tracking</option>
                </select>
              </div>
              <div class="col-span-1">
                <label class="block text-[9px] text-slate-500 uppercase font-bold mb-2 tracking-widest">Unit of Measure (UOM)</label>
                <input v-model="form.uom" type="text" placeholder="e.g. EA, CS" class="w-full bg-wms-surface border border-wms-border text-wms-text p-2.5 text-xs outline-none focus:border-indigo-500 font-mono transition-colors uppercase">
              </div>
              
              <div class="col-span-1 md:col-span-2 border border-wms-border p-4 bg-wms-surface/30">
                <label class="flex items-center gap-3 cursor-pointer group mb-4">
                  <div class="w-4 h-4 border flex items-center justify-center transition-colors" :class="form.is_expiry_managed ? 'border-indigo-500 bg-indigo-500/20' : 'border-slate-500 bg-wms-surface'">
                    <svg v-if="form.is_expiry_managed" xmlns="http://www.w3.org/2000/svg" width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="4" stroke-linecap="round" stroke-linejoin="round" class="text-indigo-400"><polyline points="20 6 9 17 4 12"></polyline></svg>
                  </div>
                  <input type="checkbox" v-model="form.is_expiry_managed" class="hidden">
                  <span class="text-[10px] uppercase font-bold tracking-widest text-indigo-300">Enable Expiry Management</span>
                </label>
                
                <div class="grid grid-cols-2 gap-4" :class="{'opacity-30 pointer-events-none': !form.is_expiry_managed}">
                  <div>
                    <label class="block text-[9px] text-slate-500 uppercase font-bold mb-2 tracking-widest">Shelf Life (Days)</label>
                    <input v-model="form.shelf_life_days" type="number" min="0" class="w-full bg-wms-surface border border-wms-border text-wms-text p-2.5 text-xs outline-none focus:border-indigo-500 font-mono transition-colors">
                  </div>
                  <div>
                    <label class="block text-[9px] text-slate-500 uppercase font-bold mb-2 tracking-widest">Min Inbound Life (%)</label>
                    <input v-model="form.min_inbound_shelf_life_percent" type="number" step="0.01" min="0" max="100" class="w-full bg-wms-surface border border-wms-border text-wms-text p-2.5 text-xs outline-none focus:border-indigo-500 font-mono transition-colors">
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Section 4: Operations & Specifications -->
          <div>
            <h5 class="text-[10px] text-indigo-400 uppercase tracking-widest font-bold border-b border-wms-border pb-2 mb-4">4. Operations & Specifications</h5>
            <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div class="col-span-1">
                <label class="block text-[9px] text-slate-500 uppercase font-bold mb-2 tracking-widest">Storage Condition</label>
                <select v-model="form.storage_condition" class="w-full bg-wms-surface border border-wms-border text-wms-text p-2.5 text-xs outline-none focus:border-indigo-500 transition-colors">
                  <option value="AMBIENT">Ambient / Normal</option>
                  <option value="CHILLED">Chilled / Cold</option>
                  <option value="FROZEN">Frozen</option>
                  <option value="HAZMAT">Hazardous Material</option>
                </select>
              </div>
              <div class="col-span-1">
                <label class="block text-[9px] text-slate-500 uppercase font-bold mb-2 tracking-widest">ABC Velocity Class</label>
                <select v-model="form.abc_analysis" class="w-full bg-wms-surface border border-wms-border text-wms-text p-2.5 text-xs outline-none focus:border-indigo-500 transition-colors">
                  <option value="A">A - High Velocity</option>
                  <option value="B">B - Medium Velocity</option>
                  <option value="C">C - Low Velocity</option>
                </select>
              </div>
              <div class="col-span-1 flex items-center pt-5">
                <label class="flex items-center gap-3 cursor-pointer group">
                  <div class="w-5 h-5 border border-wms-border bg-wms-surface flex items-center justify-center transition-colors group-hover:border-indigo-500" :class="{'bg-rose-500/20 border-rose-500': form.is_fragile}">
                    <svg v-if="form.is_fragile" xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="4" stroke-linecap="round" stroke-linejoin="round" class="text-rose-400"><polyline points="20 6 9 17 4 12"></polyline></svg>
                  </div>
                  <input type="checkbox" v-model="form.is_fragile" class="hidden">
                  <span class="text-[10px] uppercase font-bold tracking-widest text-slate-400 group-hover:text-wms-text transition-colors">Fragile Item</span>
                </label>
              </div>
              <div class="col-span-1 md:col-span-4">
                <label class="block text-[9px] text-slate-500 uppercase font-bold mb-2 tracking-widest">Technical Description</label>
                <textarea v-model="form.description" rows="3" class="w-full bg-wms-surface border border-wms-border text-wms-text p-2.5 text-xs outline-none focus:border-indigo-500 transition-colors resize-none"></textarea>
              </div>
            </div>
          </div>
          
        </form>

        <div class="p-5 border-t border-wms-border bg-wms-header flex justify-end gap-3 shrink-0">
          <button type="button" @click="isModalOpen = false" class="px-6 py-2 text-[10px] uppercase font-bold tracking-widest border border-wms-border text-slate-400 hover:text-wms-text hover:bg-white/5 transition-colors">
            Cancel
          </button>
          <button @click="saveSku" :disabled="isSaving" class="px-8 py-2 bg-indigo-600 hover:bg-indigo-500 text-wms-text text-[10px] font-bold uppercase tracking-widest disabled:opacity-50 shadow-lg transition-all">
            {{ isSaving ? 'Committing...' : 'Save Product SKU' }}
          </button>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue';
import apiClient from '../../api/client';

const skus = ref<any[]>([]);
const isLoading = ref(false);
const error = ref<string | null>(null);

const isModalOpen = ref(false);
const isEditing = ref(false);
const isSaving = ref(false);

const dropdowns = reactive({
  clients: [] as any[]
});

const form = reactive({
  id: '',
  client: '',
  part_number: '',
  barcode: '',
  name: '',
  description: '',
  length: 0,
  width: 0,
  height: 0,
  weight: 0,
  track_by: 'NONE',
  uom: 'EA',
  is_expiry_managed: false,
  shelf_life_days: 0,
  min_inbound_shelf_life_percent: 0,
  storage_condition: 'AMBIENT',
  is_fragile: false,
  abc_analysis: 'B',
  is_active: true
});

// 计算属性：前端实时预览体积
const calculatedVolume = computed(() => {
  return (Number(form.length) * Number(form.width) * Number(form.height)).toFixed(2);
});

// Helper Function: 转换 Client ID 为名称 (作为 fallback)
const getClientName = (id: string) => {
  if (!id) return '--';
  const cl = dropdowns.clients.find(c => c.id === id);
  return cl ? cl.name : id;
};

const fetchSkus = async () => {
  isLoading.value = true;
  error.value = null;
  try {
    const res = await apiClient.get('/warehouses/sku/list/');
    skus.value = Array.isArray(res.data) ? res.data : (res.data?.results || []);
  } catch (err: any) {
    error.value = "Failed to load master catalog from database.";
  } finally {
    isLoading.value = false;
  }
};

const fetchDictionaries = async () => {
  try {
    const cRes = await apiClient.get('/warehouses/client/').catch(() => ({ data: [] }));
    dropdowns.clients = Array.isArray(cRes.data) ? cRes.data : (cRes.data?.results || []);
  } catch (e) {
    console.error("Failed to load client dictionary.");
  }
};

const openModal = (sku: any = null) => {
  error.value = null;
  isEditing.value = !!sku;
  
  if (sku) {
    form.id = sku.id;
    form.client = sku.client || '';
    form.part_number = sku.part_number || '';
    form.barcode = sku.barcode || '';
    form.name = sku.name || '';
    form.description = sku.description || '';
    form.length = sku.length ?? 0;
    form.width = sku.width ?? 0;
    form.height = sku.height ?? 0;
    form.weight = sku.weight ?? 0;
    form.track_by = sku.track_by || 'NONE';
    form.uom = sku.uom || 'EA';
    form.is_expiry_managed = !!sku.is_expiry_managed;
    form.shelf_life_days = sku.shelf_life_days ?? 0;
    form.min_inbound_shelf_life_percent = sku.min_inbound_shelf_life_percent ?? 0;
    form.storage_condition = sku.storage_condition || 'AMBIENT';
    form.is_fragile = !!sku.is_fragile;
    form.abc_analysis = sku.abc_analysis || 'B';
    form.is_active = sku.is_active ?? true;
  } else {
    form.id = '';
    form.client = dropdowns.clients.length > 0 ? dropdowns.clients[0].id : ''; 
    form.part_number = '';
    form.barcode = '';
    form.name = '';
    form.description = '';
    form.length = 0;
    form.width = 0;
    form.height = 0;
    form.weight = 0;
    form.track_by = 'NONE';
    form.uom = 'EA';
    form.is_expiry_managed = false;
    form.shelf_life_days = 0;
    form.min_inbound_shelf_life_percent = 0;
    form.storage_condition = 'AMBIENT';
    form.is_fragile = false;
    form.abc_analysis = 'B';
    form.is_active = true;
  }
  
  isModalOpen.value = true;
};

const saveSku = async () => {
  if (!form.part_number || !form.client || !form.name) return;
  
  isSaving.value = true;
  error.value = null;
  
  const payload = { ...form };
  
  Object.keys(payload).forEach(key => {
    if (payload[key as keyof typeof payload] === '') {
      (payload as any)[key] = null;
    }
  });

  if (!isEditing.value) {
    delete (payload as any).id;
  }

  try {
    if (isEditing.value) {
      await apiClient.put(`/warehouses/sku/${form.id}/`, payload);
    } else {
      await apiClient.post('/warehouses/sku/list/', payload);
    }
    isModalOpen.value = false;
    await fetchSkus();
  } catch (err: any) {
    // 捕获多租户的 unique_together 冲突 (同一个 client 不能有相同 part_number)
    if (err.response?.status === 400 && err.response?.data?.non_field_errors) {
      error.value = "DUPLICATE SKU ERROR: This Part Number already exists for the selected Client.";
    } else if (err.response?.data) {
      error.value = `VALIDATION ERROR: ${JSON.stringify(err.response.data)}`;
    } else {
      error.value = "Failed to save SKU record. System error.";
    }
  } finally {
    isSaving.value = false;
  }
};

const deleteSku = async (id: string) => {
  if (!confirm('WARNING: Are you sure you want to permanently delete this SKU?')) return;
  
  try {
    await apiClient.delete(`/warehouses/sku/${id}/`);
    await fetchSkus(); 
  } catch (err: any) {
    error.value = err.response?.data?.error || "Cannot delete this SKU.";
  }
};

onMounted(() => {
  // 先拉取 Client 字典，保证名字可以映射，再拉取 SKUs
  fetchDictionaries().then(() => {
    fetchSkus();
  });
});
</script>