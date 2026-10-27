const { WebSocketServer } = require('ws');
const escpos = require('escpos');
const fs = require('fs');
const path = require('path');
const os = require('os');
const { execSync } = require('child_process');

const PORT = 8899;
const PRINTER_NAME = "Printer_POS_80"; // 确保这是你的打印机名称

class VirtualAdapter {
  constructor() { this.buffer = Buffer.alloc(0); }
  write(data) { this.buffer = Buffer.concat([this.buffer, Buffer.from(data)]); }
  open(cb) { cb && cb(); }
  close(cb) { cb && cb(); }
}

const wss = new WebSocketServer({ port: PORT });

console.log(`🚀 打印代理已启动: ws://127.0.0.1:${PORT}`);

wss.on('connection', (ws) => {
  console.log("✅ 前端客户端已连接");

  ws.on('message', (raw) => {
    let msg;
    try { msg = JSON.parse(raw); } catch { return; }

    if (msg.type === 'ping') {
      ws.send(JSON.stringify({ type: 'pong', status: 'ok' }));
      return;
    }

    if (msg.type === 'print' && msg.data) {
      const data = msg.data;
      console.log(`📝 收到打印请求: ${data.order_no || data.companyName}`);

      const device = new VirtualAdapter();
      const encoding = data.lang === 'zh' ? 'GB18030' : 'CP850';
      const printer = new escpos.Printer(device, { encoding });

      try {
        // --- 小票头部 ---
        printer.font('a').align('ct').style('b').size(1, 1)
          .text(data.companyName || 'Tostiyk ERP')
          .style('normal').size(0, 0)
        if (data.companyRif) printer.text(`RIF: ${data.companyRif}`)
        if (data.companyAddress) printer.text(data.companyAddress)
        if (data.companyPhone) printer.text(`TEL: ${data.companyPhone}`)
        
        printer.text('--------------------------------')
          .align('lt')
          .text(`单号 No: ${data.order_no || '-'}`)
          .text(`日期 Date: ${data.date || new Date().toLocaleString()}`)
          .text(`客户 Client: ${data.client_name || 'Contado (散客)'}`)
          .text(`收银 Cashier: ${data.operator || '-'}`)
          .text('--------------------------------');

        // --- 商品明细 ---
        printer.text('商品 / Producto       数量  金额')
        ;(data.items || []).forEach(item => {
          // 商品名过长时截断
          let name = String(item.name).substring(0, 15).padEnd(16, ' ');
          let qty = String(item.qty).padStart(3, ' ');
          let price = Number(item.price).toFixed(2).padStart(7, ' ');
          printer.text(`${name}${qty}${price}`);
        });
        
        printer.text('--------------------------------');

        // --- 支付明细 ---
        if (data.payment && Object.keys(data.payment).length > 0) {
          printer.text('支付方式 / Pago:')
          Object.entries(data.payment).forEach(([method, amount]) => {
            if (amount > 0) {
               printer.text(`  ${method.padEnd(12)}: $${Number(amount).toFixed(2)}`)
            }
          })
        }

        // --- 底部合计 ---
        printer.align('rt').style('b')
          .text(`TOTAL USD: $${Number(data.total_usd).toFixed(2)}`);
        
        if (data.total_bs) {
          printer.text(`TOTAL BS:  Bs.${Number(data.total_bs).toFixed(2)}`);
        }

        // --- 切纸 ---
        printer.style('normal').align('ct').text('\n¡Gracias por su compra!\n').cut().close();

        // 发送给系统队列
        setTimeout(() => {
          if (!device.buffer || device.buffer.length === 0) {
            return ws.send(JSON.stringify({ type: 'print_result', success: false, error: '生成指令失败' }));
          }

          const tmpFile = path.join(os.tmpdir(), `receipt_${Date.now()}.bin`);
          fs.writeFileSync(tmpFile, device.buffer);

          try {
            execSync(`/usr/bin/lp -d "${PRINTER_NAME}" -o raw "${tmpFile}"`);
            console.log("✅ 打印任务已发送至系统队列");
            ws.send(JSON.stringify({ type: 'print_result', success: true }));
          } catch (err) {
            console.error("❌ 打印失败:", err.message);
            ws.send(JSON.stringify({ type: 'print_result', success: false, error: err.message }));
          } finally {
            if (fs.existsSync(tmpFile)) fs.unlinkSync(tmpFile);
          }
        }, 300);

      } catch (err) {
        ws.send(JSON.stringify({ type: 'print_result', success: false, error: err.message }));
      }
    }
  });

  ws.on('close', () => console.log("❌ 客户端断开连接"));
});
