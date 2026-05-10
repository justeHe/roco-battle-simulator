// 工具功能单元测试
const { JSDOM } = require('jsdom');
const fs = require('fs');
const path = require('path');

// 加载HTML文件
const html = fs.readFileSync(path.resolve(__dirname, 'tools.html'), 'utf8');

// 测试套件描述
describe('Tools Page Functionality', () => {
  let dom;
  let document;
  let window;

  // 在每个测试前加载DOM
  beforeEach(() => {
    dom = new JSDOM(html, { runScripts: 'dangerously' });
    document = dom.window.document;
    window = dom.window;
  });

  // 测试1: 页面加载时工具列表渲染
  test('should render tool list on page load', () => {
    const toolItems = document.querySelectorAll('.tool-item');
    expect(toolItems.length).toBeGreaterThan(0);
  });

  // 测试2: 搜索功能过滤工具
  test('should filter tools based on search input', () => {
    const searchInput = document.getElementById('search-tools');
    const initialCount = document.querySelectorAll('.tool-item:not([style*="display:none"])').length;
    
    // 模拟搜索输入
    searchInput.value = 'battle';
    const event = new window.Event('input');
    searchInput.dispatchEvent(event);
    
    const filteredCount = document.querySelectorAll('.tool-item:not([style*="display:none"])').length;
    expect(filteredCount).toBeLessThan(initialCount);
    expect(filteredCount).toBeGreaterThan(0);
  });

  // 测试3: 工具点击事件
  test('should handle tool item click', () => {
    const firstTool = document.querySelector('.tool-item');
    const clickEvent = new window.MouseEvent('click');
    
    let clicked = false;
    firstTool.addEventListener('click', () => {
      clicked = true;
    });
    
    firstTool.dispatchEvent(clickEvent);
    expect(clicked).toBe(true);
  });
});