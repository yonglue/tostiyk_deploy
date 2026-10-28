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

// 左右两端对齐函数
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
console.log(`🚀 Tostiyk ERP 打印代理已启动 (多税率智能拆分完美版): ws://127.0.0.1:${PORT}`);

wss.on('connection', (ws) => {
  ws.on('message', (raw) => {
    let msg;
    try { 
        msg = JSON.parse(raw); 
    } catch (e) { 
        return; 
    }

    if (msg.type === 'ping') return ws.send(JSON.stringify({ type: 'pong' }));

    if (msg.type === 'print' && msg.data) {
      const data = msg.data;
      
      try {
        let s = '';
        // ================= 1. 硬件初始化与物理字库对齐锁死 =================
        s += '\x1B\x40';         // 初始化打印机
        s += '\x1B\x74\x02';     // CP850 西语编码
        s += '\x1B\x4D\x00';     // 强制锁定标准 Font A（42列物理大字）
        s += '\x1B\x33\x30';     // 行间距
        s += '\x1B\x4A\x20';     // 物理前进 32 点距，防切头
        s += '\x1B\x61\x00';     // 左对齐

        // ================= 2. 头部信息 (居中) =================
        s += center_text(data.companyName || 'MUNDO REPUESTOS C.A');
        s += center_text(`RIF: ${data.companyRif || 'J-307219955'}`);
        s += center_text(data.companyAddress || 'Valencia, Carabobo, Venezuela');
        s += center_text(`TEL: ${data.companyPhone || '+58 412-0000000'}`);
        s += print_divider("=");

        // ================= 3. 动态多税率解析与智能归类 (支持 0%, 8%, 16%) =================
        let totalItemsCount = 0;
        
        let exentoBase = 0;
        let bi8Base = 0;
        let tax8Val = 0;
        let bi16Base = 0;
        let tax16Val = 0;

        (data.items || []).forEach(item => {
          const qty = Number(item.quantity || item.qty || 1);
          const price = Number(item.price || item.price_usd || 0);
          const lineTotal = Number(item.total || (qty * price));
          totalItemsCount += qty;

          // 兼容获取单品税率 (0, 0.08, 0.16)
          const taxRate = Number(item.tax_rate ?? item.taxRate ?? 0.16);

          if (taxRate === 0 || taxRate === 0.00) {
              exentoBase += lineTotal;
          } else if (taxRate === 0.08) {
              const base = lineTotal / 1.08;
              bi8Base += base;
              tax8Val += (lineTotal - base);
          } else {
              const base = lineTotal / 1.16;
              bi16Base += base;
              tax16Val += (lineTotal - base);
          }
        });

        exentoBase = Number(exentoBase.toFixed(2));
        bi8Base = Number(bi8Base.toFixed(2));
        tax8Val = Number(tax8Val.toFixed(2));
        bi16Base = Number(bi16Base.toFixed(2));
        tax16Val = Number(tax16Val.toFixed(2));

        const calcTotalUsd = exentoBase + bi8Base + tax8Val + bi16Base + tax16Val;
        const totalUsd = Number(data.total_usd || data.totalUsd || calcTotalUsd).toFixed(2);

        // 汇率计算与兜底
        let tasaVal = Number(data.tasa || data.bcv_rate || data.bcvRate || data.exchange_rate || 0);
        const totalBsInput = Number(data.total_bs || data.totalBs || 0);
        
        if (tasaVal === 0 && totalBsInput > 0 && Number(totalUsd) > 0) {
            tasaVal = totalBsInput / Number(totalUsd);
        }
        if (tasaVal === 0) {
            tasaVal = 887.00; // 默认标准汇率兜底
        }
        
        const totalBs = totalBsInput > 0 ? totalBsInput : (Number(totalUsd) * tasaVal);

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

        // ================= 6. 动态财务汇总 (按需显示，零金额自动隐藏) =================
        if (exentoBase > 0) {
            s += print_row("EXENTO", `$${exentoBase.toFixed(2)}`);
        }
        if (bi8Base > 0) {
            s += print_row("BI G08,00%", `$${bi8Base.toFixed(2)}`);
            s += print_row("IVA (8%)", `$${tax8Val.toFixed(2)}`);
        }
        if (bi16Base > 0) {
            s += print_row("BI G16,00%", `$${bi16Base.toFixed(2)}`);
            s += print_row("IVA (16%)", `$${tax16Val.toFixed(2)}`);
        }
        s += print_divider("-");
        
        // ================= 7. 总计金额 (加粗) =================
        s += '\x1B\x45\x01'; 
        s += print_row("TOTAL USD", `$${totalUsd}`);
        s += print_row("TOTAL BS", `Bs.${totalBs.toFixed(2)}`);
        s += '\x1B\x45\x00'; 
        s += print_divider("=");

        // ================= 8. 页脚与支付方式 =================
        s += center_text('Forma de Pago:');
        if (data.payment) {
          if (data.payment.cardPos > 0) s += center_text(`Tarjeta: Bs. ${Number(data.payment.cardPos).toFixed(2)}`);
          if (data.payment.pagoMovil > 0) s += center_text(`Pago Movil: Bs. ${Number(data.payment.pagoMovil).toFixed(2)}`);
          if (data.payment.cashUsd > 0) s += center_text(`Efectivo USD: $${Number(data.payment.cashUsd).toFixed(2)}`);
          if (data.payment.cashBs > 0) s += center_text(`Efectivo Bs: Bs. ${Number(data.payment.cashBs).toFixed(2)}`);
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
            console.log("✅ 小票打印成功（多税率动态拆分生效）！");
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
