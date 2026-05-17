<template>
  <div class="demo-page">
    <!-- 示例1: 登录表单 -->
    <section class="demo-section">
      <h2>示例1: 登录表单</h2>
      <GlassCard type="dark" class="login-card">
        <div class="login-header">
          <h3>欢迎登录</h3>
          <p>请输入您的账号信息</p>
        </div>
        
        <div class="form-content">
          <div class="form-item">
            <label>用户名</label>
            <GlassInput 
              v-model="loginForm.username" 
              placeholder="请输入用户名"
            />
          </div>
          
          <div class="form-item">
            <label>密码</label>
            <GlassInput 
              v-model="loginForm.password" 
              type="password"
              placeholder="请输入密码"
            />
          </div>
          
          <div class="form-actions">
            <GlassButton type="primary" @click="handleLogin" class="btn-login">
              登录
            </GlassButton>
            <GlassButton type="secondary" @click="handleReset">
              重置
            </GlassButton>
          </div>
        </div>
      </GlassCard>
    </section>

    <!-- 示例2: 数据卡片列表 -->
    <section class="demo-section">
      <h2>示例2: 数据卡片列表</h2>
      <div class="card-grid">
        <GlassCard 
          v-for="item in dataCards" 
          :key="item.id"
          type="default"
          class="data-card"
        >
          <div class="card-icon" :style="{ background: item.color }">
            {{ item.icon }}
          </div>
          <div class="card-info">
            <h4>{{ item.title }}</h4>
            <p class="card-value">{{ item.value }}</p>
            <p class="card-desc">{{ item.description }}</p>
          </div>
          <GlassBadge :type="item.statusType">{{ item.status }}</GlassBadge>
        </GlassCard>
      </div>
    </section>

    <!-- 示例3: 用户管理表格 -->
    <section class="demo-section">
      <h2>示例3: 用户管理</h2>
      <GlassCard type="soft">
        <div class="table-header">
          <h3>用户列表</h3>
          <div class="header-actions">
            <GlassInput 
              v-model="searchKeyword" 
              placeholder="搜索用户..."
              class="search-input"
            />
            <GlassButton type="primary" @click="handleAddUser">
              + 添加用户
            </GlassButton>
          </div>
        </div>
        
        <div class="user-list">
          <div 
            v-for="user in filteredUsers" 
            :key="user.id"
            class="user-row"
          >
            <div class="user-info">
              <div class="user-avatar">{{ user.name.charAt(0) }}</div>
              <div>
                <p class="user-name">{{ user.name }}</p>
                <p class="user-email">{{ user.email }}</p>
              </div>
            </div>
            <div class="user-status">
              <GlassBadge :type="getUserStatusType(user.status)">
                {{ user.statusText }}
              </GlassBadge>
            </div>
            <div class="user-actions">
              <GlassButton type="ghost" size="small" @click="handleEdit(user)">
                编辑
              </GlassButton>
              <GlassButton type="danger" size="small" @click="handleDelete(user)">
                删除
              </GlassButton>
            </div>
          </div>
        </div>
      </GlassCard>
    </section>

    <!-- 示例4: 统计面板 -->
    <section class="demo-section">
      <h2>示例4: 统计面板</h2>
      <div class="stats-grid">
        <GlassCard type="default" class="stat-card">
          <div class="stat-header">
            <span class="stat-label">总用户数</span>
            <GlassBadge type="info">今日</GlassBadge>
          </div>
          <div class="stat-value">12,345</div>
          <div class="stat-change positive">+12.5% ↑</div>
        </GlassCard>
        
        <GlassCard type="soft" class="stat-card">
          <div class="stat-header">
            <span class="stat-label">活跃用户</span>
            <GlassBadge type="success">实时</GlassBadge>
          </div>
          <div class="stat-value">8,921</div>
          <div class="stat-change positive">+8.3% ↑</div>
        </GlassCard>
        
        <GlassCard type="dark" class="stat-card">
          <div class="stat-header">
            <span class="stat-label">待处理</span>
            <GlassBadge type="warning">紧急</GlassBadge>
          </div>
          <div class="stat-value">234</div>
          <div class="stat-change negative">-3.2% ↓</div>
        </GlassCard>
        
        <GlassCard type="default" class="stat-card">
          <div class="stat-header">
            <span class="stat-label">错误数</span>
            <GlassBadge type="danger">警告</GlassBadge>
          </div>
          <div class="stat-value">12</div>
          <div class="stat-change negative">+2.1% ↑</div>
        </GlassCard>
      </div>
    </section>

    <!-- 示例5: 通知和提示 -->
    <section class="demo-section">
      <h2>示例5: 通知和提示</h2>
      <GlassCard type="soft">
        <div class="notification-list">
          <div class="notification-item success">
            <div class="notif-icon">✓</div>
            <div class="notif-content">
              <h4>操作成功</h4>
              <p>数据已成功保存到数据库</p>
            </div>
            <GlassBadge type="success">成功</GlassBadge>
          </div>
          
          <div class="notification-item info">
            <div class="notif-icon">ℹ</div>
            <div class="notif-content">
              <h4>系统通知</h4>
              <p>系统将于今晚进行维护升级</p>
            </div>
            <GlassBadge type="info">信息</GlassBadge>
          </div>
          
          <div class="notification-item warning">
            <div class="notif-icon">⚠</div>
            <div class="notif-content">
              <h4>警告提示</h4>
              <p>存储空间即将用完，请及时清理</p>
            </div>
            <GlassBadge type="warning">警告</GlassBadge>
          </div>
          
          <div class="notification-item danger">
            <div class="notif-icon">✕</div>
            <div class="notif-content">
              <h4>错误信息</h4>
              <p>连接服务器失败，请检查网络设置</p>
            </div>
            <GlassBadge type="danger">错误</GlassBadge>
          </div>
        </div>
      </GlassCard>
    </section>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import GlassCard from '@/themes/dark-purple/components/GlassCard.vue'
import GlassButton from '@/themes/dark-purple/components/GlassButton.vue'
import GlassInput from '@/themes/dark-purple/components/GlassInput.vue'
import GlassBadge from '@/themes/dark-purple/components/GlassBadge.vue'

// 登录表单
const loginForm = ref({
  username: '',
  password: ''
})

const handleLogin = () => {
  console.log('登录:', loginForm.value)
  alert(`登录成功！\n用户名: ${loginForm.value.username}`)
}

const handleReset = () => {
  loginForm.value = { username: '', password: '' }
}

// 数据卡片
const dataCards = ref([
  {
    id: 1,
    title: '总收入',
    value: '¥128,430',
    description: '本月收入统计',
    icon: '💰',
    color: 'linear-gradient(135deg, rgba(244, 253, 175, 0.3), rgba(239, 221, 141, 0.2))',
    status: '增长',
    statusType: 'success'
  },
  {
    id: 2,
    title: '订单数',
    value: '1,234',
    description: '本月订单总量',
    icon: '📦',
    color: 'linear-gradient(135deg, rgba(128, 161, 212, 0.3), rgba(192, 137, 221, 0.2))',
    status: '正常',
    statusType: 'info'
  },
  {
    id: 3,
    title: '待处理',
    value: '56',
    description: '待审核订单',
    icon: '⏳',
    color: 'linear-gradient(135deg, rgba(239, 221, 141, 0.3), rgba(245, 213, 224, 0.2))',
    status: '紧急',
    statusType: 'warning'
  },
  {
    id: 4,
    title: '异常数',
    value: '3',
    description: '系统异常记录',
    icon: '⚠️',
    color: 'linear-gradient(135deg, rgba(123, 51, 126, 0.3), rgba(66, 13, 75, 0.2))',
    status: '危险',
    statusType: 'danger'
  }
])

// 用户列表
const searchKeyword = ref('')
const users = ref([
  { id: 1, name: '张三', email: 'zhangsan@example.com', status: 'active', statusText: '活跃' },
  { id: 2, name: '李四', email: 'lisi@example.com', status: 'inactive', statusText: '离线' },
  { id: 3, name: '王五', email: 'wangwu@example.com', status: 'active', statusText: '活跃' },
  { id: 4, name: '赵六', email: 'zhaoliu@example.com', status: 'pending', statusText: '待审核' },
  { id: 5, name: '孙七', email: 'sunqi@example.com', status: 'active', statusText: '活跃' }
])

const filteredUsers = computed(() => {
  if (!searchKeyword.value) return users.value
  const keyword = searchKeyword.value.toLowerCase()
  return users.value.filter(user => 
    user.name.toLowerCase().includes(keyword) ||
    user.email.toLowerCase().includes(keyword)
  )
})

const getUserStatusType = (status) => {
  const map = {
    active: 'success',
    inactive: 'info',
    pending: 'warning'
  }
  return map[status] || 'info'
}

const handleAddUser = () => {
  console.log('添加用户')
  alert('添加用户功能')
}

const handleEdit = (user) => {
  console.log('编辑用户:', user)
  alert(`编辑用户: ${user.name}`)
}

const handleDelete = (user) => {
  console.log('删除用户:', user)
  if (confirm(`确定要删除用户 ${user.name} 吗？`)) {
    users.value = users.value.filter(u => u.id !== user.id)
  }
}
</script>

<style scoped lang="scss">
@import '@/themes/dark-purple/styles/wisteria-glass-theme.scss';

.demo-page {
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
}

.demo-section {
  margin-bottom: 3rem;
  
  h2 {
    color: $text-primary;
    font-size: 1.75rem;
    font-weight: 600;
    margin-bottom: 1.5rem;
    padding-bottom: 0.75rem;
    border-bottom: 1px solid $glass-border-light;
  }
}

// 登录卡片
.login-card {
  max-width: 450px;
  margin: 0 auto;
  padding: 2.5rem;
  
  .login-header {
    text-align: center;
    margin-bottom: 2rem;
    
    h3 {
      color: $text-primary;
      font-size: 1.75rem;
      margin-bottom: 0.5rem;
    }
    
    p {
      color: $text-tertiary;
      font-size: 0.875rem;
    }
  }
}

.form-content {
  .form-item {
    margin-bottom: 1.5rem;
    
    label {
      display: block;
      color: $text-secondary;
      margin-bottom: 0.5rem;
      font-size: 0.875rem;
      font-weight: 500;
    }
  }
  
  .form-actions {
    display: flex;
    gap: 1rem;
    margin-top: 2rem;
    
    .btn-login {
      flex: 1;
    }
  }
}

// 数据卡片网格
.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
}

.data-card {
  padding: 1.5rem;
  display: flex;
  gap: 1rem;
  align-items: flex-start;
  
  .card-icon {
    width: 50px;
    height: 50px;
    border-radius: $radius-lg;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.5rem;
    flex-shrink: 0;
  }
  
  .card-info {
    flex: 1;
    
    h4 {
      color: $text-secondary;
      font-size: 0.875rem;
      margin-bottom: 0.25rem;
    }
    
    .card-value {
      color: $text-primary;
      font-size: 1.5rem;
      font-weight: 700;
      margin-bottom: 0.25rem;
    }
    
    .card-desc {
      color: $text-tertiary;
      font-size: 0.75rem;
    }
  }
}

// 用户列表
.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  
  h3 {
    color: $text-primary;
    margin: 0;
  }
  
  .header-actions {
    display: flex;
    gap: 1rem;
    
    .search-input {
      width: 250px;
    }
  }
}

.user-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.user-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.25rem;
  background: rgba(102, 103, 171, 0.2);
  border-radius: $radius-lg;
  transition: all $duration-base $ease-out;
  
  &:hover {
    background: rgba(102, 103, 171, 0.3);
    transform: translateX(4px);
  }
}

.user-info {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex: 1;
  
  .user-avatar {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background: linear-gradient(135deg, rgba(244, 253, 175, 0.3), rgba(239, 221, 141, 0.2));
    display: flex;
    align-items: center;
    justify-content: center;
    color: $text-primary;
    font-weight: 600;
    font-size: 1rem;
  }
  
  .user-name {
    color: $text-secondary;
    font-weight: 500;
    margin: 0 0 0.25rem 0;
  }
  
  .user-email {
    color: $text-tertiary;
    font-size: 0.75rem;
    margin: 0;
  }
}

.user-status {
  margin: 0 1.5rem;
}

.user-actions {
  display: flex;
  gap: 0.5rem;
}

// 统计卡片
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
}

.stat-card {
  padding: 1.5rem;
  
  .stat-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
    
    .stat-label {
      color: $text-secondary;
      font-size: 0.875rem;
    }
  }
  
  .stat-value {
    color: $text-primary;
    font-size: 2.5rem;
    font-weight: 700;
    margin-bottom: 0.5rem;
  }
  
  .stat-change {
    font-size: 0.875rem;
    font-weight: 500;
    
    &.positive {
      color: lighten($color-success, 10%);
    }
    
    &.negative {
      color: $text-accent-warm;
    }
  }
}

// 通知列表
.notification-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.notification-item {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  padding: 1.25rem;
  background: rgba(102, 103, 171, 0.2);
  border-radius: $radius-lg;
  border-left: 3px solid transparent;
  transition: all $duration-base $ease-out;
  
  &:hover {
    background: rgba(102, 103, 171, 0.3);
  }
  
  &.success {
    border-left-color: $color-success;
  }
  
  &.info {
    border-left-color: $color-info;
  }
  
  &.warning {
    border-left-color: $color-warning;
  }
  
  &.danger {
    border-left-color: $color-danger;
  }
  
  .notif-icon {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    background: rgba(244, 253, 175, 0.2);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.25rem;
    flex-shrink: 0;
  }
  
  .notif-content {
    flex: 1;
    
    h4 {
      color: $text-primary;
      margin: 0 0 0.25rem 0;
      font-size: 1rem;
    }
    
    p {
      color: $text-secondary;
      margin: 0;
      font-size: 0.875rem;
    }
  }
}

// 响应式
@media (max-width: 768px) {
  .demo-page {
    padding: 1rem;
  }
  
  .card-grid,
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .user-row {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
  
  .user-status,
  .user-actions {
    width: 100%;
    justify-content: space-between;
  }
  
  .table-header {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
    
    .header-actions {
      flex-direction: column;
      
      .search-input {
        width: 100%;
      }
    }
  }
}
</style>
