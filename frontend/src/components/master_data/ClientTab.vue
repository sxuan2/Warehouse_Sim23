<!-- src/components/master_data/ClientTab.vue -->
<template>
  <div class="h-full flex flex-col space-y-4 animate-in fade-in duration-300">
    <!-- Header / Action Bar -->
    <div class="flex justify-between items-center bg-wms-bg border border-wms-border p-4 shrink-0 shadow-sm">
      <h3 class="text-[11px] font-bold text-wms-text uppercase tracking-widest flex items-center gap-2">
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-indigo-500"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M22 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg>
        Customer Directory
      </h3>
      <div class="flex gap-3">
        <!-- 核心修复 3：新增 Refresh 按钮，解决从 Admin 修改后看不见的问题 -->
        <button @click="fetchClients" class="px-4 py-1.5 border border-indigo-500/30 text-indigo-400 hover:bg-indigo-500/10 text-[10px] font-bold uppercase tracking-widest transition-colors flex items-center gap-2">
           <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" :class="{'animate-spin': isLoading}"><polyline points="23 4 23 10 17 10"></polyline><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"></path></svg>
           Refresh Data
        </button>
        <button @click="openModal()" class="px-4 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-wms-text text-[10px] font-bold uppercase tracking-widest shadow-lg transition-colors">
          + New Customer
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
            <th class="px-4 py-3 border-r border-wms-border/50">Company Name</th>
            <th class="px-4 py-3 border-r border-wms-border/50">Alias / Ext ID</th>
            <th class="px-4 py-3 border-r border-wms-border/50">Primary Contact</th>
            <th class="px-4 py-3 border-r border-wms-border/50">City, Country</th>
            <th class="px-4 py-3 text-right">Actions</th>
          </tr>
        </thead>
        <tbody class="text-[11px] text-slate-300 font-medium">
          <tr v-if="clients.length === 0 && !isLoading">
            <td colspan="6" class="px-4 py-12 text-center text-slate-600 italic uppercase tracking-widest text-[10px]">No customers found.</td>
          </tr>
          <tr v-for="client in clients" :key="client.id" class="border-b border-wms-border/30 hover:bg-white/[0.02] transition-colors">
            <td class="px-4 py-3 border-r border-wms-border/50">
              <span :class="[
                'px-2 py-0.5 border text-[9px] font-bold tracking-widest rounded-sm',
                client.status === 'ACTIVE' ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' : 'bg-slate-500/10 text-slate-400 border-slate-500/20'
              ]">
                {{ client.status }}
              </span>
            </td>
            <td class="px-4 py-3 border-r border-wms-border/50 font-bold text-indigo-400">{{ client.name }}</td>
            <td class="px-4 py-3 border-r border-wms-border/50 font-mono text-slate-500">{{ client.alias_id || '--' }}</td>
            <td class="px-4 py-3 border-r border-wms-border/50">
              <div class="flex flex-col">
                <span>{{ client.contact_name || '--' }}</span>
                <span class="text-[9px] text-slate-500 font-mono">{{ client.contact_phone || '' }}</span>
              </div>
            </td>
            <td class="px-4 py-3 border-r border-wms-border/50">
              {{ client.city || '--' }} <span v-if="client.country" class="text-slate-500">({{ client.country }})</span>
            </td>
            <td class="px-4 py-3 text-right space-x-4">
              <button @click="openModal(client)" class="text-indigo-400 hover:text-indigo-300 uppercase text-[9px] font-bold tracking-widest transition-colors">Edit</button>
              <button @click="deleteClient(client.id)" class="text-rose-500 hover:text-rose-400 uppercase text-[9px] font-bold tracking-widest transition-colors">Delete</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Create / Edit Modal -->
    <div v-if="isModalOpen" class="fixed inset-0 z-[100] flex items-center justify-center bg-black/80 backdrop-blur-sm animate-in fade-in duration-200 p-4">
      <div class="bg-wms-bg border border-wms-border w-full max-w-4xl shadow-2xl flex flex-col max-h-[90vh]">
        
        <!-- Modal Header -->
        <div class="p-5 border-b border-wms-border bg-wms-header flex justify-between items-center shrink-0">
          <h4 class="text-wms-text text-xs font-bold uppercase tracking-[0.2em] flex items-center gap-3">
            <div class="w-1 h-5 bg-indigo-500"></div>
            {{ isEditing ? 'Edit Customer Record' : 'Create New Customer' }}
          </h4>
          <button @click="isModalOpen = false" class="text-slate-500 hover:text-wms-text transition-colors">
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
          </button>
        </div>
        
        <!-- Modal Form Body -->
        <form @submit.prevent="saveClient" class="overflow-y-auto custom-scrollbar flex-1 p-6 space-y-8">
          
          <!-- Section 1: Basic Information -->
          <div>
            <h5 class="text-[10px] text-indigo-400 uppercase tracking-widest font-bold border-b border-wms-border pb-2 mb-4">1. Basic Information</h5>
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div class="col-span-1 md:col-span-2 lg:col-span-2">
                <label class="block text-[9px] text-slate-500 uppercase font-bold mb-2 tracking-widest">Company Name *</label>
                <input v-model="form.name" type="text" required class="w-full bg-wms-surface border border-wms-border text-wms-text p-2.5 text-xs outline-none focus:border-indigo-500 transition-colors">
              </div>
              <div class="col-span-1">
                <label class="block text-[9px] text-slate-500 uppercase font-bold mb-2 tracking-widest">Alias / Ext ID</label>
                <input v-model="form.alias_id" type="text" class="w-full bg-wms-surface border border-wms-border text-wms-text p-2.5 text-xs outline-none focus:border-indigo-500 font-mono transition-colors">
              </div>
              <div class="col-span-1">
                <label class="block text-[9px] text-slate-500 uppercase font-bold mb-2 tracking-widest">Status *</label>
                <select v-model="form.status" required class="w-full bg-wms-surface border border-wms-border text-wms-text p-2.5 text-xs outline-none focus:border-indigo-500 transition-colors">
                  <option value="ACTIVE">Active</option>
                  <option value="INACTIVE">Inactive</option>
                </select>
              </div>
              <div class="col-span-1 md:col-span-2">
                <label class="block text-[9px] text-slate-500 uppercase font-bold mb-2 tracking-widest">Website</label>
                <input v-model="form.website" type="url" placeholder="https://" class="w-full bg-wms-surface border border-wms-border text-wms-text p-2.5 text-xs outline-none focus:border-indigo-500 transition-colors">
              </div>
            </div>
          </div>

          <!-- Section 2: Contact Information -->
          <div>
            <h5 class="text-[10px] text-indigo-400 uppercase tracking-widest font-bold border-b border-wms-border pb-2 mb-4">2. Contact Information</h5>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label class="block text-[9px] text-slate-500 uppercase font-bold mb-2 tracking-widest">General Phone</label>
                <input v-model="form.phone" type="text" class="w-full bg-wms-surface border border-wms-border text-wms-text p-2.5 text-xs outline-none focus:border-indigo-500 font-mono transition-colors">
              </div>
              <div>
                <label class="block text-[9px] text-slate-500 uppercase font-bold mb-2 tracking-widest">General Fax</label>
                <input v-model="form.fax" type="text" class="w-full bg-wms-surface border border-wms-border text-wms-text p-2.5 text-xs outline-none focus:border-indigo-500 font-mono transition-colors">
              </div>
              <div>
                <label class="block text-[9px] text-slate-500 uppercase font-bold mb-2 tracking-widest">General Email</label>
                <input v-model="form.email" type="email" class="w-full bg-wms-surface border border-wms-border text-wms-text p-2.5 text-xs outline-none focus:border-indigo-500 transition-colors">
              </div>
              <div>
                <label class="block text-[9px] text-slate-500 uppercase font-bold mb-2 tracking-widest">Primary Contact Name</label>
                <input v-model="form.contact_name" type="text" class="w-full bg-wms-surface border border-wms-border text-wms-text p-2.5 text-xs outline-none focus:border-indigo-500 transition-colors">
              </div>
              <div>
                <label class="block text-[9px] text-slate-500 uppercase font-bold mb-2 tracking-widest">Contact Phone</label>
                <input v-model="form.contact_phone" type="text" class="w-full bg-wms-surface border border-wms-border text-wms-text p-2.5 text-xs outline-none focus:border-indigo-500 font-mono transition-colors">
              </div>
              <div>
                <label class="block text-[9px] text-slate-500 uppercase font-bold mb-2 tracking-widest">Contact Email</label>
                <input v-model="form.contact_email" type="email" class="w-full bg-wms-surface border border-wms-border text-wms-text p-2.5 text-xs outline-none focus:border-indigo-500 transition-colors">
              </div>
            </div>
          </div>

          <!-- Section 3: Address Details -->
          <div>
            <h5 class="text-[10px] text-indigo-400 uppercase tracking-widest font-bold border-b border-wms-border pb-2 mb-4">3. Address Details</h5>
            <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div class="col-span-1 md:col-span-2">
                <label class="block text-[9px] text-slate-500 uppercase font-bold mb-2 tracking-widest">Country</label>
                <select v-model="form.country" class="w-full bg-wms-surface border border-wms-border text-wms-text p-2.5 text-xs outline-none focus:border-indigo-500 transition-colors">
                  <option value="">-- Select Country --</option>
                  <option v-for="c in dropdowns.countries" :key="c.code" :value="c.code">{{ c.name }}</option>
                </select>
              </div>
              <div class="col-span-1 md:col-span-2">
                <label class="block text-[9px] text-slate-500 uppercase font-bold mb-2 tracking-widest">State / Province</label>
                <select v-model="form.state" class="w-full bg-wms-surface border border-wms-border text-wms-text p-2.5 text-xs outline-none focus:border-indigo-500 transition-colors">
                  <option value="">-- Select State --</option>
                  <option v-for="r in dropdowns.regions" :key="r.code" :value="r.code">{{ r.name }}</option>
                </select>
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
                <label class="block text-[9px] text-slate-500 uppercase font-bold mb-2 tracking-widest">City / Township</label>
                <input v-model="form.city" type="text" class="w-full bg-wms-surface border border-wms-border text-wms-text p-2.5 text-xs outline-none focus:border-indigo-500 transition-colors">
              </div>
              <div class="col-span-1 md:col-span-2">
                <label class="block text-[9px] text-slate-500 uppercase font-bold mb-2 tracking-widest">Postal / Zip Code</label>
                <input v-model="form.postal_code" type="text" class="w-full bg-wms-surface border border-wms-border text-wms-text p-2.5 text-xs outline-none focus:border-indigo-500 font-mono transition-colors">
              </div>
            </div>
          </div>

          <!-- Section 4: Warehouse Access -->
          <div>
            <h5 class="text-[10px] text-indigo-400 uppercase tracking-widest font-bold border-b border-wms-border pb-2 mb-4">4. Accessible Warehouses</h5>
            <div v-if="dropdowns.warehouses.length === 0" class="text-slate-500 text-[10px] italic">No warehouses available in the system.</div>
            <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
              <label 
                v-for="wh in dropdowns.warehouses" 
                :key="wh.id" 
                class="flex items-center gap-3 p-3 border cursor-pointer transition-all hover:bg-white/5"
                :class="form.warehouses.includes(wh.id) ? 'border-indigo-500 bg-indigo-500/10' : 'border-wms-border bg-wms-surface'"
              >
                <input type="checkbox" :value="wh.id" v-model="form.warehouses" class="hidden">
                <div class="w-3 h-3 rounded-sm border flex items-center justify-center" :class="form.warehouses.includes(wh.id) ? 'border-indigo-400 bg-indigo-500' : 'border-slate-500'">
                   <svg v-if="form.warehouses.includes(wh.id)" xmlns="http://www.w3.org/2000/svg" width="8" height="8" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>
                </div>
                <span class="text-[10px] font-bold uppercase tracking-widest" :class="form.warehouses.includes(wh.id) ? 'text-indigo-300' : 'text-slate-400'">{{ wh.name }}</span>
              </label>
            </div>
          </div>
          
        </form>

        <!-- Modal Footer Actions -->
        <div class="p-5 border-t border-wms-border bg-wms-header flex justify-end gap-3 shrink-0">
          <button type="button" @click="isModalOpen = false" class="px-6 py-2 text-[10px] uppercase font-bold tracking-widest border border-wms-border text-slate-400 hover:text-wms-text hover:bg-white/5 transition-colors">
            Cancel
          </button>
          <button @click="saveClient" :disabled="isSaving" class="px-8 py-2 bg-indigo-600 hover:bg-indigo-500 text-wms-text text-[10px] font-bold uppercase tracking-widest disabled:opacity-50 shadow-lg transition-all">
            {{ isSaving ? 'Saving...' : 'Confirm & Save' }}
          </button>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, watch } from 'vue';
import apiClient from '../../api/client';

// Core States
const clients = ref<any[]>([]);
const isLoading = ref(false);
const error = ref<string | null>(null);

// Modal and Form States
const isModalOpen = ref(false);
const isEditing = ref(false);
const isSaving = ref(false);

// Dropdown dependencies
const dropdowns = reactive({
  countries: [] as any[],
  regions: [] as any[],
  warehouses: [] as any[]
});

const form = reactive({
  id: '',
  name: '',
  alias_id: '',
  status: 'ACTIVE',
  phone: '',
  fax: '',
  website: '',
  email: '',
  country: '',
  address1: '',
  address2: '',
  state: '',
  city: '',
  postal_code: '',
  contact_name: '',
  contact_phone: '',
  contact_email: '',
  warehouses: [] as string[]
});

// Watcher: Dynamically load State/Province when Country changes
watch(() => form.country, async (newCountryCode) => {
  if (newCountryCode) {
    try {
      // 核心修复 2：确保路径是复数的 regions （兼容大多数 DRF 设置）
      const res = await apiClient.get(`/warehouses/regions/?country=${newCountryCode}`);
      dropdowns.regions = Array.isArray(res.data) ? res.data : (res.data?.results || []);
    } catch (e) {
      // 如果后端没写 regions 这个接口或者路径不对，也不会导致整个网页卡死
      console.warn("Region endpoint failed or not found, fallback to empty.");
      dropdowns.regions = [];
    }
  } else {
    dropdowns.regions = [];
    form.state = ''; 
  }
});

// Fetch Main Clients List
const fetchClients = async () => {
  isLoading.value = true;
  error.value = null;
  try {
    const res = await apiClient.get('/warehouses/client/');
    clients.value = Array.isArray(res.data) ? res.data : (res.data?.results || []);
  } catch (err: any) {
    error.value = "Failed to load customers from database.";
  } finally {
    isLoading.value = false;
  }
};

// Fetch Dictionaries (Countries & Warehouses) on mount
const fetchDictionaries = async () => {
  try {
    // 确保 API 路径能够正确获取国家和仓库数据
    const [cRes, wRes] = await Promise.all([
      apiClient.get('/warehouses/countries/').catch(() => ({ data: [] })),
      apiClient.get('/warehouses/warehouse/').catch(() => ({ data: [] }))
    ]);
    dropdowns.countries = Array.isArray(cRes.data) ? cRes.data : (cRes.data?.results || []);
    dropdowns.warehouses = Array.isArray(wRes.data) ? wRes.data : (wRes.data?.results || []);
  } catch (e) {
    console.error("Failed to load dictionary data.");
  }
};

const openModal = (client: any = null) => {
  error.value = null;
  isEditing.value = !!client;
  
  if (client) {
    form.id = client.id;
    form.name = client.name || '';
    form.alias_id = client.alias_id || '';
    form.status = client.status || 'ACTIVE';
    form.phone = client.phone || '';
    form.fax = client.fax || '';
    form.website = client.website || '';
    form.email = client.email || '';
    form.country = client.country || '';
    form.address1 = client.address1 || '';
    form.address2 = client.address2 || '';
    form.state = client.state || '';
    form.city = client.city || '';
    form.postal_code = client.postal_code || '';
    form.contact_name = client.contact_name || '';
    form.contact_phone = client.contact_phone || '';
    form.contact_email = client.contact_email || '';
    form.warehouses = Array.isArray(client.warehouses) ? client.warehouses : [];
  } else {
    form.id = '';
    form.name = '';
    form.alias_id = '';
    form.status = 'ACTIVE';
    form.phone = '';
    form.fax = '';
    form.website = '';
    form.email = '';
    form.country = '';
    form.address1 = '';
    form.address2 = '';
    form.state = '';
    form.city = '';
    form.postal_code = '';
    form.contact_name = '';
    form.contact_phone = '';
    form.contact_email = '';
    form.warehouses = [];
  }
  
  isModalOpen.value = true;
};

const saveClient = async () => {
  if (!form.name) return;
  
  isSaving.value = true;
  error.value = null;
  
  const payload = { ...form };
  Object.keys(payload).forEach(key => {
    if (payload[key as keyof typeof payload] === '') {
      (payload as any)[key] = null;
    }
  });

  // 核心修复 1：新建记录时，必须删除空的 id 字段，否则 Django UUIDField 会崩溃
  if (!isEditing.value) {
    delete (payload as any).id;
  }

  try {
    if (isEditing.value) {
      await apiClient.put(`/warehouses/client/${form.id}/`, payload);
    } else {
      await apiClient.post('/warehouses/client/', payload);
    }
    isModalOpen.value = false;
    await fetchClients();
  } catch (err: any) {
    // 把后端的具体报错解析成字符串打印在前端横幅上
    if (err.response?.data) {
      error.value = `VALIDATION ERROR: ${JSON.stringify(err.response.data)}`;
    } else {
      error.value = "Failed to save customer record. System error.";
    }
  } finally {
    isSaving.value = false;
  }
};

const deleteClient = async (id: string) => {
  if (!confirm('WARNING: Are you sure you want to permanently delete this customer?')) return;
  
  try {
    await apiClient.delete(`/warehouses/client/${id}/`);
    await fetchClients(); 
  } catch (err: any) {
    error.value = err.response?.data?.error || "Cannot delete this customer. There may be linked inventory or orders blocking deletion.";
  }
};

onMounted(() => {
  fetchDictionaries();
  fetchClients();
});
</script>