// src/utils/pos/receipt.js
export function generateReceiptHtml(data) {
  const fmt = (v) => (Number(v) || 0).toFixed(2)
  
  const itemsHtml = (data.items || []).map(item => `
    <tr>
      <td style="padding: 4px 0; text-align: left;">${item.name || item.oem || '商品'}</td>
      <td style="padding: 4px 0; text-align: center;">${item.quantity}</td>
      <td style="padding: 4px 0; text-align: right;">$${fmt(item.price)}</td>
      <td style="padding: 4px 0; text-align: right;">$${fmt(item.price * item.quantity)}</td>
    </tr>
  `).join('')

  const payHtml = Object.entries(data.payment || {}).map(([key, val]) => {
    if (!val) return ''
    const labels = { cardPos: 'Punto de Venta', pagoMovil: 'Pago Movil', cashBs: 'Efectivo Bs', cashUsd: 'Efectivo USD', zelle: 'Zelle', usdt: 'USDT' }
    const isBs = ['cardPos', 'pagoMovil', 'cashBs'].includes(key)
    return `<div style="display: flex; justify-content: space-between;"><span> - ${labels[key] || key}</span> <span>${isBs ? 'Bs.' : '$'}${fmt(val)}</span></div>`
  }).join('')

  return `
    <html>
      <head>
        <style>
          body { font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; font-size: 12px; width: 80mm; margin: 0 auto; color: #000; }
          .text-center { text-align: center; }
          .font-bold { font-weight: bold; }
          table { width: 100%; border-collapse: collapse; margin: 10px 0; }
          th { border-bottom: 1px solid #000; padding-bottom: 4px; }
          .divider { border-top: 1px dashed #000; margin: 10px 0; }
          @media print { body { width: 100%; margin: 0; } }
        </style>
      </head>
      <body>
        <div class="text-center font-bold" style="font-size: 16px; margin-bottom: 4px;">TOSTIKYK ERP</div>
        <div class="text-center" style="margin-bottom: 10px;">RIF: J-12345678-9</div>
        <div class="divider"></div>
        
        <div style="display: flex; justify-content: space-between;">
          <span>Fecha:</span> <span>${new Date().toLocaleString()}</span>
        </div>
        <div style="display: flex; justify-content: space-between;">
          <span>Cliente:</span> <span>${data.client_name || 'Contado'}</span>
        </div>
        
        <div class="divider"></div>
        
        <table>
          <thead>
            <tr>
              <th style="text-align: left;">Desc</th>
              <th style="text-align: center;">Cant</th>
              <th style="text-align: right;">Precio</th>
              <th style="text-align: right;">Total</th>
            </tr>
          </thead>
          <tbody>
            ${itemsHtml}
          </tbody>
        </table>
        
        <div class="divider"></div>
        
        <div style="display: flex; justify-content: space-between;"><span>Subtotal:</span> <span>$${fmt(data.base_usd)}</span></div>
        <div style="display: flex; justify-content: space-between;"><span>IVA:</span> <span>$${fmt(data.tax_usd)}</span></div>
        <div style="display: flex; justify-content: space-between;" class="font-bold"><span>Total $:</span> <span>$${fmt(data.total_usd)}</span></div>
        <div style="display: flex; justify-content: space-between;"><span>Total Bs:</span> <span>Bs.${fmt(data.total_bs)}</span></div>
        <div style="display: flex; justify-content: space-between;"><span>Tasa:</span> <span>${fmt(data.exchange_rate)} Bs/$</span></div>
        
        <div class="divider"></div>
        
        ${payHtml}
        
        ${data.change > 0 ? `<div style="display: flex; justify-content: space-between;" class="font-bold"><span>Cambio:</span> <span>$${fmt(data.change)}</span></div>` : ''}
        
        <div class="divider"></div>
        
        <div class="text-center" style="margin-top: 20px;">
          ¡Gracias por su compra!<br>
          TOSTIYK ERP
        </div>
      </body>
    </html>
  `
}