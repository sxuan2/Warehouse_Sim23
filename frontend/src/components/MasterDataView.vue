<!-- src/components/MasterDataView.vue -->
<template>
  <div class="flex flex-col h-full gap-4">
    <!-- Internal Tab Navigation -->
    <div class="flex border-b border-wms-border bg-wms-header shrink-0 px-2 pt-2">
      <button 
        v-for="tab in internalTabs" 
        :key="tab.id"
        @click="activeSubTab = tab.id"
        :class="[
          'px-6 py-2.5 text-[10px] uppercase tracking-[0.15em] font-bold transition-all border-b-2 mx-1', 
          activeSubTab === tab.id 
            ? 'border-indigo-500 text-indigo-400 bg-indigo-500/5' 
            : 'border-transparent text-slate-500 hover:text-slate-300 hover:bg-white/5'
        ]"
      >
        {{ tab.label }}
      </button>
    </div>

    <!-- Dynamic Content Area -->
    <div class="flex-1 min-h-0">
      <!-- 使用 KeepAlive 保证子标签切换时不丢失状态（比如填了一半的搜索框） -->
      <keep-alive>
        <component :is="activeTabComponent"></component>
      </keep-alive>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';

// 必须加 name 才能被外部 App.vue 的 KeepAlive 缓存
defineOptions({ name: 'MasterDataView' });

// 导入 4 个子组件
import ClientTab from './master_data/ClientTab.vue';
import WarehouseTab from './master_data/WarehouseTab.vue';
import LocationTab from './master_data/LocationTab.vue';
import SkuTab from './master_data/SkuTab.vue';

const activeSubTab = ref('client');

const internalTabs = [
  { id: 'client', label: 'Customers / Clients' },
  { id: 'warehouse', label: 'Warehouses' },
  { id: 'location', label: 'Storage Locations' },
  { id: 'sku', label: 'Items (SKUs)' }
];

// 根据当前选中的 sub-tab 返回对应的组件
const activeTabComponent = computed(() => {
  switch (activeSubTab.value) {
    case 'client': return ClientTab;
    case 'warehouse': return WarehouseTab;
    case 'location': return LocationTab;
    case 'sku': return SkuTab;
    default: return ClientTab;
  }
});
</script>