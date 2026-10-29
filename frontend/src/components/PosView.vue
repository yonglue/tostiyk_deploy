<!-- src/components/PosView.vue -->
<template>
  <div class="fixed inset-0 bg-slate-950/25 backdrop-blur-md z-40 flex flex-col overflow-hidden text-slate-900 dark:text-white font-sans transition-all">
    
    <!-- 🌟 正在出单的进度条遮罩层 -->
    <Teleport to="body">
      <div v-if="isProcessingCheckout" class="fixed inset-0 z-[999] bg-slate-900/60 backdrop-blur-sm flex items-center justify-center">
        <div class="bg-white dark:bg-slate-800 p-8 rounded-2xl shadow-2xl flex flex-col items-center gap-4 border border-slate-200 dark:border-slate-700 animate-in zoom-in-95 duration-200">
          <div class="w-12 h-12 border-4 border-emerald-500 border-t-transparent rounded-full animate-spin"></div>
          <div class="text-slate-900 dark:text-white font-black text-lg">正在打印发票...</div>
          <div class="w-56 h-2.5 bg-slate-100 dark:bg-slate-700 rounded-full overflow-hidden mt-2">
            <div class="h-full bg-emerald-500 rounded-full animate-progress"></div>
          </div>
        </div>
      </div>
    </Teleport>

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
        <span>{{ toastType === 'success' ? '' : '' }}</span>
        <span>{{ toastMessage }}</span>
      </div>
    </transition>

    <!-- 顶部状态栏 -->
    <PosHeader 
      :t="t" 
      :currentUser="currentUser" 
      :heldOrders="heldOrders" 
      :isConnected="isConnected" 
      :currentDateTime="currentDateTime" 
      :bcvRate="bcvRate"
      @open-recall="openRecallModal"
      @open-history="openHistoryModal"
      @open-shift="openShiftReportModal"
      @open-help="helpModalVisible = true"
      @confirm-exit="confirmExitPos"
    />

    <!-- 中间主工作区 -->
    <div class="flex-1 flex overflow-hidden p-2 gap-2 pb-12">
      
      <!-- 左侧：商品搜索与购物车 -->
      <div class="flex-1 flex flex-col bg-white dark:bg-slate-800/75 backdrop-blur-xl rounded-xl border border-white/60 overflow-hidden shadow-lg">
        
        <!-- 搜索框与客户框完美对齐 70/30 -->
        <div class="p-2.5 border-b border-slate-200 dark:border-slate-700/60 flex gap-3 bg-white dark:bg-slate-800/40 backdrop-blur-md items-stretch w-full">
          
          <!-- 1. 搜索框 (70%) -->
          <div class="flex-[7] relative flex items-center min-w-0">
            <div class="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none">
              <Search class="h-5 w-5 text-slate-400" />
            </div>
            <input
              data-testid="pos-search-input"  
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
            <!-- 状态 1：已选择客户 (极简卡片) -->
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

            <!-- 状态 2：未选择客户 -->
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

        <PosCartTable 
          :cartItems="cartItems" 
          :itemInputQuantities="itemInputQuantities" 
          :selectedCartIndex="selectedCartIndex" 
          :bcvRate="bcvRate" 
          :tExt="tExt"
          @select-item="index => selectedCartIndex = index"
          @update-qty="(i, q) => itemInputQuantities[i] = q"
          @apply-qty="applyMultiplierQuantity"
          @remove-item="index => cartItems.splice(index, 1)"
        />
      </div>

      <!-- 右侧面板容器：收银区 -->
      <PosPaymentPanel
        ref="paymentPanelRef"
        :isOverCreditLimit="isOverCreditLimit"
        :cartItems="cartItems"
        :bcvRate="bcvRate"
        :paymentSplit="paymentSplit"
        v-model:primaryCurrency="primaryCurrency"
        :paymentReference="paymentReference"
        @update:reference="v => paymentReference = v"
        :totalBaseUsd="totalBaseUsd"
        :totalTaxUsd="totalTaxUsd"
        :totalUsd="totalUsd"
        :totalPaidUsd="totalPaidUsd"
        :balanceRemaining="balanceRemaining"
        :isFullyPaid="isFullyPaid"
        :isSubmitting="isSubmitting"
        :isProcessingCheckout="isProcessingCheckout"
        :hasClient="!!quoteClientId" 
        :t="t"
        :tExt="tExt"
        @checkout="handleDirectCheckout"
        @checkout-fiado="handleFiadoCheckout"
        @focus-channel="focusPaymentChannel"
      />

    </div>

    <!-- 底部快捷键导航栏 -->
    <PosFooter 
      :t="t"
      @focus-search="focusSearch"
      @open-client="openClientSearchModal"
      @hold-order="holdCurrentOrder"
      @clear-cart="$emit('clear-cart')"
      @delete-last="deleteLastItem"
      @confirm-exit="confirmExitPos"
    />

    <!-- 销售历史弹窗 -->
    <PosHistoryModal :visible="historyModalVisible" :orders="completedOrders" @close="historyModalVisible = false" @preview="previewOrderTicket" @reprint="reprintOrderTicket" @return="processReturnOrder" />
    
    <!-- 挂单池 -->
    <PosRecallModal 
      v-model:visible="recallModalVisible" 
      :heldOrders="heldOrders" 
      :t="t" 
      :tExt="tExt"
      @recall="recallOrder"
      @delete="deleteHeldOrder"
    />

    <!-- 交接班 Modal -->
    <PosShiftReportModal 
      v-model:visible="shiftReportModalVisible"
      :shiftStats="shiftStats"
      :bcvRate="bcvRate"
      :t="t"
      :tExt="tExt"
      @submit="(payload) => submitShiftHandover(payload.actualCounts, payload.notes)"
    />

    <!-- 小票预览 Modal -->
    <div v-if="previewModalVisible" @click.self="previewModalVisible = false" class="fixed inset-0 bg-slate-950/40 backdrop-blur-md flex items-center justify-center z-50 p-6 cursor-pointer">
      <div class="bg-white dark:bg-slate-800/90 backdrop-blur-2xl rounded-3xl shadow-2xl max-w-4xl w-full h-[88vh] max-h-[900px] overflow-hidden border border-white/80 flex flex-col cursor-default">
        <div class="p-5 border-b border-slate-200 dark:border-slate-700/60 flex items-center justify-between bg-white dark:bg-slate-800/50 shrink-0">
          <h3 class="font-extrabold text-base text-slate-900 dark:text-white flex items-center gap-2"><span>{{ tExt.ticketTitle }}</span></h3>
          <button @click="previewModalVisible = false" class="text-slate-400 hover:text-slate-700 dark:text-slate-300 text-base font-bold p-1 cursor-pointer">✕</button>
        </div>
        <div id="receipt-preview-content" class="flex-1 overflow-y-auto p-4 sm:p-6 bg-slate-50 dark:bg-slate-900/50">
          <div class="w-[300px] mx-auto bg-white text-black font-mono text-[11px] leading-tight pb-6 pt-4 px-2 shadow-md border border-slate-200">
            <div class="text-center mb-2">
              <div class="text-[15px] font-black uppercase tracking-tight">{{ printData.company_name }}</div>
              <div class="text-[10px] mt-0.5">RIF: {{ printData.rif || 'J-00000000-0' }}</div>
              <div class="text-[10px]">{{ printData.address || 'Valencia, Carabobo' }}</div>
              <div class="text-[10px]">Tel: {{ printData.phone || 'N/A' }}</div>
            </div>
            
            <div class="border-t border-black border-dashed my-1"></div>
            
            <div class="flex flex-col space-y-0.5 text-[10px]">
              <div>Factura: {{ printData.order_no }}</div>
              <div>Fecha  : {{ printData.date }}</div>
              <div>Impreso: {{ printData.print_time }}</div>
              <div>Cliente: {{ printData.client_name }}</div>
              <div v-if="printData.client_rif">RIF    : {{ printData.client_rif }}</div>
              <div>Cajero : {{ printData.cashier }}</div>
            </div>
            
            <div class="border-t border-black border-dashed my-1"></div>
            
            <div class="space-y-1">
              <div v-for="(item, idx) in printData.items" :key="idx" class="flex flex-col">
                <div class="uppercase truncate">{{ item.name }}</div>
                <div class="flex justify-between">
                  <span class="pl-2">x{{ item.quantity }} @ {{ item.price.toFixed(2) }} <span v-if="item.oem">[{{ item.oem }}]</span></span>
                  <span class="font-bold">${{ (item.price * item.quantity).toFixed(2) }}</span>
                </div>
              </div>
            </div>
            
            <div class="border-t border-black border-dashed my-1"></div>
            
            <div class="flex flex-col space-y-0.5 text-[10px]">
              <div class="flex justify-between"><span>Subtotal:</span> <span>${{ printData.base_usd.toFixed(2) }}</span></div>
              <div class="flex justify-between"><span>IVA:</span> <span>${{ printData.tax_usd.toFixed(2) }}</span></div>
              <div class="flex justify-between font-bold"><span>Total $:</span> <span>${{ printData.total_usd.toFixed(2) }}</span></div>
              <div class="flex justify-between"><span>Total Bs:</span> <span>Bs.{{ printData.total_bs.toFixed(2) }}</span></div>
              <div class="flex justify-between"><span>Tasa:</span> <span>{{ printData.exchange_rate.toFixed(2) }} Bs/$</span></div>
            </div>
            
            <div class="border-t border-black border-dashed my-1"></div>
            
            <div class="flex flex-col space-y-0.5 text-[10px]">
              <div>Pagos:</div>
              <div v-if="printData.payment.cardPos > 0" class="flex justify-between"><span> - Punto de Venta</span> <span>Bs.{{ printData.payment.cardPos.toFixed(2) }}</span></div>
              <div v-if="printData.payment.pagoMovil > 0" class="flex justify-between"><span> - Pago Movil</span> <span>Bs.{{ printData.payment.pagoMovil.toFixed(2) }}</span></div>
              <div v-if="printData.payment.cashBs > 0" class="flex justify-between"><span> - Efectivo Bs</span> <span>Bs.{{ printData.payment.cashBs.toFixed(2) }}</span></div>
              <div v-if="printData.payment.cashUsd > 0" class="flex justify-between"><span> - Efectivo USD</span> <span>${{ printData.payment.cashUsd.toFixed(2) }}</span></div>
              <div v-if="printData.payment.zelle > 0" class="flex justify-between"><span> - Zelle</span> <span>${{ printData.payment.zelle.toFixed(2) }}</span></div>
              <div v-if="printData.payment.usdt > 0" class="flex justify-between"><span> - USDT</span> <span>${{ printData.payment.usdt.toFixed(2) }}</span></div>
              <div v-if="printData.change > 0" class="flex justify-between font-bold mt-1"><span>Cambio:</span> <span>${{ printData.change.toFixed(2) }}</span></div>
            </div>
            
            <div class="border-t border-black border-dashed my-1"></div>
            
            <div class="text-center text-[10px] space-y-0.5 mt-2">
              <div>¡Gracias por su compra!</div>
              <div>Cambios dentro de 7 dias con recibo</div>
              <div>Tel: {{ printData.phone || 'N/A' }}</div>
              <div class="font-bold">Tostiyk (TK) ERP</div>
            </div>
            
            <div class="mt-4 flex flex-col items-center">
              <div class="h-8 w-4/5 bg-[repeating-linear-gradient(90deg,#000,#000_2px,transparent_2px,transparent_4px)]"></div>
              <div class="text-[9px] mt-1">{{ printData.order_no }}</div>
            </div>
          </div>
        </div>
        
        <div class="p-5 bg-white dark:bg-slate-800/80 backdrop-blur-md border-t border-slate-200 dark:border-slate-700/60 flex gap-4 shrink-0">
          <button @click="previewModalVisible = false" :disabled="isSubmitting" class="flex-1 py-3 bg-slate-200/80 hover:bg-slate-300 text-slate-700 dark:text-slate-300 rounded-xl text-xs font-bold transition-all cursor-pointer">{{ t.pos.backToEdit }}</button>
          <button @click="confirmAndPrint" :disabled="isSubmitting" class="flex-1 py-3 bg-emerald-600 hover:bg-emerald-500 disabled:bg-slate-300 text-white rounded-xl text-sm font-black shadow-sm transition-all cursor-pointer">{{ isSubmitting ? tExt.ticketPrinting : t.pos.confirmAndPrint }}</button>
        </div>
      </div>
    </div>

    <PosHelpModal :visible="helpModalVisible" @close="helpModalVisible = false" />

    <!-- ✅ 客户快速搜索 Modal (完美复刻图1大尺寸 + 丰富细节) -->
    <div v-if="clientModalVisible" @click.self="clientModalVisible = false" class="fixed inset-0 bg-slate-950/40 backdrop-blur-md flex items-center justify-center z-[60] p-6 cursor-pointer">
      <div class="bg-white dark:bg-slate-800/90 backdrop-blur-2xl rounded-3xl shadow-2xl max-w-5xl w-full h-[88vh] max-h-[900px] overflow-hidden border border-white/80 flex flex-col cursor-default">
        
        <!-- 弹窗头部 -->
        <div class="p-5 border-b border-slate-200 dark:border-slate-700/60 flex items-center justify-between bg-white dark:bg-slate-800/50 shrink-0">
          <h3 class="font-extrabold text-base text-slate-900 dark:text-white flex items-center gap-2"><span>{{ tExt.clientModalTitle }}</span></h3>
          <button @click="clientModalVisible = false" class="text-slate-400 hover:text-slate-700 dark:text-slate-300 text-base font-bold p-1 cursor-pointer">✕</button>
        </div>

        <!-- 弹窗内容 -->
        <div class="flex-1 flex flex-col overflow-hidden bg-slate-50 dark:bg-slate-900/20 p-5">
          <div class="space-y-4 shrink-0">
            <!-- 搜索框 -->
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
            
            <!-- 已选客户提示与清除 -->
            <div v-if="quoteClientId" class="flex items-center justify-between text-sm px-1">
              <span class="text-slate-500 font-medium">已选: <strong class="text-slate-800 dark:text-slate-200">{{ quoteClientName }}</strong></span>
              <button @click="clearClient(); clientModalVisible = false" class="text-rose-500 hover:text-rose-600 font-bold flex items-center gap-1 transition-colors">
                <XCircle :size="16" />
                清除客户
              </button>
            </div>
          </div>

          <!-- 客户列表（改为三段式信息网格） -->
          <div class="flex-1 overflow-y-auto mt-4 space-y-3 pb-4">
            <div 
              v-for="c in filteredModalClients" 
              :key="c.id" 
              @click="selectClient(c)" 
              class="p-4 rounded-xl border border-slate-200 dark:border-slate-700/80 bg-white dark:bg-slate-800 cursor-pointer hover:border-accent hover:shadow-md transition-all flex items-center justify-between gap-6"
            >
              <!-- 左侧区：基本资料 -->
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

              <!-- 中间区：属性与地址 -->
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

              <!-- 右侧区：财务与操作 -->
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

        <!-- 弹窗底部 -->
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

    <ConfirmDialog :visible="exitConfirmVisible" icon="⚠️" :title="tExt.exitTitle" :message="tExt.exitMsg" @cancel="exitConfirmVisible = false" @confirm="executeExitPos" />

    <!-- 打印区域 -->
    <div v-if="printData" class="print-only hidden" id="print-section">
      <div class="font-mono text-xs w-[80mm] text-black mx-auto p-4 bg-white">
        <div class="text-center mb-2">
          <h2 class="text-base font-black">{{ systemConfig.company_name || 'TOSTIYK (TK)' }}</h2>
          <p class="text-[10px]">RIF: {{ systemConfig.rif || 'J-00000000-0' }}</p>
          <p class="text-[10px]">{{ systemConfig.address || 'Valencia, Carabobo' }}</p>
          <p class="text-[10px]">Tel: {{ systemConfig.phone || 'N/A' }}</p>
        </div>
        
        <div class="border-t border-dashed border-black my-1"></div>
        
        <div class="text-[10px] leading-tight">
          <p>{{ tExt.printOrderNo }} {{ printData.order_no }}</p>
          <p>{{ tExt.printDate }} {{ printData.date }}</p>
          <p>{{ tExt.printClient }} {{ printData.client_name }}</p>
          <p>{{ tExt.printOperator }} {{ printData.operator }}</p>
        </div>
        
        <div class="border-t border-dashed border-black my-1"></div>

        <div class="text-[10px]">
          <div v-for="(item, idx) in printData.items" :key="idx" class="mb-1">
            <div class="font-bold">{{ item.name }}</div>
            <div class="flex justify-between">
              <span>{{ item.oem }} x {{ item.quantity }} @ ${{ item.price.toFixed(2) }}</span>
              <span class="font-bold">${{ (item.price * item.quantity).toFixed(2) }}</span>
            </div>
          </div>
        </div>

        <div class="border-t border-dashed border-black my-1"></div>

        <div class="text-[10px] flex flex-col gap-0.5">
          <div class="flex justify-between"><span>Base Imponible:</span> <span>${{ printData.base_usd.toFixed(2) }}</span></div>
          <div class="flex justify-between"><span>IVA:</span> <span>${{ printData.tax_usd.toFixed(2) }}</span></div>
          <div class="flex justify-between font-black text-sm mt-1">
            <span>TOTAL USD:</span> <span>${{ printData.total_usd.toFixed(2) }}</span>
          </div>
          <div class="flex justify-between font-black text-sm">
            <span>TOTAL VES:</span> <span>Bs. {{ printData.total_bs.toFixed(2) }}</span>
          </div>
        </div>

        <div class="border-t border-dashed border-black my-1"></div>
        
        <div class="text-[10px]">
          <p class="font-bold">{{ tExt.printPaymentTitle }}</p>
          <div v-if="printData.payment.cardPos > 0" class="flex justify-between"><span>- Punto de Venta:</span> <span>Bs. {{ printData.payment.cardPos.toFixed(2) }}</span></div>
          <div v-if="printData.payment.pagoMovil > 0" class="flex justify-between"><span>- Pago Móvil:</span> <span>Bs. {{ printData.payment.pagoMovil.toFixed(2) }}</span></div>
          <div v-if="printData.payment.cashBs > 0" class="flex justify-between"><span>- Efectivo Bs:</span> <span>Bs. {{ printData.payment.cashBs.toFixed(2) }}</span></div>
          <div v-if="printData.payment.cashUsd > 0" class="flex justify-between"><span>- Efectivo USD:</span> <span>${{ printData.payment.cashUsd.toFixed(2) }}</span></div>
          <p v-if="printData.reference" class="mt-1">Ref: {{ printData.reference }}</p>
        </div>

        <div class="border-t border-dashed border-black my-2"></div>
        
        <div class="text-center text-[10px]">
          <p>{{ tExt.printThanks }}</p>
          <p class="font-bold">Tostiyk (TK) ERP</p>
        </div>
      </div>
    </div>

    <!-- 小票预览弹窗 (iframe) -->
    <Transition name="fade">
      <div v-if="receiptPreviewVisible" class="fixed inset-0 z-[100] bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4">
        <div class="bg-slate-100 rounded-2xl shadow-2xl w-full max-w-md flex flex-col overflow-hidden h-[85vh]">
          <div class="p-4 border-b border-slate-200 flex justify-between items-center bg-white shrink-0">
            <h3 class="font-bold text-slate-800 flex items-center gap-2"><span></span>{{ isZh ? '小票预览 (80mm)' : isEs ? 'Vista previa de recibo (80mm)' : 'Receipt Preview (80mm)' }}</h3>
            <button @click="receiptPreviewVisible = false" class="text-slate-400 hover:text-rose-500 text-2xl leading-none font-bold">&times;</button>
          </div>
          <div class="flex-1 overflow-y-auto p-6 flex justify-center bg-slate-200/50">
            <iframe 
              ref="previewIframe" 
              class="bg-white shadow-xl border border-slate-300 rounded-sm" 
              style="width: 320px; min-height: 100%; height: max-content;"
            ></iframe>
          </div>
          <div class="p-4 border-t border-slate-200 flex gap-3 bg-white shrink-0">
            <button @click="receiptPreviewVisible = false" class="flex-1 py-3 bg-slate-100 hover:bg-slate-200 rounded-xl font-bold text-slate-700 transition">{{ isZh ? '关闭' : isEs ? 'Cerrar' : 'Close' }}</button>
            <button @click="printFromPreview" class="flex-1 py-3 bg-accent hover:bg-accent-hover rounded-xl font-bold text-white shadow-sm transition flex items-center justify-center gap-2">
              <span></span>{{ isZh ? '打印' : isEs ? 'Imprimir' : 'Print' }}</button>
          </div>
        </div>
      </div>
    </Transition>

    <!-- 🌟 店长授权超额挂账弹窗 -->
    <div v-if="showPinModal" class="fixed inset-0 z-[999] bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4 animate-in fade-in duration-200">
      <div class="bg-white dark:bg-slate-800 rounded-3xl shadow-2xl w-full max-w-sm overflow-hidden animate-in zoom-in-95 duration-200 border border-slate-200/80 dark:border-slate-700">
        <div class="p-6">
          <div class="w-14 h-14 bg-rose-100 dark:bg-rose-900/30 text-rose-600 dark:text-rose-400 rounded-full flex items-center justify-center mx-auto mb-4 animate-bounce">
            <svg xmlns="http://www.w3.org/2000/svg" class="w-7 h-7" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          </div>
          <h3 class="text-xl font-black text-center text-slate-800 dark:text-white mb-2">
            {{ isZh ? '超出信用额度' : isEs ? 'Límite Excedido' : 'Credit Limit Exceeded' }}
          </h3>
          <p class="text-xs text-center text-slate-500 dark:text-slate-400 mb-6 leading-relaxed px-2">
            {{ pendingOverrideError }}
          </p>
          
          <div class="relative mb-6">
            <input 
              v-model="pinInput" 
              type="password" 
              :placeholder="isZh ? '请输入店长安全 PIN 码' : isEs ? 'Ingrese PIN de gerente' : 'Enter Manager PIN'"
              class="w-full bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl px-4 py-3.5 text-center tracking-[0.3em] font-mono text-lg text-slate-800 dark:text-white outline-none focus:border-accent  focus:ring-0 transition-all placeholder:tracking-normal placeholder:font-sans placeholder:text-sm placeholder:text-slate-400 dark:placeholder:text-slate-500"
              @keyup.enter="submitOverridePin"
            />
          </div>
          
          <div class="flex gap-3">
            <button @click="showPinModal = false" class="flex-1 py-3 rounded-xl font-bold text-slate-600 dark:text-slate-300 bg-slate-100 dark:bg-slate-700 hover:bg-slate-200 dark:hover:bg-slate-600 transition-colors cursor-pointer">
              {{ isZh ? '取消' : isEs ? 'Cancelar' : 'Cancel' }}
            </button>
            <button @click="submitOverridePin" class="flex-1 py-3 rounded-xl font-bold text-white bg-accent hover:bg-accent-hover shadow-sm transition-all active:scale-95 cursor-pointer">
              {{ isZh ? '授权放行' : isEs ? 'Autorizar' : 'Authorize' }}
            </button>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import PosHeader from './pos/PosHeader.vue'
import PosFooter from './pos/PosFooter.vue'
import PosPaymentPanel from './pos/PosPaymentPanel.vue'
import PosRecallModal from './pos/PosRecallModal.vue'
import PosShiftReportModal from './pos/PosShiftReportModal.vue'
import { generateReceiptHtml } from '../utils/pos/receipt'
import { goodsTotalUsd as calcGoodsTotal, baseTotalUsd as calcBaseTotal, taxTotalUsd as calcTaxTotal, paidTotalUsd as calcPaidTotal, balanceUsd as calcBalance } from '../utils/pos/calc'
import { fmtPrimary, fmtBsChannel, fmtUsdChannel } from '../utils/pos/format'
import { Package, Lock, CreditCard, Search, Banknote, Minus, Receipt, XCircle, Trash2, Printer, Plus, ShoppingCart, Zap, CheckCircle2, RefreshCw, DollarSign, Wallet, User, ChevronDown, Building2 } from 'lucide-vue-next';

const isZh = computed(() => currentLang.value === 'zh')
const isEs = computed(() => currentLang.value === 'es')

const paymentPanelRef = ref(null)

import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { apiFetch } from '../utils/api'
import { useI18n } from '../composables/useI18n'
import PosCartTable from './pos/PosCartTable.vue'
import { usePrintAgent, PRINT_ENABLED } from '../composables/usePrintAgent'
import ConfirmDialog from './ConfirmDialog.vue'
import BaseModal from './ui/BaseModal.vue'
import PosHelpModal from './pos/PosHelpModal.vue'
import PosHistoryModal from './pos/PosHistoryModal.vue'

const { t, currentLang } = useI18n()

const tExt = computed(() => {
  const isZh = currentLang.value === 'zh'
  const isEs = currentLang.value === 'es'
  return {
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
const quoteClientId = ref(null)
const quoteClientRif = ref('')
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

const primaryCurrency = ref('USD')
const toggleMainCurrency = () => {
  primaryCurrency.value = primaryCurrency.value === 'USD' ? 'BS' : 'USD'
}

const cardPosInputRef = ref(null)
const pagoMovilInputRef = ref(null)
const cashBsInputRef = ref(null)
const cashUsdInputRef = ref(null)
const referenceInputRef = ref(null)

const paymentSplit = ref({
  cardPos: 0,
  pagoMovil: 0,
  cashBs: 0,
  cashUsd: 0
})
// 引入的别名函数调用
const goodsTotalUsd = computed(() => calcGoodsTotal(props.cartItems))
const totalBaseUsd = computed(() => calcBaseTotal(props.cartItems))
const totalTaxUsd = computed(() => calcTaxTotal(goodsTotalUsd.value, totalBaseUsd.value))
const igtfAmountUsd = computed(() => 0)
const totalUsd = computed(() => {
  const totalCents = Math.round(goodsTotalUsd.value * 100) + Math.round(igtfAmountUsd.value * 100)
  return totalCents / 100
})
const totalPaidUsd = computed(() => calcPaidTotal(paymentSplit.value, props.bcvRate))
const balanceRemaining = computed(() => calcBalance(totalUsd.value, totalPaidUsd.value))
const isFullyPaid = computed(() => totalUsd.value > 0 && totalPaidUsd.value >= totalUsd.value)

// 🌟 实时计算 POS 客户是否超额
const isOverCreditLimit = computed(() => {
  if (!quoteClientId.value || !props.clientsList) return false
  const client = props.clientsList.find(c => c.id === quoteClientId.value)
  if (!client) return false
  
  const currentDebt = Number(client.debt) || 0
  const limit = Number(client.credit_limit) || 500
  const projectedDebt = currentDebt + totalUsd.value
  
  return projectedDebt > limit
})

const handlePaymentKeydown = (e, channelKey) => {
  const orderSequence = ['cardPos', 'pagoMovil', 'cashBs', 'cashUsd', 'reference']
  const currentIndex = orderSequence.indexOf(channelKey)

  if (e.ctrlKey && e.key === 'Enter') {
    e.preventDefault()
    e.stopPropagation()
    if (isFullyPaid.value && props.cartItems.length > 0 && !isSubmitting.value) {
      handleDirectCheckout()
    }
    return
  }

  if (e.key === 'ArrowUp') {
    e.preventDefault()
    if (currentIndex > 0) {
      const prevKey = orderSequence[currentIndex - 1]
      focusPaymentChannel(prevKey)
    }
    return
  }

  if (e.key === 'ArrowDown') {
    e.preventDefault()
    if (currentIndex !== -1 && currentIndex < orderSequence.length - 1) {
      const nextKey = orderSequence[currentIndex + 1]
      focusPaymentChannel(nextKey)
    }
    return
  }

  if (channelKey === 'reference') return

  if (e.key === ' ' || e.key === '=') {
    e.preventDefault()
    const rate = props.bcvRate || 1

    let otherPaidInUsd = 0
    for (const k in paymentSplit.value) {
      if (k !== channelKey) {
        const val = Number(paymentSplit.value[k]) || 0
        if (k === 'cashUsd') {
          otherPaidInUsd += val
        } else {
          otherPaidInUsd += val / rate
        }
      }
    }

    if (channelKey === 'cashUsd') {
      const goodsNeeded = Math.max(0, goodsTotalUsd.value - otherPaidInUsd)
      paymentSplit.value.cashUsd = Number(goodsNeeded.toFixed(2))
    } else {
      const neededUsd = Math.max(0, goodsTotalUsd.value - otherPaidInUsd)
      paymentSplit.value[channelKey] = Number((neededUsd * rate).toFixed(2))
    }
    return
  }

  if (e.key === 'Enter') {
    e.preventDefault()
    if (isFullyPaid.value && !isSubmitting.value) {
      handleDirectCheckout()
      return
    }
    if (currentIndex !== -1 && currentIndex < orderSequence.length - 1) {
      const nextKey = orderSequence[currentIndex + 1]
      focusPaymentChannel(nextKey)
    }
  }
}

const focusPaymentChannel = (channel) => {
  if (!paymentPanelRef.value) return
  const refs = {
    cardPos: paymentPanelRef.value.cardPosInputRef,
    pagoMovil: paymentPanelRef.value.pagoMovilInputRef,
    cashBs: paymentPanelRef.value.cashBsInputRef,
    cashUsd: paymentPanelRef.value.cashUsdInputRef
  }
  if (refs[channel] && refs[channel].value) {
    refs[channel].value.focus()
  }
}

watch(goodsTotalUsd, (newVal) => {
  const rate = props.bcvRate || 1
  if (newVal > 0) {
    paymentSplit.value = {
      cardPos: Number((newVal * rate).toFixed(2)),
      pagoMovil: 0,
      cashBs: 0,
      cashUsd: 0
    }
  } else {
    paymentSplit.value = { cardPos: 0, pagoMovil: 0, cashBs: 0, cashUsd: 0 }
  }
}, { immediate: true })

watch(() => props.cartItems.length, (newLen) => {
  if (newLen === 0) {
    selectedCartIndex.value = 0
  } else if (selectedCartIndex.value >= newLen) {
    selectedCartIndex.value = newLen - 1
  }
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

const heldOrders = ref([])
const recallModalVisible = ref(false)
const fetchHeldOrders = async () => {
  try {
    const res = await apiFetch('/api/held-orders')
    if (res.ok) heldOrders.value = await res.json()
  } catch (e) { console.error(e) }
}

const completedOrders = ref([])
const historyModalVisible = ref(false)
const shiftReportModalVisible = ref(false)
const shiftStats = ref({
  cardPos: { amount: 0, count: 0 },
  pagoMovil: { amount: 0, count: 0 },
  cashBs: { amount: 0, count: 0 },
  cashUsd: { amount: 0, count: 0 },
  baseUsd: 0,
  taxUsd: 0,
  igtfUsd: 0,
  totalUsd: 0,
  totalCount: 0
})

const actualCounts = ref({
  cardPos: 0,
  pagoMovil: 0,
  cashBs: 0,
  cashUsd: 0
})
const handoverNotes = ref('')

const cardPosDiff = computed(() => Number(((actualCounts.value.cardPos || 0) - (shiftStats.value.cardPos.amount * (props.bcvRate || 1))).toFixed(2)))
const pagoMovilDiff = computed(() => Number(((actualCounts.value.pagoMovil || 0) - (shiftStats.value.pagoMovil.amount * (props.bcvRate || 1))).toFixed(2)))
const cashBsDiff = computed(() => Number(((actualCounts.value.cashBs || 0) - (shiftStats.value.cashBs.amount * (props.bcvRate || 1))).toFixed(2)))
const cashUsdDiff = computed(() => Number(((actualCounts.value.cashUsd || 0) - shiftStats.value.cashUsd.amount).toFixed(2)))

const totalUsdDiff = computed(() => {
  const rate = props.bcvRate || 1
  const diffInUsd = (cardPosDiff.value / rate) + (pagoMovilDiff.value / rate) + (cashBsDiff.value / rate) + cashUsdDiff.value
  return Number(diffInUsd.toFixed(2))
})

const submitShiftHandover = async (actualCounts, handoverNotes) => {
  try {
    const rate = Number(props.bcvRate) || 0
    if (rate <= 0) {
      showToast('❌ ' + tExt.value.toastShiftError, 'error')
      return
    }
    const money = (n) => Number((Number(n) || 0).toFixed(2))
    const payload = {
      // ... 前面的 system 相关的不变 ...
      actual_card_pos_bs: money(actualCounts.cardPos),
      actual_pago_movil_bs: money(actualCounts.pagoMovil),
      actual_cash_bs: money(actualCounts.cashBs),
      actual_cash_usd: money(actualCounts.cashUsd),
      // ... 后面的零值保持不变 ...
      notes: handoverNotes || ''
    }
    const res = await apiFetch('/api/pos/shift-handover', { method: 'POST', body: JSON.stringify(payload) })
    if (!res.ok) throw new Error(tExt.value.toastShiftError)
    showToast('' + tExt.value.toastShiftSuccess, 'success')
    shiftReportModalVisible.value = false
  } catch (err) { showToast('' + err.message, 'error') }
}

const previewModalVisible = ref(false)
const pendingRequestId = ref(null)
const makeRequestId = () => {
  try {
    return crypto.randomUUID()
  } catch (e) {
    return `req-${Date.now()}-${Math.random().toString(16).slice(2)}`
  }
}
watch(previewModalVisible, (visible) => {
  if (!visible) pendingRequestId.value = null
})
const isPreviewReady = ref(false)
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

const clientModalVisible = ref(false)
const clientFilterQuery = ref('')
const clientModalInputRef = ref(null)

// 🌟 新增：本地变量，专门用于弹窗显示
const localClientsList = ref([])

const openClientSearchModal = async () => {
  clientFilterQuery.value = quoteClientName.value || ''
  
  // 🌟 强制向后端请求最新的客户数据，不再依赖父组件
  try {
    const res = await apiFetch('/api/clients')
    if (res.ok) {
      localClientsList.value = await res.json()
    }
  } catch (e) {
    console.error('拉取客户列表失败', e)
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
  quoteClientRif.value = client?.rif || ''
  clientModalVisible.value = false
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
  if (!localClientsList.value) return []
  if (!clientFilterQuery.value.trim()) return localClientsList.value
  const q = clientFilterQuery.value.toUpperCase()
  return localClientsList.value.filter(c => 
    (c.name && c.name.toUpperCase().includes(q)) || 
    (c.phone && c.phone.toUpperCase().includes(q))
  )
})

// 🌟 提取当前选中客户的详细信息（用于顶部展示）
const selectedClientDetails = computed(() => {
  if (!quoteClientId.value) return null
  const list = localClientsList.value.length > 0 ? localClientsList.value : props.clientsList
  return list?.find(c => c.id === quoteClientId.value) || null
})

// 🌟 清除当前选中的客户
const clearClient = () => {
  quoteClientName.value = ''
  quoteClientId.value = null
  quoteClientRif.value = ''
}

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
  if (newClientForm.value.rif_number && !/^\d{8,9}$/.test(newClientForm.value.rif_number)) {
    showToast('RIF格式错误', 'error')
    return
  }
  if (newClientForm.value.phone && newClientForm.value.phone.length !== 10) {
    showToast('电话格式错误', 'error')
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
      quoteClientRif.value = data.rif || ''
      clientFilterQuery.value = ''
      clientModalVisible.value = false
      showToast('' + tExt.value.toastClientCreated, 'success')
      emit('refresh-clients')
    } else {
      let errorMsg = 'Unknown Error'
      try {
        const err = await res.json()
        if (typeof err.detail === 'string') errorMsg = err.detail
        else if (Array.isArray(err.detail)) errorMsg = err.detail[0]?.msg || 'Validation Error'
      } catch (e) {}
      showToast(`${errorMsg}`, 'error')
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
      tax_rate: part.tax_rate ?? 0.16, // 🌟 确保正确读取商品档案中的税率（0.16, 0.08, 0）
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
    if (e.key === 'ArrowDown') {
      e.preventDefault()
      e.stopPropagation()
      selectedIndex.value = (selectedIndex.value + 1) % results.length
      return
    } else if (e.key === 'ArrowUp') {
      e.preventDefault()
      e.stopPropagation()
      selectedIndex.value = (selectedIndex.value - 1 + results.length) % results.length
      return
    } else if (e.key === 'Enter') {
      e.preventDefault()
      e.stopPropagation()
      selectAndAddToCart(results[selectedIndex.value] || results[0])
      return
    }
  }

  if (e.key === 'ArrowDown' && (!hasSearchQuery || results.length === 0) && props.cartItems.length > 0) {
    e.preventDefault()
    e.stopPropagation()
    if (searchInputRef.value) searchInputRef.value.blur()
    selectedCartIndex.value = 0
    return
  }

  if (e.key === 'Enter' && results.length > 0) {
    e.preventDefault()
    e.stopPropagation()
    selectAndAddToCart(results[0])
  }
}

const focusSearch = () => { if (searchInputRef.value) searchInputRef.value.focus() }
const deleteLastItem = () => { if (props.cartItems.length > 0) props.cartItems.pop() }

const holdCurrentOrder = async () => {
  if (props.cartItems.length === 0) {
    showToast('📌 ' + tExt.value.toastHoldEmpty, 'error')
    return
  }
  try {
    const res = await apiFetch('/api/held-orders', {
      method: 'POST',
      body: JSON.stringify({
        client_name: quoteClientName.value || 'Cliente General',
        payment_method: 'Pago_Mixto',
        items: props.cartItems,
        total_amount: totalUsd.value
      })
    })
    if (res.ok) {
      props.cartItems.splice(0, props.cartItems.length)
      quoteClientName.value = ''
      quoteClientId.value = null
      showToast('📌 ' + tExt.value.toastHoldSuccess, 'success')
      fetchHeldOrders()
    }
  } catch (e) { showToast('' + tExt.value.toastHoldEmpty, 'error') }
}

const openRecallModal = async () => {
  await fetchHeldOrders()
  if (heldOrders.value.length === 0) {
    showToast('' + tExt.value.recallEmpty, 'error')
    return
  }
  recallModalVisible.value = true
}

const recallOrder = (order) => {
  try {
    const parsedItems = JSON.parse(order.items_json)
    props.cartItems.splice(0, props.cartItems.length, ...parsedItems)
    const matchedClient = props.clientsList?.find(c => c.name === order.client_name)
    quoteClientName.value = order.client_name
    quoteClientId.value = matchedClient?.id ?? null
    apiFetch(`/api/held-orders/${order.id}`, { method: 'DELETE' }).then(() => fetchHeldOrders())
    recallModalVisible.value = false
    showToast('' + tExt.value.toastRecallSuccess, 'success')
  } catch (e) { showToast('' + tExt.value.toastRecallError, 'error') }
}

const deleteHeldOrder = async (id) => {
  await apiFetch(`/api/held-orders/${id}`, { method: 'DELETE' })
  fetchHeldOrders()
}

const fetchCompletedOrders = async () => {
  try {
    const res = await apiFetch('/api/pos/orders')
    if (!res.ok) return
    const ordersData = await res.json()
    completedOrders.value = ordersData

    const todayStr = new Date().toLocaleDateString('en-CA', { timeZone: 'America/Caracas' })

    let cardAmtCents = 0, pUsdCents = 0, cBsCents = 0, cUsdCents = 0, tUsdCents = 0
    let baseCents = 0, taxCents = 0, igtfCents = 0
    let todayOrderCount = 0

    ordersData.forEach(o => {
      if (o.status === 'REFUNDED') return
      if (o.time && o.time.startsWith(todayStr)) {
        const amtCents = Math.round(o.totalUsd * 100)
        tUsdCents += amtCents
        baseCents += Math.round((o.baseAmountUsd || 0) * 100)
        taxCents += Math.round((o.taxAmountUsd || 0) * 100)
        igtfCents += Math.round((o.igtfAmountUsd || 0) * 100)
        todayOrderCount++
        if (o.paymentMethod === 'Card_POS') cardAmtCents += amtCents
        else if (o.paymentMethod === 'Pago_Movil') pUsdCents += amtCents
        else if (o.paymentMethod === 'Cash_Bs') cBsCents += amtCents
        else if (o.paymentMethod === 'Cash_USD') cUsdCents += amtCents
      }
    })

    shiftStats.value = {
      cardPos: { amount: cardAmtCents / 100, count: 0 },
      pagoMovil: { amount: pUsdCents / 100, count: 0 },
      cashBs: { amount: cBsCents / 100, count: 0 },
      cashUsd: { amount: cUsdCents / 100, count: todayOrderCount },
      baseUsd: baseCents / 100,
      taxUsd: taxCents / 100,
      igtfUsd: igtfCents / 100,
      totalUsd: tUsdCents / 100,
      totalCount: todayOrderCount
    }

    actualCounts.value = {
      cardPos: Number(((cardAmtCents / 100) * (props.bcvRate || 1)).toFixed(2)),
      pagoMovil: Number(((pUsdCents / 100) * (props.bcvRate || 1)).toFixed(2)),
      cashBs: Number(((cBsCents / 100) * (props.bcvRate || 1)).toFixed(2)),
      cashUsd: cUsdCents / 100
    }
  } catch (e) { console.error(e) }
}

const openHistoryModal = async () => { await fetchCompletedOrders(); historyModalVisible.value = true }
const openShiftReportModal = async () => { await fetchCompletedOrders(); shiftReportModalVisible.value = true }
const processReturnOrder = async (dbId) => {
  try {
    const res = await apiFetch(`/api/pos/orders/${dbId}/refund`, { method: 'POST' })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      showToast('' + (err.detail || tExt.value.toastReturnError), 'error')
      return
    }
    showToast('' + tExt.value.toastReturnSuccess, 'success')
    fetchCompletedOrders()
  } catch (e) {
    showToast('' + tExt.value.toastReturnError, 'error')
  }
}

const confirmExitPos = () => { exitConfirmVisible.value = true }
const executeExitPos = () => { exitConfirmVisible.value = false; emit('exit-pos') }

const isFiadoMode = ref(false)

const handleFiadoCheckout = async () => {
  if (!quoteClientId.value) return
  if (props.cartItems.length === 0) return

  // 🌟 开启全屏进度条
  isProcessingCheckout.value = true
  isFiadoMode.value = true
  if (!pendingRequestId.value) pendingRequestId.value = makeRequestId()

  const delay = new Promise(resolve => setTimeout(resolve, 1400))

  try {
    await confirmAndPrint()
  } catch (error) {
    console.error("Fiado error:", error)
  } finally {
    await delay 
    isProcessingCheckout.value = false
    isFiadoMode.value = false
  }
}

const isSubmitting = ref(false)
const isProcessingCheckout = ref(false)
const { isConnected, printReceipt } = usePrintAgent()
const printData = ref(null)

const showPinModal = ref(false)
const pinInput = ref('')
const pendingOverrideError = ref('')
const pendingPinPayload = ref(null)

const submitOverridePin = async () => {
  if (!pinInput.value) return
  showPinModal.value = false
  await confirmAndPrint(pinInput.value)
}

const confirmAndPrint = async (overridePin = null) => {
  if (isSubmitting.value) return 
  isSubmitting.value = true

  try {
    let dominantMethod = 'Cash_USD'
    const split = paymentSplit.value
    if (isFiadoMode.value) {
      dominantMethod = 'Fiado_USD'
    } else {
      if ((split.cardPos || 0) > 0) dominantMethod = 'Card_POS'
      if ((split.pagoMovil || 0) > 0) dominantMethod = 'Pago_Movil'
      if ((split.cashBs || 0) > 0) dominantMethod = 'Cash_Bs'
      if ((split.cashUsd || 0) > 0) dominantMethod = 'Cash_USD'
      const activeChannelsCount = Object.values(split).filter(v => Number(v) > 0).length
      if (activeChannelsCount > 1) dominantMethod = 'Pago_Mixto'
    }

    const activeChannelsCount = Object.values(split).filter(v => Number(v) > 0).length
    if (activeChannelsCount > 1) {
      dominantMethod = 'Pago_Mixto'
    }

    const payload = {
      client_name: quoteClientName.value || "Cliente General",
      client_id: quoteClientId.value || null,
      request_id: pendingRequestId.value || makeRequestId(),
      payment_method: dominantMethod,
      payment_reference: paymentReference.value,
      bcv_rate: props.bcvRate,
      igtf_amount: igtfAmountUsd.value,
      items: props.cartItems.map(i => ({ 
        oem: i.oem, 
        name: i.name, 
        brand: i.brand || "GENERAL", 
        quantity: i.quantity, 
        price: i.price,
        tax_rate: i.tax_rate ?? 0.16 // 🌟 确保后端数据库记录订单明细时也能拿到正确税率
      }))
    }

    if (overridePin) {
      payload.force_override_pin = overridePin
    }

    const res = await apiFetch('/api/pos/orders', {
      method: 'POST',
      body: JSON.stringify(payload),
      offline: { queueOnFail: true },
    })
    
    // 🌟 4.4：离线入队（202）——网络断时订单已进 IndexedDB，UI 按"成功"处理
    if (res.status === 202) {
      const offlineData = await res.json()
      const offlineMsg = isZh.value
        ? '已离线入队，联网后自动同步'
        : isEs.value
          ? 'En cola offline, se sincronizará al reconectar'
          : 'Queued offline, will sync when online'
      
      props.cartItems.splice(0, props.cartItems.length)
      emit('clear-cart')
      paymentReference.value = ''
      quoteClientName.value = ''
      quoteClientId.value = null
      quoteClientRif.value = ''
      emit('generate-quote')
      checkoutSuccessVisible.value = true
      setTimeout(() => { checkoutSuccessVisible.value = false }, 1500)
      showToast(`📴 ${offlineMsg} ${offlineData.order_no || ''}`, 'success')
      // 不打印：离线订单无真实 order_no
      return
    }

    if (!res.ok) {
      const errorData = await res.json().catch(() => ({}))
      const errMsg = errorData.detail || tExt.value.toastCheckoutError
      
      isProcessingCheckout.value = false 
      isSubmitting.value = false 
      
      if (!overridePin && res.status === 400 && errMsg.includes('信用额度')) {
        pendingPinPayload.value = payload
        pendingOverrideError.value = errMsg
        pinInput.value = ''
        showPinModal.value = true
        return 
      }
      
      throw new Error(errMsg)
    }
    
    const data = await res.json()
    
    // 🌟 1. 先组装好打印数据
    printData.value = {
      company_name: systemConfig.value?.company_name || 'TOSTIYK (TK)',
      rif: systemConfig.value?.rif || '',
      address: systemConfig.value?.address || '',
      phone: systemConfig.value?.phone || '',
      order_no: data.order_no,
      date: new Date().toLocaleString(),
      print_time: new Date().toLocaleString(),
      client_name: quoteClientName.value || 'Cliente General',
      client_rif: quoteClientRif.value || '', 
      cashier: props.currentUser?.username || 'Admin',
      exchange_rate: props.bcvRate || 0,
      
      // 找零计算：(现金美元 + 刷卡玻利瓦尔/汇率 + 移动支付/汇率 + 现金玻利瓦尔/汇率) - 总应收美元
      change: Math.max(0, (
        (paymentSplit.value.cashUsd || 0) + 
        ((paymentSplit.value.cardPos || 0) / (props.bcvRate || 1)) + 
        ((paymentSplit.value.pagoMovil || 0) / (props.bcvRate || 1)) + 
        ((paymentSplit.value.cashBs || 0) / (props.bcvRate || 1)) + 
        (paymentSplit.value.zelle || 0) + 
        (paymentSplit.value.usdt || 0)
      ) - totalUsd.value),
      
      items: props.cartItems.map(item => ({
        name: item.name,
        oem: item.oem || '',
        quantity: item.quantity,
        price: item.price,
        tax_rate: item.tax_rate ?? 0.16 // 🌟 让 WebSocket 代理能够按商品独立识别 8%、16% 或 0%
      })),
      
      base_usd: totalBaseUsd.value,
      tax_usd: totalTaxUsd.value,
      total_usd: totalUsd.value,
      total_bs: totalUsd.value * (props.bcvRate || 0),
      payment: { ...paymentSplit.value },
      reference: paymentReference.value
    }

    // 🌟 2. 先关弹窗、反馈成功（不依赖打印）
    // 修复：之前 await 打印会因后端 /api/printer/receipt 阻塞而卡住订单完成流程
    // 生产收益：print-agent 挂掉时收银员仍能继续开单（只是没纸票）
    
    checkoutSuccessVisible.value = true
    setTimeout(() => { checkoutSuccessVisible.value = false }, 1500)

    showToast(`${tExt.value.toastCheckoutSuccess} ${data.order_no}`, 'success')

    //  立即清空购物车（双保险）：不依赖任何后续异步
    // 历史问题：清空放在最后，pendingQid 的 await / fetchCompletedOrders 挂住就清不掉
    props.cartItems.splice(0, props.cartItems.length)
    emit('clear-cart')
    paymentReference.value = ''
    quoteClientName.value = ''
    quoteClientId.value = null
    quoteClientRif.value = ''
    emit('generate-quote')

    // 后台任务（全部 fire-and-forget，失败不影响已完成的订单）
    autoPrintReceipt(printData.value).catch(err => {
      console.warn('打印失败（不影响订单完成）:', err)
    })

    const pendingQid = localStorage.getItem('pending_quotation_id')
    if (pendingQid && data.order_id) {
      apiFetch(`/api/quotations/${pendingQid}/mark-converted`, {
        method: 'POST',
        body: JSON.stringify({ order_id: data.order_id })
      }).catch(() => {}).finally(() => {
        localStorage.removeItem('pending_quotation_id')
      })
    }
    fetchCompletedOrders().catch(() => {})

  } catch (err) { 
    showToast(err.message || tExt.value.toastCheckoutError, 'error') 
  } finally {
    setTimeout(() => {
      isSubmitting.value = false
    }, 1000)
  }
}

const handleGlobalKeydown = (e) => {
  const isInput = ['INPUT', 'TEXTAREA', 'SELECT'].includes(document.activeElement.tagName)
  
  // 搜索聚焦: / 
  if (e.key === '/' && !isInput) {
    e.preventDefault()
    searchInputRef.value?.focus()
    return
  }

  // 👤 选客户: F3
  if (e.key === 'F3') {
    e.preventDefault()
    clientModalVisible.value = true
    setTimeout(() => { clientModalInputRef.value?.focus() }, 100)
    return
  }

  // 支付通道切换: F4 - F7
  if (e.key === 'F4') { e.preventDefault(); focusPaymentChannel('cardPos'); return; }
  if (e.key === 'F5') { e.preventDefault(); focusPaymentChannel('pagoMovil'); return; }
  if (e.key === 'F6') { e.preventDefault(); focusPaymentChannel('cashBs'); return; }
  if (e.key === 'F7') { e.preventDefault(); focusPaymentChannel('cashUsd'); return; }

  // 挂单: F8 
  if (e.key === 'F8') {
    e.preventDefault()
    if (typeof saveHeldOrder === 'function') saveHeldOrder()
    else if (typeof holdOrder === 'function') holdOrder()
    return
  }

  // 结账: F12 或 Ctrl+Enter
  if (e.key === 'F12' || (e.ctrlKey && e.key === 'Enter')) {
    e.preventDefault()
    if (isFullyPaid.value && props.cartItems.length > 0 && !isSubmitting.value && !isProcessingCheckout.value) {
      handleDirectCheckout()
    }
    return
  }

  // 删除: Delete 删末项，Alt+Delete 清空
  if (e.key === 'Delete') {
    if (e.altKey) {
      e.preventDefault()
      if (props.cartItems.length > 0) {
        props.cartItems.splice(0, props.cartItems.length)
        emit('clear-cart')
      }
    } else if (!isInput && props.cartItems.length > 0) {
      e.preventDefault()
      props.cartItems.pop()
    }
    return
  }
}

// F9 唤起打印机设置
const handleKeydown = (e) => {
  if (e.key === 'F9') {
    e.preventDefault()
  }
}
onMounted(() => {
  window.addEventListener('keydown', handleKeydown)
})
onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown)
})

onMounted(() => {
  window.addEventListener('keydown', handleGlobalKeydown)
  focusSearch()
  fetchCompletedOrders()
  fetchSystemSettings()
  fetchHeldOrders()
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleGlobalKeydown)
  if (toastTimer) clearTimeout(toastTimer)
})

// ================= 打印系统核心逻辑 =================
const receiptPreviewVisible = ref(false)
const previewIframe = ref(null)

const autoPrintReceipt = async (receiptData) => {
  if (!PRINT_ENABLED) return  // 🚫 打印功能已暂停，恢复时移除此行
  //  优先使用本地 WebSocket 代理打印
  if (isConnected.value) {
    printReceipt({
      lang: isZh.value ? 'zh' : isEs.value ? 'es' : 'en',
      companyName: receiptData.company_name || systemConfig.value?.company_name || 'Tostiyk ERP',
      companyRif: receiptData.rif || systemConfig.value?.rif || '',
      companyAddress: receiptData.address || systemConfig.value?.address || '',
      companyPhone: receiptData.phone || systemConfig.value?.phone || '',
      order_no: receiptData.order_no || '-',
      date: receiptData.date || new Date().toLocaleString(),
      client_name: receiptData.client_name || 'Contado',
      operator: receiptData.cashier || receiptData.operator || 'Admin',
      items: receiptData.items || [],
      
      // 🌟 关键补齐：让 WebSocket 代理拿到准确的税额和净额
      subtotal: receiptData.base_usd || receiptData.subtotal || 0,
      iva: receiptData.tax_usd || receiptData.iva || 0,

      total_usd: receiptData.total_usd || 0,
      total_bs: receiptData.total_bs || 0,
      payment: receiptData.payment || {}
    }).then(() => console.log('WebSocket 打印成功'))
      .catch(err => console.warn('WebSocket 打印失败:', err.message));
      
    return; 
  }

  try {
    await apiFetch('/api/printer/receipt', {
      method: 'POST',
      body: JSON.stringify({ data: receiptData })
    }).catch(() => {})
  } catch(e) {}

  const html = generateReceiptHtml(receiptData)
  const iframe = document.createElement('iframe')
  iframe.style.position = 'fixed'
  iframe.style.width = '0'
  iframe.style.height = '0'
  iframe.style.border = 'none'
  document.body.appendChild(iframe)
  
  const doc = iframe.contentWindow.document
  doc.open()
  doc.write(html)
  doc.close()
  
  setTimeout(() => {
    iframe.contentWindow.focus()
    iframe.contentWindow.print()
    setTimeout(() => {
      if (document.body.contains(iframe)) document.body.removeChild(iframe)
    }, 3000)
  }, 500)
}

const previewOrderTicket = (order) => {
  const receiptData = {
    company_name: systemConfig.value?.company_name || 'TOSTIYK (TK)',
    rif: systemConfig.value?.rif || '',
    address: systemConfig.value?.address || '',
    phone: systemConfig.value?.phone || '',
    order_no: order.orderId || order.order_no || 'REIMPRESION', 
    date: order.date || new Date().toLocaleString(),
    print_time: new Date().toLocaleString(),
    client_name: order.clientName || order.client_name || 'Cliente General',
    client_rif: order.client_rif || '',
    cashier: order.operator || 'Admin',
    exchange_rate: systemConfig.value?.bcv_rate || 0,
    items: order.items || [],
    base_usd: order.base_usd || order.baseAmountUsd || 0,
    tax_usd: order.tax_usd || order.taxAmountUsd || 0,
    total_usd: order.total || order.total_usd || order.totalAmountUsd || 0,
    total_bs: order.total_bs || order.totalAmountBs || 0,
    exchange_rate: order.exchange_rate || order.bcvRate || systemConfig.value?.bcv_rate || 0,
    payment: order.payment || order.paymentSplit || { cashUsd: order.total || 0 }
  }
  
  const html = generateReceiptHtml(receiptData)
  receiptPreviewVisible.value = true
  
  nextTick(() => {
    if (previewIframe.value) {
      const doc = previewIframe.value.contentWindow.document
      doc.open()
      doc.write(html)
      doc.close()
    }
  })
}

const printFromPreview = () => {
  if (previewIframe.value) {
    previewIframe.value.contentWindow.focus()
    previewIframe.value.contentWindow.print()
  }
}

const reprintOrderTicket = (order) => {
  showToast(`${tExt.value.toastReprint} #${order.orderId}`, 'success')
  
  const receiptData = {
    company_name: systemConfig.value?.company_name || 'TOSTIYK (TK)',
    rif: systemConfig.value?.rif || '',
    address: systemConfig.value?.address || '',
    phone: systemConfig.value?.phone || '',
    order_no: order.orderId || order.order_no || 'REIMPRESION', 
    date: order.date || new Date().toLocaleString(),
    print_time: new Date().toLocaleString(),
    client_name: order.clientName || order.client_name || 'Cliente General',
    client_rif: order.client_rif || '',
    cashier: order.operator || 'Admin',
    exchange_rate: systemConfig.value?.bcv_rate || 0,
    items: order.items || [],
    base_usd: order.base_usd || order.baseAmountUsd || 0,
    tax_usd: order.tax_usd || order.taxAmountUsd || 0,
    total_usd: order.total || order.total_usd || order.totalAmountUsd || 0,
    total_bs: order.total_bs || order.totalAmountBs || 0,
    exchange_rate: order.exchange_rate || order.bcvRate || systemConfig.value?.bcv_rate || 0,
    payment: order.payment || order.paymentSplit || { cashUsd: order.total || 0 }
  }
  
  autoPrintReceipt(receiptData)
}

</script>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity 0.2s ease, transform 0.2s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; transform: translateY(-10px); }

input.no-spinner::-webkit-outer-spin-button,
input.no-spinner::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}
input[type=number].no-spinner {
  -moz-appearance: textfield;
}

@keyframes popIn {
  0% { transform: scale(0.5); opacity: 0; }
  70% { transform: scale(1.1); opacity: 1; }
  100% { transform: scale(1); opacity: 1; }
}
.animate-pop-in {
  animation: popIn 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards;
}

@media print {
  body * {
    visibility: hidden;
  }
  #print-section, #print-section * {
    visibility: visible;
  }
  #print-section {
    position: absolute;
    left: 0;
    top: 0;
    width: 80mm;
    margin: 0;
    padding: 5px;
    font-family: 'Courier New', Courier, monospace;
    font-size: 12px;
    color: #000;
    background: #fff;
    line-height: 1.2;
  }

  @page {
    size: auto;
    margin: 0mm; 
  }

  .print-header, .print-footer {
    text-align: center;
  }
  .print-header h2 {
    font-size: 16px;
    margin: 0 0 4px 0;
  }
  .print-header p, .print-footer p {
    margin: 0;
    font-size: 10px;
  }
  
  .divider {
    text-align: center;
    margin: 4px 0;
    overflow: hidden;
    white-space: nowrap;
  }

  .print-meta p {
    margin: 2px 0;
    font-size: 11px;
  }

  .print-items table {
    width: 100%;
    border-collapse: collapse;
  }
  .print-items th, .print-items td {
    padding: 2px 0;
    font-size: 11px;
  }
  .print-items th {
    border-bottom: 1px dashed #000;
  }

  .print-totals p {
    display: flex;
    justify-content: space-between;
    margin: 2px 0;
    font-size: 11px;
  }
  .print-totals .bold {
    font-weight: bold;
    font-size: 13px;
  }

  .print-payments p {
    margin: 2px 0;
    font-size: 10px;
  }

  .print-footer {
    margin-top: 10px;
  }
}
</style>