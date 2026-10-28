import { ref } from 'vue';

// 🚫 打印功能开关：暂停时改为 false（print-agent 归档于 .archive/print-agent/）
// 恢复步骤：① .archive/print-agent/ 移回 print-agent/ ② app/main.py 两行取消注释
//          ③ 本常量改为 true ④ PosView/QuotationView 的 autoPrintReceipt 移除早返回
export const PRINT_ENABLED = false;

// 全局单例状态
const isConnected = ref(false);
const isPrinting = ref(false);
let ws = null;
let reconnectTimer = null;
let heartTimer = null;
let currentResolve = null;
let currentReject = null;
let isInitialized = false;

const WS_URL = 'ws://127.0.0.1:8899';

const connect = () => {
  if (!PRINT_ENABLED) return;  // 🚫 停用时不连 ws，避免每 5 秒重连噪音
  if (ws && (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING)) return;

  ws = new WebSocket(WS_URL);

  ws.onopen = () => {
    isConnected.value = true;
    if (reconnectTimer) clearTimeout(reconnectTimer);
    if (heartTimer) clearInterval(heartTimer);
    heartTimer = setInterval(() => {
      if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ type: 'ping' }));
      }
    }, 5000);
  };

  ws.onmessage = (event) => {
    try {
      const msg = JSON.parse(event.data);
      if (msg.type === 'print_result') {
        isPrinting.value = false;
        if (currentResolve && currentReject) {
          if (msg.success) currentResolve();
          else currentReject(new Error(msg.error || '打印失败'));
          currentResolve = null;
          currentReject = null;
        }
      }
    } catch (err) {}
  };

  ws.onclose = () => {
    isConnected.value = false;
    if (heartTimer) clearInterval(heartTimer);
    reconnectTimer = setTimeout(connect, 5000);
  };
};

export function usePrintAgent() {
  if (!isInitialized && typeof window !== 'undefined') {
    connect();
    isInitialized = true;
  }

  const printReceipt = (orderData) => {
    if (!PRINT_ENABLED) {
      return Promise.resolve({ success: false, disabled: true });  // resolve 避免 unhandled rejection
    }
    return new Promise((resolve, reject) => {
      if (!isConnected.value) return reject(new Error('代理未运行'));
      isPrinting.value = true;
      currentResolve = resolve;
      currentReject = reject;
      ws.send(JSON.stringify({ type: 'print', data: orderData }));
      setTimeout(() => {
        if (isPrinting.value) {
          isPrinting.value = false;
          reject(new Error('打印超时'));
          currentResolve = null; currentReject = null;
        }
      }, 10000);
    });
  };

  return { isConnected, isPrinting, printReceipt };
}
