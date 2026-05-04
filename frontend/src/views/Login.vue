<template>
  <div class="flex items-center justify-center min-h-screen bg-slate-900 font-mono">
    <div class="p-8 bg-black border border-indigo-500/30 w-full max-w-sm">
      <h2 class="text-indigo-500 font-bold mb-6 tracking-tighter text-sm uppercase">WAREHOUSE_SYSTEM_AUTH</h2>
      <form @submit.prevent="handleLogin" class="space-y-4">
        <div>
          <label class="text-[9px] text-slate-500 block mb-1">USER_ID</label>
          <input v-model="form.username" type="text" required 
                 class="w-full bg-slate-800 border border-slate-700 p-2 text-xs text-white outline-none focus:border-indigo-500" />
        </div>
        <div>
          <label class="text-[9px] text-slate-500 block mb-1">ACCESS_KEY</label>
          <input v-model="form.password" type="password" required 
                 class="w-full bg-slate-800 border border-slate-700 p-2 text-xs text-white outline-none focus:border-indigo-500" />
        </div>
        <button type="submit" class="w-full bg-indigo-600 py-2 text-[10px] font-bold text-white uppercase hover:bg-indigo-500 transition-colors">
          Initialize_Session
        </button>
      </form>
      <p v-if="error" class="mt-4 text-rose-500 text-[9px] uppercase">{{ error }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue';
import apiClient from '../api/client';

const form = reactive({ username: '', password: '' });
const error = ref('');

const handleLogin = async () => {
  try {
    // 这里的 /token/ 对应你在 Django urls.py 里配的 TokenObtainPairView
    const res = await apiClient.post('/token/', form);
    localStorage.setItem('auth_token', res.data.access);
    // 登录成功后刷新，main.ts 就会显示 App.vue 了
    window.location.reload(); 
  } catch (e: any) {
    error.value = 'Invalid Credentials / Access Denied';
  }
};
</script>