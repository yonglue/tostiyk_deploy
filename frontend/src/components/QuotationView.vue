<!-- src/components/QuotationDeskView.vue -->
<template>
  <div class="fixed inset-0 bg-slate-950/25 backdrop-blur-md z-40 flex flex-col overflow-hidden text-slate-900 dark:text-white font-sans transition-all">
    
    <!-- 结账成功的全屏绿色对勾遮罩 -->
    <div v-if="checkoutSuccessVisible" class="fixed inset-0 z-[100] bg-slate-900/80 backdrop-blur-sm flex items-center justify-center flex-col transition-all duration-300">
      <div class="w-40 h-40 bg-emerald-500 rounded-full flex items-center justify-center shadow-[0_0_60px_rgba(16,185,129,0.6)] animate-pop-in">
        <svg class="w-24 h-24 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7"></path>
        </svg>
      </div>
      <h2 class="text-white text-2xl font-black mt-8 tracking-widest drop-shadow-lg">{{ tExt.checkoutSuccessTitle }}</h2>
    </div>

    <!-- 右上角提示条 -->
    <transition name="fade">
      <div v-if="toastMessage" :class="toastType === 'success' ? 'bg-emerald-600/90 border-emerald-400/30' : 'bg-rose-600/90 border-rose-400/30'" class="fixed top-2 right-4 z-[100] text-white px-4 py-3 rounded-xl shadow-xl backdrop-blur-md border flex items-center gap-2 text-sm font-bold animate-bounce">
        <span>{{ toastType === 'success' ? '✅' : '❌' }}</span>
        <span>{{ toastMessage }}</span>
      </div>
    </transition>

    <!-- 顶部状态栏 -->
    <header class="h-12 bg-white dark:bg-slate-800/75 backdrop-blur-xl border-b border-white/60 px-4 flex items-center justify-between shrink-0 shadow-2xs">
      <div class="flex items-center space-x-3">
        <span class="text-white text-xs px-2.5 py-1 rounded-lg font-mono font-bold shadow-2xs bg-amber-500">
          QUOTE v1.0
        </span>
        <!-- 🖨️ 打印状态指示灯 (打印机图标版) -->
        <div class="flex items-center justify-center p-1 cursor-pointer transition-all"
             :title="isConnected ? '打印机已连接' : '⚠️ 打印服务离线，点击查看修复方法'"
             @click="!isConnected && alert('⚠️ 打印服务已离线！请检查后台代理程序，或双击桌面的“一键修复打印.bat”。')">
          <svg class="w-5 h-5 transition-colors duration-300" 
               :class="isConnected ? 'text-emerald-500' : 'text-slate-400 dark:text-slate-500'" 
               fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z"></path>
          </svg>
        </div>
        <span class="text-sm font-bold text-slate-700 dark:text-slate-300">📅 {{ currentDateTime }}</span>
        <span class="text-sm text-emerald-600 font-mono font-bold">{{ t.dashboard.bcvLabel }}: {{ bcvRate }}</span>
      </div>
      
      <div class="flex items-center space-x-2.5">
        <button @click="helpModalVisible = true" class="bg-white dark:bg-slate-800/70 hover:bg-white dark:bg-slate-800/90 text-blue-600 border border-slate-200 dark:border-slate-700 hover:border-blue-300 px-3 py-1.5 rounded-xl text-xs font-bold transition-all flex items-center gap-1 cursor-pointer shadow-2xs hover:scale-[1.02]">
          <span>⌨️ {{ t.pos.shortcutGuide }}</span>
        </button>

        <div class="flex items-center gap-2.5 pl-2.5 border-l border-slate-200 dark:border-slate-700/60">
          <div class="flex items-center gap-2 bg-white dark:bg-slate-800/70 hover:bg-blue-50/90 border border-slate-200 dark:border-slate-700 hover:border-blue-300 pl-2 pr-3.5 py-1.5 rounded-xl shadow-2xs backdrop-blur-md cursor-pointer transition-all hover:scale-[1.02]">
            <div class="relative flex items-center justify-center w-7 h-7 rounded-lg bg-gradient-to-tr from-blue-600 to-indigo-600 text-white font-black text-xs uppercase shrink-0 shadow-md shadow-blue-500/20">
              {{ currentUser?.username ? currentUser.username.charAt(0) : 'U' }}
              <span class="absolute -bottom-0.5 -right-0.5 w-2.5 h-2.5 bg-emerald-500 border-2 border-white rounded-full"></span>
            </div>
            <div class="text-left">
              <span class="text-[9px] text-slate-400 block uppercase font-extrabold tracking-wider leading-none">{{ currentUser?.role || 'staff' }}</span>
              <span class="text-xs font-bold text-slate-800 dark:text-slate-200 leading-tight block mt-0.5">{{ currentUser?.username || 'User' }}</span>
            </div>
          </div>
          <button @click="confirmExitPos" class="px-3 py-1.5 bg-white dark:bg-slate-800/70 hover:bg-rose-500/15 border border-slate-200 dark:border-slate-700 hover:border-rose-300 text-rose-600 rounded-xl text-xs font-bold transition-all cursor-pointer shadow-2xs hover:scale-[1.02]">
            {{ t.pos.exit }}
          </button>
        </div>
      </div>
    </header>

    <!-- 中间主工作区 -->
    <div class="flex-1 flex overflow-hidden p-2 gap-2 pb-12">
      <!-- 左侧：商品搜索与购物车 -->
      <div class="flex-1 flex flex-col bg-white dark:bg-slate-800/75 backdrop-blur-xl rounded-xl border border-white/60 overflow-hidden shadow-lg">
        <!-- 顶部工具栏 -->
        <div class="p-2.5 border-b border-slate-200 dark:border-slate-700/60 flex gap-2 bg-white dark:bg-slate-800/40 backdrop-blur-md items-center w-full">
          <div class="relative w-1/2">
            <input
              data-testid="quote-search-input" 
              ref="searchInputRef"
              v-model="deskSearchQuery" 
              @keydown="handleSearchKeydown"
              type="text" 
              :placeholder="t.pos.searchPlaceholder" 
              class="w-full bg-white dark:bg-slate-800/90 hover:bg-white dark:bg-slate-800 focus:bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700/80 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/30 rounded-lg px-3.5 py-2.5 text-sm text-slate-900 dark:text-white placeholder-slate-400 outline-none font-mono shadow-2xs transition-all font-bold"
            />
          </div>
          
          <div class="w-1/4">
            <div v-if="quoteClientName" class="flex items-center justify-between bg-blue-50/80 border border-blue-200/80 px-3 py-1.5 rounded-lg shadow-2xs w-full">
              <div class="flex items-center gap-2 flex-1 truncate">
                <span class="text-blue-600 text-lg">👤</span>
                <div class="truncate">
                  <div class="text-sm font-bold text-slate-800 dark:text-slate-200 leading-tight truncate">{{ quoteClientName }}</div>
                  <div class="text-[10px] text-blue-600/70 font-semibold truncate">{{ tExt.clientSelected }}</div>
                </div>
              </div>
              <button @click="quoteClientName = ''; quoteClientId = null" :title="tExt.clearClient" class="text-slate-400 hover:text-rose-500 hover:bg-rose-100 rounded-md p-1 transition-colors cursor-pointer shrink-0 ml-1">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
              </button>
            </div>
            <div v-else class="flex items-center justify-center border border-dashed border-slate-300 dark:border-slate-600 bg-slate-50 dark:bg-slate-900/50 rounded-lg px-3 py-2.5 text-slate-400 text-xs font-semibold w-full">
              {{ tExt.noClientSelected }}
            </div>
          </div>

          <div class="w-1/4">
            <button 
              @click="openClientSearchModal" 
              type="button"
              class="w-full flex items-center justify-between bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 hover:border-blue-400 hover:bg-blue-50 text-slate-600 dark:text-slate-400 rounded-lg px-3.5 py-2.5 text-xs font-bold transition-all shadow-2xs cursor-pointer"
            >
              <div class="flex items-center gap-1.5 truncate">
                <span class="text-blue-500">🔍</span>
                <span class="truncate">{{ t.pos.selectClient }}</span>
              </div>
            </button>
          </div>
        </div>

        <!-- 购物车明细表格 -->
        <div class="flex-1 overflow-y-auto p-2.5">
          <table data-testid="cart-table" class="w-full text-left border-collapse">
            <thead>
              <tr class="border-b-2 border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-400 text-xs font-extrabold uppercase bg-slate-100 dark:bg-slate-800/50">
                <th class="py-3 px-3">{{ tExt.cartOem }}</th>
                <th class="py-3 px-3">{{ tExt.cartName }}</th>
                <th class="py-3 px-3 text-right">{{ tExt.cartPrice }}</th>
                <th class="py-3 px-3 text-center">{{ tExt.cartQty }}</th>
                <th class="py-3 px-3 text-right">{{ tExt.cartSubtotal }}</th>
                <th class="py-3 px-3 text-center">{{ tExt.cartAction }}</th>
              </tr>
            </thead>
            <tbody class="text-sm font-medium">
              <tr 
                v-for="(item, index) in cartItems" 
                :key="item.oem" 
                @click="selectedCartIndex = index"
                :class="[
                  selectedCartIndex === index ? 'bg-blue-500/15 border-blue-400 ring-1 ring-blue-400' : (index % 2 === 0 ? 'bg-white dark:bg-slate-800/80' : 'bg-slate-50 dark:bg-slate-900/70'),
                  'border-b border-slate-200 dark:border-slate-700/70 hover:bg-blue-50/50 transition-all shadow-2xs cursor-pointer'
                ]"
              >
                <td class="py-3 px-3 font-mono font-black text-blue-600 text-sm">{{ item.oem }}</td>
                <td class="py-3 px-3 text-slate-900 dark:text-white font-bold">{{ item.name }}</td>
                <td class="py-3 px-3 text-right font-mono text-slate-700 dark:text-slate-300 font-bold">
                  <div>${{ item.price.toFixed(2) }}</div>
                  <div class="text-xs text-slate-400 font-normal">Bs. {{ (item.price * bcvRate).toFixed(2) }}</div>
                </td>
                <td class="py-3 px-3 text-center" @click.stop>
                  <div class="inline-flex items-center border border-slate-300 dark:border-slate-600 rounded-lg overflow-hidden bg-white dark:bg-slate-800 shadow-2xs focus-within:ring-2 focus-within:ring-blue-500 focus-within:border-blue-500">
                    <button @click="item.quantity > 1 ? item.quantity-- : null" class="px-2.5 py-1 text-slate-600 dark:text-slate-400 hover:bg-slate-200 font-bold text-sm">-</button>
                    <input v-model="itemInputQuantities[index]" @focus="$event.target.select()" @blur="applyMultiplierQuantity(index)" @keydown.enter="applyMultiplierQuantity(index)" type="text" class="w-12 text-center bg-transparent text-slate-900 dark:text-white text-sm font-mono outline-none font-black" />
                    <button @click="item.quantity++; itemInputQuantities[index] = item.quantity" class="px-2.5 py-1 text-slate-600 dark:text-slate-400 hover:bg-slate-200 font-bold text-sm">+</button>
                  </div>
                </td>
                <td class="py-3 px-3 text-right font-mono font-black text-emerald-600">
                  <div>${{ (item.price * item.quantity).toFixed(2) }}</div>
                  <div class="text-xs text-emerald-700/80 font-normal">Bs. {{ (item.price * item.quantity * bcvRate).toFixed(2) }}</div>
                </td>
                <td class="py-3 px-3 text-center" @click.stop>
                  <button @click="cartItems.splice(index, 1)" class="text-rose-600 text-xs font-bold px-2.5 py-1 bg-rose-500/10 hover:bg-rose-500/20 rounded-lg transition-all cursor-pointer shadow-2xs">{{ t.common.delete }}</button>
                </td>
              </tr>
              <tr v-if="cartItems.length === 0">
                <td colspan="6" class="text-center py-20 text-slate-400 text-sm font-bold">🛒 {{ tExt.cartEmpty }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- 右侧面板容器 -->
      <div class="w-[410px] flex flex-col bg-white dark:bg-slate-800/75 backdrop-blur-xl rounded-xl border border-white/60 shadow-lg shrink-0 overflow-hidden transition-all">
        <div class="flex flex-col h-full w-full p-4 justify-between animate-in fade-in duration-200">
          <div class="space-y-4">
            <div class="flex items-center justify-between border-b border-slate-200 dark:border-slate-700/60 pb-2">
              <h3 class="font-bold text-sm text-slate-800 dark:text-slate-200 flex items-center gap-2">📄 {{ tExt.quoteInfoTitle }}</h3>
            </div>
            <div>
              <label class="block text-xs font-bold text-slate-500 dark:text-slate-400 mb-1">{{ tExt.quoteNotesLabel }}</label>
              <textarea v-model="quoteNotes" class="w-full border border-slate-300 dark:border-slate-600 rounded-lg p-3 text-sm outline-none focus:border-amber-500 focus:ring-2 focus:ring-amber-500/20 shadow-inner" rows="6" :placeholder="tExt.quoteNotesPlaceholder"></textarea>
            </div>
            <div class="bg-amber-50 dark:bg-amber-900/30/50 p-4 rounded-xl border border-amber-200/60">
              <div class="text-xs text-amber-800 dark:text-amber-400 font-bold mb-1">{{ tExt.quoteTipTitle }}</div>
              <div class="text-xs text-amber-700/80 leading-relaxed">{{ tExt.quoteTipText }}</div>
            </div>
          </div>

          <div class="p-3 bg-white dark:bg-slate-800/90 backdrop-blur-md border-t border-slate-200 dark:border-slate-700/60 shrink-0 flex flex-col gap-2">
            <button @click="generateQuotationPDF" :disabled="cartItems.length === 0 || isSubmitting" class="w-full py-3 bg-amber-500 hover:bg-amber-400 disabled:bg-slate-200 disabled:text-slate-400 text-white rounded-xl font-black text-sm shadow-md shadow-amber-500/30 transition-all cursor-pointer flex items-center justify-center gap-1.5">
              <span>💾 {{ isSubmitting ? tExt.savingQuote : tExt.saveQuoteBtn }}</span>
            </button>
            <button data-testid="quote-credit-btn" @click="submitOrderAsCredit()" :disabled="!quoteClientId || cartItems.length === 0 || isSubmitting" class="w-full py-3 bg-rose-600 hover:bg-rose-500 disabled:bg-slate-200 disabled:text-slate-400 text-white rounded-xl font-black text-sm shadow-md shadow-rose-500/30 transition-all cursor-pointer flex items-center justify-center gap-1.5">
              <span>{{ isZh ? '📝 确认全单挂账 (Fiado)' : isEs ? '📝 Confirmar fiado completo' : '📝 Confirm Entire Credit' }}</span>
            </button>
            <p v-if="!quoteClientId && cartItems.length > 0" class="text-[10px] text-rose-500 text-center font-bold">{{ isZh ? '* 挂账前请先在顶部搜索并选择客户' : isEs ? '* Busque y seleccione cliente antes de fiar' : '* Search and select client before crediting' }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 底部快捷键导航栏 -->
    <footer class="absolute bottom-0 left-0 right-0 h-11 bg-white dark:bg-slate-800/75 backdrop-blur-xl border-t border-white/60 px-3 flex items-center justify-between z-30 shadow-md">
      <div class="grid grid-cols-6 gap-2 w-full">
        <div @click="focusSearch" class="bg-white dark:bg-slate-800/70 hover:bg-blue-500/10 border border-slate-200 dark:border-slate-700 hover:border-blue-300 rounded-lg px-2.5 py-1.5 flex items-center justify-between text-xs cursor-pointer transition-all shadow-2xs">
          <span class="text-slate-800 dark:text-slate-200 font-bold">{{ t.pos.keyFocus }} [/]</span>
          <span class="bg-blue-500/15 text-blue-700 font-mono font-bold px-1.5 py-0.5 rounded text-[10px]">{{ isZh ? '搜索' : isEs ? 'Buscar' : 'Search' }}</span>
        </div>
        <div @click="openClientSearchModal" class="bg-white dark:bg-slate-800/70 hover:bg-blue-500/10 border border-slate-200 dark:border-slate-700 hover:border-blue-300 rounded-lg px-2.5 py-1.5 flex items-center justify-between text-xs cursor-pointer transition-all shadow-2xs">
          <span class="text-slate-800 dark:text-slate-200 font-bold">{{ t.pos.keyClient }}</span>
          <span class="bg-blue-500/15 text-blue-700 font-mono font-bold px-1.5 py-0.5 rounded text-[10px]">Ctrl+F</span>
        </div>
        <div @click="generateQuotationPDF" class="bg-white dark:bg-slate-800/70 hover:bg-amber-500/10 border border-slate-200 dark:border-slate-700 hover:border-amber-300 rounded-lg px-2.5 py-1.5 flex items-center justify-between text-xs cursor-pointer transition-all shadow-2xs">
          <span class="text-slate-800 dark:text-slate-200 font-bold">{{ isZh ? '保存报价' : isEs ? 'Guardar Cotización' : 'Save Quote' }}</span>
          <span class="bg-amber-500/15 text-amber-700 font-mono font-bold px-1.5 py-0.5 rounded text-[10px]">Ctrl+S</span>
        </div>
        <div @click="$emit('clear-cart')" class="bg-white dark:bg-slate-800/70 hover:bg-rose-500/10 border border-slate-200 dark:border-slate-700 hover:border-rose-300 rounded-lg px-2.5 py-1.5 flex items-center justify-between text-xs cursor-pointer transition-all shadow-2xs">
          <span class="text-slate-800 dark:text-slate-200 font-bold">{{ t.pos.keyClear }}</span>
          <span class="bg-rose-500/15 text-rose-700 font-mono font-bold px-1.5 py-0.5 rounded text-[10px]">Ctrl+B</span>
        </div>
        <div @click="deleteLastItem" class="bg-white dark:bg-slate-800/70 hover:bg-rose-500/10 border border-slate-200 dark:border-slate-700 hover:border-rose-300 rounded-lg px-2.5 py-1.5 flex items-center justify-between text-xs cursor-pointer transition-all shadow-2xs">
          <span class="text-slate-800 dark:text-slate-200 font-bold">{{ t.pos.keyDeleteLast }}</span>
          <span class="bg-rose-500/15 text-rose-700 font-mono font-bold px-1.5 py-0.5 rounded text-[10px]">Delete</span>
        </div>
        <div @click="confirmExitPos" class="bg-white dark:bg-slate-800/70 hover:bg-slate-200/80 border border-slate-200 dark:border-slate-700 hover:border-slate-300 dark:border-slate-600 rounded-lg px-2.5 py-1.5 flex items-center justify-between text-xs cursor-pointer transition-all shadow-2xs">
          <span class="text-slate-800 dark:text-slate-200 font-bold">{{ isZh ? '退出界面' : isEs ? 'Salir' : 'Exit' }}</span>
          <span class="bg-slate-200 text-slate-800 dark:text-slate-200 font-mono font-bold px-1.5 py-0.5 rounded text-[10px]">Esc</span>
        </div>
      </div>
    </footer>

    <PosHelpModal :visible="helpModalVisible" @close="helpModalVisible = false" />

    <!-- 客户快速搜索 -->
    <div v-if="clientModalVisible" @click.self="clientModalVisible = false" class="fixed inset-0 bg-slate-950/40 backdrop-blur-md flex items-center justify-center z-50 p-4 cursor-pointer">
      <div class="bg-white dark:bg-slate-800 rounded-3xl shadow-2xl max-w-lg w-full h-[600px] max-h-[85vh] overflow-hidden border border-slate-100 dark:border-slate-800 flex flex-col cursor-default animate-in zoom-in-95 duration-150">
        <div class="p-5 border-b border-slate-100 dark:border-slate-800 flex items-center justify-between shrink-0 bg-white dark:bg-slate-800/50">
          <h3 class="font-extrabold text-base text-slate-900 dark:text-white">{{ tExt.clientModalTitle }}</h3>
          <button @click="clientModalVisible = false" class="text-slate-400 hover:text-slate-700 dark:text-slate-300 font-bold text-base p-1">✕</button>
        </div>
        <div class="p-4 border-b border-slate-100 dark:border-slate-800 bg-slate-50 dark:bg-slate-900/50 shrink-0">
          <input ref="clientModalInputRef" v-model="clientFilterQuery" @keydown="handleClientModalKeydown" type="text" :placeholder="tExt.clientModalSearch" class="w-full bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl px-4 py-3 text-sm outline-none focus:border-blue-500 shadow-sm font-bold text-slate-900 dark:text-white" />
        </div>
        <div class="flex-1 overflow-y-auto p-3 space-y-2 bg-white dark:bg-slate-800">
          <div v-for="c in filteredModalClients" :key="c.id" @click="selectClient(c)" class="p-3.5 rounded-xl border border-slate-200 dark:border-slate-700/80 bg-white dark:bg-slate-800 cursor-pointer hover:bg-blue-50 hover:border-blue-300 transition-all flex items-center justify-between text-xs shadow-2xs">
            <div>
              <div class="font-black text-slate-900 dark:text-white text-sm">🏢 {{ c.name }}</div>
            </div>
            <span class="text-blue-600 font-bold bg-blue-100/50 px-3 py-1.5 rounded-lg">{{ tExt.clientSelectBtn }} ↵</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 退出确认 -->
    <ConfirmDialog :visible="exitConfirmVisible" icon="⚠️" :title="tExt.exitTitle" :message="tExt.exitMsg" @cancel="exitConfirmVisible = false" @confirm="executeExitPos" />

    <!-- 🌟 店长授权超额挂账弹窗 (直接内联，绝对不掉链子) -->
    <div v-if="showPinModal" class="fixed inset-0 z-[9999] bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4 animate-in fade-in duration-200">
      <div class="bg-white dark:bg-slate-800 rounded-3xl shadow-2xl w-full max-w-sm overflow-hidden animate-in zoom-in-95 duration-200 border border-slate-200/80 dark:border-slate-700">
        <div class="p-6">
          <div class="w-14 h-14 bg-rose-100 dark:bg-rose-900/30 text-rose-600 dark:text-rose-400 rounded-full flex items-center justify-center mx-auto mb-4 animate-bounce">
            <svg xmlns="http://www.w3.org/2000/svg" class="w-7 h-7" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          </div>
          <h3 class="text-xl font-black text-center text-slate-800 dark:text-white mb-2">超出信用额度</h3>
          <p class="text-xs text-center text-slate-500 dark:text-slate-400 mb-6 leading-relaxed px-2">
            {{ pendingOverrideError }}
          </p>
          
          <!-- 🌟 这里加上了 form 表单 -->
          <form @submit.prevent="submitOverridePin">
            <div class="relative mb-6">
              <input 
                v-model="pinInput" 
                type="password" 
                autocomplete="new-password"
                placeholder="请输入店长安全 PIN 码"
                class="w-full bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl px-4 py-3.5 text-center tracking-[0.3em] font-mono text-lg text-slate-800 dark:text-white outline-none focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 transition-all placeholder:tracking-normal placeholder:font-sans placeholder:text-sm placeholder:text-slate-400"
              />
            </div>
            
            <div class="flex gap-3">
              <button type="button" @click="showPinModal = false" class="flex-1 py-3 rounded-xl font-bold text-slate-600 bg-slate-100 hover:bg-slate-200 transition-colors cursor-pointer">取消</button>
              <button type="submit" class="flex-1 py-3 rounded-xl font-bold text-white bg-blue-600 hover:bg-blue-700 shadow-lg shadow-blue-500/30 transition-all active:scale-95 cursor-pointer">授权放行</button>
            </div>
          </form>
          
        </div>
      </div>
    </div>

  </div> <!-- 这是最外层包裹所有界面的 div，只能有一个 -->
</template> <!-- 这是 template 的结束标签，只能有一个 -->

<script setup>
import { usePrintAgent } from '../composables/usePrintAgent'
const { isConnected } = usePrintAgent()

import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { apiFetch } from '../utils/api'
import { useI18n } from '../composables/useI18n'
import ConfirmDialog from './ConfirmDialog.vue'
import PosHelpModal from './pos/PosHelpModal.vue'
import PosHistoryModal from './pos/PosHistoryModal.vue'

const { t, currentLang } = useI18n()
const isZh = computed(() => currentLang.value === 'zh')
const isEs = computed(() => currentLang.value === 'es')

const tExt = computed(() => {
  const isZh = currentLang.value === 'zh'
  const isEs = currentLang.value === 'es'
  
  return {
    switchToCashier: isZh ? '🔄 切换回收银' : isEs ? '🔄 Cambiar a Caja' : '🔄 Switch to Cashier',
    switchToQuote: isZh ? '📄 切换到报价' : isEs ? '📄 Cambiar a Cotización' : '📄 Switch to Quote',
    quoteInfoTitle: isZh ? '报价单信息' : isEs ? 'Información de Cotización' : 'Quotation Info',
    quoteNotesLabel: isZh ? '销售备注' : isEs ? 'Notas de Venta' : 'Sales Notes',
    quoteNotesPlaceholder: isZh ? '填写客户要求、保修说明、交货期等...' : isEs ? 'Requisitos del cliente, garantía, entrega...' : 'Client requirements, warranty, delivery...',
    quoteTipTitle: isZh ? '💡 温馨提示:' : isEs ? '💡 Nota:' : '💡 Tip:',
    quoteTipText: isZh ? '生成报价单不会扣减库存。客户确认购买后，请切回收银模式重新开单收款。' : isEs ? 'Generar cotización no descuenta inventario. Cámbiese a Caja para cobrar.' : 'Quotation does not deduct inventory. Switch to Cashier to charge.',
    savingQuote: isZh ? '正在生成...' : isEs ? 'Generando...' : 'Generating...',
    saveQuoteBtn: isZh ? '保存并生成报价单 PDF' : isEs ? 'Guardar y Generar PDF' : 'Save & Generate PDF',
    genQuoteSuccess: isZh ? '报价单已生成并下载' : isEs ? 'Cotización generada y descargada' : 'Quotation generated and downloaded',
    genQuotePdfError: isZh ? '报价单生成成功，但 PDF 下载失败' : isEs ? 'Cotización generada, pero fallo al descargar PDF' : 'Quotation generated, but PDF download failed',
    genQuoteFail: isZh ? '生成报价单失败' : isEs ? 'Error al generar cotización' : 'Failed to generate quotation',
    toastInvalidRif: isZh ? 'RIF 格式错误：必须是 8 到 9 位数字' : isEs ? 'Formato RIF inválido: 8 a 9 dígitos' : 'Invalid RIF: 8-9 digits',
    toastInvalidPhone: isZh ? '电话号码错误：必须是 10 位数字' : isEs ? 'Teléfono inválido: 10 dígitos' : 'Invalid phone: 10 digits',
    
    clearClient: isZh ? '清除当前选中客户' : isEs ? 'Limpiar cliente' : 'Clear client',
    clientSelected: isZh ? '当前已选客户' : isEs ? 'Cliente Seleccionado' : 'Selected Client',
    noClientSelected: isZh ? '未选择客户' : isEs ? 'Sin cliente' : 'No Client',
    cartOem: isZh ? 'OEM 编号' : isEs ? 'OEM' : 'OEM',
    cartName: isZh ? '配件名称' : isEs ? 'Descripción' : 'Description',
    cartPrice: isZh ? '单价 ($ / Bs.)' : isEs ? 'Precio ($ / Bs.)' : 'Price ($ / Bs.)',
    cartQty: isZh ? '数量' : isEs ? 'Cant.' : 'Qty',
    cartSubtotal: isZh ? '小计 ($ / Bs.)' : isEs ? 'Subtotal ($ / Bs.)' : 'Subtotal ($ / Bs.)',
    cartAction: isZh ? '操作' : isEs ? 'Acción' : 'Action',
    cartEmpty: isZh ? '购物车为空，请按 [/] 键搜索添加...' : isEs ? 'Carrito vacío, presione [/]...' : 'Cart is empty, press [/]...',
    recallTitle: isZh ? '云端挂单恢复大厅' : isEs ? 'Sala de Recuperación de Pedidos' : 'Held Orders Recovery',
    recallBtn: isZh ? '恢复取单' : isEs ? 'Recuperar' : 'Recall',
    recallVoid: isZh ? '作废' : isEs ? 'Anular' : 'Void',
    recallTime: isZh ? '挂单时间:' : isEs ? 'Hora:' : 'Time:',
    recallEmpty: isZh ? '当前云端挂单池为空' : isEs ? 'No hay pedidos en espera' : 'No held orders',
    recallFound: isZh ? '笔挂单' : isEs ? 'pedidos' : 'orders',
    shiftTitle: isZh ? '收银交接班与营业汇总' : isEs ? 'Cierre de Caja y Resumen' : 'Shift Handover & Summary',
    shiftSystemTitle: isZh ? '1. 系统统计应收' : isEs ? '1. Esperado por Sistema' : '1. System Snapshot',
    shiftTodayOnly: isZh ? '仅统计今日订单' : isEs ? 'Solo hoy' : 'Today only',
    shiftTotalRevenue: isZh ? '系统总营业额' : isEs ? 'Total Ventas' : 'Total Revenue',
    shiftActualTitle: isZh ? '2. 收银员实盘录入款项' : isEs ? '2. Conteo Real del Cajero' : '2. Actual Count',
    shiftActualDesc: isZh ? '请仔细清点并录入抽屉及账面实际金额' : isEs ? 'Ingrese el monto real contado' : 'Enter actual counted amount',
    shiftDiff: isZh ? '盈亏' : isEs ? 'Diferencia' : 'Difference',
    shiftTotalDiff: isZh ? '折算总盈亏' : isEs ? 'Diferencia Total' : 'Total Difference',
    shiftNotes: isZh ? '盈亏原因备注' : isEs ? 'Notas de Diferencia' : 'Difference Notes',
    shiftNotesPlace: isZh ? '例如：Bs. 零钱误差...' : isEs ? 'Ej: Error de cambio...' : 'E.g. Change error...',
    shiftConfirm: isZh ? '确认交班并锁定归档' : isEs ? 'Confirmar Cierre' : 'Confirm Shift',
    ticketTitle: isZh ? '收银小票实时预览与出单' : isEs ? 'Vista Previa de Recibo' : 'Ticket Preview',
    ticketClient: isZh ? '客户' : isEs ? 'Cliente' : 'Client',
    ticketOperator: isZh ? '收银员' : isEs ? 'Cajero' : 'Operator',
    ticketPayment: isZh ? '支付明细' : isEs ? 'Desglose de Pago' : 'Payment Breakdown',
    ticketTotal: isZh ? '总计' : isEs ? 'Total' : 'Total',
    ticketPrinting: isZh ? '正在出单...' : isEs ? 'Emitiendo...' : 'Printing...',
    clientModalTitle: isZh ? '快捷选择客户' : isEs ? 'Selección Rápida de Cliente' : 'Quick Client Select',
    clientModalSearch: isZh ? '输入客户名称或电话搜索...' : isEs ? 'Buscar por nombre o teléfono...' : 'Search by name or phone...',
    clientNoPhone: isZh ? '无电话' : isEs ? 'Sin teléfono' : 'No phone',
    clientSelectBtn: isZh ? '选择此客户' : isEs ? 'Seleccionar' : 'Select',
    clientNotFound: isZh ? '未找到客户' : isEs ? 'Cliente no encontrado' : 'Client not found',
    createThisClient: isZh ? '一键新建客户' : isEs ? 'Crear nuevo cliente' : 'Create new client',
    typeToSearch: isZh ? '请输入客户名称进行搜索...' : isEs ? 'Escriba el nombre para buscar...' : 'Type name to search...',
    createClientTitle: isZh ? '快速新建客户档案' : isEs ? 'Creación Rápida de Cliente' : 'Quick Create Client',
    newClientBtn: isZh ? '新建客户' : isEs ? 'Nuevo Cliente' : 'New Client',
    clientTypeRegular: isZh ? 'Regular (零售)' : isEs ? 'Regular (Minorista)' : 'Regular (Retail)',
    clientTypeTaller: isZh ? 'Taller (修理厂)' : isEs ? 'Taller (Mecánico)' : 'Workshop',
    clientTypeMayorista: isZh ? 'Mayorista (批发商)' : isEs ? 'Mayorista (Distribuidor)' : 'Wholesaler',
    isSpecialTaxpayer: isZh ? '标记为特殊纳税人 (需代扣 IVA)' : isEs ? 'Contribuyente Especial (Retención IVA)' : 'Special Taxpayer (VAT withholding)',
    specialTaxpayerNotice: isZh ? '该客户为 SENIAT 特殊纳税人，依法需开具发票并代扣部分 IVA。' : isEs ? 'Cliente Especial (SENIAT). Requiere factura y retención de IVA.' : 'Special Taxpayer (SENIAT). Requires invoice and VAT withholding.',
    exitTitle: isZh ? '确认退出收银台？' : isEs ? '¿Salir de Caja?' : 'Exit POS?',
    exitMsg: isZh ? '当前收银台若有未结算商品，是否继续？' : isEs ? '¿Seguro? El carrito actual se perderá.' : 'Cart will be cleared. Continue?',
    toastStockError: isZh ? '库存不足' : isEs ? 'Stock insuficiente' : 'Insufficient stock',
    toastHoldSuccess: isZh ? '订单已成功挂入云端挂单池！' : isEs ? '¡Pedido pausado exitosamente!' : 'Order held successfully!',
    toastHoldEmpty: isZh ? '当前购物车为空，无需挂单！' : isEs ? 'Carrito vacío' : 'Cart is empty',
    toastRecallSuccess: isZh ? '成功取回挂单' : isEs ? 'Pedido recuperado' : 'Order recalled',
    toastRecallError: isZh ? '解析失败' : isEs ? 'Error al analizar' : 'Parse error',
    toastShiftSuccess: isZh ? '交接班成功，班次已成功锁定归档！' : isEs ? '¡Cierre de caja exitoso!' : 'Shift closed successfully!',
    toastShiftError: isZh ? '交接班归档失败' : isEs ? 'Error al cerrar caja' : 'Shift close failed',
    toastCheckoutSuccess: isZh ? '开单成功！单号:' : isEs ? '¡Venta exitosa! Nro:' : 'Checkout success! No:',
    toastCheckoutError: isZh ? '结账失败' : isEs ? 'Error al cobrar' : 'Checkout failed',
    toastReturnSuccess: isZh ? '退货成功' : isEs ? 'Devolución exitosa' : 'Return successful',
    toastReturnError: isZh ? '退货失败' : isEs ? 'Error en la devolución' : 'Return failed',
    toastReprint: isZh ? '打印小票' : isEs ? 'Reimprimir ticket' : 'Reprint ticket',
    checkoutSuccessTitle: isZh ? '交易完成！' : isEs ? '¡Pago Exitoso!' : 'Payment Successful!',
    toastClientCreated: isZh ? '客户创建成功并已选中！' : isEs ? '¡Cliente creado y seleccionado!' : 'Client created and selected!',
    errorRequired: isZh ? '请输入客户名称' : isEs ? 'Ingrese el nombre del cliente' : 'Enter client name',

    printOrderNo: isZh ? '单号:' : isEs ? 'Nro:' : 'No:',
    printDate: isZh ? '日期:' : isEs ? 'Fecha:' : 'Date:',
    printClient: isZh ? '客户:' : isEs ? 'Cliente:' : 'Client:',
    printOperator: isZh ? '收银:' : isEs ? 'Cajero:' : 'Operator:',
    printItemsTitle: isZh ? '商品' : isEs ? 'Producto' : 'Item',
    printQtyTitle: isZh ? '数量' : isEs ? 'Cant.' : 'Qty',
    printSubtotalTitle: isZh ? '小计' : isEs ? 'Subtotal' : 'Subtotal',
    printPaymentTitle: isZh ? '支付明细:' : isEs ? 'Pagos:' : 'Payments:',
    printThanks: isZh ? '感谢惠顾！' : isEs ? '¡Gracias por su compra!' : 'Thank you!',
  }
})

const props = defineProps({
  partsList: Array,
  clientsList: Array,
  cartItems: Array,
  bcvRate: Number,
  currentDateTime: String,
  currentUser: Object
})

const emit = defineEmits(['add-to-cart', 'generate-quote', 'exit-pos', 'clear-cart', 'refresh-clients'])

const deskSearchQuery = ref('')
const quoteClientName = ref('')
const quoteNotes = ref('')
const quoteClientId = ref(null)
const paymentReference = ref('')
const searchInputRef = ref(null)
const selectedIndex = ref(0)
const selectedCartIndex = ref(0)
const activeItemRef = ref(null)
const exitConfirmVisible = ref(false)

const itemInputQuantities = ref([])

watch(() => props.cartItems, (newItems) => {
  itemInputQuantities.value = newItems.map(i => String(i.quantity))
}, { deep: true, immediate: true })

const applyMultiplierQuantity = (index) => {
  const raw = String(itemInputQuantities.value[index] || '').trim()
  const item = props.cartItems[index]
  if (!item) return
  let targetQty = item.quantity
  if (raw.includes('*')) {
    const parts = raw.split('*')
    const multiplier = parseInt(parts[0])
    if (!isNaN(multiplier) && multiplier > 0) targetQty = multiplier
  } else {
    const parsed = parseInt(raw)
    if (!isNaN(parsed) && parsed > 0) targetQty = parsed
  }
  item.quantity = Math.max(1, targetQty)
  itemInputQuantities.value[index] = String(item.quantity)
}

const goodsTotalUsd = computed(() => {
  const totalCents = props.cartItems.reduce((sum, item) => {
    return sum + Math.round(item.price * 100) * item.quantity
  }, 0)
  return totalCents / 100
})

const totalBaseUsd = computed(() => {
  let totalCents = 0
  props.cartItems.forEach(item => {
    const rate = item.tax_rate ?? 0.16
    const lineTotalCents = Math.round(item.price * 100) * item.quantity
    if (rate > 0) {
      totalCents += Math.round(lineTotalCents / (1.0 + rate))
    } else {
      totalCents += lineTotalCents
    }
  })
  return totalCents / 100
})

const totalTaxUsd = computed(() => {
  const diffCents = Math.round(goodsTotalUsd.value * 100) - Math.round(totalBaseUsd.value * 100)
  return diffCents / 100
})

const totalUsd = computed(() => {
  const totalCents = Math.round(goodsTotalUsd.value * 100)
  return totalCents / 100
})

const systemConfig = ref({ company_name: 'TOSTIYK (TK) - VENEZUELA', rif: 'J-00000000-0', address: 'Valencia, Carabobo' })

const fetchSystemSettings = async () => {
  try {
    const res = await apiFetch('/api/settings')
    if (res.ok) {
      const data = await res.json()
      systemConfig.value = { ...systemConfig.value, ...data }
    }
  } catch (e) { console.error(e) }
}

const helpModalVisible = ref(false)
const toastMessage = ref('')
const toastType = ref('success')
const checkoutSuccessVisible = ref(false)
let toastTimer = null

const showToast = (msg, type = 'error') => {
  toastMessage.value = msg
  toastType.value = type
  if (toastTimer) clearTimeout(toastTimer)
  toastTimer = setTimeout(() => { toastMessage.value = '' }, 1500)
}

// 🌟 客户弹窗逻辑
const clientModalVisible = ref(false)
const clientFilterQuery = ref('')
const clientModalInputRef = ref(null)

const openClientSearchModal = async () => {
  clientFilterQuery.value = quoteClientName.value || ''
  clientModalVisible.value = true
  await nextTick()
  if (clientModalInputRef.value) {
    clientModalInputRef.value.focus()
    clientModalInputRef.value.select()
  }
}

const selectClient = (client) => {
  quoteClientName.value = client?.name || ''
  quoteClientId.value = client?.id ?? null
  clientModalVisible.value = false
}

const handleClientModalKeydown = (e) => {
  if (e.key === 'Enter') {
    const matched = filteredModalClients.value
    if (matched.length > 0) {
      selectClient(matched[0])
    }
  }
}

const filteredModalClients = computed(() => {
  if (!props.clientsList) return []
  if (!clientFilterQuery.value.trim()) return props.clientsList
  const q = clientFilterQuery.value.toUpperCase()
  return props.clientsList.filter(c => c.name.toUpperCase().includes(q) || (c.phone && c.phone.toUpperCase().includes(q)))
})

const filteredParts = computed(() => {
  const qStr = deskSearchQuery.value.trim().toUpperCase()
  if (!qStr) return []
  return props.partsList.filter(p => p.oem.toUpperCase().includes(qStr) || p.name.toUpperCase().includes(qStr)).slice(0, 10)
})

const selectAndAddToCart = (part) => {
  if (part.stock <= 0) {
    showToast(`${tExt.value.toastStockError}: ${part.oem}`, 'error')
    return
  }
  const existing = props.cartItems.find(i => i.oem === part.oem)
  if (existing) {
    existing.quantity += 1
  } else {
    props.cartItems.push({
      oem: part.oem,
      name: part.name,
      brand: part.brand || 'GENERAL',
      price: part.price,
      tax_rate: part.tax_rate ?? 0.16,
      quantity: 1
    })
  }
  deskSearchQuery.value = ''
  selectedIndex.value = 0
  focusSearch()
}

const handleSearchKeydown = (e) => {
  const results = filteredParts.value
  const hasSearchQuery = deskSearchQuery.value.trim().length > 0

  if (hasSearchQuery && results.length > 0) {
    if (e.key === 'ArrowDown') { e.preventDefault(); selectedIndex.value = (selectedIndex.value + 1) % results.length; return }
    if (e.key === 'ArrowUp') { e.preventDefault(); selectedIndex.value = (selectedIndex.value - 1 + results.length) % results.length; return }
    if (e.key === 'Enter') { e.preventDefault(); selectAndAddToCart(results[selectedIndex.value] || results[0]); return }
  }
  if (e.key === 'Enter' && results.length > 0) { e.preventDefault(); selectAndAddToCart(results[0]) }
}

const focusSearch = () => { if (searchInputRef.value) searchInputRef.value.focus() }
const deleteLastItem = () => { if (props.cartItems.length > 0) props.cartItems.pop() }
const confirmExitPos = () => { exitConfirmVisible.value = true }
const executeExitPos = () => { exitConfirmVisible.value = false; emit('exit-pos') }

const isSubmitting = ref(false)

const generateQuotationPDF = async () => {
  if (props.cartItems.length === 0) return
  isSubmitting.value = true
  
  try {
    const payload = {
      client_name: quoteClientName.value || "Cliente General",
      payment_method: "quotation",
      lang: currentLang.value,
      items: props.cartItems.map(i => ({ 
        oem: i.oem, name: i.name, brand: i.brand || "GENERAL", 
        quantity: i.quantity, price: i.price 
      }))
    }

    const res = await apiFetch('/api/quotations/generate', { method: 'POST', body: JSON.stringify(payload) })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || tExt.value.genQuoteFail)
    }
    
    checkoutSuccessVisible.value = true
    setTimeout(() => { checkoutSuccessVisible.value = false }, 1500)
    showToast('✅ ' + tExt.value.genQuoteSuccess, 'success')
    
    emit('clear-cart')
    quoteClientName.value = ''
    quoteClientId.value = null
    quoteNotes.value = ''
    
  } catch (err) {
    showToast('❌ ' + err.message, 'error')
  } finally {
    isSubmitting.value = false
  }
}

// 🌟 新增：全单挂账函数及状态
const showPinModal = ref(false)
const pinInput = ref('')
const pendingOverrideError = ref('')

const submitOverridePin = async () => {
  if (!pinInput.value) return
  showPinModal.value = false
  await submitOrderAsCredit(pinInput.value)
}

const submitOrderAsCredit = async (overridePin = null) => {
  if (!quoteClientId.value) {
    showToast('❌ 必须先选中具体客户才能挂账！', 'error')
    return
  }
  if (props.cartItems.length === 0) return

  isSubmitting.value = true
  try {
    const payload = {
      client_name: quoteClientName.value,
      client_id: quoteClientId.value,
      request_id: crypto.randomUUID ? crypto.randomUUID() : Date.now().toString(),
      payment_method: 'Fiado_USD',
      payment_reference: '全单挂账',
      bcv_rate: props.bcvRate,
      igtf_amount: 0,
      items: props.cartItems.map(i => ({ 
        oem: i.oem, name: i.name, brand: i.brand || "GENERAL", 
        quantity: i.quantity, price: i.price 
      }))
    }

    if (overridePin) {
      payload.force_override_pin = overridePin
    }

    const res = await apiFetch('/api/pos/orders', { method: 'POST', body: JSON.stringify(payload) })
    
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      
      // 🌟 拦截核心
      if (!overridePin) {
        pendingOverrideError.value = err.detail || '超出信用额度'
        showPinModal.value = true
        isSubmitting.value = false
        return
      }
      
      throw new Error(err.detail || '挂账失败')
    }
    
    const data = await res.json()
    
    // 成功提示
    checkoutSuccessVisible.value = true
    setTimeout(() => { checkoutSuccessVisible.value = false }, 1500)
    showToast(`✅ 挂账成功！单号: ${data.order_no}`, 'success')

    // 清空状态
    paymentReference.value = ''
    quoteClientName.value = ''
    quoteClientId.value = null

    // 强制清空购物车
    props.cartItems.splice(0, props.cartItems.length)
    
    emit('generate-quote')

  } catch (err) {
    showToast('❌ ' + err.message, 'error')
  } finally {
    isSubmitting.value = false
  }
}

const handleGlobalKeydown = (e) => {
  if (clientModalVisible.value || helpModalVisible.value || exitConfirmVisible.value) {
    if (e.key === 'Escape') {
      e.preventDefault()
      if (exitConfirmVisible.value) exitConfirmVisible.value = false
      else { clientModalVisible.value = false; helpModalVisible.value = false; }
      return
    }
    return
  }

  if (e.key === 'Escape') {
    e.preventDefault()
    confirmExitPos()
    return
  }

  if (e.key === '/' && document.activeElement !== searchInputRef.value) { e.preventDefault(); focusSearch(); return }
  if (e.ctrlKey && e.key.toLowerCase() === 'f') { e.preventDefault(); openClientSearchModal(); return }
  if (e.ctrlKey && e.key.toLowerCase() === 'b') { e.preventDefault(); emit('clear-cart'); return }
}

onMounted(() => {
  window.addEventListener('keydown', handleGlobalKeydown)
  focusSearch()
  fetchSystemSettings()
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleGlobalKeydown)
  if (toastTimer) clearTimeout(toastTimer)
})
</script>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity 0.2s ease, transform 0.2s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; transform: translateY(-10px); }

@keyframes popIn {
  0% { transform: scale(0.5); opacity: 0; }
  70% { transform: scale(1.1); opacity: 1; }
  100% { transform: scale(1); opacity: 1; }
}
.animate-pop-in {
  animation: popIn 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards;
}
</style>
