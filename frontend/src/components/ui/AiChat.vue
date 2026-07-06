<template>
  <div class="ai-chat-widget">
    <!-- Floating button -->
    <button class="ac-toggle" @click="open = !open" :class="{ active: open }">
      <svg v-if="!open" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M8 14s1.5 2 4 2 4-2 4-2"/><line x1="9" y1="9" x2="9.01" y2="9"/><line x1="15" y1="9" x2="15.01" y2="9"/></svg>
      <svg v-else width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
    </button>

    <!-- Chat panel -->
    <div v-if="open" class="ac-panel">
      <div class="ac-header">
        <span>AI 助手</span>
        <span class="ac-badge">DeepSeek</span>
      </div>
      <div class="ac-messages" ref="msgBox">
        <div v-for="(m, i) in messages" :key="i" :class="['ac-msg', m.role]">
          {{ m.content }}
        </div>
        <div v-if="loading" class="ac-msg assistant typing">
          <span class="dot"></span><span class="dot"></span><span class="dot"></span>
        </div>
      </div>
      <div class="ac-input-row">
        <input
          v-model="input"
          @keydown.enter="send"
          placeholder="问我租房问题..."
          :disabled="loading"
        />
        <button @click="send" :disabled="loading || !input.trim()">发送</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, watch } from 'vue'
import axios from 'axios'

const open = ref(false)
const input = ref('')
const loading = ref(false)
const messages = ref([])
const msgBox = ref(null)

function scrollDown() {
  nextTick(() => {
    if (msgBox.value) msgBox.value.scrollTop = msgBox.value.scrollHeight
  })
}

async function send() {
  const text = input.value.trim()
  if (!text || loading.value) return
  messages.value.push({ role: 'user', content: text })
  input.value = ''
  loading.value = true
  scrollDown()
  try {
    const history = messages.value.slice(-10, -1)
    const res = await axios.post('/api/v1/chat', { message: text, history })
    messages.value.push({ role: 'assistant', content: res.data.reply })
  } catch {
    messages.value.push({ role: 'assistant', content: '抱歉，暂时无法连接 AI 服务。请稍后再试。' })
  } finally {
    loading.value = false
    scrollDown()
  }
}

watch(open, (v) => {
  if (v) scrollDown()
})
</script>

<style scoped>
.ai-chat-widget { position: fixed; bottom: 24px; right: 24px; z-index: 3000; }

.ac-toggle {
  width: 52px; height: 52px; border-radius: 50%;
  background: var(--primary-gradient); color: #fff;
  border: none; cursor: pointer; display: flex; align-items: center;
  justify-content: center; box-shadow: 0 4px 20px rgba(245,158,11,0.35);
  transition: transform .2s, box-shadow .2s;
}
.ac-toggle:hover { transform: scale(1.08); }
.ac-toggle.active { background: #fff; color: var(--text); box-shadow: var(--shadow-lg); }

.ac-panel {
  position: absolute; bottom: 64px; right: 0;
  width: 360px; height: 500px; background: #fff;
  border-radius: var(--radius-lg); box-shadow: var(--shadow-lg);
  display: flex; flex-direction: column; overflow: hidden;
}
.ac-header {
  background: var(--primary-gradient); color: #fff;
  padding: 12px 16px; display: flex; align-items: center;
  justify-content: space-between; font-size: 15px; font-weight: 700;
}
.ac-badge { font-size: 11px; background: rgba(255,255,255,0.25); padding: 2px 8px; border-radius: var(--radius-full); font-weight: 500; }

.ac-messages { flex: 1; overflow-y: auto; padding: 12px; display: flex; flex-direction: column; gap: 10px; }
.ac-msg { padding: 8px 12px; border-radius: var(--radius-sm); font-size: 13px; line-height: 1.6; max-width: 85%; }
.ac-msg.user { align-self: flex-end; background: var(--bg-warm); color: var(--text); }
.ac-msg.assistant { align-self: flex-start; background: #F3F4F6; color: var(--text); }
.ac-msg.typing { display: flex; gap: 4px; padding: 12px 16px; }
.dot { width: 6px; height: 6px; border-radius: 50%; background: var(--text-muted); animation: blink 1.4s infinite; }
.dot:nth-child(2) { animation-delay: .2s; }
.dot:nth-child(3) { animation-delay: .4s; }
@keyframes blink { 0%,60%,100% { opacity: .3; } 30% { opacity: 1; } }

.ac-input-row { display: flex; gap: 6px; padding: 10px 12px; border-top: 1px solid var(--border); }
.ac-input-row input { flex: 1; padding: 8px 12px; border: 1.5px solid var(--border-strong); border-radius: var(--radius-full); font-size: 13px; outline: none; }
.ac-input-row input:focus { border-color: var(--primary); }
.ac-input-row button { padding: 8px 16px; border: none; border-radius: var(--radius-full); background: var(--primary); color: #fff; font-size: 13px; font-weight: 600; cursor: pointer; white-space: nowrap; }
.ac-input-row button:disabled { opacity: 0.5; }

@media (max-width: 480px) {
  .ac-panel { width: calc(100vw - 32px); right: -8px; }
}
</style>
