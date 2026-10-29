<!-- src/components/pos/PosHeader.vue -->
<script setup>
import { BarChart3, LogOut, Calendar, Keyboard, History } from 'lucide-vue-next';

defineProps({
  t: { type: Object, required: true },
  currentUser: { type: Object },
  heldOrders: { type: Array, default: () => [] },
  isConnected: { type: Boolean, default: false },
  currentDateTime: { type: String, default: '' },
  bcvRate: { type: Number, default: 1 }
})
defineEmits(['open-recall', 'open-history', 'open-shift', 'open-help', 'confirm-exit'])
</script>

<template>
  <header class="h-12 bg-surface backdrop-blur-xl border-b border-line px-4 flex items-center justify-between shrink-0 shadow-sm">
    <div class="flex items-center space-x-3">
      <span class="text-white text-xs px-2.5 py-1 rounded-lg font-mono font-bold shadow-sm bg-accent">
        POS v3.1
      </span>
      
      <!-- 打印状态指示灯 -->
      <div class="flex items-center justify-center p-1 cursor-pointer transition-all"
           :title="isConnected ? '打印机已连接' : '⚠️ 打印服务离线，点击查看修复方法'"
           @click="!isConnected && alert('⚠️ 打印服务已离线！请检查后台代理程序。')">
        <svg class="w-5 h-5 transition-colors duration-300" 
             :class="isConnected ? 'text-success' : 'text-muted'" 
             fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z"></path>
        </svg>
      </div>
      
      <span class="text-sm font-bold text-secondary">{{ currentDateTime }}</span>
      <span class="text-sm text-success font-mono font-bold">{{ t.dashboard.bcvLabel }}: {{ bcvRate }}</span>
      
      <button v-if="heldOrders.length > 0" @click="$emit('open-recall')" class="bg-surface-raised hover:bg-amber-500/10 text-amber-600 border border-line hover:border-amber-300 px-3 py-1.5 rounded-xl text-xs font-bold transition-all flex items-center gap-1 cursor-pointer shadow-sm hover:scale-[1.02]">
        <span> {{ t.pos.holdPool }} ({{ heldOrders.length }}) [Ctrl+R]</span>
      </button>
    </div>
    
    <div class="flex items-center space-x-2.5">
      <button @click="$emit('open-history')" class="bg-surface-raised hover:bg-surface-muted text-indigo-600 border border-line hover:border-indigo-300 px-3 py-1.5 rounded-xl text-xs font-bold transition-all flex items-center gap-1 cursor-pointer shadow-sm hover:scale-[1.02]">
        <span>{{ t.pos.salesHistory }}</span>
      </button>
      <button @click="$emit('open-shift')" class="bg-surface-raised hover:bg-surface-muted text-success border border-line hover:border-success/50 px-3 py-1.5 rounded-xl text-xs font-bold transition-all flex items-center gap-1 cursor-pointer shadow-sm hover:scale-[1.02]">
        <span>{{ t.pos.shiftReport }}</span>
      </button>
      <button @click="$emit('open-help')" class="bg-surface-raised hover:bg-surface-muted text-accent border border-line hover:border-accent/50 px-3 py-1.5 rounded-xl text-xs font-bold transition-all flex items-center gap-1 cursor-pointer shadow-sm hover:scale-[1.02]">
        <span>{{ t.pos.shortcutGuide }}</span>
      </button>

      <div class="flex items-center gap-2.5 pl-2.5 border-l border-line">
        <div class="flex items-center gap-2 bg-surface-raised border border-line pl-2 pr-3.5 py-1.5 rounded-xl shadow-sm backdrop-blur-md cursor-pointer transition-all hover:scale-[1.02]">
          <div class="relative flex items-center justify-center w-7 h-7 rounded-lg bg-gradient-to-tr from-accent to-indigo-600 text-white font-black text-xs uppercase shrink-0 shadow-md shadow-accent/20">
            {{ currentUser?.username ? currentUser.username.charAt(0) : 'U' }}
          </div>
          <div class="text-left">
            <span class="text-[9px] text-muted block uppercase font-extrabold tracking-wider leading-none">{{ currentUser?.role || 'staff' }}</span>
            <span class="text-xs font-bold text-primary leading-tight block mt-0.5">{{ currentUser?.username || 'User' }}</span>
          </div>
        </div>
        <button @click="$emit('confirm-exit')" class="px-3 py-1.5 bg-surface-raised hover:bg-rose-500/15 border border-line hover:border-rose-300 text-danger rounded-xl text-xs font-bold transition-all cursor-pointer shadow-sm hover:scale-[1.02]">
          {{ t.pos.exit }}
        </button>
      </div>
    </div>
  </header>
</template>