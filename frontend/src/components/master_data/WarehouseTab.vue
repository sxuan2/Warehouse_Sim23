<!-- src/components/master_data/WarehouseTab.vue -->
<template>
  <div class="h-full flex flex-col space-y-4 animate-in fade-in duration-300">
    <!-- Header / Action Bar -->
    <div class="flex justify-between items-center bg-wms-bg border border-wms-border p-4 shrink-0 shadow-sm">
      <h3 class="text-[11px] font-bold text-wms-text uppercase tracking-widest flex items-center gap-2">
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-indigo-500"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path><polyline points="9 22 9 12 15 12 15 22"></polyline></svg>
        Warehouse Operations
      </h3>
      <div class="flex gap-3">
        <button @click="fetchWarehouses" class="px-4 py-1.5 border border-indigo-500/30 text-indigo-400 hover:bg-indigo-500/10 text-[10px] font-bold uppercase tracking-widest transition-colors flex items-center gap-2">
           <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" :class="{'animate-spin': isLoading}"><polyline points="23 4 23 10 17 10"></polyline><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"></path></svg>
           Refresh Data
        </button>
        <button @click="openModal()" class="px-4 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-wms-text text-[10px] font-bold uppercase tracking-widest shadow-lg transition-colors">
          + New Warehouse
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
            <th class="px-4 py-3 border-r border-wms-border/50">Status</th>
            <th class="px-4 py-3 border-r border-wms-border/50">Warehouse Code</th>
            <th class="px-4 py-3 border-r border-wms-border/50">Name</th>
            <th class="px-4 py-3 border-r border-wms-border/50">Zone</th>
            <th class="px-4 py-3 border-r border-wms-border/50">Time Zone</th>
            <th class="px-4 py-3 border-r border-wms-border/50">City, Country</th>
            <th class="px-4 py-3 text-right">Actions</th>
          </tr>
        </thead>
        <tbody class="text-[11px] text-slate-300 font-medium">
          <tr v-if="warehouses.length === 0 && !isLoading">
            <td colspan="7" class="px-4 py-12 text-center text-slate-600 italic uppercase tracking-widest text-[10px]">No warehouses found.</td>
          </tr>
          <tr v-for="wh in warehouses" :key="wh.id" class="border-b border-wms-border/30 hover:bg-white/[0.02] transition-colors">
            <td class="px-4 py-3 border-r border-wms-border/50">
              <span :class="[
                'px-2 py-0.5 border text-[9px] font-bold tracking-widest rounded-sm',
                wh.status === 'ACTIVE' ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' : 'bg-slate-500/10 text-slate-400 border-slate-500/20'
              ]">
                {{ wh.status }}
              </span>
            </td>
            <td class="px-4 py-3 border-r border-wms-border/50 font-mono text-indigo-400 font-bold">{{ wh.code || '--' }}</td>
            <td class="px-4 py-3 border-r border-wms-border/50 font-bold text-wms-text">{{ wh.name }}</td>
            <td class="px-4 py-3 border-r border-wms-border/50">{{ wh.zone || '--' }}</td>
            <td class="px-4 py-3 border-r border-wms-border/50 font-mono">{{ wh.time_zone || 'UTC' }}</td>
            <td class="px-4 py-3 border-r border-wms-border/50">
              {{ wh.city || '--' }} <span v-if="wh.country" class="text-slate-500">({{ wh.country }})</span>
            </td>
            <td class="px-4 py-3 text-right space-x-4">
              <button @click="openModal(wh)" class="text-indigo-400 hover:text-indigo-300 uppercase text-[9px] font-bold tracking-widest transition-colors">Edit</button>
              <button @click="deleteWarehouse(wh.id)" class="text-rose-500 hover:text-rose-400 uppercase text-[9px] font-bold tracking-widest transition-colors">Delete</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Create / Edit Modal -->
    <div v-if="isModalOpen" class="fixed inset-0 z-[100] flex items-center justify-center bg-black/80 backdrop-blur-sm animate-in fade-in duration-200 p-4">
      <div class="bg-wms-bg border border-wms-border w-full max-w-4xl shadow-2xl flex flex-col max-h-[90vh]">
        
        <div class="p-5 border-b border-wms-border bg-wms-header flex justify-between items-center shrink-0">
          <h4 class="text-wms-text text-xs font-bold uppercase tracking-[0.2em] flex items-center gap-3">
            <div class="w-1 h-5 bg-indigo-500"></div>
            {{ isEditing ? 'Edit Warehouse Settings' : 'Initialize New Warehouse' }}
          </h4>
          <button @click="isModalOpen = false" class="text-slate-500 hover:text-wms-text transition-colors">
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
          </button>
        </div>
        
        <form @submit.prevent="saveWarehouse" class="overflow-y-auto custom-scrollbar flex-1 p-6 space-y-8">
          
          <!-- Section 1: Identification -->
          <div>
            <h5 class="text-[10px] text-indigo-400 uppercase tracking-widest font-bold border-b border-wms-border pb-2 mb-4">1. Warehouse Identification</h5>
            <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div class="col-span-1 md:col-span-2">
                <label class="block text-[9px] text-slate-500 uppercase font-bold mb-2 tracking-widest">Warehouse Name *</label>
                <input v-model="form.name" type="text" required class="w-full bg-wms-surface border border-wms-border text-wms-text p-2.5 text-xs outline-none focus:border-indigo-500 transition-colors">
              </div>
              <div class="col-span-1">
                <label class="block text-[9px] text-slate-500 uppercase font-bold mb-2 tracking-widest">Warehouse Code</label>
                <input v-model="form.code" type="text" class="w-full bg-wms-surface border border-wms-border text-wms-text p-2.5 text-xs outline-none focus:border-indigo-500 font-mono transition-colors">
              </div>
              <div class="col-span-1">
                <label class="block text-[9px] text-slate-500 uppercase font-bold mb-2 tracking-widest">Status *</label>
                <select v-model="form.status" required class="w-full bg-wms-surface border border-wms-border text-wms-text p-2.5 text-xs outline-none focus:border-indigo-500 transition-colors">
                  <option value="ACTIVE">Active</option>
                  <option value="INACTIVE">Inactive</option>
                </select>
              </div>
              <div class="col-span-1 md:col-span-2">
                <label class="block text-[9px] text-slate-500 uppercase font-bold mb-2 tracking-widest">Facility Zone / Region Group</label>
                <input v-model="form.zone" type="text" class="w-full bg-wms-surface border border-wms-border text-wms-text p-2.5 text-xs outline-none focus:border-indigo-500 transition-colors">
              </div>
            </div>
          </div>

          <!-- Section 2: Contact & Communications -->
          <div>
            <h5 class="text-[10px] text-indigo-400 uppercase tracking-widest font-bold border-b border-wms-border pb-2 mb-4">2. Contact & Communications</h5>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label class="block text-[9px] text-slate-500 uppercase font-bold mb-2 tracking-widest">Main Phone</label>
                <input v-model="form.phone" type="text" class="w-full bg-wms-surface border border-wms-border text-wms-text p-2.5 text-xs outline-none focus:border-indigo-500 font-mono transition-colors">
              </div>
              <div>
                <label class="block text-[9px] text-slate-500 uppercase font-bold mb-2 tracking-widest">Fax</label>
                <input v-model="form.fax" type="text" class="w-full bg-wms-surface border border-wms-border text-wms-text p-2.5 text-xs outline-none focus:border-indigo-500 font-mono transition-colors">
              </div>
              <div>
                <label class="block text-[9px] text-slate-500 uppercase font-bold mb-2 tracking-widest">Facility Email</label>
                <input v-model="form.email" type="email" class="w-full bg-wms-surface border border-wms-border text-wms-text p-2.5 text-xs outline-none focus:border-indigo-500 transition-colors">
              </div>
            </div>
          </div>

          <!-- Section 3: Physical Address & Geography -->
          <div>
            <h5 class="text-[10px] text-indigo-400 uppercase tracking-widest font-bold border-b border-wms-border pb-2 mb-4">3. Physical Address & Geography</h5>
            <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div class="col-span-1 md:col-span-2">
                <label class="block text-[9px] text-slate-500 uppercase font-bold mb-2 tracking-widest">Country</label>
                <select v-model="form.country" class="w-full bg-wms-surface border border-wms-border text-wms-text p-2.5 text-xs outline-none focus:border-indigo-500 transition-colors">
                  <option value="">-- Select Country --</option>
                  <option v-for="c in dropdowns.countries" :key="c.code" :value="c.code">{{ c.name }}</option>
                </select>
              </div>
              <div class="col-span-1 md:col-span-2">
                <label class="block text-[9px] text-slate-500 uppercase font-bold mb-2 tracking-widest">Time Zone</label>
                <select v-model="form.time_zone" class="w-full bg-wms-surface border border-wms-border text-wms-text p-2.5 text-xs outline-none focus:border-indigo-500 transition-colors">
                  <option value="UTC">UTC (Default)</option>
                  <option v-for="t in dropdowns.timezones" :key="t.timezone_id || t.v" :value="t.timezone_id || t.v">{{ t.display_name || t.n }}</option>
                </select>
              </div>
              <div class="col-span-1 md:col-span-2">
                <label class="block text-[9px] text-slate-500 uppercase font-bold mb-2 tracking-widest">State / Province</label>
                <select v-model="form.state" class="w-full bg-wms-surface border border-wms-border text-wms-text p-2.5 text-xs outline-none focus:border-indigo-500 transition-colors">
                  <option value="">-- Select State --</option>
                  <option v-for="r in dropdowns.regions" :key="r.code || r.v" :value="r.code || r.v">{{ r.name || r.n }}</option>
                </select>
              </div>
              <div class="col-span-1 md:col-span-2">
                <label class="block text-[9px] text-slate-500 uppercase font-bold mb-2 tracking-widest">City / Township</label>
                <input v-model="form.city" type="text" class="w-full bg-wms-surface border border-wms-border text-wms-text p-2.5 text-xs outline-none focus:border-indigo-500 transition-colors">
              </div>
              <div class="col-span-1 md:col-span-2">
                <label class="block text-[9px] text-slate-500 uppercase font-bold mb-2 tracking-widest">Address Line 1</label>
                <input v-model="form.address1" type="text" class="w-full bg-wms-surface border border-wms-border text-wms-text p-2.5 text-xs outline-none focus:border-indigo-500 transition-colors">
              </div>
              <div class="col-span-1 md:col-span-2">
                <label class="block text-[9px] text-slate-500 uppercase font-bold mb-2 tracking-widest">Address Line 2</label>
                <input v-model="form.address2" type="text" class="w-full bg-wms-surface border border-wms-border text-wms-text p-2.5 text-xs outline-none focus:border-indigo-500 transition-colors">
              </div>
              <div class="col-span-1 md:col-span-2">
                <label class="block text-[9px] text-slate-500 uppercase font-bold mb-2 tracking-widest">Postal / Zip Code</label>
                <input v-model="form.postal_code" type="text" class="w-full bg-wms-surface border border-wms-border text-wms-text p-2.5 text-xs outline-none focus:border-indigo-500 font-mono transition-colors">
              </div>
            </div>
          </div>
          
        </form>

        <div class="p-5 border-t border-wms-border bg-wms-header flex justify-end gap-3 shrink-0">
          <button type="button" @click="isModalOpen = false" class="px-6 py-2 text-[10px] uppercase font-bold tracking-widest border border-wms-border text-slate-400 hover:text-wms-text hover:bg-white/5 transition-colors">
            Cancel
          </button>
          <button @click="saveWarehouse" :disabled="isSaving" class="px-8 py-2 bg-indigo-600 hover:bg-indigo-500 text-wms-text text-[10px] font-bold uppercase tracking-widest disabled:opacity-50 shadow-lg transition-all">
            {{ isSaving ? 'Committing...' : 'Save Facility' }}
          </button>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, watch } from 'vue';
import apiClient from '../../api/client';

const warehouses = ref<any[]>([]);
const isLoading = ref(false);
const error = ref<string | null>(null);

const isModalOpen = ref(false);
const isEditing = ref(false);
const isSaving = ref(false);

const dropdowns = reactive({
  countries: [] as any[],
  regions: [] as any[],
  timezones: [] as any[]
});

const form = reactive({
  id: '',
  name: '',
  code: '',
  zone: '',
  address1: '',
  address2: '',
  country: '',
  state: '',
  city: '',
  postal_code: '',
  time_zone: 'UTC',
  phone: '',
  fax: '',
  email: '',
  status: 'ACTIVE'
});

// Watcher: Dynamically fetch states & timezones based on backend get_region_choices structure
watch(() => form.country, async (newCountryCode) => {
  if (newCountryCode) {
    try {
      const res = await apiClient.get(`/warehouses/region/?country=${newCountryCode}`);
      // Based on your django view `get_region_choices` which returns a dict
      if (res.data && res.data.regions) {
        dropdowns.regions = res.data.regions;
        dropdowns.timezones = res.data.timezones;
      } else {
        dropdowns.regions = Array.isArray(res.data) ? res.data : [];
        dropdowns.timezones = [];
      }
    } catch (e) {
      dropdowns.regions = [];
      dropdowns.timezones = [];
    }
  } else {
    dropdowns.regions = [];
    dropdowns.timezones = [];
    form.state = '';
    form.time_zone = 'UTC';
  }
});

const fetchWarehouses = async () => {
  isLoading.value = true;
  error.value = null;
  try {
    const res = await apiClient.get('/warehouses/warehouse/');
    warehouses.value = Array.isArray(res.data) ? res.data : (res.data?.results || []);
  } catch (err: any) {
    error.value = "Failed to load warehouse directory from database.";
  } finally {
    isLoading.value = false;
  }
};

const fetchDictionaries = async () => {
  try {
    const cRes = await apiClient.get('/warehouses/countries/').catch(() => ({ data: [] }));
    dropdowns.countries = Array.isArray(cRes.data) ? cRes.data : (cRes.data?.results || []);
  } catch (e) {
    console.error("Failed to load country dictionary.");
  }
};

const openModal = (wh: any = null) => {
  error.value = null;
  isEditing.value = !!wh;
  
  if (wh) {
    form.id = wh.id;
    form.name = wh.name || '';
    form.code = wh.code || '';
    form.zone = wh.zone || '';
    form.address1 = wh.address1 || '';
    form.address2 = wh.address2 || '';
    form.country = wh.country || '';
    form.state = wh.state || '';
    form.city = wh.city || '';
    form.postal_code = wh.postal_code || '';
    form.time_zone = wh.time_zone || 'UTC';
    form.phone = wh.phone || '';
    form.fax = wh.fax || '';
    form.email = wh.email || '';
    form.status = wh.status || 'ACTIVE';
  } else {
    form.id = '';
    form.name = '';
    form.code = '';
    form.zone = '';
    form.address1 = '';
    form.address2 = '';
    form.country = '';
    form.state = '';
    form.city = '';
    form.postal_code = '';
    form.time_zone = 'UTC';
    form.phone = '';
    form.fax = '';
    form.email = '';
    form.status = 'ACTIVE';
  }
  
  isModalOpen.value = true;
};

const saveWarehouse = async () => {
  if (!form.name) return;
  
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
      await apiClient.put(`/warehouses/warehouse/${form.id}/`, payload);
    } else {
      await apiClient.post('/warehouses/warehouse/', payload);
    }
    isModalOpen.value = false;
    await fetchWarehouses();
  } catch (err: any) {
    if (err.response?.data) {
      error.value = `VALIDATION ERROR: ${JSON.stringify(err.response.data)}`;
    } else {
      error.value = "Failed to save warehouse record. System error.";
    }
  } finally {
    isSaving.value = false;
  }
};

const deleteWarehouse = async (id: string) => {
  if (!confirm('WARNING: Are you sure you want to permanently delete this warehouse facility?')) return;
  
  try {
    await apiClient.delete(`/warehouses/warehouse/${id}/`);
    await fetchWarehouses(); 
  } catch (err: any) {
    error.value = err.response?.data?.error || "Cannot delete this warehouse. It contains active locations or inventory.";
  }
};

onMounted(() => {
  fetchDictionaries();
  fetchWarehouses();
});
</script>