<template>
  <div class="flex flex-col gap-6 h-full relative">
    
    <!-- 顶部数据看板 -->
    <div class="bg-wms-bg border border-wms-border p-4 shrink-0 flex flex-col md:flex-row gap-6 justify-between">
      <div>
        <div class="text-[10px] text-indigo-400 font-bold uppercase tracking-widest">Order Flow Overview</div>
        <div class="text-[10px] text-slate-500 mt-1">
          Lifecycle: PENDING => COMPLETE => SHIPPED. Fulfillment starts at PENDING.
        </div>
      </div>
      <div class="flex gap-4">
        <div class="border border-amber-500/20 bg-amber-500/5 px-4 py-3 min-w-[120px]">
          <div class="text-[9px] uppercase font-bold tracking-widest text-amber-400">1. Queue</div>
          <div class="text-lg font-bold text-wms-text mt-1">{{ pendingOrdersCount }}</div>
          <div class="text-[10px] text-slate-500 mt-1">PENDING orders</div>
        </div>
        <div class="border border-indigo-500/20 bg-indigo-500/5 px-4 py-3 min-w-[120px]">
          <div class="text-[9px] uppercase font-bold tracking-widest text-indigo-400">2. Fulfillment</div>
          <div class="text-lg font-bold text-wms-text mt-1">{{ completeOrdersCount }}</div>
          <div class="text-[10px] text-slate-500 mt-1">COMPLETE orders</div>
        </div>
        <div class="border border-emerald-500/20 bg-emerald-500/5 px-4 py-3 min-w-[120px]">
          <div class="text-[9px] uppercase font-bold tracking-widest text-emerald-400">3. Closed</div>
          <div class="text-lg font-bold text-wms-text mt-1">{{ shippedOrdersCount }}</div>
          <div class="text-[10px] text-slate-500 mt-1">SHIPPED orders</div>
        </div>
      </div>
    </div>

    <!-- 错误横幅 -->
    <div v-if="orderStore.error" class="bg-rose-500/10 border border-rose-500/20 p-4 shrink-0 flex items-center justify-between">
      <div class="flex items-center gap-2">
        <AlertCircle class="text-rose-500" :size="16" />
        <span class="text-rose-500 text-[10px] font-bold uppercase tracking-widest">SYSTEM HALT: {{ orderStore.error }}</span>
      </div>
      <button @click="orderStore.error = null" class="text-rose-500 hover:text-wms-text transition-colors">
        <X :size="14" />
      </button>
    </div>

    <!-- 订单详情视图 -->
    <div v-if="selectedOrder" class="bg-wms-surface border border-wms-border flex flex-col flex-1 min-h-0">
      <div class="bg-wms-header border-b border-wms-border p-4 flex justify-between items-center shrink-0 shadow-lg">
        <div class="flex items-center gap-6">
          <button @click="selectedOrder = null" class="text-slate-400 hover:text-indigo-400 transition-colors bg-white/5 p-1 rounded">
            <ChevronLeft :size="18" />
          </button>
          <div>
            <div>
              <div class="text-[10px] text-slate-500 uppercase font-bold tracking-widest flex items-center gap-2">
                Order Review <span class="text-slate-700">|</span> 
                
                <!-- 系统流水号 (TXN) -->
                <span class="text-indigo-400">TXN: {{ selectedOrder.transaction_id || 'N/A' }}</span>
                
                <span class="text-slate-700">|</span> 
                
                <!-- 客户参考单号 (REF) -->
                <span class="text-indigo-400">REF: {{ selectedOrder.order_number || 'N/A' }}</span>
                
                <span class="text-slate-700">|</span> 
                
                <!-- 客户名称 -->
                <span>Client: {{ selectedOrder.client_name || 'UNKNOWN' }}</span>
              </div>
            </div>

          </div>
        </div>
        
        <div class="flex items-center gap-2">
          <!-- 取消按钮 (仅PENDING显示) -->
          <button 
            v-if="selectedOrder.status === 'PENDING'"
            @click="handleCancelOrder"
            :disabled="orderStore.isLoading"
            class="bg-rose-600/10 hover:bg-rose-600/20 text-rose-400 border border-rose-500/30 text-[10px] font-bold px-4 py-2 flex items-center gap-2 rounded shadow-sm transition-all uppercase tracking-widest mr-2"
          >
            Cancel Order
          </button>

          <button 
            v-if="selectedOrder.status === 'PENDING'"
            @click="handleFulfillOrder"
            :disabled="orderStore.isLoading"
            class="bg-indigo-600 hover:bg-indigo-500 text-wms-text text-[10px] font-bold px-4 py-2 flex items-center gap-2 rounded shadow-sm transition-all"
          >
            <Truck :size="14" /> Complete Fulfillment
          </button>
          
          <button 
            v-if="selectedOrder.status === 'COMPLETE'"
            @click="handleMarkShipped"
            :disabled="orderStore.isLoading"
            class="bg-[#0e7490] hover:bg-[#0891b2] disabled:bg-white/10 disabled:text-slate-500 text-wms-text text-[10px] font-bold px-4 py-2 flex items-center gap-2 rounded shadow-sm transition-all"
          >
            <Truck v-if="!orderStore.isLoading" :size="14" />
            <RefreshCcw v-else class="animate-spin" :size="14" />
            {{ orderStore.isLoading ? 'Updating...' : 'Mark as Shipped' }}
          </button>
          
          <span v-if="selectedOrder.status === 'COMPLETE' || selectedOrder.status === 'SHIPPED'" class="border border-emerald-500/20 text-emerald-500 text-[10px] font-bold px-4 py-2 rounded uppercase tracking-widest">
            Order Complete
          </span>

          <span v-if="selectedOrder.status === 'CANCELLED'" class="border border-rose-500/20 text-rose-500 text-[10px] font-bold px-4 py-2 rounded uppercase tracking-widest">
            Order Cancelled
          </span>

          <button
            v-if="selectedOrder.status === 'COMPLETE' || selectedOrder.status === 'SHIPPED'"
            @click="handleRevertToPending"
            :disabled="orderStore.isLoading"
            class="bg-amber-600/20 hover:bg-amber-600/30 disabled:opacity-30 text-amber-300 text-[10px] font-bold px-4 py-2 rounded uppercase tracking-widest border border-amber-500/30 transition-all"
          >
            Revert to Pending
          </button>
        </div>
      </div>

      <!-- Tab 切换 -->
      <div class="bg-wms-header border-b border-wms-border flex gap-1 px-4 pt-4 shrink-0">
        <button 
          v-for="tab in ['items', 'details']" 
          :key="tab"
          @click="activeSubTab = tab"
          :class="['px-4 py-2 text-[10px] uppercase tracking-widest font-bold transition-all border-x border-t rounded-t-sm', 
                   activeSubTab === tab ? 'bg-[#0e7490] text-wms-text border-[#0e7490]' : 'bg-white/5 text-slate-500 border-wms-border hover:bg-white/10']"
        >
          {{ tab === 'items' ? 'Order Line Items' : 'Shipping Details' }}
        </button>
      </div>

      <!-- Tab 内容 -->
      <div class="p-6 overflow-y-auto flex-1">
        <!-- Tab: Items -->
        <div v-if="activeSubTab === 'items'" class="bg-white border border-slate-200 rounded-sm shadow-sm overflow-hidden animate-in fade-in zoom-in-95 duration-200">
          <div class="p-3 bg-slate-50 border-b border-slate-200 flex justify-between items-center">
            <h4 class="text-[10px] text-[#0e7490] uppercase font-bold tracking-widest">Requested Items</h4>
          </div>
          <table class="w-full text-left border-collapse">
            <thead class="bg-[#cbd5e1] text-[10px] text-slate-700 uppercase font-bold border-b border-slate-300">
              <tr>
                <th class="p-2 border-r border-slate-300 w-16">Quantity</th>
                <th class="p-2 border-r border-slate-300">SKU Code</th>
                <th class="p-2 border-r border-slate-300">Unit of Measure</th>
                <th class="p-2 text-right">Extended Total</th>
              </tr>
            </thead>
            <tbody class="text-[11px] text-slate-700">
              <tr v-for="item in selectedOrder.items" :key="item.id" class="border-b border-slate-200 even:bg-slate-50 hover:bg-indigo-50/50 transition-colors">
                <td class="p-2 border-r border-slate-200 font-bold">{{ item.qty }}</td>
                <td class="p-2 border-r border-slate-200 font-mono text-[#0e7490]">{{ item.sku_part_number }}</td>
                <td class="p-2 border-r border-slate-200">{{ item.uom || 'Unit' }}</td>
                <td class="p-2 text-right font-bold">${{ item.price || '0.00' }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Tab: Details -->
        <div v-if="activeSubTab === 'details'" class="bg-white border border-slate-200 rounded-sm p-6 shadow-sm animate-in fade-in duration-200 text-slate-800 space-y-6">
          <div v-if="selectedOrder.cancel_reason" class="mb-4 p-4 bg-rose-50 border border-rose-200 rounded-sm">
            <span class="text-[10px] text-rose-500 font-bold uppercase tracking-widest">Cancellation Reason</span>
            <p class="text-xs font-medium text-rose-700 mt-1">{{ selectedOrder.cancel_reason }}</p>
          </div>
          
          <div class="grid grid-cols-2 md:grid-cols-4 gap-6">
            <div class="flex flex-col gap-1">
              <span class="text-[10px] text-slate-400 font-bold uppercase tracking-widest">Recipient</span>
              <span class="text-xs font-medium">{{ selectedOrder.recipient_name || 'N/A' }}</span>
            </div>
            <div class="flex flex-col gap-1">
              <span class="text-[10px] text-slate-400 font-bold uppercase tracking-widest">Company</span>
              <span class="text-xs font-medium">{{ selectedOrder.company_name || 'N/A' }}</span>
            </div>
            <div class="flex flex-col gap-1">
              <span class="text-[10px] text-slate-400 font-bold uppercase tracking-widest">Destination City</span>
              <span class="text-xs font-medium">{{ selectedOrder.city || 'N/A' }}</span>
            </div>
            <div class="flex flex-col gap-1">
              <span class="text-[10px] text-slate-400 font-bold uppercase tracking-widest">Earliest Ship Date</span>
              <span class="text-xs font-medium">{{ selectedOrder.earliest_ship_date ? new Date(selectedOrder.earliest_ship_date).toLocaleDateString() : 'Immediate' }}</span>
            </div>
            <div class="flex flex-col gap-1 md:col-span-2">
              <span class="text-[10px] text-slate-400 font-bold uppercase tracking-widest">Address</span>
              <span class="text-xs font-medium">
                {{ [selectedOrder.address1, selectedOrder.address2, selectedOrder.city, selectedOrder.state, selectedOrder.postal_code, selectedOrder.country].filter(Boolean).join(', ') || 'N/A' }}
              </span>
            </div>
            <div class="flex flex-col gap-1">
              <span class="text-[10px] text-slate-400 font-bold uppercase tracking-widest">Purchase Order</span>
              <span class="text-xs font-medium">{{ selectedOrder.purchase_order || 'N/A' }}</span>
            </div>
            <div class="flex flex-col gap-1">
              <span class="text-[10px] text-slate-400 font-bold uppercase tracking-widest">Created By</span>
              <span class="text-xs font-medium">{{ selectedOrder.created_by || 'N/A' }}</span>
            </div>
          </div>

          <div class="border-t border-slate-200 pt-4 grid grid-cols-2 md:grid-cols-4 gap-6">
            <div class="flex flex-col gap-1">
              <span class="text-[10px] text-slate-400 font-bold uppercase tracking-widest">Carrier</span>
              <span class="text-xs font-medium">{{ selectedOrder.carrier || 'N/A' }}</span>
            </div>
            <div class="flex flex-col gap-1">
              <span class="text-[10px] text-slate-400 font-bold uppercase tracking-widest">Service</span>
              <span class="text-xs font-medium">{{ selectedOrder.service || 'N/A' }}</span>
            </div>
            <div class="flex flex-col gap-1">
              <span class="text-[10px] text-slate-400 font-bold uppercase tracking-widest">Tracking #</span>
              <span class="text-xs font-medium">{{ selectedOrder.tracking_number || 'N/A' }}</span>
            </div>
            <div class="flex flex-col gap-1">
              <span class="text-[10px] text-slate-400 font-bold uppercase tracking-widest">Pickup Date</span>
              <span class="text-xs font-medium">{{ selectedOrder.pickup_date ? new Date(selectedOrder.pickup_date).toLocaleString() : 'N/A' }}</span>
            </div>

            <div class="flex flex-col gap-1">
              <span class="text-[10px] text-slate-400 font-bold uppercase tracking-widest">BOL</span>
              <span class="text-xs font-medium">{{ selectedOrder.bol_number || 'N/A' }}</span>
            </div>
            <div class="flex flex-col gap-1">
              <span class="text-[10px] text-slate-400 font-bold uppercase tracking-widest">Trailer</span>
              <span class="text-xs font-medium">{{ selectedOrder.trailer_number || 'N/A' }}</span>
            </div>
            <div class="flex flex-col gap-1">
              <span class="text-[10px] text-slate-400 font-bold uppercase tracking-widest">Door</span>
              <span class="text-xs font-medium">{{ selectedOrder.door || 'N/A' }}</span>
            </div>
            <div class="flex flex-col gap-1">
              <span class="text-[10px] text-slate-400 font-bold uppercase tracking-widest">Insurance</span>
              <span class="text-xs font-medium">{{ selectedOrder.insurance ? `Yes (${selectedOrder.insurance_amount || 0})` : 'No' }}</span>
            </div>
          </div>

          <div class="border-t border-slate-200 pt-4 grid grid-cols-1 md:grid-cols-2 gap-6">
            <div class="flex flex-col gap-1">
              <span class="text-[10px] text-slate-400 font-bold uppercase tracking-widest">Warehouse Instructions</span>
              <span class="text-xs font-medium whitespace-pre-wrap">{{ selectedOrder.warehouse_instructions || 'N/A' }}</span>
            </div>
            <div class="flex flex-col gap-1">
              <span class="text-[10px] text-slate-400 font-bold uppercase tracking-widest">Carrier Instructions</span>
              <span class="text-xs font-medium whitespace-pre-wrap">{{ selectedOrder.carrier_instructions || 'N/A' }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 订单列表视图 -->
    <div v-else class="bg-wms-bg border border-wms-border flex flex-col flex-1 min-h-0">
      <div class="flex justify-between items-center p-4 border-b border-wms-border shrink-0">
        <div class="text-xs font-bold text-wms-text tracking-widest flex items-center gap-2 uppercase">
          <ArrowRightLeft class="text-indigo-500" :size="16" />
          Order Manifests
        </div>
        <button 
          @click="orderStore.fetchOrders()"
          class="text-slate-500 hover:text-wms-text transition-colors"
        >
          <RefreshCcw :size="14" :class="{'animate-spin': orderStore.isLoading}" />
        </button>
      </div>

      <div class="overflow-y-auto flex-1">
        <table class="w-full text-left">
          <thead class="bg-wms-header text-[10px] text-slate-500 uppercase tracking-widest font-bold border-b border-wms-border sticky top-0">
            <tr>
              <!-- <th class="p-4">Transaction ID</th> -->
              <th class="p-4">Txn / Ref Number</th>
              <th class="p-4">Customer</th>
              <th class="p-4">Warehouse</th>
              <th class="p-4">Total Lines</th>
              <th class="p-4">Status</th>
              <th class="p-4 text-right">Actions</th>
            </tr>
          </thead>
          <tbody class="text-[12px] text-slate-400">
            <tr v-if="orderStore.orders.length === 0">
              <td colspan="6" class="p-20 text-center uppercase tracking-tighter opacity-30 italic">No Active Order Manifests</td>
            </tr>
            <tr 
              v-for="order in orderStore.orders" 
              :key="order.id" 
              @click="selectedOrder = order"
              class="border-b border-wms-border hover:bg-white/[0.02] cursor-pointer group transition-colors"
            >
              <!-- <td class="p-4 font-mono font-bold text-wms-text group-hover:text-indigo-400">{{ order.transaction_id || order.order_number }}</td> -->
              <td class="p-4">
                <div class="flex flex-col gap-0.5">
                  <!-- 主单号：Transaction ID -->
                  <span class="font-mono font-bold text-wms-text group-hover:text-indigo-400 transition-colors">
                    {{ order.transaction_id || 'N/A' }}
                  </span>
                  <!-- 副单号：Ref Number (变灰、字号缩小) -->
                  <span class="text-[9px] text-slate-500 font-mono uppercase tracking-widest">
                    REF: {{ order.order_number || 'N/A' }}
                  </span>
                </div>
              </td>
              <td class="p-4 opacity-80">{{ order.client_name || 'Default Client' }}</td>
              <td class="p-4 opacity-80">{{ order.warehouse_name || 'N/A' }}</td>
              <td class="p-4 font-mono">{{ order.items.length }}</td>
              <td class="p-4">
                <span :class="[
                  'px-2 py-0.5 border text-[10px] font-bold',
                  order.status === 'PENDING' ? 'bg-amber-500/10 text-amber-400 border-amber-500/20' : 
                  order.status === 'COMPLETE' ? 'bg-indigo-500/10 text-indigo-400 border-indigo-500/20' :
                  order.status === 'SHIPPED' ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' :
                  order.status === 'CANCELLED' ? 'bg-rose-500/10 text-rose-400 border-rose-500/20' :
                  'bg-slate-500/10 text-slate-400 border-slate-500/20'
                ]">
                  {{ order.status }}
               </span>
              </td>
              <td class="p-4 text-right">
                <ChevronRight :size="14" class="inline opacity-20 group-hover:opacity-100 group-hover:translate-x-1 transition-all" />
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 取消原因弹窗 -->
    <div v-if="showCancelModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
      <div class="bg-wms-surface border border-wms-border rounded shadow-2xl w-full max-w-md flex flex-col overflow-hidden animate-in fade-in zoom-in-95 duration-200">
        
        <!-- 弹窗 Header (采用经典分隔符排版) -->
        <div class="bg-rose-500/10 border-b border-rose-500/20 p-4 flex items-center justify-between">
            <h3 class="text-rose-400 font-bold uppercase tracking-widest text-[11px] flex items-center flex-wrap gap-2">
                <AlertTriangle :size="16" class="shrink-0" />
                <span>Cancel Order</span>
                <span class="text-rose-500/30 font-normal px-1">|</span>
                <span class="flex items-center gap-1">
                    <span class="text-rose-400/60">TXN:</span>
                    <span class="font-mono text-rose-200">{{ selectedOrder?.transaction_id || 'N/A' }}</span>
                </span>
                <span class="text-rose-500/30 font-normal px-1">|</span>
                <span class="flex items-center gap-1">
                    <span class="text-rose-400/60">REF:</span>
                    <span class="font-mono text-rose-200">{{ selectedOrder?.order_number || 'N/A' }}</span>
                </span>
            </h3>
            <button @click="showCancelModal = false" class="text-slate-400 hover:text-white transition-colors shrink-0">
                <X :size="16"/>
            </button>
        </div>
        
        <!-- 弹窗 Body -->
        <div class="p-6">
          <p class="text-xs text-slate-400 mb-4 leading-relaxed">
            This action will immediately set the order to <span class="text-rose-400 font-bold">CANCELLED</span> and release any locked inventory back to the warehouse pool.
          </p>
          <div class="flex flex-col gap-2">
            <label class="text-[10px] text-slate-500 font-bold uppercase tracking-widest">Cancellation Reason (Required)</label>
            <textarea 
              v-model="cancelReasonInput" 
              rows="3" 
              class="w-full bg-black/20 border border-wms-border rounded p-3 text-xs text-wms-text focus:border-rose-500/50 focus:ring-1 focus:ring-rose-500/50 outline-none transition-all placeholder:text-slate-600 resize-none" 
              placeholder="e.g. Customer requested cancellation via phone..."
            ></textarea>
          </div>
        </div>
        
        <!-- 弹窗 Footer -->
        <div class="bg-wms-header border-t border-wms-border p-4 flex justify-end gap-3">
          <button 
            @click="showCancelModal = false" 
            :disabled="isCancelling"
            class="px-4 py-2 text-[10px] font-bold text-slate-400 hover:text-white uppercase tracking-widest transition-colors disabled:opacity-50"
          >
            Abort
          </button>
          
          <button 
            @click="confirmCancel" 
            :disabled="!cancelReasonInput.trim() || isCancelling" 
            class="px-4 py-2 text-[10px] font-bold bg-rose-600 hover:bg-rose-500 disabled:opacity-30 disabled:hover:bg-rose-600 text-white rounded shadow-sm uppercase tracking-widest transition-all flex items-center gap-2"
          >
             <Loader2 v-if="isCancelling" class="animate-spin" :size="14"/>
             {{ isCancelling ? 'Processing...' : 'Confirm Cancel' }}
          </button>
        </div>
        
      </div>
    </div>

    <!-- 成功提示 Toast -->
    <transition
      enter-active-class="transition duration-300 ease-out"
      enter-from-class="transform translate-y-4 opacity-0"
      enter-to-class="transform translate-y-0 opacity-100"
      leave-active-class="transition duration-200 ease-in"
      leave-from-class="transform translate-y-0 opacity-100"
      leave-to-class="transform translate-y-4 opacity-0"
    >
      <div 
        v-if="toastMessage" 
        class="absolute bottom-6 right-6 z-[100] flex items-center gap-3 bg-[#064e3b]/80 border border-emerald-500/30 px-5 py-3 rounded shadow-2xl backdrop-blur-md"
      >
        <CheckCircle :size="18" class="text-emerald-400 shrink-0" />
        <span class="text-emerald-400 text-xs font-bold uppercase tracking-widest">{{ toastMessage }}</span>
      </div>
    </transition>

  </div>
</template>

<script setup lang="ts">
defineOptions({ name: 'OrderView' });
import { ref, computed, onMounted } from 'vue';
import { useOrderStore, type Order } from '../store/order';
import apiClient from '../api/client';
import { 
  ArrowRightLeft, 
  Truck, 
  ChevronLeft, 
  ChevronRight, 
  RefreshCcw,
  AlertCircle,
  X,
  AlertTriangle,
  Loader2,
  CheckCircle // [新增了勾选图标]
} from 'lucide-vue-next';

const showCancelModal = ref(false);
const cancelReasonInput = ref('');
const isCancelling = ref(false);

// [新增] 用于控制 Toast 提示的变量
const toastMessage = ref('');

const orderStore = useOrderStore();
const selectedOrder = ref<Order | null>(null);
const activeSubTab = ref('items');

const pendingOrdersCount = computed(() => (orderStore.orders || []).filter(o => o.status === 'PENDING').length);
const completeOrdersCount = computed(() => (orderStore.orders || []).filter(o => o.status === 'COMPLETE').length);
const shippedOrdersCount = computed(() => (orderStore.orders || []).filter(o => o.status === 'SHIPPED').length);

onMounted(() => {
  orderStore.fetchOrders();
});

// [新增] 显示 Toast 的方法，3秒后自动消失
const showToast = (msg: string) => {
  toastMessage.value = msg;
  setTimeout(() => {
    toastMessage.value = '';
  }, 3000);
};

const handleCancelOrder = () => {
  cancelReasonInput.value = ''; 
  showCancelModal.value = true;
};

const confirmCancel = async () => {
  if (!cancelReasonInput.value.trim()) return;

  const orderId = selectedOrder.value?.id;
  if (!orderId) return;

  isCancelling.value = true;
  try {
    await apiClient.post(`/warehouses/orders/${orderId}/cancel/`, {
      reason: cancelReasonInput.value.trim()
    });
    
    await orderStore.fetchOrders();
    selectedOrder.value = null;
    showCancelModal.value = false;
    
    // [修改] 调用 Toast 替代原生 alert
    showToast('Order has been cancelled successfully.'); 
  } catch (error: any) {
    const errorMsg = error.response?.data?.error || 'System error during cancellation.';
    alert(`Cancellation Failed: ${errorMsg}`);
  } finally {
    isCancelling.value = false;
  }
};

const handleFulfillOrder = async () => {
  const orderKey = selectedOrder.value?.transaction_id || selectedOrder.value?.id;
  if (!orderKey) return;
  
  try {
    const updatedOrder = await orderStore.fulfillOrder(orderKey);
    selectedOrder.value = updatedOrder;
  } catch (error) {
    console.error("Fulfillment failed due to inventory mismatch or lock error.", error);
  }
};

const handleMarkShipped = async () => {
  const orderKey = selectedOrder.value?.transaction_id || selectedOrder.value?.id;
  if (!orderKey) return;

  try {
    const updatedOrder = await orderStore.shipOrder(orderKey);
    selectedOrder.value = updatedOrder;
  } catch (error) {
    console.error('Mark as shipped failed.', error);
  }
};

const handleRevertToPending = async () => {
  const orderKey = selectedOrder.value?.transaction_id || selectedOrder.value?.id;
  if (!orderKey) return;

  try {
    const updatedOrder = await orderStore.revertOrderToPending(orderKey);
    selectedOrder.value = updatedOrder;
  } catch (error) {
    console.error('Revert to pending failed.', error);
  }
};
</script>