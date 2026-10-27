const { WebSocketServer } = require('ws');
const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');
const iconv = require('iconv-lite');

const PORT = 8899;
const PRINTER_NAME = "Printer_POS_80"; 

// ==========================================
// 🌟 标准 42 字符满宽居中网格系统
// ==========================================
const LINE_WIDTH = 42;
const LEFT_PAD = "  "; // 2个空格的左边距

const print_divider = (char = "-") => LEFT_PAD + char.repeat(LINE_WIDTH) + "\n";

// 修复变量声明问题的两端对齐函数
const print_row = (left_text, right_text) => {
    let r_str = String(right_text || '');
    let l_str = String(left_text || '');
    
    if (r_str.length >= LINE_WIDTH) {
        r_str = r_str.substring(0, LINE_WIDTH);
    }
    
    const max_left_len = LINE_WIDTH - r_str.length - 1;
    if (l_str.length > max_left_len) {
        l_str = l_str.substring(0, max_left_len);
    }
    
    const spaces_count = LINE_WIDTH - l_str.length - r_str.length;
    const spaces = " ".repeat(spaces_count > 0 ? spaces_count : 0);
    return `${LEFT_PAD}${l_str}${spaces}${r_str}\n`;
};

// 单行居中对齐函数
const center_text = (str) => {
    let s = String(str || '').trim();
    if (!s) return '\n';
    
    let result = '';
    while (s.length > 0) {
        let chunk = s.substring(0, LINE_WIDTH);
        s = s.substring(LINE_WIDTH);
        const left_pad = Math.floor((LINE_WIDTH - chunk.length) / 2);
        result += `${LEFT_PAD}${" ".repeat(left_pad > 0 ? left_pad : 0)}${chunk}\n`;
    }
    return result;
};

// 普通左对齐带边距
const left_line = (str) => `${LEFT_PAD}${str}\n`;

const wss = new WebSocketServer({ port: PORT });
console.log(`🚀 Tostiyk ERP 打印代理已启动 (42列完美修复版): ws://127.0.0.1:${PORT}`);

wss.on('connection', (ws) => {
  ws.on('message', (raw) => {
    let msg;
    try { msg = JSON.parse(raw); } catch { return; }

    if (msg.type === 'ping') return ws.send(JSON.stringify({ type: 'pong' }));

    if (msg.type === 'print' && msg.data) {
      const data = msg.data;
      
      try {
        let s = '';
        // ================= 1. 硬件初始化与防吞头预热（终极稳定版） =================
        s += '\x1B\x40';         // 初始化打印机
        s += '\x1B\x74\x02';     // CP850 编码
        s += '\x1B\x33\x30';     // 稍微加大行间距，防止文字黏连
        s += '\n\n\n';           // 强制预热走纸 3 行，让打印头彻底离开切刀物理盲区，无论长短绝不切头！
        s += '\x1B\x61\x00';     // 左对齐

        // ================= 2. 头部信息 (居中) =================
        s += center_text(data.companyName || 'MUNDO REPUESTOS C.A');
        s += center_text(`RIF: ${data.companyRif || 'J-307219955'}`);
        s += center_text(data.companyAddress || 'Valencia, Carabobo, Venezuela');
        s += center_text(`TEL: ${data.companyPhone || '+58 412-0000000'}`);
        s += print_divider("=");

        // ================= 3. 数据解析 =================
        let calcTotalUsd = 0;
        let totalItemsCount = 0;

        (data.items || []).forEach(item => {
          const qty = Number(item.quantity || item.qty || 1);
          const price = Number(item.price || item.price_usd || 0);
          const subtotal = Number(item.total || (qty * price));
          calcTotalUsd += subtotal;
          totalItemsCount += qty;
        });

        const totalUsd = Number(data.total_usd || data.totalUsd || calcTotalUsd || 0);
        
        let tasaVal = Number(data.tasa || data.bcv_rate || data.bcvRate || data.exchange_rate || 0);
        const totalBsInput = Number(data.total_bs || data.totalBs || 0);
        
        if (tasaVal === 0 && totalBsInput > 0 && totalUsd > 0) {
            tasaVal = totalBsInput / totalUsd;
        }
        if (tasaVal === 0) {
            tasaVal = 887.00;
        }
        
        const totalBs = totalBsInput > 0 ? totalBsInput : (totalUsd * tasaVal);

        // ================= 4. 单据基础信息 =================
        s += left_line(`Factura:  ${data.order_no || data.orderId || '-'}`);
        s += left_line(`Fecha:    ${data.date || data.time || '-'}`);
        s += left_line(`Cliente:  ${data.client_name || data.clientName || 'Cliente General'}`);
        
        const clientRif = data.client_rif || data.client_id || data.rif || data.ci || data.clientId || '-';
        s += left_line(`CI/RIF:   ${clientRif}`);
        
        s += left_line(`Cajero:   ${data.operator || 'Admin'}`);
        s += left_line(`Tasa Ref: Bs. ${tasaVal.toFixed(2)} / USD`);
        s += print_divider("-");

        // ================= 5. 商品明细 (42列宽度) =================
        (data.items || []).forEach(item => {
          const qty = Number(item.quantity || item.qty || 1);
          const price = Number(item.price || item.price_usd || 0);
          const subtotal = Number(item.total || (qty * price)).toFixed(2);
          
          let itemName = String(item.name || 'Producto').trim();
          
          let firstLineMax = LINE_WIDTH;
          let subLineMax = LINE_WIDTH - 2;

          if (itemName.length <= firstLineMax) {
              s += left_line(itemName);
          } else {
              s += left_line(itemName.substring(0, firstLineMax));
              itemName = itemName.substring(firstLineMax);
              
              while (itemName.length > 0) {
                  s += left_line("  " + itemName.substring(0, subLineMax));
                  itemName = itemName.substring(subLineMax);
              }
          }
          
          let left_info = `  ${qty} x $${price.toFixed(2)}`;
          let right_info = `$${subtotal}`;
          s += print_row(left_info, right_info);
        });

        s += print_divider("-");

        // 商品总件数统计
        s += print_row("CANT. PRODUCTOS:", `${totalItemsCount}`);
        s += print_divider("-");

        // ================= 6. 财务汇总 =================
        const exentoVal = Number(data.exento || 0);
        const ivaVal = Number(data.iva || data.taxAmountUsd || 0);
        s += print_row("EXENTO", `$${exentoVal.toFixed(2)}`);
        s += print_row("BI G16,00%", `$${totalUsd.toFixed(2)}`);
        s += print_row("IVA (16%)", `$${ivaVal.toFixed(2)}`);
        s += print_divider("-");
        
        // ================= 7. 总计金额 (加粗) =================
        s += '\x1B\x45\x01'; 
        s += print_row("TOTAL USD", `$${totalUsd.toFixed(2)}`);
        s += print_row("TOTAL BS", `Bs.${totalBs.toFixed(2)}`);
        s += '\x1B\x45\x00'; 
        s += print_divider("=");

        // ================= 8. 页脚与支付方式 =================
        s += center_text('Forma de Pago:');
        if (data.payment) {
          if (data.payment.cardPos > 0) s += center_text(`Tarjeta: Bs. ${Number(data.payment.cardPos).toFixed(2)}`);
          if (data.payment.pagoMovil > 0) s += center_text(`Pago Movil: Bs. ${Number(data.payment.pagoMovil).toFixed(2)}`);
          if (data.payment.cashUsd > 0) s += center_text(`Efectivo USD: $${Number(data.payment.cashUsd).toFixed(2)}`);
        } else {
          s += center_text(String(data.payment_method || 'CONTADO'));
        }
        s += '\n';
        s += center_text('Gracias por su compra!');
        
        // ================= 9. 切纸 =================
        s += '\n\n\n\n'; 
        s += '\x1D\x56\x41\x00'; 

        const finalBuffer = iconv.encode(s, 'CP850');

        setTimeout(() => {
          const tmpFile = path.join(__dirname, 'print_temp.bin');
          fs.writeFileSync(tmpFile, finalBuffer);
          
          try {
            execSync('/usr/bin/cancel -a || true', { timeout: 3000 });
            execSync(`/usr/bin/lp -d "${PRINTER_NAME}" -o raw "${tmpFile}"`, { timeout: 5000 });
            console.log("✅ 42列全宽小票打印成功！");
            ws.send(JSON.stringify({ type: 'print_result', success: true }));
          } catch (err) {
            console.error("❌ 打印失败:", err.message);
            ws.send(JSON.stringify({ type: 'print_result', success: false, error: err.message }));
          } finally {
            if (fs.existsSync(tmpFile)) fs.unlinkSync(tmpFile);
          }
        }, 300);
        
      } catch (err) { 
        console.error("代码执行出错:", err);
        ws.send(JSON.stringify({ type: 'print_result', success: false, error: err.message }));
      }
    }
  });
});