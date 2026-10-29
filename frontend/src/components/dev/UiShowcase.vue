<!-- src/components/dev/UiShowcase.vue -->
<!-- dev-only 预览页：访问 http://localhost:5173/?dev=ui 查看 -->
<script setup>
import { ref } from 'vue'
import BaseInput from '../ui/BaseInput.vue'
import BaseSearchInput from '../ui/BaseSearchInput.vue'
import BaseSelect from '../ui/BaseSelect.vue'
import BaseModal from '../ui/BaseModal.vue'

/* —— 明暗切换（只改 html class，不引 useTheme，避免副作用） —— */
const isDark = ref(document.documentElement.classList.contains('dark'))
function toggleDark() {
  isDark.value = !isDark.value
  document.documentElement.classList.toggle('dark', isDark.value)
}

/* —— BaseInput state —— */
const txt = ref('')
const num = ref(0)
const errInput = ref('bad value')

/* —— BaseSearchInput state —— */
const search = ref('')
const lastSearch = ref('')

/* —— BaseSelect state —— */
const selCity = ref('BJ')
const selSearchable = ref(null)
const selDisabled = ref('A')
const cityOptions = [
  { label: '北京', value: 'BJ' },
  { label: '上海', value: 'SH' },
  { label: '广州', value: 'GZ' },
  { label: '深圳', value: 'SZ' },
]
const countryOptions = Array.from({ length: 15 }, (_, i) => ({
  label: `Country ${i + 1}`,
  value: `C${i + 1}`,
}))

/* —— BaseModal state —— */
const modalVisible = ref(false)
const modalSize = ref('md')
function openModal(size) {
  modalSize.value = size
  modalVisible.value = true
}
</script>

<template>
  <div class="min-h-screen bg-surface text-primary p-8 space-y-8">
    <!-- 头部 -->
    <header class="flex items-center justify-between border-b border-line pb-4">
      <div>
        <h1 class="text-2xl font-extrabold">UI Showcase (dev only)</h1>
        <p class="text-xs text-muted mt-1">
          访问 <code class="bg-surface-muted px-1 rounded">/?dev=ui</code> 查看。生产环境不打包。
        </p>
      </div>
      <button
        class="px-3 py-1.5 bg-accent text-white rounded-md text-sm font-bold cursor-pointer"
        @click="toggleDark"
      >
        {{ isDark ? '切到浅色' : '切到深色' }}
      </button>
    </header>

    <!-- ============ BaseInput ============ -->
    <section class="space-y-4">
      <h2 class="text-lg font-bold text-accent">BaseInput</h2>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <BaseInput v-model="txt" label="普通输入" placeholder="请输入..." />
        <BaseInput v-model="num" type="number" label="数字输入" placeholder="0" />
        <BaseInput
          v-model="errInput"
          label="错误态"
          error="此字段必填"
        />
        <BaseInput
          v-model="txt"
          label="带提示"
          hint="例：+58 412 1234567"
        />
        <BaseInput
          :model-value="'disabled'"
          label="禁用态"
          disabled
        />
        <BaseInput
          v-model="txt"
          label="带图标前缀"
          prefix-icon
          placeholder="搜索..."
        >
          <template #icon>
            <svg class="w-4 h-4" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.5">
              <circle cx="9" cy="9" r="6" />
              <path d="m14 14 3 3" stroke-linecap="round" />
            </svg>
          </template>
        </BaseInput>
      </div>
      <p class="text-xs text-muted font-mono">txt = {{ JSON.stringify(txt) }} / num = {{ num }}</p>
    </section>

    <!-- ============ BaseSearchInput ============ -->
    <section class="space-y-4">
      <h2 class="text-lg font-bold text-accent">BaseSearchInput</h2>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <BaseSearchInput v-model="search" placeholder="搜索商品..." @search="lastSearch = $event" />
        <BaseSearchInput v-model="search" placeholder="带 disabled" disabled />
      </div>
      <p class="text-xs text-muted font-mono">
        value = {{ JSON.stringify(search) }} / 最近一次触发 search = {{ JSON.stringify(lastSearch) }}
      </p>
    </section>

    <!-- ============ BaseSelect ============ -->
    <section class="space-y-4">
      <h2 class="text-lg font-bold text-accent">BaseSelect</h2>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div>
          <label class="text-xs font-semibold text-secondary block mb-1.5">普通下拉</label>
          <BaseSelect v-model="selCity" :options="cityOptions" placeholder="请选择城市" />
        </div>
        <div>
          <label class="text-xs font-semibold text-secondary block mb-1.5">可搜索 + 可清空</label>
          <BaseSelect
            v-model="selSearchable"
            :options="countryOptions"
            searchable
            clearable
            placeholder="搜索国家..."
          />
        </div>
        <div>
          <label class="text-xs font-semibold text-secondary block mb-1.5">禁用态</label>
          <BaseSelect v-model="selDisabled" :options="cityOptions" disabled />
        </div>
      </div>
      <p class="text-xs text-muted font-mono">
        city = {{ selCity }} / searchable = {{ selSearchable }} / disabled = {{ selDisabled }}
      </p>
    </section>

    <!-- ============ BaseModal ============ -->
    <section class="space-y-4">
      <h2 class="text-lg font-bold text-accent">BaseModal</h2>
      <div class="flex flex-wrap gap-2">
        <button class="px-3 py-1.5 bg-accent text-white rounded-md text-sm font-bold cursor-pointer" @click="openModal('sm')">打开 sm</button>
        <button class="px-3 py-1.5 bg-accent text-white rounded-md text-sm font-bold cursor-pointer" @click="openModal('md')">打开 md</button>
        <button class="px-3 py-1.5 bg-accent text-white rounded-md text-sm font-bold cursor-pointer" @click="openModal('lg')">打开 lg</button>
        <button class="px-3 py-1.5 bg-accent text-white rounded-md text-sm font-bold cursor-pointer" @click="openModal('xl')">打开 xl</button>
      </div>
    </section>

    <!-- 底部信息 -->
    <footer class="border-t border-line pt-4 text-xs text-muted">
      当前主题：<b>{{ isDark ? 'dark' : 'light' }}</b>。
      所有视觉由 style.css 全局 + token 类（bg-surface / text-primary / border-line / bg-accent）驱动。
    </footer>

    <!-- BaseModal 实例 -->
    <BaseModal v-model:visible="modalVisible" :title="`Modal size = ${modalSize}`" :size="modalSize">
      <div class="p-6 space-y-3">
        <p class="text-sm">这是 BaseModal 示例内容。size={{ modalSize }}。</p>
        <BaseInput v-model="txt" label="弹窗里的输入框" placeholder="验证嵌套" />
      </div>
      <template #footer>
        <div class="flex justify-end gap-2">
          <button
            class="px-4 py-2 bg-surface-muted text-primary rounded-md text-sm font-bold cursor-pointer"
            @click="modalVisible = false"
          >取消</button>
          <button
            class="px-4 py-2 bg-accent text-white rounded-md text-sm font-bold cursor-pointer"
            @click="modalVisible = false"
          >确定</button>
        </div>
      </template>
    </BaseModal>
  </div>
</template>