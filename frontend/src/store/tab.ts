import { defineStore } from 'pinia';
import { ref, computed } from 'vue';

export interface Tab {
  id: string;
  title: string;
  componentName: string;
  group?: string;
}

export const useTabStore = defineStore('tab', () => {
  // 默认固定打开 Dashboard
  const tabs = ref<Tab[]>([
    { id: 'dashboard', title: 'Dashboards', componentName: 'DashboardView', group: 'system' }
  ]);
  
  const activeTabId = ref('dashboard');

  const activeTab = computed(() => 
    tabs.value.find(t => t.id === activeTabId.value) || tabs.value[0]
  );

  // 提取所有需要被 KeepAlive 缓存的组件名
  const cachedComponents = computed(() => 
    Array.from(new Set(tabs.value.map(t => t.componentName)))
  );

  const openTab = (tab: Tab) => {
    const exists = tabs.value.find(t => t.id === tab.id);
    if (!exists) {
      tabs.value.push(tab);
    }
    activeTabId.value = tab.id;
  };

  const closeTab = (id: string) => {
    if (id === 'dashboard') return; // Dashboard 不允许关闭

    const index = tabs.value.findIndex(t => t.id === id);
    if (index !== -1) {
      tabs.value.splice(index, 1);
      // 如果关闭的是当前激活的，自动跳到前一个标签
      if (activeTabId.value === id) {
        activeTabId.value = tabs.value[index - 1]?.id || 'dashboard';
      }
    }
  };

  return {
    tabs,
    activeTabId,
    activeTab,
    cachedComponents,
    openTab,
    closeTab
  };
});