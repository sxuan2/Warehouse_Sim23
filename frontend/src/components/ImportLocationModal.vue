<!-- src/components/ImportLocationModal.vue -->
<template>
  <!-- Modal Overlay (Background) -->
  <div class="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/90 backdrop-blur-md animate-in fade-in duration-300">
    <!-- Modal Container -->
    <div class="bg-wms-bg border border-indigo-500/30 w-full max-w-4xl max-h-[90vh] flex flex-col shadow-[0_0_50px_rgba(99,102,241,0.2)] relative">
      
      <!-- Header -->
      <div class="p-6 border-b border-wms-border flex justify-between items-center shrink-0 bg-wms-header">
        <h2 class="text-wms-text text-sm font-bold uppercase tracking-[0.2em] flex items-center gap-3">
          <div class="w-1 h-5 bg-indigo-500"></div>
          Bulk Import Locations
        </h2>
        <!-- Close Button -->
        <button @click="$emit('close')" class="text-slate-500 hover:text-wms-text transition-colors">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
        </button>
      </div>

      <!-- Main Content Area -->
      <div class="p-6 overflow-y-auto flex-1 space-y-6">
        
        <!-- Action Bar (Download Template & File Upload) -->
        <div class="flex justify-between items-center bg-white/5 border border-wms-border p-4">
          <div class="text-[10px] text-slate-400 uppercase tracking-widest font-bold">
            Step 1: Download template, fill data, and upload.
          </div>
          <div class="flex gap-3">
            <!-- Download Template Button -->
            <button @click="downloadTemplate" class="px-4 py-2 border border-indigo-500/30 text-indigo-400 text-[10px] font-bold uppercase tracking-widest hover:bg-indigo-500/10 transition-colors">
              Download Template
            </button>
            <!-- File Upload Input (Hidden actual input, styled label) -->
            <label class="px-6 py-2 bg-indigo-600 hover:bg-indigo-500 text-wms-text text-[10px] font-bold uppercase tracking-widest cursor-pointer shadow-lg transition-colors flex items-center gap-2">
              <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="17 8 12 3 7 8"></polyline><line x1="12" y1="3" x2="12" y2="15"></line></svg>
              Select File (.csv, .xlsx)
              <input type="file" accept=".csv, application/vnd.openxmlformats-officedocument.spreadsheetml.sheet, application/vnd.ms-excel" class="hidden" @change="handleFileUpload">
            </label>
          </div>
        </div>

        <!-- Pre-check Errors Display (Frontend Validation) -->
        <div v-if="validationErrors.length > 0" class="bg-rose-500/10 border border-rose-500/20 p-4 animate-in fade-in zoom-in-95">
          <h4 class="text-[10px] font-bold text-rose-500 uppercase tracking-widest mb-3 flex items-center gap-2">
             <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>
             Frontend Pre-check Failed (Fix before import)
          </h4>
          <ul class="list-disc pl-5 text-rose-400 text-[11px] font-mono space-y-1">
            <li v-for="(err, idx) in validationErrors" :key="idx">{{ err }}</li>
          </ul>
        </div>

        <!-- Backend Result Message (Success or Rollback Error) -->
        <div v-if="importResult" :class="['p-4 border text-[11px] font-bold uppercase tracking-widest flex items-center justify-between', importResult.success ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400' : 'bg-rose-500/10 border-rose-500/20 text-rose-500']">
          <div class="flex items-center gap-3">
             <span v-if="importResult.success" class="flex items-center justify-center w-5 h-5 rounded-full bg-emerald-500/20"><svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg></span>
             <span v-else class="flex items-center justify-center w-5 h-5 rounded-full bg-rose-500/20"><svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg></span>
             {{ importResult.message }}
          </div>
          <button v-if="importResult.success" @click="$emit('success')" class="underline hover:text-white">Close & Refresh</button>
        </div>

        <!-- Preview Table -->
        <div v-if="previewData.length > 0" class="space-y-4 animate-in fade-in slide-in-from-bottom-4">
          <div class="flex justify-between items-end border-b border-wms-border pb-2">
            <span class="text-[10px] text-indigo-400 uppercase tracking-widest font-bold">
              Step 2: Previewing {{ previewData.length }} records ready for import
            </span>
          </div>
          
          <div class="overflow-x-auto border border-wms-border max-h-[400px] custom-scrollbar bg-wms-header/50">
            <table class="w-full text-left border-collapse whitespace-nowrap">
              <thead class="bg-wms-header text-[9px] text-slate-500 uppercase tracking-[0.2em] font-bold sticky top-0 z-10 shadow-sm">
                <tr>
                  <th class="px-4 py-3 border-b border-wms-border">Location ID</th>
                  <th class="px-4 py-3 border-b border-wms-border">Type</th>
                  <th class="px-4 py-3 border-b border-wms-border">Zone</th>
                  <th class="px-4 py-3 border-b border-wms-border text-right">Pick Path</th>
                  <th class="px-4 py-3 border-b border-wms-border text-right">Warehouse ID</th>
                </tr>
              </thead>

              <tbody class="text-[11px] text-wms-text font-mono font-medium">
                <tr v-for="(row, idx) in previewData.slice(0, 50)" :key="idx" class="border-b border-wms-border/30 hover:bg-white/[0.02]">
                  <td class="px-4 py-2 font-bold text-indigo-400">{{ row.name }}</td>
                  <td class="px-4 py-2">
                    <span class="px-2 py-0.5 border border-slate-500/30 bg-slate-500/10 rounded-sm text-[9px]">{{ row.type }}</span>
                  </td>
                  <td class="px-4 py-2">{{ row.zone || '--' }}</td>
                  <td class="px-4 py-2 text-right">{{ row.pick_path }}</td>
                  <td class="px-4 py-2 text-right">{{ row.warehouse_id || '--' }}</td>
                </tr>
                <tr v-if="previewData.length > 50">
                  <td colspan="5" class="px-4 py-6 text-center text-slate-500 text-[10px] italic tracking-widest uppercase bg-black/20">
                    ... and {{ previewData.length - 50 }} more rows hidden in preview.
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

      </div>

      <!-- Footer (Confirm Action) -->
      <div class="p-6 border-t border-wms-border bg-wms-header flex justify-end shrink-0">
         <button 
           @click="executeImport" 
           :disabled="previewData.length === 0 || validationErrors.length > 0 || isImporting" 
           class="px-8 py-3 bg-[#0e7490] hover:bg-[#0891b2] disabled:opacity-20 text-wms-text text-[10px] font-bold uppercase tracking-widest shadow-lg transition-all"
         >
          {{ isImporting ? 'Processing Transaction...' : 'Step 3: Confirm & Execute Import' }}
        </button>
      </div>

    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import * as XLSX from 'xlsx';
import apiClient from '../api/client';

// Define Events
const emit = defineEmits(['close', 'success']);

// State variables
const previewData = ref<any[]>([]);
const validationErrors = ref<string[]>([]);
const importResult = ref<{success: boolean, message: string} | null>(null);
const isImporting = ref(false);

/**
 * Generates and triggers download of the CSV template
 */
const downloadTemplate = () => {
  const headers = [
    "Location ID*", "Warehouse ID", "Location Type Identifier", "Location Zone", 
    "Location Description", "Pick Path", "Non-pickable (TRUE/FALSE)", "Width", 
    "Length", "Height", "Max Weight", "Min Temperature", "Min Quantity", 
    "Allocation Priority", "Billing Type"
  ];
  
  const exampleRow = [
    "ZONE-A-01-01", "1", "STORAGE", "A-Zone", 
    "Heavy duty rack", "10", "FALSE", "120.00", 
    "100.00", "150.00", "1000.00", "-18.00", "5", 
    "1", "Standard"
  ];

  const csvContent = "data:text/csv;charset=utf-8," 
    + headers.join(",") + "\n" 
    + exampleRow.join(",");

  const encodedUri = encodeURI(csvContent);
  const link = document.createElement("a");
  link.setAttribute("href", encodedUri);
  link.setAttribute("download", "wms_location_import_template.csv");
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};

/**
 * Handles file selection and initiates parsing
 */
const handleFileUpload = (event: Event) => {
  const file = (event.target as HTMLInputElement).files?.[0];
  if (!file) return;

  // Reset states
  validationErrors.value = [];
  importResult.value = null;
  previewData.value = [];

  const reader = new FileReader();
  reader.onload = (e) => {
    const data = new Uint8Array(e.target?.result as ArrayBuffer);
    const workbook = XLSX.read(data, { type: 'array' });
    const firstSheetName = workbook.SheetNames[0];
    const worksheet = workbook.Sheets[firstSheetName];
    
    // Convert Excel sheet to JSON array
    const rawJson = XLSX.utils.sheet_to_json(worksheet, { defval: "" });
    processAndValidateData(rawJson);
  };
  // Handle errors in file reading
  reader.onerror = () => {
      validationErrors.value.push("Failed to read the file. It might be corrupted.");
  }
  reader.readAsArrayBuffer(file);
};

/**
 * Validates required fields and formats data for backend
 */
const processAndValidateData = (rawJson: any[]) => {
  const processed = [];
  const errors = [];
  const seenNames = new Set();

  for (let i = 0; i < rawJson.length; i++) {
    const row = rawJson[i];
    // Allow fallback to generic "Location ID" if user removed the asterisk
    const rawName = row["Location ID*"] || row["Location ID"]; 
    const name = rawName?.toString().trim();
    
    // 1. Mandatory Field Check
    if (!name) {
      errors.push(`Row ${i + 2}: Location ID is required and cannot be empty.`);
      continue;
    }

    // 2. Intra-file Duplication Check
    if (seenNames.has(name)) {
      errors.push(`Row ${i + 2}: Duplicate Location ID "${name}" detected within the file.`);
      continue;
    }
    seenNames.add(name);

    // Map properties and format types
    processed.push({
      name: name,
      warehouse_id: row["Warehouse ID"] || null,
      type: row["Location Type Identifier"] || 'STORAGE',
      zone: row["Location Zone"] || null,
      description: row["Location Description"] || null,
      pick_path: parseInt(row["Pick Path"]) || 0,
      is_non_pickable: row["Non-pickable (TRUE/FALSE)"]?.toString().toUpperCase() === 'TRUE',
      width: parseFloat(row["Width"]) || 0,
      length: parseFloat(row["Length"]) || 0,
      height: parseFloat(row["Height"]) || 0,
      max_weight: parseFloat(row["Max Weight"]) || 0,
      min_temperature: parseFloat(row["Min Temperature"]) || 0,
      min_quantity: parseInt(row["Min Quantity"]) || 0,
      allocation_priority: parseInt(row["Allocation Priority"]) || 10,
      billing_type: row["Billing Type"] || null
    });
  }

  validationErrors.value = errors;
  // Only set preview data if there are no errors to prevent accidental import of partial data
  if(errors.length === 0){
     previewData.value = processed;
  }
};

/**
 * Sends the validated JSON array to the backend for bulk creation
 */
const executeImport = async () => {
  if (validationErrors.value.length > 0 || previewData.value.length === 0) return;
  
  isImporting.value = true;
  importResult.value = null; // Clear previous results
  
  try {
    const response = await apiClient.post('/warehouses/location/bulk_import/', previewData.value);
    importResult.value = { success: true, message: response.data.message };
    // Clear preview to prevent double submission
    previewData.value = []; 
  } catch (error: any) {
    // Capture backend rollback message
    importResult.value = { 
      success: false, 
      message: error.response?.data?.message || "Critical System Error during import. Transaction rolled back."
    };
  } finally {
    isImporting.value = false;
  }
};
</script>