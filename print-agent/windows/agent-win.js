const { WebSocketServer } = require('ws');
const { printer: ThermalPrinter, types: PrinterTypes } = require('node-thermal-printer');

const PORT = 8899;
// ⚠️ 需要客户在 Windows "设备和打印机" 中看到的名字
const WINDOWS_PRINTER_NAME = "XP-80C"; 

const wss = new WebSocketServer({ port: PORT });
console.log(`🚀 Windows 打印代理已启动: ws://127.0.0.1:${PORT}`);

wss.on('connection', (ws) => {
  console.log("✅ 前端已连接");

  ws.on('message', async (raw) => {
    let msg;
    try { msg = JSON.parse(raw); } catch { return; }

    if (msg.type === 'ping') {
      ws.send(JSON.stringify({ type: 'pong', status: 'ok' }));
      return;
    }

    if (msg.type === 'print' && msg.data) {
      const data = msg.data;
      console.log(`📝 收到打印请求: ${data.order_no || '小票'}`);

      try {
        const printer = new ThermalPrinter({
          type: PrinterTypes.EPSON,
          interface: `printer:${WINDOWS_PRINTER_NAME}`, // 走 Windows 打印队列
          characterSet: 'SINGAPORE', // 支持中文
          removeSpecialCharacters: false,
          lineCharacter: "-",
        });

        const isConnected = await printer.isPrinterConnected();
        if (!isConnected) {
          throw new Error(`找不到打印机: ${WINDOWS_PRINTER_NAME}`);
        }

        // --- 小票排版 ---
        printer.alignCenter();
        printer.bold(true);
        printer.println(data.companyName || 'Tostiyk ERP');
        printer.bold(false);
        printer.drawLine();
        
        printer.alignLeft();
        printer.println(`单号: ${data.order_no || '-'}`);
        printer.println(`日期: ${data.date || new Date().toLocaleString()}`);
        printer.println(`客户: ${data.client_name || 'Contado'}`);
        printer.drawLine();

        printer.println("商品                数量   金额");
        (data.items || []).forEach(item => {
          let name = String(item.name).substring(0, 15).padEnd(16, ' ');
          let qty = String(item.qty).padStart(4, ' ');
          let price = Number(item.price).toFixed(2).padStart(7, ' ');
          printer.println(`${name}${qty}${price}`);
        });
        
        printer.drawLine();
        printer.alignRight();
        printer.bold(true);
        printer.println(`TOTAL USD: $${Number(data.total_usd).toFixed(2)}`);
        if (data.total_bs) {
          printer.println(`TOTAL BS:  Bs.${Number(data.total_bs).toFixed(2)}`);
        }
        
        printer.alignCenter();
        printer.println("\n¡Gracias por su compra!");
        printer.cut();
        printer.beep(); // 蜂鸣器提示

        await printer.execute();
        console.log("✅ 打印成功");
        ws.send(JSON.stringify({ type: 'print_result', success: true }));
      } catch (err) {
        console.error("❌ 打印失败:", err.message);
        ws.send(JSON.stringify({ type: 'print_result', success: false, error: err.message }));
      }
    }
  });

  ws.on('close', () => console.log("❌ 前端断开连接"));
});
