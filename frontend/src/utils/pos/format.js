// src/utils/pos/format.js
export function fmtUsd(v) {
  return `$${(Number(v) || 0).toFixed(2)}`
}

export function fmtBs(v) {
  return `Bs. ${(Number(v) || 0).toFixed(2)}`
}

export function fmt2(v) {
  return (Number(v) || 0).toFixed(2)
}

export function fmtSigned(v) {
  const n = Number(v) || 0
  return `${n >= 0 ? '+' : ''}${n.toFixed(2)}`
}

/** 通用主货币格式化：输入的是 USD */
export function fmtPrimary(usdVal, rate, primary) {
  const n = Number(usdVal) || 0
  if (primary === 'USD') return `$${n.toFixed(2)}`
  return `Bs. ${(n * (Number(rate) || 1)).toFixed(2)}`
}

/** 支付通道-玻利瓦尔：输入的是 Bs */
export function fmtBsChannel(valBs, rate, primary) {
  const n = Number(valBs) || 0
  if (primary === 'USD') return `≈ $${(n / (Number(rate) || 1)).toFixed(2)}`
  return `Bs. ${n.toFixed(2)}`
}

/** 支付通道-美元：输入的是 USD */
export function fmtUsdChannel(valUsd, rate, primary) {
  const n = Number(valUsd) || 0
  if (primary === 'USD') return `≈ $${n.toFixed(2)}`
  return `≈ Bs. ${(n * (Number(rate) || 1)).toFixed(2)}`
}