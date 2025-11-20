<template>
  <div class="notification-container">
    <button class="notification-bell" @click="toggleDropdown" :title="unreadCount > 0 ? `${unreadCount} notification(s) non lue(s)` : 'Notifications'">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/>
        <path d="M13.73 21a2 2 0 0 1-3.46 0"/>
      </svg>
      <span v-if="unreadCount > 0" class="notification-badge">{{ unreadCount > 99 ? '99+' : unreadCount }}</span>
    </button>

    <div v-if="showDropdown" class="notification-dropdown">
      <div class="dropdown-header">
        <h4>Notifications</h4>
        <button v-if="unreadCount > 0" @click="markAllAsRead" class="mark-all-read">
          Tout marquer comme lu
        </button>
      </div>

      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
        Chargement...
      </div>

      <div v-else-if="notifications.length === 0" class="empty-state">
        <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/>
          <path d="M13.73 21a2 2 0 0 1-3.46 0"/>
        </svg>
        <p>Aucune notification</p>
      </div>

      <div v-else class="notification-list">
        <div
          v-for="notif in notifications"
          :key="notif.id"
          class="notification-item"
          :class="{ 'unread': !notif.lu }"
          @click="handleNotificationClick(notif)"
        >
          <div class="notif-icon" :class="'type-' + notif.type">
            <svg v-if="notif.type === 'statut_change'" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 22c5.523 0 10-4.477 10-10S17.523 2 12 2 2 6.477 2 12s4.477 10 10 10z"/>
              <path d="M12 6v6l4 2"/>
            </svg>
            <svg v-else-if="notif.type === 'nouveau_message'" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
            </svg>
            <svg v-else-if="notif.type === 'complement_requis'" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"/>
              <line x1="12" y1="8" x2="12" y2="12"/>
              <line x1="12" y1="16" x2="12.01" y2="16"/>
            </svg>
            <svg v-else-if="notif.type === 'avis_rendu'" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
              <polyline points="22 4 12 14.01 9 11.01"/>
            </svg>
            <svg v-else-if="notif.type === 'document_ajoute'" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
              <polyline points="14 2 14 8 20 8"/>
            </svg>
            <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"/>
              <line x1="12" y1="16" x2="12" y2="12"/>
              <line x1="12" y1="8" x2="12.01" y2="8"/>
            </svg>
          </div>

          <div class="notif-content">
            <div class="notif-titre">{{ notif.titre }}</div>
            <div class="notif-message">{{ notif.message }}</div>
            <div class="notif-date">{{ formatDate(notif.date_creation) }}</div>
          </div>

          <button v-if="!notif.lu" @click.stop="markAsRead(notif)" class="mark-read-btn" title="Marquer comme lu">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="20 6 9 17 4 12"/>
            </svg>
          </button>
        </div>
      </div>

      <div v-if="notifications.length > 0" class="dropdown-footer">
        <button @click="loadMore" v-if="hasMore" class="load-more-btn">
          Voir plus
        </button>
      </div>
    </div>

    <!-- Overlay pour fermer le dropdown -->
    <div v-if="showDropdown" class="dropdown-overlay" @click="showDropdown = false"></div>
  </div>
</template>

<script>
export default {
  name: 'NotificationBell',
  data() {
    return {
      showDropdown: false,
      notifications: [],
      unreadCount: 0,
      loading: false,
      hasMore: true,
      limit: 10,
      pollInterval: null
    };
  },
  computed: {
    username() {
      const user = JSON.parse(localStorage.getItem('user') || '{}');
      return user.username || '';
    }
  },
  mounted() {
    if (this.username) {
      this.fetchUnreadCount();
      // Polling toutes les 30 secondes
      this.pollInterval = setInterval(() => {
        this.fetchUnreadCount();
      }, 30000);
    }
  },
  beforeUnmount() {
    if (this.pollInterval) {
      clearInterval(this.pollInterval);
    }
  },
  methods: {
    async fetchUnreadCount() {
      if (!this.username) return;

      try {
        const response = await fetch(`/api/notifications/count?username=${encodeURIComponent(this.username)}`);
        if (response.ok) {
          const data = await response.json();
          this.unreadCount = data.count;
        }
      } catch (error) {
        console.error('Erreur fetch unread count:', error);
      }
    },

    async fetchNotifications() {
      if (!this.username) return;

      this.loading = true;
      try {
        const response = await fetch(
          `/api/notifications?username=${encodeURIComponent(this.username)}&limit=${this.limit}`
        );
        if (response.ok) {
          this.notifications = await response.json();
          this.hasMore = this.notifications.length >= this.limit;
        }
      } catch (error) {
        console.error('Erreur fetch notifications:', error);
      } finally {
        this.loading = false;
      }
    },

    async toggleDropdown() {
      this.showDropdown = !this.showDropdown;
      if (this.showDropdown) {
        await this.fetchNotifications();
      }
    },

    async markAsRead(notif) {
      try {
        const response = await fetch(`/api/notifications/${notif.id}/read`, {
          method: 'PUT'
        });
        if (response.ok) {
          notif.lu = true;
          this.unreadCount = Math.max(0, this.unreadCount - 1);
        }
      } catch (error) {
        console.error('Erreur mark as read:', error);
      }
    },

    async markAllAsRead() {
      try {
        const response = await fetch('/api/notifications/read-all', {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ username: this.username })
        });
        if (response.ok) {
          this.notifications.forEach(n => n.lu = true);
          this.unreadCount = 0;
        }
      } catch (error) {
        console.error('Erreur mark all as read:', error);
      }
    },

    handleNotificationClick(notif) {
      // Marquer comme lu
      if (!notif.lu) {
        this.markAsRead(notif);
      }

      // Naviguer si lien présent
      if (notif.lien) {
        this.showDropdown = false;
        this.$router.push(notif.lien);
      }
    },

    async loadMore() {
      this.limit += 10;
      await this.fetchNotifications();
    },

    formatDate(dateStr) {
      if (!dateStr) return '';
      const date = new Date(dateStr);
      const now = new Date();
      const diffMs = now - date;
      const diffMins = Math.floor(diffMs / 60000);
      const diffHours = Math.floor(diffMs / 3600000);
      const diffDays = Math.floor(diffMs / 86400000);

      if (diffMins < 1) return "À l'instant";
      if (diffMins < 60) return `Il y a ${diffMins} min`;
      if (diffHours < 24) return `Il y a ${diffHours}h`;
      if (diffDays < 7) return `Il y a ${diffDays}j`;

      return date.toLocaleDateString('fr-FR', {
        day: 'numeric',
        month: 'short'
      });
    }
  }
};
</script>

<style scoped>
.notification-container {
  position: relative;
}

.notification-bell {
  position: relative;
  background: transparent;
  border: none;
  cursor: pointer;
  padding: 8px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s;
}

.notification-bell:hover {
  background: rgba(0, 0, 0, 0.1);
}

.notification-bell svg {
  color: #4a5568;
}

.notification-badge {
  position: absolute;
  top: 2px;
  right: 2px;
  background: #ef4444;
  color: white;
  font-size: 0.65rem;
  font-weight: 700;
  min-width: 16px;
  height: 16px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 4px;
}

.dropdown-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 999;
}

.notification-dropdown {
  position: absolute;
  top: 100%;
  right: 0;
  width: 360px;
  max-height: 480px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
  z-index: 1000;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.dropdown-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border-bottom: 1px solid #e5e7eb;
}

.dropdown-header h4 {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
  color: #111827;
}

.mark-all-read {
  background: none;
  border: none;
  color: #2563eb;
  font-size: 0.8rem;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
}

.mark-all-read:hover {
  background: #eff6ff;
}

.loading-state,
.empty-state {
  padding: 2rem;
  text-align: center;
  color: #6b7280;
}

.empty-state svg {
  margin: 0 auto 0.5rem;
  opacity: 0.5;
}

.empty-state p {
  margin: 0;
  font-size: 0.875rem;
}

.spinner {
  width: 24px;
  height: 24px;
  border: 3px solid #e5e7eb;
  border-top-color: #2563eb;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 0.5rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.notification-list {
  overflow-y: auto;
  max-height: 360px;
}

.notification-item {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  padding: 0.875rem 1rem;
  border-bottom: 1px solid #f3f4f6;
  cursor: pointer;
  transition: background 0.2s;
}

.notification-item:hover {
  background: #f9fafb;
}

.notification-item.unread {
  background: #eff6ff;
}

.notification-item.unread:hover {
  background: #dbeafe;
}

.notif-icon {
  flex-shrink: 0;
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #e5e7eb;
}

.notif-icon.type-statut_change { background: #fef3c7; color: #d97706; }
.notif-icon.type-nouveau_message { background: #dbeafe; color: #2563eb; }
.notif-icon.type-complement_requis { background: #fef2f2; color: #dc2626; }
.notif-icon.type-avis_rendu { background: #d1fae5; color: #059669; }
.notif-icon.type-document_ajoute { background: #e0e7ff; color: #4f46e5; }
.notif-icon.type-assignation { background: #f3e8ff; color: #7c3aed; }

.notif-content {
  flex: 1;
  min-width: 0;
}

.notif-titre {
  font-weight: 600;
  font-size: 0.875rem;
  color: #111827;
  margin-bottom: 2px;
}

.notif-message {
  font-size: 0.8rem;
  color: #6b7280;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.notif-date {
  font-size: 0.7rem;
  color: #9ca3af;
  margin-top: 4px;
}

.mark-read-btn {
  flex-shrink: 0;
  background: none;
  border: none;
  color: #9ca3af;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
}

.mark-read-btn:hover {
  background: #f3f4f6;
  color: #059669;
}

.dropdown-footer {
  padding: 0.75rem;
  border-top: 1px solid #e5e7eb;
  text-align: center;
}

.load-more-btn {
  background: none;
  border: none;
  color: #2563eb;
  font-size: 0.8rem;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
}

.load-more-btn:hover {
  background: #eff6ff;
}

@media (max-width: 480px) {
  .notification-dropdown {
    width: 100vw;
    right: -16px;
    border-radius: 0 0 12px 12px;
  }
}
</style>
