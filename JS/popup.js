console.log("popup.js loaded");
document.addEventListener('DOMContentLoaded', function() {
  const summarizeBtn = document.getElementById('summarizeBtn');
  const replyBtn = document.getElementById('replyBtn');
  const emailContent = document.getElementById('emailContent');
  const result = document.getElementById('result');
  const wordCount = document.querySelector('.word-count');

  // 自動調整文本框高度
  function adjustTextareaHeight() {
      emailContent.style.height = 'auto';
      emailContent.style.height = Math.max(120, emailContent.scrollHeight) + 'px';
  }

  // 更新字數統計
  function updateWordCount() {
      const count = emailContent.value.trim().length;
      wordCount.textContent = `${count} words`;
      
      // 根據內容決定按鈕狀態
      const buttonsEnabled = count > 0;
      summarizeBtn.disabled = !buttonsEnabled;
      replyBtn.disabled = !buttonsEnabled;
  }

  // 監聽輸入事件
  emailContent.addEventListener('input', () => {
      adjustTextareaHeight();
      updateWordCount();
  });

  // 初始化
  updateWordCount();

  // 生成摘要
  async function generateSummary(content) {
    const response = await fetch('http://localhost:5001/summary', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ content: content })
    });

    if (!response.ok) {
        const data = await response.json();
        throw new Error(data.error || 'Server processing failed, please try again later');
    }

    return await response.json();
  }

  // 生成回覆
  async function generateReply(content) {
    const response = await fetch('http://localhost:5001/reply', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ content: content })
    });

    if (!response.ok) {
        const data = await response.json();
        throw new Error(data.error || 'Server processing failed, please try again later');
    }

    return await response.json();
  }

  // 處理生成摘要
  summarizeBtn.addEventListener('click', async () => {
      try {
          const content = emailContent.value.trim();
          
          if (!content) {
              result.innerHTML = '<div class="error">Please input email content</div>';
              return;
          }

          // 更新 UI 狀態
          summarizeBtn.disabled = true;
          replyBtn.disabled = true;
          summarizeBtn.textContent = 'Generating...';
          result.innerHTML = '<div class="loading">Generating<span class="loading-dots"></span></div>';

          // 發送請求
          console.log('Starting to generate summary...');
          const data = await generateSummary(content);
          console.log('Finished:', data);
          
          // 處理響應
          if (data.error) {
              result.innerHTML = `<div class="error">Error: ${data.error}</div>`;
          } else {
              result.textContent = data.summary;
          }
      } catch (error) {
          console.error('Error:', error);
          result.innerHTML = `<div class="error">Error: ${error.message}</div>`;
      } finally {
          // 恢復按鈕狀態
          summarizeBtn.disabled = false;
          replyBtn.disabled = false;
          summarizeBtn.textContent = 'Summarize';
      }
  });

  // 處理生成回覆
  replyBtn.addEventListener('click', async () => {
      try {
          const content = emailContent.value.trim();
          
          if (!content) {
              result.innerHTML = '<div class="error">Please input email content</div>';
              return;
          }

          // 更新 UI 狀態
          summarizeBtn.disabled = true;
          replyBtn.disabled = true;
          replyBtn.textContent = 'Generating...';
          result.innerHTML = '<div class="loading">Generating<span class="loading-dots"></span></div>';

          // 發送請求
          console.log('Starting to generate reply...');
          const data = await generateReply(content);
          console.log('Finished:', data);
          
          // 處理響應
          if (data.error) {
              result.innerHTML = `<div class="error">Error: ${data.error}</div>`;
          } else {
              // 使用 pre 標籤保持郵件格式
              result.innerHTML = `<pre>${data.reply}</pre>`;
          }
      } catch (error) {
          console.error('Error:', error);
          result.innerHTML = `<div class="error">Error: ${error.message}</div>`;
      } finally {
          summarizeBtn.disabled = false;
          replyBtn.disabled = false;
          replyBtn.textContent = 'Reply';
      }
  });
});