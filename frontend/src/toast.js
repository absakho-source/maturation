import { reactive } from 'vue';

export const toastState = reactive({ list: [] });
let nextId = 1;

function push(message, type = 'info', duration = 3500) {
  const id = nextId++;
  toastState.list.push({ id, message, type });
  if (duration > 0) {
    setTimeout(() => {
      const i = toastState.list.findIndex(t => t.id === id);
      if (i >= 0) toastState.list.splice(i, 1);
    }, duration);
  }
  return id;
}

export const toast = {
  success(msg, d)  { return push(msg, 'success', d); },
  error(msg, d)    { return push(msg, 'error',   d ?? 5000); },
  warning(msg, d)  { return push(msg, 'warning', d); },
  info(msg, d)     { return push(msg, 'info',    d); },
};

// Plugin Vue pour exposer $toast dans toutes les vues
export const ToastPlugin = {
  install(app) {
    app.config.globalProperties.$toast = toast;
  }
};
