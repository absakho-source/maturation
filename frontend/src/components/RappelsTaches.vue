<template>
  <div v-if="rappels.length > 0" class="rappels-container">
    <div class="rappels-header">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M22 17H2a3 3 0 0 0 3-3V9a7 7 0 0 1 14 0v5a3 3 0 0 0 3 3zm-8.27 4a2 2 0 0 1-3.46 0"/>
      </svg>
      <h3>Rappels</h3>
    </div>
    <div class="rappels-list">
      <div v-for="(rappel, index) in rappels" :key="index"
           class="rappel-item"
           :class="rappel.urgence"
           @click="handleClick(rappel)">
        <div class="rappel-icon">{{ rappel.icon || '📌' }}</div>
        <div class="rappel-content">
          <div class="rappel-message">{{ rappel.message }}</div>
          <div v-if="rappel.detail" class="rappel-detail">{{ rappel.detail }}</div>
        </div>
        <div class="rappel-count" v-if="rappel.count">{{ rappel.count }}</div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'RappelsTaches',
  props: {
    rappels: {
      type: Array,
      required: true,
      // Structure: [{ message, detail?, count?, urgence?, icon?, action? }]
    }
  },
  methods: {
    handleClick(rappel) {
      if (rappel.action) {
        this.$emit('action-clicked', rappel.action);
      }
    }
  }
};
</script>

<style scoped>
.rappels-container {
  background: linear-gradient(135deg, #fff5e6 0%, #ffe6cc 100%);
  border-left: 4px solid #ff9800;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 24px;
  box-shadow: 0 2px 8px rgba(255, 152, 0, 0.15);
}

.rappels-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  color: #e65100;
}

.rappels-header svg {
  animation: ring 2s ease-in-out infinite;
}

@keyframes ring {
  0%, 100% { transform: rotate(0deg); }
  10%, 30% { transform: rotate(-10deg); }
  20%, 40% { transform: rotate(10deg); }
}

.rappels-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 700;
}

.rappels-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.rappel-item {
  display: flex;
  align-items: center;
  gap: 12px;
  background: white;
  padding: 12px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
  border-left: 3px solid transparent;
}

.rappel-item:hover {
  transform: translateX(4px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.rappel-item.urgent {
  border-left-color: #f44336;
  background: #ffebee;
}

.rappel-item.important {
  border-left-color: #ff9800;
}

.rappel-item.normal {
  border-left-color: #2196f3;
}

.rappel-icon {
  font-size: 24px;
  flex-shrink: 0;
}

.rappel-content {
  flex: 1;
}

.rappel-message {
  font-size: 14px;
  font-weight: 600;
  color: #333;
  margin-bottom: 2px;
}

.rappel-detail {
  font-size: 12px;
  color: #666;
}

.rappel-count {
  background: #ff9800;
  color: white;
  padding: 4px 12px;
  border-radius: 12px;
  font-weight: 700;
  font-size: 14px;
}
</style>
