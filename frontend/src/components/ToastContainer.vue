<template>
  <teleport to="body">
    <div class="toast-container" aria-live="polite">
      <transition-group name="toast">
        <div
          v-for="t in toasts"
          :key="t.id"
          class="toast"
          :class="`toast--${t.type}`"
          role="status"
          @click="remove(t.id)"
        >
          <span class="toast-icon" aria-hidden="true">{{ iconFor(t.type) }}</span>
          <span class="toast-message">{{ t.message }}</span>
          <button class="toast-close" @click.stop="remove(t.id)" aria-label="Fermer">✕</button>
        </div>
      </transition-group>
    </div>
  </teleport>
</template>

<script>
import { toastState } from '../toast.js';

export default {
  name: 'ToastContainer',
  computed: {
    toasts() { return toastState.list; }
  },
  methods: {
    remove(id) {
      const i = toastState.list.findIndex(t => t.id === id);
      if (i >= 0) toastState.list.splice(i, 1);
    },
    iconFor(type) {
      return { success: '✅', error: '❌', warning: '⚠️', info: 'ℹ️' }[type] || 'ℹ️';
    }
  }
}
</script>

<style scoped>
.toast-container {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 100000;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  max-width: 420px;
  pointer-events: none;
}
.toast {
  display: flex;
  align-items: flex-start;
  gap: 0.6rem;
  padding: 0.8rem 1rem;
  border-radius: 10px;
  box-shadow: 0 8px 24px rgba(0,0,0,0.18);
  background: #fff;
  border-left: 4px solid #64748b;
  color: #1e293b;
  font-size: 0.95rem;
  line-height: 1.35;
  pointer-events: auto;
  cursor: pointer;
}
.toast--success { border-left-color: #10b981; }
.toast--error   { border-left-color: #ef4444; }
.toast--warning { border-left-color: #f59e0b; }
.toast--info    { border-left-color: #0ea5e9; }

.toast-icon { font-size: 1.1rem; flex-shrink: 0; }
.toast-message { flex: 1; white-space: pre-line; }
.toast-close {
  background: transparent;
  border: none;
  color: #94a3b8;
  font-size: 1rem;
  cursor: pointer;
  padding: 0 0.25rem;
  line-height: 1;
}
.toast-close:hover { color: #1e293b; }

.toast-enter-from { opacity: 0; transform: translateX(40px); }
.toast-enter-to   { opacity: 1; transform: translateX(0); }
.toast-leave-from { opacity: 1; transform: translateX(0); }
.toast-leave-to   { opacity: 0; transform: translateX(40px); }
.toast-enter-active, .toast-leave-active { transition: opacity 0.25s, transform 0.25s; }

@media (max-width: 600px) {
  .toast-container { top: 10px; right: 10px; left: 10px; max-width: none; }
}
</style>
