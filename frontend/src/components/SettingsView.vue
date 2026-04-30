<template>
  <div class="max-w-3xl space-y-6 animate-in fade-in duration-300">
    <div class="bg-wms-bg border border-wms-border p-6 space-y-5">
      <div>
        <h2 class="text-sm font-bold uppercase tracking-widest text-wms-text">Company Settings</h2>
        <p class="text-[11px] text-slate-500 mt-1">Update company branding used on the dashboard and sidebar.</p>
      </div>

      <div class="space-y-2">
        <label class="text-[10px] uppercase tracking-widest font-bold text-slate-500">Company Name</label>
        <input
          :value="companyName"
          @input="onCompanyNameInput"
          type="text"
          placeholder="Enter company name"
          class="w-full bg-wms-header border border-wms-border text-[12px] px-3 py-2 text-wms-text outline-none focus:border-indigo-500"
        />
      </div>

      <div class="space-y-2">
        <label class="text-[10px] uppercase tracking-widest font-bold text-slate-500">Company Logo</label>
        <input
          type="file"
          accept="image/*"
          @change="onLogoUpload"
          class="w-full text-[12px] text-slate-400 file:mr-2 file:px-2 file:py-1 file:border file:border-wms-border file:bg-wms-header file:text-slate-300 file:text-[10px] file:uppercase file:font-bold"
        />
      </div>

      <div class="flex items-center gap-3">
        <div class="h-16 w-16 overflow-hidden rounded border border-wms-border bg-wms-header">
          <img v-if="logoUrl" :src="logoUrl" alt="Company Logo" class="h-full w-full object-cover" />
        </div>
        <div>
          <div class="text-[10px] uppercase tracking-widest font-bold text-slate-500">Preview</div>
          <div class="text-xs text-wms-text font-semibold">{{ companyName || 'No company name' }}</div>
        </div>
      </div>

      <button
        type="button"
        @click="emit('clear-branding')"
        class="px-3 py-2 text-[10px] uppercase font-bold tracking-widest border border-wms-border text-slate-500 hover:text-wms-text hover:bg-wms-header transition-colors"
      >
        Clear Branding
      </button>
    </div>
    
    <!-- Trigger Button -->
    <div class="mt-8 pt-6 border-t border-wms-border">
      <h2 class="text-sm font-bold uppercase tracking-widest text-wms-text mb-4">Data Management</h2>
      <button
        type="button"
        @click="isImportModalOpen = true"
        class="px-4 py-2 text-[10px] uppercase font-bold tracking-widest border border-indigo-500/50 text-indigo-400 hover:bg-indigo-500/10 transition-colors"
      >
        Open Location Bulk Import Tool
      </button>
    </div>

    <!-- The Modal Component -->
    <ImportLocationModal 
      v-if="isImportModalOpen" 
      @close="isImportModalOpen = false"
      @success="isImportModalOpen = false"
    />
  </div>
</template>

<script setup lang="ts">
defineOptions({ name: 'SettingsView' });

import ImportLocationModal from './ImportLocationModal.vue';
import { ref } from 'vue';
const isImportModalOpen = ref(false);

defineProps<{
  companyName: string;
  logoUrl: string;
}>();

const emit = defineEmits<{
  (e: 'update-company-name', value: string): void;
  (e: 'update-logo', value: string): void;
  (e: 'clear-branding'): void;
}>();

const onCompanyNameInput = (event: Event) => {
  const input = event.target as HTMLInputElement;
  emit('update-company-name', input.value);
};

const onLogoUpload = (event: Event) => {
  const input = event.target as HTMLInputElement;
  const file = input.files?.[0];
  if (!file) {
    return;
  }
  const reader = new FileReader();
  reader.onload = () => {
    if (typeof reader.result === 'string') {
      emit('update-logo', reader.result);
    }
  };
  reader.readAsDataURL(file);
};
</script>
