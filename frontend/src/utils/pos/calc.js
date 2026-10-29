// src/utils/pos/calc.js
// POS 所有金额计算纯函数。保留原有的“分(cents)”计算以避免浮点误差。

/** 货品总价（含税，USD） */
export function goodsTotalUsd(items) {
  const totalCents = items.reduce((sum, item) => {
    return sum + Math.round(item.price * 100) * item.quantity
  }, 0)
  return totalCents / 100
}

/** 反推税前总价（USD） */
export function baseTotalUsd(items) {
  let totalCents = 0
  items.forEach(item => {
    const rate = item.tax_rate ?? 0.16
    const lineTotalCents = Math.round(item.price * 100) * item.quantity
    if (rate > 0) {
      totalCents += Math.round(lineTotalCents / (1.0 + rate))
    } else {
      totalCents += lineTotalCents
    }
  })
  return totalCents / 100
}

/** 税额（USD） */
export function taxTotalUsd(goodsTotal, baseTotal) {
  const diffCents = Math.round(goodsTotal * 100) - Math.round(baseTotal * 100)
  return diffCents / 100
}

/** 已付合计（USD） */
export function paidTotalUsd(split, rate) {
  const r = rate || 1
  const cCardCents = Math.round((Number(split.cardPos) || 0) / r * 100)
  const cPagoCents = Math.round((Number(split.pagoMovil) || 0) / r * 100)
  const cBsCents = Math.round((Number(split.cashBs) || 0) / r * 100)
  const cUsdCents = Math.round((Number(split.cashUsd) || 0) * 100)
  
  const paidCents = cCardCents + cPagoCents + cBsCents + cUsdCents
  return paidCents / 100
}

/** 余额（USD） */
export function balanceUsd(total, paid) {
  const balanceCents = Math.round(total * 100) - Math.round(paid * 100)
  return balanceCents / 100
}