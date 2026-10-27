import { ref } from 'vue';

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
