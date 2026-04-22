<template>
  <div class="flex flex-col h-full overflow-hidden border border-wms-border bg-wms-bg animate-in fade-in duration-300">
    <div class="p-5 border-b border-wms-border bg-wms-header flex justify-between items-center shrink-0">
      <h3 class="font-bold text-wms-text text-xs tracking-widest flex items-center gap-3 uppercase">
        <ActivitySquareIcon :size="16" class="text-indigo-500" />
        System Audit Ledger
      </h3>
      <div class="flex items-center gap-4">
        <span class="text-[10px] text-slate-500 font-mono">Immutable Transaction History</span>
        <button 
          @click="auditStore.fetchTransactions()"
          class="bg-white/5 hover:bg-white/10 text-slate-400 p-2 rounded transition-colors"
        >
          <RefreshCcwIcon :size="14" :class="{'animate-spin': auditStore.isLoading}" />
        </button>
      </div>
    </div>

    <div class="flex-1 overflow-y-auto">
      <table class="w-full text-left border-collapse">
        <thead class="bg-wms-header text-[9px] text-[#8b949e] uppercase tracking-[0.2em] font-bold sticky top-0 z-10 border-b border-wms-border">
          <tr>
            <th class="px-6 py-4">Timestamp (UTC)</th>
            <th class="px-6 py-4">Operation Type</th>
            <th class="px-6 py-4">SKU Code</th>
            <th class="px-6 py-4 text-right">Qty Delta</th>
            <th class="px-6 py-4">Bin Routing</th>
            <th class="px-6 py-4">Reference</th>
          </tr>
        </thead>
        <tbody class="text-[11px] font-mono text-slate-400">
          <tr v-if="auditStore.transactions.length === 0 && !auditStore.isLoading">
            <td colspan="6" class="px-6 py-20 text-center text-slate-600 italic uppercase tracking-widest text-[10px]">
              No transactions recorded in ledger.
            </td>
          </tr>
          <tr 
            v-for="tx in auditStore.transactions" 
            :key="tx.id"
            class="border-b border-wms-border hover:bg-white/[0.02] transition-colors"
          >
            <td class="px-6 py-3 whitespace-nowrap">
              {{ new Date(tx.timestamp).toLocaleString() }}
            </td>
            <td class="px-6 py-3">
              <span :class="[
                'px-2 py-0.5 border text-[9px] font-bold tracking-widest rounded-sm',
                tx.type === 'INBOUND' ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' :
                tx.type === 'OUTBOUND' ? 'bg-rose-500/10 text-rose-400 border-rose-500/20' :
                'bg-slate-500/10 text-slate-400 border-slate-500/20'
              ]">
                {{ tx.type }}
              </span>
            </td>
            <td class="px-6 py-3 font-bold text-indigo-400">{{ tx.sku_part_number }}</td>
            <td :class="[
              'px-6 py-3 text-right font-bold',
              tx.change_qty > 0 ? 'text-emerald-400' : 'text-rose-400'
            ]">
              {{ tx.change_qty > 0 ? '+' : '' }}{{ tx.change_qty }}
            </td>
            <td class="px-6 py-3 text-[#8b949e] text-[10px]">
              <span v-if="tx.from_bin_name">{{ tx.from_bin_name }} &rarr; </span>
              <span v-if="tx.to_bin_name">{{ tx.to_bin_name }}</span>
              <span v-if="!tx.from_bin_name && !tx.to_bin_name">N/A</span>
            </td>
            <td class="px-6 py-3 text-[#8b949e]">
              {{ tx.reference_id || tx.reason || 'SYSTEM_OP' }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue';
import { useAuditStore } from '../store/audit';
import { ActivitySquareIcon, RefreshCcwIcon } from 'lucide-vue-next';

const auditStore = useAuditStore();

onMounted(() => {
  auditStore.fetchTransactions();
});
</script>