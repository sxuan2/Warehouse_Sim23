<template>
  <div class="flex w-full h-screen bg-wms-surface text-wms-muted font-sans selection:bg-indigo-500/30 transition-colors duration-300">
    <aside class="w-64 bg-wms-bg border-r border-wms-border flex flex-col z-20 shadow-2xl">
      <div class="p-6 border-b border-wms-border shrink-0 space-y-3">
        <div class="flex items-center gap-3">
          <span class="text-sm font-bold tracking-widest text-wms-text uppercase">3PL Storage Simulator</span>
        </div>
        <div v-if="branding.companyName || branding.logoUrl" class="rounded border border-wms-border bg-wms-surface p-3">
          <div class="flex items-center gap-3">
            <div class="h-10 w-10 overflow-hidden rounded border border-wms-border bg-wms-header">
              <img v-if="branding.logoUrl" :src="branding.logoUrl" alt="Company Logo" class="h-full w-full object-cover" />
            </div>
            <div class="min-w-0">
              <div class="text-[9px] uppercase tracking-widest text-slate-500 font-bold">Company</div>
              <div class="text-xs font-semibold text-wms-text truncate">{{ branding.companyName || 'Not set' }}</div>
            </div>
          </div>
        </div>
      </div>

      <nav class="flex-1 overflow-y-auto py-4 custom-scrollbar">
        <ul class="space-y-1 px-3">
          <li>
            <button @click="setActiveTab('dashboard')" :class="['w-full flex items-center gap-3 px-3 py-2.5 rounded transition-all', activeTab === 'dashboard' ? 'bg-indigo-500/10 text-indigo-400' : 'text-slate-400 hover:text-wms-text hover:bg-white/[0.02]']">
              <LayoutDashboardIcon :size="16" />
              <span class="text-xs font-semibold tracking-wide">Dashboards</span>
            </button>
          </li>
          
          <li>
            <button @click="toggleMenu('orders')" class="w-full flex items-center justify-between px-3 py-2.5 rounded text-slate-400 hover:text-wms-text hover:bg-white/[0.02] transition-all">
              <div class="flex items-center gap-3">
                <BoxIcon :size="16" :class="{ 'text-indigo-400': expandedMenu === 'orders' || activeGroup === 'orders' }" />
                <span :class="['text-xs font-semibold tracking-wide', { 'text-wms-text': expandedMenu === 'orders' || activeGroup === 'orders' }]">Orders</span>
              </div>
              <ChevronDownIcon :size="14" :class="['transition-transform', expandedMenu === 'orders' ? 'rotate-180' : '']" />
            </button>
            <ul v-show="expandedMenu === 'orders'" class="mt-1 mb-2 space-y-1 border-l border-wms-border ml-5 pl-2 animate-in slide-in-from-top-2 duration-200">
              <li>
                <button @click="setActiveTab('orders', 'orders')" :class="['w-full text-left px-3 py-2 text-[11px] rounded transition-colors', activeTab === 'orders' ? 'bg-indigo-500/10 text-indigo-400 font-bold' : 'text-slate-500 hover:text-slate-300 hover:bg-white/5']">Find Orders</button>
              </li>
              <li>
                <button @click="setActiveTab('create_order', 'orders')" :class="['w-full text-left px-3 py-2 text-[11px] rounded transition-colors', activeTab === 'create_order' ? 'bg-indigo-500/10 text-indigo-400 font-bold' : 'text-slate-500 hover:text-slate-300 hover:bg-white/5']">+ Create Order</button>
              </li>
            </ul>
          </li>

          <li>
            <button @click="toggleMenu('receipts')" class="w-full flex items-center justify-between px-3 py-2.5 rounded text-slate-400 hover:text-wms-text hover:bg-white/[0.02] transition-all">
              <div class="flex items-center gap-3">
                <FileDownIcon :size="16" :class="{ 'text-indigo-400': expandedMenu === 'receipts' || activeGroup === 'receipts' }" />
                <span :class="['text-xs font-semibold tracking-wide', { 'text-wms-text': expandedMenu === 'receipts' || activeGroup === 'receipts' }]">Receipts</span>
              </div>
              <ChevronDownIcon :size="14" :class="['transition-transform', expandedMenu === 'receipts' ? 'rotate-180' : '']" />
            </button>
            <ul v-show="expandedMenu === 'receipts'" class="mt-1 mb-2 space-y-1 border-l border-wms-border ml-5 pl-2 animate-in slide-in-from-top-2 duration-200">
              <li>
                <button @click="setActiveTab('receipts', 'receipts')" :class="['w-full text-left px-3 py-2 text-[11px] rounded transition-colors', activeTab === 'receipts' ? 'bg-indigo-500/10 text-indigo-400 font-bold' : 'text-slate-500 hover:text-slate-300 hover:bg-white/5']">Find Receipts</button>
              </li>
              <li>
                <button @click="setActiveTab('create_receipt', 'receipts')" :class="['w-full text-left px-3 py-2 text-[11px] rounded transition-colors', activeTab === 'create_receipt' ? 'bg-indigo-500/10 text-indigo-400 font-bold' : 'text-slate-500 hover:text-slate-300 hover:bg-white/5']">+ Create Receipt</button>
              </li>
            </ul>
          </li>

          <li>
            <button @click="toggleMenu('inventory')" class="w-full flex items-center justify-between px-3 py-2.5 rounded text-slate-400 hover:text-wms-text hover:bg-white/[0.02] transition-all">
              <div class="flex items-center gap-3">
                <LayersIcon :size="16" :class="{ 'text-indigo-400': expandedMenu === 'inventory' || activeGroup === 'inventory' }" />
                <span :class="['text-xs font-semibold tracking-wide', { 'text-wms-text': expandedMenu === 'inventory' || activeGroup === 'inventory' }]">Inventory</span>
              </div>
              <ChevronDownIcon :size="14" :class="['transition-transform', expandedMenu === 'inventory' ? 'rotate-180' : '']" />
            </button>
            <ul v-show="expandedMenu === 'inventory'" class="mt-1 mb-2 space-y-1 border-l border-wms-border ml-5 pl-2 animate-in slide-in-from-top-2 duration-200">
              <li>
                <button @click="setActiveTab('inventory', 'inventory')" :class="['w-full text-left px-3 py-2 text-[11px] rounded transition-colors', activeTab === 'inventory' ? 'bg-indigo-500/10 text-indigo-400 font-bold' : 'text-slate-500 hover:text-slate-300 hover:bg-white/5']">Manage Inventory</button>
              </li>
              <li>
                <button @click="setActiveTab('audit', 'inventory')" :class="['w-full text-left px-3 py-2 text-[11px] rounded transition-colors', activeTab === 'audit' ? 'bg-indigo-500/10 text-indigo-400 font-bold' : 'text-slate-500 hover:text-slate-300 hover:bg-white/5']">Audit Ledger</button>
              </li>
            </ul>
          </li>

          <div class="my-4 border-t border-wms-border mx-2"></div>

          <li>
            <button @click="setActiveTab('settings', 'system')" :class="['w-full flex items-center gap-3 px-3 py-2.5 rounded transition-all', activeTab === 'settings' ? 'bg-indigo-500/10 text-indigo-400' : 'text-slate-400 hover:text-wms-text hover:bg-white/[0.02]']">
              <SettingsIcon :size="16" />
              <span class="text-xs font-semibold tracking-wide">Settings</span>
            </button>
          </li>

          <div class="my-4 border-t border-wms-border mx-2"></div>
          
          <li>
            <a href="http://127.0.0.1:8000/admin/warehouses/client/" target="_blank" class="w-full flex items-center gap-3 px-3 py-2.5 rounded text-slate-500 hover:text-wms-text hover:bg-white/[0.02] transition-all">
              <UsersIcon :size="16" />
              <span class="text-xs font-semibold tracking-wide">Customers</span>
              <ExternalLinkIcon :size="12" class="ml-auto opacity-50" />
            </a>
          </li>
          <li>
            <a href="http://127.0.0.1:8000/admin/warehouses/sku/" target="_blank" class="w-full flex items-center gap-3 px-3 py-2.5 rounded text-slate-500 hover:text-wms-text hover:bg-white/[0.02] transition-all">
              <PackageIcon :size="16" />
              <span class="text-xs font-semibold tracking-wide">Items</span>
              <ExternalLinkIcon :size="12" class="ml-auto opacity-50" />
            </a>
          </li>
          <li>
            <a href="http://127.0.0.1:8000/admin/warehouses/warehouse/" target="_blank" class="w-full flex items-center gap-3 px-3 py-2.5 rounded text-slate-500 hover:text-wms-text hover:bg-white/[0.02] transition-all">
              <HomeIcon :size="16" />
              <span class="text-xs font-semibold tracking-wide">Warehouse</span>
              <ExternalLinkIcon :size="12" class="ml-auto opacity-50" />
            </a>
          </li>
        </ul>
      </nav>
    </aside>

    <main class="flex-1 flex flex-col overflow-hidden bg-wms-bg">
      <header class="h-14 bg-wms-header border-b border-wms-border flex items-center justify-between px-6 shrink-0 shadow-sm z-10">
        <div class="flex items-center gap-3 text-sm text-slate-400">
          <span v-if="activeGroup" class="text-slate-500 font-medium uppercase text-[10px] tracking-widest">{{ activeGroup }}</span>
          <ChevronRightIcon v-if="activeGroup" :size="14" class="text-slate-600" />
          <span class="text-wms-text font-bold uppercase text-[11px] tracking-widest">{{ activeTab.replace('_', ' ') }}</span>
        </div>

        <div class="flex items-center gap-4">
          <div class="relative">
            <button @click="isSettingsOpen = !isSettingsOpen" 
              class="p-2 text-slate-500 hover:text-indigo-400 transition-colors rounded-full hover:bg-black/5">
              <PaletteIcon :size="18" />
            </button>
            
            <div v-if="isSettingsOpen" 
              class="absolute right-0 mt-2 w-48 bg-wms-surface border border-wms-border shadow-2xl rounded-sm p-2 z-50 animate-in fade-in zoom-in-95 duration-200">
              <div class="text-[9px] uppercase font-bold text-wms-muted mb-2 px-2 tracking-widest border-b border-wms-border pb-1">Interface Theme</div>
              <div class="space-y-1">
                <button v-for="t in themes" :key="t.value" 
                  @click="selectTheme(t.value)"
                  :class="['w-full text-left px-3 py-2 text-[11px] font-bold uppercase tracking-tighter rounded-sm transition-colors', 
                           currentTheme === t.value ? 'bg-indigo-500/10 text-indigo-400' : 'text-slate-600 hover:bg-black/5']">
                  {{ t.name }}
                </button>
              </div>
            </div>
          </div>

          <div class="bg-wms-surface px-3 py-1.5 border border-wms-border flex items-center gap-2 w-64 rounded-sm">
            <SearchIcon :size="14" class="text-slate-500" />
            <input type="text" placeholder="Find Orders, Receipts, SKUs..." class="bg-transparent border-none text-xs focus:outline-none w-full placeholder:text-slate-600 text-wms-text" />
          </div>
        </div>
      </header>

      <div class="p-6 overflow-y-auto h-full relative">
        <DashboardView v-if="activeTab === 'dashboard'" :company-name="branding.companyName" :logo-url="branding.logoUrl" />
        
        <OrderView v-else-if="activeTab === 'orders'" />
        <CreateOrderView 
          v-else-if="activeTab === 'create_order'" 
          @cancel="setActiveTab('orders', 'orders')" 
          @success="setActiveTab('orders', 'orders')" 
        />
        
        <ReceiptView v-else-if="activeTab === 'receipts'" />
        <CreateReceiptView 
          v-else-if="activeTab === 'create_receipt'" 
          @cancel="setActiveTab('receipts', 'receipts')" 
          @success="setActiveTab('receipts', 'receipts')" 
        />
        
        <InventoryView v-else-if="activeTab === 'inventory'" />
        <AuditView v-else-if="activeTab === 'audit'" />
        <SettingsView
          v-else-if="activeTab === 'settings'"
          :company-name="branding.companyName"
          :logo-url="branding.logoUrl"
          @update-company-name="updateCompanyName"
          @update-logo="updateLogo"
          @clear-branding="clearBranding"
        />
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, watch } from 'vue';
import { 
  LayoutDashboardIcon, BoxIcon, FileDownIcon, LayersIcon,
  UsersIcon, PackageIcon, HomeIcon, ExternalLinkIcon,
  ChevronDownIcon, ChevronRightIcon, SearchIcon,
  PaletteIcon, SettingsIcon
} from 'lucide-vue-next';

import DashboardView from './components/DashboardView.vue';
import InventoryView from './components/InventoryView.vue';
import OrderView from './components/OrderView.vue';
import AuditView from './components/AuditView.vue';
import ReceiptView from './components/ReceiptView.vue';
import CreateReceiptView from './components/CreateReceiptView.vue';
import CreateOrderView from './components/CreateOrderView.vue';
import SettingsView from './components/SettingsView.vue';

// 响应式状态
const themeStorageKey = 'wms-theme';
const brandingStorageKey = 'wms-branding';
const currentTheme = ref(localStorage.getItem(themeStorageKey) || 'theme-light');
const isSettingsOpen = ref(false); // 主题菜单开关

type Branding = {
  companyName: string;
  logoUrl: string;
};

const defaultBranding: Branding = {
  companyName: '',
  logoUrl: ''
};

const loadBranding = (): Branding => {
  const raw = localStorage.getItem(brandingStorageKey);
  if (!raw) {
    return { ...defaultBranding };
  }
  try {
    const parsed = JSON.parse(raw) as Partial<Branding>;
    return {
      companyName: parsed.companyName || '',
      logoUrl: parsed.logoUrl || ''
    };
  } catch {
    return { ...defaultBranding };
  }
};

const branding = reactive<Branding>(loadBranding());

const themes = [
  { name: 'Standard Light', value: 'theme-light' },
  { name: 'Midnight Ocean', value: 'theme-ocean' },
  { name: 'Nordic Sage', value: 'theme-nordic' },
  { name: 'Cyber Industrial', value: 'theme-cyber' }
];

const activeTab = ref('dashboard');
const activeGroup = ref<string | null>(null);
const expandedMenu = ref<string | null>(null);

const toggleMenu = (menu: string) => {
  expandedMenu.value = expandedMenu.value === menu ? null : menu;
};

const setActiveTab = (tab: string, group: string | null = null) => {
  activeTab.value = tab;
  activeGroup.value = group;
};

const applyThemeClass = (theme: string) => {
  const root = document.documentElement;
  for (const className of Array.from(root.classList)) {
    if (className.startsWith('theme-')) {
      root.classList.remove(className);
    }
  }
  root.classList.add(theme);
};

const selectTheme = (theme: string) => {
  currentTheme.value = theme;
  isSettingsOpen.value = false;
};

const updateCompanyName = (value: string) => {
  branding.companyName = value;
};

const updateLogo = (value: string) => {
  branding.logoUrl = value;
};

const clearBranding = () => {
  branding.companyName = '';
  branding.logoUrl = '';
};

watch(
  currentTheme,
  (theme) => {
    applyThemeClass(theme);
    localStorage.setItem(themeStorageKey, theme);
  },
  { immediate: true }
);

watch(
  () => ({ ...branding }),
  (value) => {
    localStorage.setItem(brandingStorageKey, JSON.stringify(value));
  },
  { deep: true }
);
</script>

<style>
.custom-scrollbar::-webkit-scrollbar { width: 4px; }
.custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: #1e293b; border-radius: 4px; }
.custom-scrollbar:hover::-webkit-scrollbar-thumb { background: #334155; }
</style>