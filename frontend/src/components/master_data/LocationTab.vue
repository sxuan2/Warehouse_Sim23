<!-- src/components/master_data/LocationTab.vue -->
<template>
  <div class="h-full flex flex-col space-y-4 animate-in fade-in duration-300">
    <!-- Header / Action Bar -->
    <div class="flex justify-between items-center bg-wms-bg border border-wms-border p-4 shrink-0 shadow-sm">
      <h3 class="text-[11px] font-bold text-wms-text uppercase tracking-widest flex items-center gap-2">
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-indigo-500"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect><line x1="3" y1="9" x2="21" y2="9"></line><line x1="9" y1="21" x2="9" y2="9"></line></svg>
        Location Directory
      </h3>
      <div class="flex gap-3">
        <button @click="fetchLocations" class="px-4 py-1.5 border border-indigo-500/30 text-indigo-400 hover:bg-indigo-500/10 text-[10px] font-bold uppercase tracking-widest transition-colors flex items-center gap-2">
           <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" :class="{'animate-spin': isLoading}"><polyline points="23 4 23 10 17 10"></polyline><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"></path></svg>
           Refresh Data
        </button>
        <!-- 批量导入触发器 -->
        <button @click="isImportModalOpen = true" class="px-4 py-1.5 border border-emerald-500/30 text-emerald-400 hover:bg-emerald-500/10 text-[10px] font-bold uppercase tracking-widest transition-colors">
          Bulk Import (Excel/CSV)
        </button>
        <button @click="openModal()" class="px-4 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-wms-text text-[10px] font-bold uppercase tracking-widest shadow-lg transition-colors">
          + New Location
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
        <span class="text-indigo-400 text-[10px] uppercase font-bold tracking-widest animate-pulse">Syncing Database...</span>
      </div>
      
      <table class="w-full text-left border-collapse whitespace-nowrap">
        <thead class="bg-wms-header text-[9px] text-slate-500 uppercase tracking-[0.2em] font-bold sticky top-0 z-10 shadow-sm border-b border-wms-border">
          <tr>
            <th class="px-4 py-3 border-r border-wms-border/50">Location ID</th>
            <th class="px-4 py-3 border-r border-wms-border/50">Warehouse</th>
            <th class="px-4 py-3 border-r border-wms-border/50">Zone</th>
            <th class="px-4 py-3 border-r border-wms-border/50">Type</th>
            <th class="px-4 py-3 border-r border-wms-border/50 text-right">Pick Path</th>
            <th class="px-4 py-3 border-r border-wms-border/50 text-center">Status</th>
            <th class="px-4 py-3 text-right">Actions</th>
          </tr>
        </thead>
        <tbody class="text-[11px] text-slate-300 font-medium font-mono">
          <tr v-if="locations.length === 0 && !isLoading">
            <td colspan="7" class="px-4 py-12 text-center text-slate-600 italic uppercase tracking-widest text-[10px] font-sans">No locations found.</td>
          </tr>
          <tr v-for="loc in locations" :key="loc.id" class="border-b border-wms-border/30 hover:bg-white/[0.02] transition-colors">
            <td class="px-4 py-3 border-r border-wms-border/50 font-bold text-indigo-400">{{ loc.name }}</td>
            <!-- 直接使用你后端 Serializer 传来的 warehouse_name -->
            <td class="px-4 py-3 border-r border-wms-border/50 font-sans font-bold text-wms-text">{{ loc.warehouse_name || getWarehouseName(loc.warehouse) }}</td>
            <td class="px-4 py-3 border-r border-wms-border/50">{{ loc.zone || '--' }}</td>
            <td class="px-4 py-3 border-r border-wms-border/50 font-sans">
              <span class="px-2 py-0.5 border border-slate-500/30 bg-slate-500/10 rounded-sm text-[9px] font-bold tracking-widest">{{ loc.type }}</span>
            </td>
            <td class="px-4 py-3 border-r border-wms-border/50 text-right">{{ loc.pick_path }}</td>
            <td class="px-4 py-3 border-r border-wms-border/50 text-center">
              <span v-if="loc.is_non_pickable" class="text-rose-400 text-[9px] font-bold uppercase tracking-widest font-sans">Non-Pickable</span>
              <span v-else class="text-emerald-400 text-[9px] font-bold uppercase tracking-widest font-sans">Active</span>
            </td>
            <td class="px-4 py-3 text-right space-x-4 font-sans">
              <button @click="openModal(loc)" class="text-indigo-400 hover:text-indigo-300 uppercase text-[9px] font-bold tracking-widest transition-colors">Edit</button>
              <button @click="deleteLocation(loc.id)" class="text-rose-500 hover:text-rose-400 uppercase text-[9px] font-bold tracking-widest transition-colors">Delete</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 挂载批量导入组件 -->
    <ImportLocationModal 
      v-if="isImportModalOpen" 
      @close="isImportModalOpen = false"
      @success="handleImportSuccess"
    />

    <!-- Create / Edit Modal -->
    <div v-if="isModalOpen" class="fixed inset-0 z-[100] flex items-center justify-center bg-black/80 backdrop-blur-sm animate-in fade-in duration-200 p-4">
      <div class="bg-wms-bg border border-wms-border w-full max-w-5xl shadow-2xl flex flex-col max-h-[90vh]">
        
        <div class="p-5 border-b border-wms-border bg-wms-header flex justify-between items-center shrink-0">
          <h4 class="text-wms-text text-xs font-bold uppercase tracking-[0.2em] flex items-center gap-3">
            <div class="w-1 h-5 bg-indigo-500"></div>
            {{ isEditing ? 'Edit Location Configuration' : 'Create New Location' }}
          </h4>
          <button @click="isModalOpen = false" class="text-slate-500 hover:text-wms-text transition-colors">
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
          </button>
        </div>
        
        <form @submit.prevent="saveLocation" class="overflow-y-auto custom-scrollbar flex-1 p-6 space-y-8">
          
          <!-- Section 1: Basic Identifiers -->
          <div>
            <h5 class="text-[10px] text-indigo-400 uppercase tracking-widest font-bold border-b border-wms-border pb-2 mb-4">1. Basic Identification</h5>
            <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div class="col-span-1 md:col-span-2">
                <label class="block text-[9px] text-slate-500 uppercase font-bold mb-2 tracking-widest">Location ID / Barcode *</label>
                <input v-model="form.name" type="text" required placeholder="e.g. A-01-01-01" class="w-full bg-wms-surface border border-wms-border text-wms-text p-2.5 text-xs outline-none focus:border-indigo-500 font-mono transition-colors">
              </div>
              <div class="col-span-1 md:col-span-2">
                <label class="block text-[9px] text-slate-500 uppercase font-bold mb-2 tracking-widest">Facility / Warehouse *</label>
                <select v-model="form.warehouse" required class="w-full bg-wms-surface border border-wms-border text-wms-text p-2.5 text-xs outline-none focus:border-indigo-500 transition-colors">
                  <option value="">-- Select Warehouse --</option>
                  <option v-for="wh in dropdowns.warehouses" :key="wh.id" :value="wh.id">{{ wh.name }} ({{ wh.code }})</option>
                </select>
              </div>
              <div class="col-span-1">
                <label class="block text-[9px] text-slate-500 uppercase font-bold mb-2 tracking-widest">Location Type</label>
                <select v-model="form.type" class="w-full bg-wms-surface border border-wms-border text-wms-text p-2.5 text-xs outline-none focus:border-indigo-500 transition-colors">
                  <option value="STORAGE">Storage</option>
                  <option value="STAGING">Staging</option>
                  <option value="PUTAWAY">Put-away Vehicle</option>
                  <option value="QUARANTINE">Quarantine</option>
                  <option value="PICKLINE">PickLine</option>
                </select>
              </div>
              <div class="col-span-1">
                <label class="block text-[9px] text-slate-500 uppercase font-bold mb-2 tracking-widest">Zone</label>
                <input v-model="form.zone" type="text" class="w-full bg-wms-surface border border-wms-border text-wms-text p-2.5 text-xs outline-none focus:border-indigo-500 font-mono transition-colors">
              </div>
              <div class="col-span-1 md:col-span-2">
                <label class="block text-[9px] text-slate-500 uppercase font-bold mb-2 tracking-widest">Description</label>
                <input v-model="form.description" type="text" class="w-full bg-wms-surface border border-wms-border text-wms-text p-2.5 text-xs outline-none focus:border-indigo-500 transition-colors">
              </div>
            </div>
          </div>

          <!-- Section 2: Fulfillment Logic -->
          <div>
            <h5 class="text-[10px] text-indigo-400 uppercase tracking-widest font-bold border-b border-wms-border pb-2 mb-4">2. Operations & Picking Logic</h5>
            <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div class="col-span-1">
                <label class="block text-[9px] text-slate-500 uppercase font-bold mb-2 tracking-widest">Pick Path Index</label>
                <input v-model="form.pick_path" type="number" min="0" class="w-full bg-wms-surface border border-wms-border text-wms-text p-2.5 text-xs outline-none focus:border-indigo-500 font-mono transition-colors">
              </div>
              <div class="col-span-1">
                <label class="block text-[9px] text-slate-500 uppercase font-bold mb-2 tracking-widest">Allocation Priority</label>
                <input v-model="form.allocation_priority" type="number" class="w-full bg-wms-surface border border-wms-border text-wms-text p-2.5 text-xs outline-none focus:border-indigo-500 font-mono transition-colors">
              </div>
              <div class="col-span-1">
                <label class="block text-[9px] text-slate-500 uppercase font-bold mb-2 tracking-widest">Min Quantity Threshold</label>
                <input v-model="form.min_quantity" type="number" min="0" class="w-full bg-wms-surface border border-wms-border text-wms-text p-2.5 text-xs outline-none focus:border-indigo-500 font-mono transition-colors">
              </div>
              <div class="col-span-1 flex items-center pt-5">
                <label class="flex items-center gap-3 cursor-pointer group">
                  <div class="w-5 h-5 border border-wms-border bg-wms-surface flex items-center justify-center transition-colors group-hover:border-indigo-500" :class="{'bg-rose-500/20 border-rose-500': form.is_non_pickable}">
                    <svg v-if="form.is_non_pickable" xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="4" stroke-linecap="round" stroke-linejoin="round" class="text-rose-400"><polyline points="20 6 9 17 4 12"></polyline></svg>
                  </div>
                  <input type="checkbox" v-model="form.is_non_pickable" class="hidden">
                  <span class="text-[10px] uppercase font-bold tracking-widest text-slate-400 group-hover:text-wms-text transition-colors">Is Non-Pickable</span>
                </label>
              </div>
            </div>
          </div>

          <!-- Section 3: Physical Constraints -->
          <div>
            <h5 class="text-[10px] text-indigo-400 uppercase tracking-widest font-bold border-b border-wms-border pb-2 mb-4">3. Physical Constraints</h5>
            <div class="grid grid-cols-2 md:grid-cols-5 gap-4">
              <div class="col-span-1">
                <label class="block text-[9px] text-slate-500 uppercase font-bold mb-2 tracking-widest">Length (cm)</label>
                <input v-model="form.length" type="number" step="0.01" min="0" class="w-full bg-wms-surface border border-wms-border text-wms-text p-2.5 text-xs outline-none focus:border-indigo-500 font-mono transition-colors">
              </div>
              <div class="col-span-1">
                <label class="block text-[9px] text-slate-500 uppercase font-bold mb-2 tracking-widest">Width (cm)</label>
                <input v-model="form.width" type="number" step="0.01" min="0" class="w-full bg-wms-surface border border-wms-border text-wms-text p-2.5 text-xs outline-none focus:border-indigo-500 font-mono transition-colors">
              </div>
              <div class="col-span-1">
                <label class="block text-[9px] text-slate-500 uppercase font-bold mb-2 tracking-widest">Height (cm)</label>
                <input v-model="form.height" type="number" step="0.01" min="0" class="w-full bg-wms-surface border border-wms-border text-wms-text p-2.5 text-xs outline-none focus:border-indigo-500 font-mono transition-colors">
              </div>
              <div class="col-span-1">
                <label class="block text-[9px] text-slate-500 uppercase font-bold mb-2 tracking-widest">Max Weight (kg)</label>
                <input v-model="form.max_weight" type="number" step="0.01" min="0" class="w-full bg-wms-surface border border-wms-border text-wms-text p-2.5 text-xs outline-none focus:border-indigo-500 font-mono transition-colors">
              </div>
              <div class="col-span-1">
                <label class="block text-[9px] text-slate-500 uppercase font-bold mb-2 tracking-widest">Min Temp (°C)</label>
                <input v-model="form.min_temperature" type="number" step="0.01" class="w-full bg-wms-surface border border-wms-border text-wms-text p-2.5 text-xs outline-none focus:border-indigo-500 font-mono transition-colors">
              </div>
            </div>
          </div>

          <!-- Section 4: Admin / Billing -->
          <div>
            <h5 class="text-[10px] text-indigo-400 uppercase tracking-widest font-bold border-b border-wms-border pb-2 mb-4">4. Administrative</h5>
            <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div class="col-span-1 md:col-span-2">
                <label class="block text-[9px] text-slate-500 uppercase font-bold mb-2 tracking-widest">Billing Type Config</label>
                <input v-model="form.billing_type" type="text" placeholder="e.g. Standard Pallet, Cold Storage" class="w-full bg-wms-surface border border-wms-border text-wms-text p-2.5 text-xs outline-none focus:border-indigo-500 transition-colors">
              </div>
            </div>
          </div>
          
        </form>

        <div class="p-5 border-t border-wms-border bg-wms-header flex justify-end gap-3 shrink-0">
          <button type="button" @click="isModalOpen = false" class="px-6 py-2 text-[10px] uppercase font-bold tracking-widest border border-wms-border text-slate-400 hover:text-wms-text hover:bg-white/5 transition-colors">
            Cancel
          </button>
          <button @click="saveLocation" :disabled="isSaving" class="px-8 py-2 bg-indigo-600 hover:bg-indigo-500 text-wms-text text-[10px] font-bold uppercase tracking-widest disabled:opacity-50 shadow-lg transition-all">
            {{ isSaving ? 'Committing...' : 'Save Location' }}
          </button>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue';
import apiClient from '../../api/client';
import ImportLocationModal from '../ImportLocationModal.vue'; // 确保路径正确

const locations = ref<any[]>([]);
const isLoading = ref(false);
const error = ref<string | null>(null);

const isModalOpen = ref(false);
const isEditing = ref(false);
const isSaving = ref(false);

const isImportModalOpen = ref(false);

const dropdowns = reactive({
  warehouses: [] as any[]
});

const form = reactive({
  id: '',
  name: '',
  warehouse: '',
  type: 'STORAGE',
  zone: '',
  description: '',
  pick_path: 0,
  is_non_pickable: false,
  width: 0.00,
  length: 0.00,
  height: 0.00,
  max_weight: 0.00,
  min_temperature: 0.00,
  min_quantity: 0,
  allocation_priority: 10,
  billing_type: ''
});

// 降级方案：如果没有从后端拿到 warehouse_name，就在前端手动匹配
const getWarehouseName = (id: string) => {
  if (!id) return '--';
  const wh = dropdowns.warehouses.find(w => w.id === id);
  return wh ? wh.name : id;
};

// 导入成功后的回调
const handleImportSuccess = () => {
  isImportModalOpen.value = false;
  fetchLocations(); 
};

const fetchLocations = async () => {
  isLoading.value = true;
  error.value = null;
  try {
    const res = await apiClient.get('/warehouses/location/list/');
    locations.value = Array.isArray(res.data) ? res.data : (res.data?.results || []);
  } catch (err: any) {
    error.value = "Failed to load location directory from database.";
  } finally {
    isLoading.value = false;
  }
};

const fetchDictionaries = async () => {
  try {
    const wRes = await apiClient.get('/warehouses/warehouse/').catch(() => ({ data: [] }));
    dropdowns.warehouses = Array.isArray(wRes.data) ? wRes.data : (wRes.data?.results || []);
  } catch (e) {
    console.error("Failed to load warehouse dictionary.");
  }
};

const openModal = (loc: any = null) => {
  error.value = null;
  isEditing.value = !!loc;
  
  if (loc) {
    form.id = loc.id;
    form.name = loc.name || '';
    form.warehouse = loc.warehouse || '';
    form.type = loc.type || 'STORAGE';
    form.zone = loc.zone || '';
    form.description = loc.description || '';
    form.pick_path = loc.pick_path ?? 0;
    form.is_non_pickable = !!loc.is_non_pickable;
    form.width = loc.width ?? 0;
    form.length = loc.length ?? 0;
    form.height = loc.height ?? 0;
    form.max_weight = loc.max_weight ?? 0;
    form.min_temperature = loc.min_temperature ?? 0;
    form.min_quantity = loc.min_quantity ?? 0;
    form.allocation_priority = loc.allocation_priority ?? 10;
    form.billing_type = loc.billing_type || '';
  } else {
    form.id = '';
    form.name = '';
    form.warehouse = dropdowns.warehouses.length > 0 ? dropdowns.warehouses[0].id : ''; 
    form.type = 'STORAGE';
    form.zone = '';
    form.description = '';
    form.pick_path = 0;
    form.is_non_pickable = false;
    form.width = 0;
    form.length = 0;
    form.height = 0;
    form.max_weight = 0;
    form.min_temperature = 0;
    form.min_quantity = 0;
    form.allocation_priority = 10;
    form.billing_type = '';
  }
  
  isModalOpen.value = true;
};

const saveLocation = async () => {
  if (!form.name || !form.warehouse) return;
  
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
      await apiClient.put(`/warehouses/location/${form.id}/`, payload);
    } else {
      await apiClient.post('/warehouses/location/list/', payload);
    }
    isModalOpen.value = false;
    await fetchLocations();
  } catch (err: any) {
    if (err.response?.data) {
      error.value = `VALIDATION ERROR: ${JSON.stringify(err.response.data)}`;
    } else {
      error.value = "Failed to save location record. System error.";
    }
  } finally {
    isSaving.value = false;
  }
};

const deleteLocation = async (id: string) => {
  if (!confirm('WARNING: Are you sure you want to permanently delete this location?')) return;
  
  try {
    await apiClient.delete(`/warehouses/location/${id}/`);
    await fetchLocations(); 
  } catch (err: any) {
    error.value = err.response?.data?.error || "Cannot delete this location. It contains active inventory.";
  }
};

onMounted(() => {
  fetchDictionaries().then(() => {
    fetchLocations();
  });
});
</script>