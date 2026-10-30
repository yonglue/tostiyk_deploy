/**
 * 全局智能模糊搜索工具
 * 逻辑：
 * 1. 将搜索词按空格拆分为多个 token。
 * 2. 将商品的所有关键字段拼接成一个大字符串（包含特殊符号），并同时生成一个去除特殊符号（仅保留A-Z0-9）的字符串。
 * 3. 所有 token 必须同时命中（AND逻辑）：只要 token 在原始串或清洗串中出现，即算命中。
 * 4. 完美支持：无顺序限制、跨字段混搜、OEM尾号盲搜。
 */
export function matchSmartSearch(item, query, fields) {
  if (!query || !query.trim()) return true;
  
  // 1. 拆词并转大写
  const tokens = query.trim().toUpperCase().split(/\s+/).filter(Boolean);
  if (tokens.length === 0) return true;

  // 2. 拼接指定的字段内容
  const fullText = fields
    .map(f => item[f] ? String(item[f]) : '')
    .join(' ')
    .toUpperCase();

  // 3. 生成清洗后的纯字母数字串（用于匹配含 - 或 / 的 OEM 等）
  const cleanText = fullText.replace(/[^A-Z0-9]/g, '');

  // 4. AND 匹配：所有词都必须在上面两个串之一找到
  return tokens.every(token => {
    // 原串包含（支持名称、品牌等带有空格的字段）
    if (fullText.includes(token)) return true;
    // 清洗串包含（支持 OEM 尾号，例如搜 98918 命中 12345-98918）
    const cleanToken = token.replace(/[^A-Z0-9]/g, '');
    if (cleanToken && cleanText.includes(cleanToken)) return true;
    return false;
  });
}
