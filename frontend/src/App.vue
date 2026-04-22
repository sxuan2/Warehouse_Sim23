<template>
  <div class="flex w-full h-screen bg-[#0f1115] text-[#94a3b8] font-sans selection:bg-indigo-500/30">
    
    <aside class="w-64 bg-[#0a0b0d] border-r border-[#1e293b] flex flex-col">
      <div class="p-6 flex items-center gap-3 border-b border-[#1e293b]">
        <div class="w-6 h-6 bg-white flex items-center justify-center font-bold text-black text-[10px]">
          LC
        </div>
        <span class="text-sm font-bold tracking-widest text-white uppercase italic">
          LogiCore<span class="text-indigo-500">_PRO</span>
        </span>
      </div>

      <nav class="flex-1 px-4 space-y-1 mt-4">
        <button 
          @click="activeTab = 'dashboard'"
          :class="['w-full flex items-center gap-3 p-3 cursor-pointer transition-all border border-transparent', activeTab === 'dashboard' ? 'bg-indigo-500/5 text-indigo-400 border-[#1e293b]' : 'text-slate-500 hover:text-white hover:bg-white/[0.02]']"
        >
          <LayoutDashboardIcon :size="16" :class="activeTab === 'dashboard' ? 'text-indigo-500' : 'opacity-40'" />
          <span class="text-[11px] font-semibold tracking-normal">Dashboard</span>
          <div v-if="activeTab === 'dashboard'" class="ml-auto w-1 h-3 bg-indigo-500 shadow-[0_0_8px_rgba(99,102,241,0.8)]"></div>
        </button>

        <button 
          @click="activeTab = 'inventory'"
          :class="['w-full flex items-center gap-3 p-3 cursor-pointer transition-all border border-transparent', activeTab === 'inventory' ? 'bg-indigo-500/5 text-indigo-400 border-[#1e293b]' : 'text-slate-500 hover:text-white hover:bg-white/[0.02]']"
        >
          <PackageIcon :size="16" :class="activeTab === 'inventory' ? 'text-indigo-500' : 'opacity-40'" />
          <span class="text-[11px] font-semibold tracking-normal">Inventory Control</span>
          <div v-if="activeTab === 'inventory'" class="ml-auto w-1 h-3 bg-indigo-500 shadow-[0_0_8px_rgba(99,102,241,0.8)]"></div>
        </button>

        <button 
          @click="activeTab = 'orders'"
          :class="['w-full flex items-center gap-3 p-3 cursor-pointer transition-all border border-transparent', activeTab === 'orders' ? 'bg-indigo-500/5 text-indigo-400 border-[#1e293b]' : 'text-slate-500 hover:text-white hover:bg-white/[0.02]']"
        >
          <ArrowRightLeftIcon :size="16" :class="activeTab === 'orders' ? 'text-indigo-500' : 'opacity-40'" />
          <span class="text-[11px] font-semibold tracking-normal">Order Flow</span>
          <div v-if="activeTab === 'orders'" class="ml-auto w-1 h-3 bg-indigo-500 shadow-[0_0_8px_rgba(99,102,241,0.8)]"></div>
        </button>
      </nav>

      <div class="p-6 border-t border-[#1e293b] space-y-4 bg-[#0d0f12]">
        <div class="text-[10px] text-slate-500 uppercase tracking-widest font-bold">
          [ SYSTEM_STATUS ]
        </div>
        <div class="flex items-center gap-3">
          <div class="w-1.5 h-1.5 rounded-none bg-indigo-500 shadow-[0_0_8px_rgba(99,102,241,0.8)]"></div>
          <span class="text-[10px] text-slate-500 font-semibold tracking-normal">Django Backend</span>
          <span class="ml-auto text-[8px] text-indigo-500/50 font-bold tracking-widest">ONLINE</span>
        </div>
      </div>
    </aside>

    <main class="flex-1 flex flex-col overflow-hidden">
      <header class="h-16 bg-slate-900/50 border-b border-[#1e293b] flex items-center justify-between px-8 backdrop-blur-md">
        <div class="flex items-center gap-4 text-sm text-slate-400">
          <span class="hover:text-slate-200 cursor-pointer transition-colors text-xs font-mono">SYS_ROOT</span>
          <ChevronRightIcon :size="14" class="text-slate-600" />
          <span class="text-slate-200 font-medium uppercase text-[11px] tracking-widest">{{ activeTab }}</span>
        </div>

        <div class="flex items-center gap-6">
          <div class="bg-[#0f1115] px-4 py-2 border border-[#1e293b] flex items-center gap-3 w-72 transition-all">
            <SearchIcon :size="16" class="text-slate-500" />
            <input 
              type="text" 
              placeholder="Query Serial_Hash..." 
              class="bg-transparent border-none text-sm focus:outline-none w-full placeholder:text-slate-700"
            />
          </div>
        </div>
      </header>

      <div class="p-8 space-y-6 overflow-y-auto h-full relative">
        <DashboardView v-if="activeTab === 'dashboard'" />     <InventoryView v-else-if="activeTab === 'inventory'" />
        <OrderView v-else-if="activeTab === 'orders'" />
        
        <div v-else class="flex flex-col items-center justify-center p-20 bg-[#0a0b0d] border border-[#1e293b] h-full">
          <div class="text-indigo-400 font-mono mb-2 uppercase tracking-[0.3em] text-[10px] font-bold">{{ activeTab }}_MODULE</div>
          <div class="text-slate-600 text-[10px] uppercase tracking-tighter">Module loaded. Component integration pending.</div>
        </div>
      </div>
    </main>

  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { 
  LayoutDashboardIcon, 
  PackageIcon, 
  ArrowRightLeftIcon, 
  ChevronRightIcon, 
  SearchIcon 
} from 'lucide-vue-next';

// Import child components
import InventoryView from './components/InventoryView.vue';
import OrderView from './components/OrderView.vue';
import DashboardView from './components/DashboardView.vue';

// Local state for routing
const activeTab = ref('inventory');
</script>