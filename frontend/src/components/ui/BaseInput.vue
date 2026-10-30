<!-- src/components/ui/BaseInput.vue -->
<script setup>
import { computed, useAttrs, ref, watch } from 'vue'

defineOptions({ inheritAttrs: false })

const props = defineProps({
  modelValue: { type: [String, Number], default: '' },
  label:       { type: String, default: '' },
  error:       { type: String, default: '' },
  hint:        { type: String, default: '' },
  type:        { type: String, default: 'text' },
  size:        { type: String, default: 'md' },        // sm | md | lg
  disabled:    { type: Boolean, default: false },
  readonly:    { type: Boolean, default: false },
  prefixIcon:  { type: Boolean, default: false },      // true → 左侧留 40px 给图标
  allowCalc:   { type: Boolean, default: false },      // true → 支持四则运算
})
const emit = defineEmits(['update:modelValue', 'enter', 'blur', 'focus'])
const attrs = useAttrs()

const sizeClass = computed(
  () => ({ sm: 'text-xs', md: 'text-sm', lg: 'text-base' }[props.size] || 'text-sm')
)

const internalValue = ref(props.modelValue)
watch(() => props.modelValue, (val) => {
  if (String(val) !== String(internalValue.value)) {
    internalValue.value = val
  }
})

function onInput(e) {
  if (props.allowCalc) {
    internalValue.value = e.target.value
  } else {
    emit('update:modelValue', e.target.value)
  }
}

// 安全计算引擎（商业友好版）
function safeEval(expr) {
  if (typeof expr !== 'string') return null;
  
  let sanitized = expr
    .replace(/％/g, '%')
    .replace(/＋/g, '+')
    .replace(/－/g, '-')
    .replace(/＊/g, '*')
    .replace(/／/g, '/')
    .replace(/（/g, '(')
    .replace(/）/g, ')')
    .replace(/\s+/g, '');

  sanitized = sanitized.replace(/([\d\.]+)([\+\-])([\d\.]+)%/g, '($1*(1$2$3/100))');
  sanitized = sanitized.replace(/([\d\.]+)%/g, '($1/100)');

  if (!/^[\d+\-*/().]+$/.test(sanitized)) return null;
  
  try {
    const res = new Function('return (' + sanitized + ')')();
    if (typeof res === 'number' && isFinite(res)) {
      return String(Math.round(res * 10000) / 10000);
    }
  } catch (e) {
    return null;
  }
  return null;
}

function tryCalc(e) {
  if (!props.allowCalc) return false;
  const val = e.target.value;
  
  if (val && typeof val === 'string' && /[\+\-*\/\(\)%％]/.test(val)) {
    const calcResult = safeEval(val);
    if (calcResult !== null) {
      e.target.value = calcResult;
      internalValue.value = calcResult;
      emit('update:modelValue', props.type === 'number' ? Number(calcResult) : calcResult);
      return true; 
    }
  } else if (val && props.type === 'number') {
    emit('update:modelValue', Number(val));
  }
  return false;
}

function handleBlur(e) {
  tryCalc(e);
  emit('blur', e);
}

function handleEnter(e) {
  // 1. 先尝试计算
  const didCalculate = tryCalc(e);
  
  // 如果算出了结果，阻止默认行为，光标停在当前框，不跳转
  if (didCalculate) {
    e.preventDefault();
    e.stopPropagation();
    return;
  }

  // 2. 如果没在计算，拦截原生的表单提交行为，改用“跳转下一个框”逻辑
  e.preventDefault();
  e.stopPropagation();

  // 查找当前所在表单内的下一个可输入元素
  const form = e.target.closest('form');
  if (form) {
    const inputs = Array.from(form.querySelectorAll('input:not([type="hidden"]):not([disabled]):not([readonly]), select:not([disabled]), textarea:not([disabled])'));
    const idx = inputs.indexOf(e.target);
    
    if (idx > -1 && idx < inputs.length - 1) {
      // 跳转到下一个输入框
      inputs[idx + 1].focus();
      if (typeof inputs[idx + 1].select === 'function') {
        inputs[idx + 1].select();
      }
    } else {
      // 如果已经是最后一个框，触发自定义的 enter 事件（留给父级决定是否保存）
      emit('enter', e);
    }
  } else {
    // 不在 form 内（比如搜索框），直接抛出 enter 事件
    emit('enter', e);
  }
}
</script>

<template>
  <div class="flex flex-col gap-1.5 w-full">
    <label v-if="label" class="text-xs font-semibold text-secondary">{{ label }}</label>

    <div class="relative w-full">
      <div v-if="prefixIcon" class="absolute left-3 top-1/2 -translate-y-1/2 text-muted pointer-events-none z-10">
        <slot name="icon" />
      </div>

      <input
        :value="allowCalc ? internalValue : modelValue"
        :type="allowCalc ? 'text' : type"
        :inputmode="allowCalc ? 'decimal' : undefined"
        :disabled="disabled"
        :readonly="readonly"
        v-bind="attrs"
        :class="[
          'w-full transition-colors',
          sizeClass,
          prefixIcon ? '!pl-10' : '',
          error ? 'input-error' : '',
        ]"
        @input="onInput"
        @keydown.enter="handleEnter"
        @blur="handleBlur"
        @focus="$emit('focus', e)"
      />

      <div v-if="$slots.suffix" class="absolute right-3 top-1/2 -translate-y-1/2 text-muted z-10">
        <slot name="suffix" />
      </div>
    </div>

    <span v-if="error" class="text-xs text-danger">{{ error }}</span>
    <span v-else-if="hint" class="text-xs text-muted">{{ hint }}</span>
  </div>
</template>
