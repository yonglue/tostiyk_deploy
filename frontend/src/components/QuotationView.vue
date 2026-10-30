<!-- src/components/QuotationView.vue -->
<template>
  <div class="fixed inset-0 bg-slate-950/25 backdrop-blur-md z-40 flex flex-col overflow-hidden text-slate-900 dark:text-white font-sans transition-all">
    
    <!-- 结账成功的全屏绿色对勾遮罩 -->
    <div v-if="checkoutSuccessVisible" class="fixed inset-0 z-[100] bg-slate-900/80 backdrop-blur-sm flex items-center justify-center flex-col transition-all duration-300">
      <div class="w-40 h-40 bg-emerald-500 rounded-full flex items-center justify-center shadow-sm animate-pop-in">
        <svg class="w-24 h-24 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7"></path>
        </svg>
      </div>
      <h2 class="text-white text-2xl font-black mt-8 tracking-widest drop-shadow-lg">{{ tExt.checkoutSuccessTitle }}</h2>
    </div>

    <!-- 右上角提示条 -->
    <transition name="fade">
      <div v-if="toastMessage" :class="toastType === 'success' ? 'bg-emerald-600/90 border-emerald-400/30' : 'bg-rose-600/90 border-rose-400/30'" class="fixed top-2 right-4 z-[100] text-white px-4 py-3 rounded-xl shadow-xl backdrop-blur-md border flex items-center gap-2 text-sm font-bold animate-bounce">
        <CheckCircle2 v-if="toastType === 'success'" :size="18" />
        <XCircle v-else :size="18" />
        <span>{{ toastMessage }}</span>
      </div>
    </transition>

    <!-- 顶部状态栏 -->
    <header class="h-12 bg-white dark:bg-slate-800/75 backdrop-blur-xl border-b border-white/60 px-4 flex items-center justify-between shrink-0 shadow-2xs">
      <div class="flex items-center space-x-3">
        <span class="text-white text-xs px-2.5 py-1 rounded-lg font-mono font-bold shadow-2xs bg-amber-500">
          Cotización v1.0
        </span>
        <!-- 打印状态指示灯 -->
        <div class="flex items-center justify-center p-1 cursor-pointer transition-all"
             :title="isConnected ? '打印机已连接' : '打印服务离线，点击查看修复方法'"
             @click="!isConnected && alert('⚠️ 打印服务已离线！请检查后台代理程序。')">
          <svg class="w-5 h-5 transition-colors duration-300" 
               :class="isConnected ? 'text-emerald-500' : 'text-slate-400 dark:text-slate-500'" 
               fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z"></path>
          </svg>
        </div>
        <span class="text-sm font-bold text-slate-700 dark:text-slate-300">{{ currentDateTime }}</span>
        <span class="text-sm text-emerald-600 font-mono font-bold">{{ t.dashboard.bcvLabel }}: {{ bcvRate }}</span>
      </div>
      
      <div class="flex items-center space-x-2.5">
        <!-- 🌟 顶部右上角：切回 POS 收银台按钮 -->
        <button @click="goToPosFromQuote" class="bg-blue-50 dark:bg-blue-900/30 hover:bg-blue-100 dark:hover:bg-blue-900/50 text-blue-600 dark:text-blue-400 border border-blue-200 dark:border-blue-700/60 px-3 py-1.5 rounded-xl text-xs font-bold transition-all flex items-center gap-1.5 cursor-pointer shadow-2xs hover:scale-[1.02]">
          <ShoppingCart :size="14" />
          <span>{{ tExt.goToPosBtn }}</span>
        </button>

        <!-- 历史报价按钮 -->
        <button @click="openQuoteHistoryModal" class="bg-white dark:bg-slate-800/70 hover:bg-white dark:bg-slate-800/90 text-indigo-600 border border-slate-200 dark:border-slate-700 hover:border-indigo-300 px-3 py-1.5 rounded-xl text-xs font-bold transition-all flex items-center gap-1 cursor-pointer shadow-2xs hover:scale-[1.02]">
          <History :size="14" />
          <span>{{ tExt.historyTitle }}</span>
        </button>

        <!-- 快捷键指南按钮 -->
        <button @click="helpModalVisible = true" class="bg-white dark:bg-slate-800/70 hover:bg-white dark:bg-slate-800/90 text-accent border border-slate-200 dark:border-slate-700 hover:border-blue-300 px-3 py-1.5 rounded-xl text-xs font-bold transition-all flex items-center gap-1 cursor-pointer shadow-2xs hover:scale-[1.02]">
          <Keyboard :size="14" />
          <span>{{ t.pos.shortcutGuide }}</span>
        </button>

        <div class="flex items-center gap-2.5 pl-2.5 border-l border-slate-200 dark:border-slate-700/60">
          <div class="flex items-center gap-2 bg-white dark:bg-slate-800/70 hover:bg-accent/10/90 border border-slate-200 dark:border-slate-700 hover:border-blue-300 pl-2 pr-3.5 py-1.5 rounded-xl shadow-2xs backdrop-blur-md cursor-pointer transition-all hover:scale-[1.02]">
            <div class="relative flex items-center justify-center w-7 h-7 rounded-lg bg-gradient-to-tr from-blue-600 to-indigo-600 text-white font-black text-xs uppercase shrink-0 shadow-sm">
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
        <div class="p-2.5 border-b border-slate-200 dark:border-slate-700/60 flex gap-3 bg-white dark:bg-slate-800/40 backdrop-blur-md items-stretch w-full">
          
          <!-- 1. 搜索框 (70%) -->
          <div class="flex-[7] relative flex items-center min-w-0">
            <div class="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none">
              <Search class="h-5 w-5 text-slate-400" />
            </div>
            <input
              data-testid="quote-search-input" 
              ref="searchInputRef"
              v-model="deskSearchQuery" 
              @keydown="handleSearchKeydown"
              type="text" 
              :placeholder="t.pos.searchPlaceholder" 
              class="w-full h-12 bg-slate-50 dark:bg-slate-900/50 hover:bg-slate-100 dark:hover:bg-slate-900 focus:bg-white dark:focus:bg-slate-900 border border-slate-200 dark:border-slate-700 focus:border-accent focus:ring-2 focus:ring-accent/20 rounded-xl pl-11 pr-4 text-sm text-slate-900 dark:text-white placeholder-slate-400 outline-none font-mono shadow-sm transition-all font-bold"
            />
          </div>
          
          <!-- 2. 客户选择框 (30%) -->
          <div class="flex-[3] flex items-center min-w-0">
            <button 
              v-if="quoteClientName" 
              @click="openClientSearchModal"
              type="button"
              class="w-full h-12 flex items-center justify-between bg-blue-50/60 dark:bg-blue-900/20 hover:bg-blue-100/80 dark:hover:bg-blue-900/40 border border-blue-200/60 dark:border-blue-700/50 px-3.5 rounded-xl shadow-sm transition-all group overflow-hidden cursor-pointer"
            >
              <div class="flex items-center gap-3 truncate w-full">
                <div class="w-8 h-8 rounded-full bg-blue-100 dark:bg-blue-800/50 flex items-center justify-center shrink-0">
                  <User :size="16" class="text-blue-600 dark:text-blue-400" />
                </div>
                <div class="flex flex-col text-left truncate leading-tight flex-1">
                  <div class="text-sm font-bold text-slate-800 dark:text-slate-200 truncate">
                    {{ selectedClientDetails?.store_name || quoteClientName }}
                  </div>
                  <div class="text-[10px] text-slate-500 dark:text-slate-400 font-semibold flex items-center gap-2 mt-0.5 truncate">
                    <span v-if="selectedClientDetails?.store_name" class="truncate">👤 {{ quoteClientName }}</span>
                    <span v-if="selectedClientDetails?.phone" class="truncate">📞 {{ selectedClientDetails.phone }}</span>
                    <span v-if="selectedClientDetails?.debt > 0" class="text-rose-500 font-bold shrink-0">欠款: ${{ selectedClientDetails.debt.toFixed(2) }}</span>
                  </div>
                </div>
              </div>
              <div class="shrink-0 text-blue-400 group-hover:text-blue-600 dark:group-hover:text-blue-300 ml-2">
                <ChevronDown :size="18" />
              </div>
            </button>

            <button 
              v-else
              @click="openClientSearchModal" 
              type="button"
              class="w-full h-12 flex items-center justify-between bg-slate-50 dark:bg-slate-900/50 border border-dashed border-slate-300 dark:border-slate-600 hover:border-blue-400 dark:hover:border-blue-500 hover:bg-blue-50 dark:hover:bg-slate-800 text-slate-500 dark:text-slate-400 rounded-xl px-4 text-sm font-bold transition-all shadow-sm cursor-pointer"
            >
              <div class="flex items-center gap-2 truncate">
                <Search :size="16" />
                <span class="truncate">{{ t.pos.selectClient }}</span>
              </div>
              <span class="text-slate-400 font-mono text-[10px] hidden sm:inline shrink-0">Ctrl+F</span>
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
                  selectedCartIndex === index ? 'bg-accent/100/15 border-blue-400 ring-1 ring-blue-400' : (index % 2 === 0 ? 'bg-white dark:bg-slate-800/80' : 'bg-slate-50 dark:bg-slate-900/70'),
                  'border-b border-slate-200 dark:border-slate-700/70 hover:bg-accent/10/50 transition-all shadow-2xs cursor-pointer'
                ]"
              >
                <td class="py-3 px-3 font-mono font-black text-accent text-sm">{{ item.oem }}</td>
                <td class="py-3 px-3 text-slate-900 dark:text-white font-bold">{{ item.name }}</td>
                <td class="py-3 px-3 text-right font-mono font-bold text-slate-700 dark:text-slate-300">
                  <div 
                    class="inline-flex items-center justify-end gap-1"
                    :title="item.price < item.cost_price ? `注意：当前售价低于成本价 $${item.cost_price.toFixed(2)}` : ''"
                  >
                    <span class="text-slate-400 text-sm" :class="{ 'text-rose-400': item.price < item.cost_price }">$</span>
                    
                    <input 
                      v-model.number="item.price"
                      type="number"
                      step="0.01"
                      min="0"
                      @blur="(e) => { item.price = Number(Number(e.target.value).toFixed(2)) }"
                      @keyup.enter="(e) => { item.price = Number(Number(e.target.value).toFixed(2)); e.target.blur() }"
                      :class="[
                        'w-20 text-right bg-surface-raised border rounded px-2 py-1 outline-none transition-colors',
                        item.price < item.cost_price 
                          ? 'border-rose-400 text-rose-600 focus:border-rose-500' 
                          : 'border-line text-primary focus:border-accent'
                      ]"
                    />
                    
                    <div v-if="item.price < item.cost_price" class="text-rose-500 cursor-help">
                      <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path></svg>
                    </div>
                  </div>
                  
                  <div class="text-xs text-slate-400 font-normal mt-1">
                    Bs. {{ (item.price * bcvRate).toFixed(2) }}
                  </div>
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
                <td colspan="6" class="text-center py-20 text-slate-400 text-sm font-bold">
                  {{ tExt.cartEmpty }}
                </td>
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
              <h3 class="font-bold text-sm text-slate-800 dark:text-slate-200 flex items-center gap-2">
                <FileText :size="18" /> {{ tExt.quoteInfoTitle }}
              </h3>
            </div>
            <div>
              <label class="block text-xs font-bold text-slate-500 dark:text-slate-400 mb-1">{{ tExt.quoteNotesLabel }}</label>
              <textarea v-model="quoteNotes" class="w-full border border-slate-300 dark:border-slate-600 rounded-lg p-3 text-sm outline-none focus:border-amber-500 focus:ring-0 shadow-inner" rows="6" :placeholder="tExt.quoteNotesPlaceholder"></textarea>
            </div>
            <div class="bg-amber-50 dark:bg-amber-900/30/50 p-4 rounded-xl border border-amber-200/60">
              <div class="text-xs text-amber-800 dark:text-amber-400 font-bold mb-1 flex items-center gap-1">
                <Info :size="14" />
                {{ tExt.quoteTipTitle }}
              </div>
              <div class="text-xs text-amber-700/80 leading-relaxed">{{ tExt.quoteTipText }}</div>
            </div>
          </div>

          <div class="p-3 bg-white dark:bg-slate-800/90 backdrop-blur-md border-t border-slate-200 dark:border-slate-700/60 shrink-0 flex flex-col gap-2">
            
            <!-- 实时超额警告 -->
            <div v-if="isOverCreditLimit" class="bg-rose-50 dark:bg-rose-900/30 border border-rose-200 p-2.5 rounded-lg flex items-start gap-2 animate-pulse">
              <AlertTriangle :size="16" class="text-rose-500 mt-0.5 shrink-0" />
              <div class="text-xs text-rose-600 font-bold leading-tight">
                {{ isZh ? '该客户信用额度已超限！' : isEs ? '¡Límite excedido!' : 'Credit limit exceeded.' }}
              </div>
            </div>

            <!-- Guardar 与 Imprimir 双按钮 -->
            <div class="flex gap-2 w-full mt-2">
              <button @click="generateQuotationPDF" :disabled="cartItems.length === 0 || isSubmitting" class="flex-1 py-3 bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-600 hover:bg-slate-50 dark:hover:bg-slate-700 disabled:opacity-50 text-slate-700 dark:text-slate-300 rounded-xl font-black text-sm shadow-sm transition-all cursor-pointer flex items-center justify-center gap-2">
                <Download :size="18" />
                {{ tExt.guardarBtn }}
              </button>
              <button @click="printQuotationReceipt" :disabled="cartItems.length === 0 || isSubmitting || !isConnected" class="flex-1 py-3 bg-accent hover:bg-accent/100 disabled:bg-slate-300 dark:disabled:bg-slate-700 text-white rounded-xl font-black text-sm shadow-sm transition-all cursor-pointer flex items-center justify-center gap-2">
                <Printer :size="18" />
                {{ tExt.printBtn }}
              </button>
            </div>

          </div>
        </div>
      </div>
    </div>

    <!-- 底部快捷键导航栏 -->
    <footer class="absolute bottom-0 left-0 right-0 h-11 bg-white dark:bg-slate-800/75 backdrop-blur-xl border-t border-white/60 px-3 flex items-center justify-between z-30 shadow-md">
      <div class="grid grid-cols-6 gap-2 w-full">
        <div @click="focusSearch" class="bg-white dark:bg-slate-800/70 hover:bg-accent/100/10 border border-slate-200 dark:border-slate-700 hover:border-blue-300 rounded-lg px-2.5 py-1.5 flex items-center justify-between text-xs cursor-pointer transition-all shadow-2xs">
          <span class="text-slate-800 dark:text-slate-200 font-bold">{{ t.pos.keyFocus }} [/]</span>
          <span class="bg-accent/100/15 text-accent font-mono font-bold px-1.5 py-0.5 rounded text-[10px]">{{ isZh ? '搜索' : isEs ? 'Buscar' : 'Search' }}</span>
        </div>
        <div @click="openClientSearchModal" class="bg-white dark:bg-slate-800/70 hover:bg-accent/100/10 border border-slate-200 dark:border-slate-700 hover:border-blue-300 rounded-lg px-2.5 py-1.5 flex items-center justify-between text-xs cursor-pointer transition-all shadow-2xs">
          <span class="text-slate-800 dark:text-slate-200 font-bold">{{ t.pos.keyClient }}</span>
          <span class="bg-accent/100/15 text-accent font-mono font-bold px-1.5 py-0.5 rounded text-[10px]">Ctrl+F</span>
        </div>
        <div @click="generateQuotationPDF" class="bg-white dark:bg-slate-800/70 hover:bg-amber-500/10 border border-slate-200 dark:border-slate-700 hover:border-amber-300 rounded-lg px-2.5 py-1.5 flex items-center justify-between text-xs cursor-pointer transition-all shadow-2xs">
          <span class="text-slate-800 dark:text-slate-200 font-bold">{{ isZh ? '保存报价' : isEs ? 'Guardar' : 'Save' }}</span>
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

    <!-- 客户快速搜索 Modal -->
    <div v-if="clientModalVisible" @click.self="clientModalVisible = false" class="fixed inset-0 bg-slate-950/40 backdrop-blur-md flex items-center justify-center z-[60] p-6 cursor-pointer">
      <div class="bg-white dark:bg-slate-800/90 backdrop-blur-2xl rounded-3xl shadow-2xl max-w-5xl w-full h-[88vh] max-h-[900px] overflow-hidden border border-white/80 flex flex-col cursor-default">
        
        <div class="p-5 border-b border-slate-200 dark:border-slate-700/60 flex items-center justify-between bg-white dark:bg-slate-800/50 shrink-0">
          <h3 class="font-extrabold text-base text-slate-900 dark:text-white flex items-center gap-2"><span>{{ tExt.clientModalTitle }}</span></h3>
          <button @click="clientModalVisible = false" class="text-slate-400 hover:text-slate-700 dark:text-slate-300 text-base font-bold p-1 cursor-pointer">✕</button>
        </div>

        <div class="flex-1 flex flex-col overflow-hidden bg-slate-50 dark:bg-slate-900/20 p-5">
          <div class="space-y-4 shrink-0">
            <div class="relative">
              <div class="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none">
                <Search class="h-5 w-5 text-slate-400" />
              </div>
              <input 
                ref="clientModalInputRef" 
                v-model="clientFilterQuery" 
                @keydown="handleClientModalKeydown" 
                type="text" 
                :placeholder="tExt.clientModalSearch" 
                class="w-full h-12 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl pl-11 pr-4 text-sm outline-none focus:border-accent focus:ring-2 focus:ring-accent/20 shadow-sm font-bold text-slate-900 dark:text-white transition-all" 
              />
            </div>
            
            <div v-if="quoteClientId" class="flex items-center justify-between text-sm px-1">
              <span class="text-slate-500 font-medium">已选: <strong class="text-slate-800 dark:text-slate-200">{{ quoteClientName }}</strong></span>
              <button @click="clearClient(); clientModalVisible = false" class="text-rose-500 hover:text-rose-600 font-bold flex items-center gap-1 transition-colors">
                <XCircle :size="16" />
                清除客户
              </button>
            </div>
          </div>

          <div class="flex-1 overflow-y-auto mt-4 space-y-3 pb-4">
            <div 
              v-for="c in filteredModalClients" 
              :key="c.id" 
              @click="selectClient(c)" 
              class="p-4 rounded-xl border border-slate-200 dark:border-slate-700/80 bg-white dark:bg-slate-800 cursor-pointer hover:border-accent hover:shadow-md transition-all flex items-center justify-between gap-6"
            >
              <div class="flex items-center gap-4 w-[35%] shrink-0">
                <div class="w-12 h-12 rounded-full bg-slate-100 dark:bg-slate-700 flex items-center justify-center shrink-0">
                  <Building2 :size="20" class="text-slate-500 dark:text-slate-400" />
                </div>
                <div class="flex flex-col truncate">
                  <span class="font-bold text-base text-slate-900 dark:text-white truncate">{{ c.store_name || c.name }}</span>
                  <span class="text-xs text-slate-500 font-medium flex flex-wrap gap-2 mt-1">
                    <span v-if="c.store_name" class="truncate">👤 {{ c.name }}</span>
                    <span v-if="c.phone" class="truncate">📞 {{ c.phone }}</span>
                    <span v-if="c.rif" class="truncate font-mono">ID: {{ c.rif }}</span>
                  </span>
                </div>
              </div>

              <div class="flex-1 flex flex-col min-w-0 border-l border-slate-100 dark:border-slate-700/50 pl-6">
                <div class="flex flex-wrap gap-1.5 mb-1">
                  <span class="px-2 py-0.5 bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300 text-[10px] font-bold rounded">
                    {{ c.client_type || 'Regular' }}
                  </span>
                  <span v-if="c.is_special_taxpayer" class="px-2 py-0.5 bg-amber-100 dark:bg-amber-900/40 text-amber-700 dark:text-amber-400 text-[10px] font-bold rounded border border-amber-200 dark:border-amber-800">
                    Contribuyente Especial
                  </span>
                </div>
                <span class="text-xs text-slate-400 truncate">📍 {{ c.address || 'No hay dirección registrada' }}</span>
              </div>

              <div class="w-[30%] shrink-0 flex items-center justify-end gap-4 border-l border-slate-100 dark:border-slate-700/50 pl-6">
                <div class="flex flex-col items-end gap-0.5">
                  <span class="text-[10px] text-slate-400 font-bold uppercase tracking-wider">Deuda Actual</span>
                  <span :class="Number(c.debt) > 0 ? 'text-rose-500' : 'text-slate-400'" class="font-black font-mono text-base">
                    ${{ Number(c.debt || 0).toFixed(2) }}
                  </span>
                  <span v-if="c.credit_limit" class="text-[9px] text-slate-400 font-medium">Límite: ${{ Number(c.credit_limit).toFixed(2) }}</span>
                </div>
                <button class="px-5 py-2.5 bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 rounded-lg text-sm font-bold shadow-sm hover:bg-blue-100 dark:hover:bg-blue-900/50 transition-colors shrink-0">{{ tExt.clientSelectBtn }}</button>
              </div>
            </div>
            
            <div v-if="filteredModalClients.length === 0" class="h-full flex flex-col items-center justify-center text-slate-400 text-sm font-bold gap-3 py-10">
              <span>{{ tExt.clientNotFound }}</span>
              <button v-if="clientFilterQuery.trim()" @click="prepareCreateClient(clientFilterQuery)" class="px-6 py-3 bg-accent text-white rounded-xl font-bold text-sm shadow-md hover:bg-accent-hover transition-colors">
                + {{ tExt.createThisClient }}
              </button>
            </div>
          </div>
        </div>

        <div class="p-5 bg-white dark:bg-slate-800/80 backdrop-blur-md border-t border-slate-200 dark:border-slate-700/60 flex items-center justify-between shrink-0">
          <span class="text-xs text-slate-600 dark:text-slate-400 font-mono font-bold">Encontrados: <strong class="text-slate-900 dark:text-white">{{ filteredModalClients.length }}</strong></span>
          <button @click="clientModalVisible = false" class="px-6 py-2 bg-slate-200/80 hover:bg-slate-300 text-slate-700 dark:text-slate-300 rounded-xl text-xs font-bold transition-colors cursor-pointer">{{ t.common.cancel }}</button>
        </div>
      </div>
    </div>

    <!-- 新建客户 Modal -->
    <div v-if="newClientModalVisible" @click.self="newClientModalVisible = false" class="fixed inset-0 bg-slate-950/60 backdrop-blur-md flex items-center justify-center z-[60] p-6">
      <div class="bg-white dark:bg-slate-800 rounded-3xl shadow-2xl max-w-lg w-full overflow-hidden border border-slate-100 dark:border-slate-800 flex flex-col animate-in zoom-in-95 duration-150">
        <div class="p-5 border-b border-slate-200 dark:border-slate-700/60 flex items-center justify-between bg-white dark:bg-slate-800/50 shrink-0">
          <h3 class="font-extrabold text-base text-slate-900 dark:text-white">{{ tExt.createClientTitle }}</h3>
          <button @click="newClientModalVisible = false" class="text-slate-400 hover:text-slate-700 dark:text-slate-300 font-bold text-base p-1">✕</button>
        </div>
        <div class="p-5 space-y-4">
          <div><label class="block text-xs font-semibold text-slate-500 dark:text-slate-400 mb-1">{{ t.clients.colName }} *</label><input v-model="newClientForm.name" type="text" class="w-full bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl px-3.5 py-2.5 text-sm outline-none focus:border-accent font-bold text-slate-900 dark:text-white" placeholder="Ej: Auto Taller Valencia" /></div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-semibold text-slate-500 dark:text-slate-400 mb-1">{{ t.clients.colRif }}</label>
              <div class="flex gap-2">
                <select v-model="newClientForm.rif_type" class="w-16 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl px-2 py-2.5 text-sm outline-none focus:border-accent font-bold text-slate-900 dark:text-white cursor-pointer"><option value="V">V</option><option value="E">E</option><option value="J">J</option><option value="G">G</option></select>
                <input v-model="newClientForm.rif_number" @input="formatRifNumber" type="text" maxlength="9" class="flex-1 w-full bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl px-3.5 py-2.5 text-sm outline-none focus:border-accent font-mono text-slate-900 dark:text-white" placeholder="12345678" />
              </div>
            </div>
            <div>
              <label class="block text-xs font-semibold text-slate-500 dark:text-slate-400 mb-1">{{ t.clients.colPhone }}</label>
              <div class="flex">
                <span class="inline-flex items-center px-3 rounded-l-xl border border-r-0 border-slate-200 dark:border-slate-700 bg-slate-100 dark:bg-slate-800 text-slate-500 dark:text-slate-400 text-sm font-mono font-bold">+58</span>
                <input v-model="newClientForm.phone" @input="formatPhoneNumber" type="text" maxlength="10" class="flex-1 w-full bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-r-xl px-3.5 py-2.5 text-sm outline-none focus:border-accent font-mono text-slate-900 dark:text-white" placeholder="4121234567" />
              </div>
            </div>
          </div>
          <div><label class="block text-xs font-semibold text-slate-500 dark:text-slate-400 mb-1">{{ t.clients.colType }}</label><select v-model="newClientForm.client_type" class="w-full bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl px-3.5 py-2.5 text-sm outline-none focus:border-accent font-semibold text-slate-900 dark:text-white cursor-pointer"><option value="Regular">{{ tExt.clientTypeRegular }}</option><option value="Taller">{{ tExt.clientTypeTaller }}</option><option value="Mayorista">{{ tExt.clientTypeMayorista }}</option></select></div>
          <div class="flex items-center gap-3 bg-amber-50 dark:bg-amber-900/30 border border-amber-200 p-3 rounded-xl"><input type="checkbox" id="specialTax" v-model="newClientForm.is_special_taxpayer" class="w-4 h-4 text-amber-600 rounded border-amber-300 focus:ring-0 cursor-pointer" /><label for="specialTax" class="text-xs font-bold text-amber-900 cursor-pointer">{{ tExt.isSpecialTaxpayer }}</label></div>
        </div>
        <div class="p-5 border-t border-slate-100 dark:border-slate-800 flex justify-end gap-3 bg-slate-50 dark:bg-slate-900/50">
          <button @click="newClientModalVisible = false" class="px-5 py-2.5 rounded-xl text-xs font-bold bg-slate-200 text-slate-600 dark:text-slate-400 hover:bg-slate-300 transition-colors cursor-pointer">{{ t.common.cancel }}</button>
          <button @click="saveNewClient" :disabled="isSavingClient" class="px-6 py-2.5 rounded-xl text-xs font-bold bg-accent text-white hover:bg-accent-hover shadow-md transition-colors cursor-pointer disabled:opacity-50">{{ isSavingClient ? '...' : t.common.save }}</button>
        </div>
      </div>
    </div>

    <!-- 退出确认 -->
    <ConfirmDialog :visible="exitConfirmVisible" icon="" :title="tExt.exitTitle" :message="tExt.exitMsg" @cancel="exitConfirmVisible = false" @confirm="executeExitPos" />

  </div>

  <!-- 历史报价弹窗 -->
  <div v-if="quoteHistoryModalVisible" @click.self="quoteHistoryModalVisible = false" class="fixed inset-0 bg-slate-900/40 backdrop-blur-md flex items-center justify-center z-50 p-6 cursor-pointer">
    <div class="bg-white/95 backdrop-blur-2xl rounded-3xl shadow-2xl max-w-5xl w-full h-[88vh] max-h-[900px] overflow-hidden border border-white/80 flex flex-col cursor-default">
      
      <!-- 头部 -->
      <div class="p-5 border-b border-slate-200/60 flex items-center justify-between bg-white/50 shrink-0">
        <h3 class="font-extrabold text-base text-slate-900 flex items-center gap-2">
          <span>{{ tExt.historyTitle }}</span>
        </h3>
        <button @click="quoteHistoryModalVisible = false" class="text-slate-400 hover:text-slate-700 text-base font-bold p-1 cursor-pointer">✕</button>
      </div>

      <!-- 工具栏 (搜索与日期) -->
      <div class="p-4 border-b border-slate-200/60 bg-white/40 shrink-0 flex flex-wrap gap-4 items-center">
        <div class="relative flex-1 min-w-[200px]">
          <Search class="absolute left-3.5 top-3 text-slate-400" :size="16" />
          <input v-model="historySearchQuery" type="text" :placeholder="isZh ? '搜索单号/客户...' : isEs ? 'Buscar Nro. / Cliente...' : 'Search Quote / Client...'" class="w-full bg-white border border-slate-200 rounded-xl pl-10 pr-4 py-2.5 text-xs outline-none focus:border-accent font-bold text-slate-900 transition-colors" />
        </div>
        
        <div class="flex items-center gap-2 flex-wrap">
          <div class="flex items-center gap-1 bg-white border border-slate-200 rounded-xl px-2 py-1 focus-within:border-accent transition-colors">
            <input type="date" :lang="currentLang" v-model="historyStartDate" class="bg-transparent border-none text-xs outline-none font-mono font-bold text-slate-700 cursor-pointer" />
            <span class="text-slate-400 text-xs font-bold px-1">~</span>
            <input type="date" :lang="currentLang" v-model="historyEndDate" class="bg-transparent border-none text-xs outline-none font-mono font-bold text-slate-700 cursor-pointer" />
          </div>
          <button @click="setHistoryDateToday" class="px-3 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-xl text-xs font-bold transition-colors cursor-pointer">{{ isZh ? '今日' : isEs ? 'Hoy' : 'Today' }}</button>
          <button @click="setHistoryDateAll" class="px-3 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-xl text-xs font-bold transition-colors cursor-pointer">{{ isZh ? '全部历史' : isEs ? 'Todo el Historial' : 'All History' }}</button>
        </div>
      </div>

      <!-- 状态 Tabs -->
      <div class="px-5 py-3 border-b border-slate-200/60 bg-white/30 flex items-center gap-2 shrink-0">
        <button 
          @click="historyStatusFilter = 'ALL'" 
          :class="['px-4 py-1.5 rounded-lg text-xs font-bold transition-all', historyStatusFilter === 'ALL' ? 'bg-slate-800 text-white shadow-sm' : 'text-slate-600 hover:bg-slate-100']"
        >{{ isZh ? '全部' : isEs ? 'Todo' : 'All' }}</button>
        <button 
          @click="historyStatusFilter = 'PENDING'" 
          :class="['px-4 py-1.5 rounded-lg text-xs font-bold transition-all', historyStatusFilter === 'PENDING' ? 'bg-amber-500 text-white shadow-sm' : 'text-slate-600 hover:bg-slate-100']"
        >{{ isZh ? '待结算' : isEs ? 'Pendiente' : 'Pending' }}</button>
        <button 
          @click="historyStatusFilter = 'CONVERTED'" 
          :class="['px-4 py-1.5 rounded-lg text-xs font-bold transition-all', historyStatusFilter === 'CONVERTED' ? 'bg-indigo-600 text-white shadow-sm' : 'text-slate-600 hover:bg-slate-100']"
        >{{ isZh ? '已转单' : isEs ? 'Convertido' : 'Converted' }}</button>
      </div>

      <!-- 列表区 -->
      <div class="flex-1 overflow-y-auto p-5 bg-white/20 space-y-3 custom-scrollbar">
        <div v-if="isLoadingHistory" class="text-center py-8 text-slate-400 text-sm font-bold">
          {{ tExt.historyLoading }}
        </div>
        
        <div v-else-if="filteredHistoryList.length === 0" class="text-center py-8 text-slate-400 text-sm font-bold">
          {{ tExt.historyEmpty }}
        </div>
        
        <template v-else>
          <div 
            v-for="q in filteredHistoryList" 
            :key="q.id" 
            :class="[
              'p-4 rounded-2xl border transition-all flex flex-wrap items-center justify-between gap-4 shadow-2xs',
              q.converted_order_id ? 'bg-slate-50/50 border-slate-200 opacity-60' : 'bg-white/90 border-slate-200/80 hover:bg-white'
            ]"
          >
            <!-- 左侧信息 -->
            <div class="space-y-1">
              <div class="font-black text-sm text-slate-900 flex items-center gap-2 flex-wrap">
                <span :class="['font-mono', q.converted_order_id ? 'text-slate-400 line-through' : 'text-accent']">{{ q.quotation_no || q.id }}</span>
                <span v-if="q.converted_order_id" class="px-2 py-0.5 bg-indigo-100 text-indigo-700 text-[10px] font-black rounded border border-indigo-200">{{ isZh ? '【已转单】' : isEs ? '【Convertido】' : '【Converted】' }}</span>
                <span>👤 {{ q.client_name || 'Cliente General' }}</span>
              </div>
              <div class="text-xs text-slate-500 font-mono flex items-center gap-3">
                <span>{{ (q.timestamp || q.created_at || '').replace('T', ' ').substring(0, 16) }}</span>
                <span class="text-slate-400">|</span>
                <span class="truncate max-w-[300px]">📦 {{ parseQuoteItems(q.items_json) }}</span>
              </div>
            </div>
            
            <!-- 右侧金额与操作 -->
            <div class="flex items-center gap-6">
              <div class="text-right">
                <div :class="['text-sm font-black font-mono', q.converted_order_id ? 'text-slate-400 line-through' : 'text-emerald-600']">$ {{ Number(q.total_usd || 0).toFixed(2) }}</div>
              </div>
              <div class="flex items-center gap-2">
                <button @click="loadHistoricalQuote(q)" class="px-3 py-1.5 border border-slate-300 text-slate-700 rounded-md text-xs font-bold hover:bg-slate-50 transition-colors cursor-pointer">{{ isZh ? '载入修改' : isEs ? 'Cargar' : 'Load' }}</button>
                <button @click="downloadQuotePdf(q.quotation_no)" class="px-3 py-1.5 border border-slate-300 text-slate-700 rounded-md text-xs font-bold hover:bg-slate-50 transition-colors cursor-pointer">PDF</button>
                <button v-if="!q.converted_order_id" @click="emit('convert-to-pos', { id: q.id, client_id: q.client_id, client_name: q.client_name, items: JSON.parse(q.items_json) }); quoteHistoryModalVisible = false" class="px-3 py-1.5 border border-rose-600 text-rose-600 rounded-md text-xs font-bold hover:bg-rose-50 transition-colors cursor-pointer">{{ isZh ? '转收银台' : isEs ? 'A Caja POS' : 'To POS' }}</button>
                <span v-else class="px-3 py-1.5 text-xs font-bold text-slate-400 bg-slate-100 border border-slate-200 rounded-md">{{ isZh ? '已转单' : isEs ? 'Convertido' : 'Converted' }}</span>
              </div>
            </div>
          </div>
        </template>
      </div>
      
      <!-- 底部 -->
      <div class="p-5 border-t border-slate-200/60 bg-white/80 flex items-center justify-between shrink-0">
        <span class="text-xs text-slate-500 font-bold">{{ isZh ? '共找到' : isEs ? 'Encontrados' : 'Found' }} <strong class="text-slate-900">{{ filteredHistoryList.length }}</strong> {{ isZh ? '笔报价单' : isEs ? 'cotizaciones' : 'quotations' }}</span>
        <button @click="quoteHistoryModalVisible = false" class="px-6 py-2 bg-slate-200 hover:bg-slate-300 text-slate-700 rounded-xl text-xs font-bold transition-colors cursor-pointer">
          {{ isZh ? '关闭' : isEs ? 'Cerrar' : 'Close' }}
        </button>
      </div>
    </div>
  </div>
</template> 

<script setup>
import BaseModal from './ui/BaseModal.vue'
import { Keyboard, ShoppingCart, Search, RefreshCw, AlertTriangle, Building2, XCircle, FileText, CheckCircle2, Calendar, User, Download, Printer, Info, History, ChevronDown } from 'lucide-vue-next';

import { usePrintAgent, PRINT_ENABLED } from '../composables/usePrintAgent'
const { isConnected, printReceipt } = usePrintAgent()

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
    quoteInfoTitle: isZh ? '报价单信息' : isEs ? 'Información de Cotización' : 'Quotation Info',
    quoteNotesLabel: isZh ? '销售备注' : isEs ? 'Notas de Venta' : 'Sales Notes',
    quoteNotesPlaceholder: isZh ? '填写客户要求、保修说明、交货期等...' : isEs ? 'Requisitos del cliente, garantía, entrega...' : 'Client requirements, warranty, delivery...',
    quoteTipTitle: isZh ? '温馨提示:' : isEs ? 'Nota:' : 'Tip:',
    quoteTipText: isZh ? '生成报价单不会扣减库存。' : isEs ? 'Generar cotización no descuenta inventario.' : 'Quotation does not deduct inventory.',
    genQuoteSuccess: isZh ? '报价单已保存并生成' : isEs ? 'Cotización guardada' : 'Quotation saved',
    genQuoteFail: isZh ? '生成报价单失败' : isEs ? 'Error al generar cotización' : 'Failed to generate quotation',
    
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
    
    clientModalTitle: isZh ? '快捷选择客户' : isEs ? 'Selección Rápida de Cliente' : 'Quick Client Select',
    clientModalSearch: isZh ? '输入客户名称或电话搜索...' : isEs ? 'Buscar por nombre o teléfono...' : 'Search by name or phone...',
    clientSelectBtn: isZh ? '选择此客户' : isEs ? 'Seleccionar' : 'Select',
    clientNotFound: isZh ? '未找到客户' : isEs ? 'Cliente no encontrado' : 'Client not found',
    createThisClient: isZh ? '一键新建客户' : isEs ? 'Crear nuevo cliente' : 'Create new client',
    createClientTitle: isZh ? '快速新建客户档案' : isEs ? 'Creación Rápida de Cliente' : 'Quick Create Client',
    clientTypeRegular: isZh ? 'Regular (零售)' : isEs ? 'Regular (Minorista)' : 'Regular (Retail)',
    clientTypeTaller: isZh ? 'Taller (修理厂)' : isEs ? 'Taller (Mecánico)' : 'Workshop',
    clientTypeMayorista: isZh ? 'Mayorista (批发商)' : isEs ? 'Mayorista (Distribuidor)' : 'Wholesaler',
    isSpecialTaxpayer: isZh ? '标记为特殊纳税人 (需代扣 IVA)' : isEs ? 'Contribuyente Especial (Retención IVA)' : 'Special Taxpayer (VAT withholding)',
    
    exitTitle: isZh ? '确认退出报价界面？' : isEs ? '¿Salir de Cotización?' : 'Exit Quotation?',
    exitMsg: isZh ? '当前购物车若有商品，是否继续？' : isEs ? '¿Seguro? El carrito actual se perderá.' : 'Cart will be cleared. Continue?',
    toastStockError: isZh ? '库存不足' : isEs ? 'Stock insuficiente' : 'Insufficient stock',
    toastCheckoutSuccess: isZh ? '操作成功！' : isEs ? '¡Éxito!' : 'Success!',
    toastClientCreated: isZh ? '客户创建成功并已选中！' : isEs ? '¡Cliente creado y seleccionado!' : 'Client created and selected!',
    errorRequired: isZh ? '请输入客户名称' : isEs ? 'Ingrese el nombre del cliente' : 'Enter client name',

    guardarBtn: isZh ? '保存' : isEs ? 'Guardar' : 'Save',
    historyTitle: isZh ? '历史报价记录' : isEs ? 'Historial de Cotizaciones' : 'Quotation History',
    historyLoading: isZh ? '正在加载历史记录...' : isEs ? 'Cargando historial...' : 'Loading history...',
    historyEmpty: isZh ? '暂无历史报价记录' : isEs ? 'Sin cotizaciones registradas' : 'No quotations found',
    historyLoad: isZh ? '载入修改' : isEs ? 'Cargar' : 'Load',
    printBtn: isZh ? '打印' : isEs ? 'Imprimir' : 'Print',
    goToPosBtn: isZh ? '收银台' : isEs ? 'Ir a Caja POS' : 'POS Checkout',
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

const emit = defineEmits(['add-to-cart', 'generate-quote', 'exit-pos', 'clear-cart', 'refresh-clients', 'go-to-pos', 'convert-to-pos', 'show-toast'])

const deskSearchQuery = ref('')
const quoteClientName = ref('')
const quoteNotes = ref('')
const quoteClientId = ref(null)
const searchInputRef = ref(null)
const selectedIndex = ref(0)
const selectedCartIndex = ref(0)
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
const quoteHistoryModalVisible = ref(false)
const quoteHistoryList = ref([])
const historySearchQuery = ref('')
const todayStr = new Date().toLocaleDateString('en-CA')
const historyStartDate = ref(todayStr)
const historyEndDate = ref(todayStr)
const historyStatusFilter = ref('ALL')

const setHistoryDateToday = () => {
  historyStartDate.value = todayStr
  historyEndDate.value = todayStr
}
const setHistoryDateAll = () => {
  historyStartDate.value = ''
  historyEndDate.value = ''
}

const filteredHistoryList = computed(() => {
  let result = quoteHistoryList.value || []
  
  if (historySearchQuery.value) {
    const q = historySearchQuery.value.toUpperCase()
    result = result.filter(item => 
      (item.quotation_no && item.quotation_no.toUpperCase().includes(q)) || 
      (item.client_name && item.client_name.toUpperCase().includes(q))
    )
  }
  
  if (historyStartDate.value) {
    result = result.filter(item => (item.timestamp || item.created_at || '').slice(0, 10) >= historyStartDate.value)
  }
  if (historyEndDate.value) {
    result = result.filter(item => (item.timestamp || item.created_at || '').slice(0, 10) <= historyEndDate.value)
  }

  if (historyStatusFilter.value === 'PENDING') {
    result = result.filter(item => !item.converted_order_id)
  } else if (historyStatusFilter.value === 'CONVERTED') {
    result = result.filter(item => item.converted_order_id)
  }

  return result
})
const isLoadingHistory = ref(false)

const openQuoteHistoryModal = async () => {
  isLoadingHistory.value = true
  quoteHistoryModalVisible.value = true
  try {
    const res = await apiFetch('/api/quotations')
    if (res.ok) {
      const data = await res.json()
      quoteHistoryList.value = data.sort((a, b) => (b.timestamp || '').localeCompare(a.timestamp || ''))
    }
  } catch (e) {
    showToast('网络异常', 'error')
  } finally {
    isLoadingHistory.value = false
  }
}

const loadHistoricalQuote = (quote) => {
  try {
    const items = JSON.parse(quote.items_json || '[]')
    props.cartItems.splice(0, props.cartItems.length, ...items.map(i => ({
      ...i,
      cost_price: i.cost_price || 0,
      tax_rate: i.tax_rate ?? 0.16
    })))
    
    quoteClientName.value = quote.client_name || ''
    const matchedClient = props.clientsList?.find(c => c.name === quote.client_name)
    quoteClientId.value = matchedClient ? matchedClient.id : null
    
    if (quote.notes) quoteNotes.value = quote.notes

    quoteHistoryModalVisible.value = false
    showToast('✅ 历史报价已载入', 'success')
  } catch (e) {
    showToast('❌ 解析历史报价失败', 'error')
  }
}

const parseQuoteItems = (jsonStr) => {
  try {
    const items = JSON.parse(jsonStr || '[]')
    if (!items.length) return '无明细'
    const names = items.slice(0, 3).map(i => `${i.name} x${i.quantity}`).join(', ')
    return items.length > 3 ? `${names} 等 ${items.length} 件商品` : names
  } catch (e) {
    return '解析失败'
  }
}

const downloadQuotePdf = async (quotationNo) => {
  if (!quotationNo) return
  try {
    const res = await apiFetch(`/api/quotation/pdf/download?quotation_no=${quotationNo}&lang=${currentLang.value}`)
    if (!res.ok) throw new Error('PDF download failed')
    
    const blob = await res.blob()
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `Quotation_${quotationNo}.pdf`
    document.body.appendChild(a)
    a.click()
    a.remove()
    window.URL.revokeObjectURL(url)
    showToast(isZh.value ? 'PDF 下载成功' : 'PDF descargado', 'success')
  } catch (err) {
    showToast(isZh.value ? 'PDF 下载失败' : 'Error al descargar PDF', 'error')
  }
}

// 🌟 点击右上角按钮切回 POS 收银台
const goToPosFromQuote = () => {
  emit('go-to-pos')
}

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

const clientModalVisible = ref(false)
const clientFilterQuery = ref('')
const clientModalInputRef = ref(null)
const localClientsList = ref([])

const openClientSearchModal = async () => {
  clientFilterQuery.value = quoteClientName.value || ''
  try {
    const res = await apiFetch('/api/clients')
    if (res.ok) {
      localClientsList.value = await res.json()
    }
  } catch (e) {
    localClientsList.value = props.clientsList || []
  }

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

const clearClient = () => {
  quoteClientName.value = ''
  quoteClientId.value = null
}

const handleClientModalKeydown = (e) => {
  if (e.key === 'Enter') {
    const matched = filteredModalClients.value
    if (matched.length > 0) {
      selectClient(matched[0])
    } else if (clientFilterQuery.value.trim()) {
      prepareCreateClient(clientFilterQuery.value)
    }
  }
}

const filteredModalClients = computed(() => {
  const list = localClientsList.value.length > 0 ? localClientsList.value : props.clientsList
  if (!list) return []
  if (!clientFilterQuery.value.trim()) return list
  const q = clientFilterQuery.value.toUpperCase()
  return list.filter(c => 
    (c.name && c.name.toUpperCase().includes(q)) || 
    (c.phone && c.phone.toUpperCase().includes(q))
  )
})

const selectedClientDetails = computed(() => {
  if (!quoteClientId.value) return null
  const list = localClientsList.value.length > 0 ? localClientsList.value : props.clientsList
  return list?.find(c => c.id === quoteClientId.value) || null
})

const newClientModalVisible = ref(false)
const isSavingClient = ref(false)
const newClientForm = ref({
  name: '',
  rif_type: 'V',
  rif_number: '',
  phone: '',
  client_type: 'Regular',
  address: '',
  notes: '',
  is_special_taxpayer: false
})

const formatPhoneNumber = (e) => {
  let val = e.target.value.replace(/\D/g, '')
  if (val.length > 10) val = val.slice(0, 10)
  newClientForm.value.phone = val
}

const formatRifNumber = (e) => {
  let val = e.target.value.replace(/\D/g, '')
  if (val.length > 9) val = val.slice(0, 9)
  newClientForm.value.rif_number = val
}

const prepareCreateClient = (nameToCreate) => {
  newClientForm.value = { 
    name: nameToCreate || '', 
    rif_type: 'V',
    rif_number: '', 
    phone: '', 
    client_type: 'Regular', 
    address: '', 
    notes: '',
    is_special_taxpayer: false
  }
  clientModalVisible.value = false 
  newClientModalVisible.value = true 
}

const saveNewClient = async () => {
  if (!newClientForm.value.name.trim()) {
    showToast(tExt.value.errorRequired, 'error')
    return
  }
  const finalRif = newClientForm.value.rif_number ? `${newClientForm.value.rif_type}-${newClientForm.value.rif_number}` : ""
  const finalPhone = newClientForm.value.phone ? `+58${newClientForm.value.phone}` : ""
  
  const payload = {
    name: newClientForm.value.name,
    rif_or_cedula: finalRif,
    phone: finalPhone,
    client_type: newClientForm.value.client_type,
    address: newClientForm.value.address,
    notes: newClientForm.value.notes,
    is_special_taxpayer: newClientForm.value.is_special_taxpayer
  }

  isSavingClient.value = true
  try {
    const res = await apiFetch('/api/clients', {
      method: 'POST',
      body: JSON.stringify(payload)
    })
    if (res.ok) {
      const data = await res.json()
      newClientModalVisible.value = false
      quoteClientName.value = data.name
      quoteClientId.value = data.id ?? null
      clientFilterQuery.value = ''
      clientModalVisible.value = false
      showToast('' + tExt.value.toastClientCreated, 'success')
      emit('refresh-clients')
    }
  } catch (e) {
    showToast('' + t.common.error, 'error')
  } finally {
    isSavingClient.value = false
  }
}

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
      cost_price: part.cost_price || 0,
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
const confirmExitPos = () => { exitConfirmVisible.value = true }
const executeExitPos = () => { exitConfirmVisible.value = false; emit('exit-pos') }

const isSubmitting = ref(false)

const isOverCreditLimit = computed(() => {
  if (!quoteClientId.value || !props.clientsList) return false
  const client = props.clientsList.find(c => c.id === quoteClientId.value)
  if (!client) return false
  
  const currentDebt = Number(client.debt) || 0
  const limit = Number(client.credit_limit) || 500
  const projectedDebt = currentDebt + goodsTotalUsd.value
  
  return projectedDebt > limit
})

const printQuotationReceipt = async () => {
  if (!PRINT_ENABLED) return
  if (props.cartItems.length === 0) return
  if (!isConnected.value) {
    alert(isZh.value ? '打印服务离线' : 'Servicio offline.')
    return
  }
  
  isSubmitting.value = true
  try {
    await printReceipt({
      lang: currentLang.value === 'zh' ? 'zh' : currentLang.value === 'es' ? 'es' : 'en',
      companyName: systemConfig.value?.company_name || 'Tostiyk ERP',
      companyRif: systemConfig.value?.rif || '',
      companyAddress: systemConfig.value?.address || '',
      companyPhone: systemConfig.value?.phone || '',
      order_no: 'COT-' + new Date().getTime().toString().slice(-6),
      date: new Date().toLocaleString(),
      client_name: quoteClientName.value || 'Cliente General',
      operator: 'Admin',
      items: props.cartItems.map(i => ({ name: i.name, qty: i.quantity, price: i.price })),
      total_usd: goodsTotalUsd.value,
      total_bs: 0,
      payment: {}
    })
  } catch (err) {
    alert('打印失败')
  } finally {
    isSubmitting.value = false
  }
}

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
    showToast(tExt.value.genQuoteSuccess, 'success')
    
    emit('clear-cart')
    quoteClientName.value = ''
    quoteClientId.value = null
    quoteNotes.value = ''
  } catch (err) {
    showToast(err.message, 'error')
  } finally {
    isSubmitting.value = false
  }
}

const handleGlobalKeydown = (e) => {
  if (clientModalVisible.value || helpModalVisible.value || exitConfirmVisible.value || newClientModalVisible.value || quoteHistoryModalVisible.value) {
    if (e.key === 'Escape') {
      e.preventDefault()
      if (exitConfirmVisible.value) exitConfirmVisible.value = false
      else if (quoteHistoryModalVisible.value) quoteHistoryModalVisible.value = false
      else { clientModalVisible.value = false; helpModalVisible.value = false; newClientModalVisible.value = false; }
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
  if (e.key === 'F3' || (e.ctrlKey && e.key.toLowerCase() === 'f')) { e.preventDefault(); openClientSearchModal(); return }
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