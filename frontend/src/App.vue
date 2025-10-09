<template>
  <n-config-provider :theme="darkTheme">
    <n-layout has-sider>
      <!-- 侧边栏 -->
      <n-layout-sider
        bordered
        collapse-mode="width"
        :collapsed-width="64"
        :width="240"
        show-trigger
        @collapse="collapsed = true"
        @expand="collapsed = false"
      >
        <n-menu
          v-model:value="activeKey"
          :collapsed="collapsed"
          :collapsed-width="64"
          :collapsed-icon-size="22"
          :options="menuOptions"
        />
      </n-layout-sider>

      <!-- 主内容区 -->
      <n-layout>
        <n-layout-header bordered>
          <div class="header-content">
            <h2>LoRaWAN Web Dashboard</h2>
          </div>
        </n-layout-header>

        <n-layout-content content-style="padding: 24px;">
          <router-view></router-view>
        </n-layout-content>
      </n-layout>
    </n-layout>
  </n-config-provider>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { 
  NConfigProvider, 
  NLayout, 
  NLayoutSider, 
  NLayoutHeader, 
  NLayoutContent, 
  NMenu 
} from 'naive-ui'
import { darkTheme } from 'naive-ui'

const router = useRouter()
const collapsed = ref(false)
const activeKey = ref('dashboard')

const menuOptions = [
  {
    label: 'Dashboard',
    key: 'dashboard',
    onClick: () => router.push('/')
  },
  {
    label: 'Device Management',
    key: 'devices',
    onClick: () => router.push('/devices')
  },
  {
    label: 'Historical Data',
    key: 'history',
    onClick: () => router.push('/history')
  }
]
</script>

<style>
html, body {
  margin: 0;
  padding: 0;
  height: 100vh;
  width: 100vw;
}

#app {
  height: 100vh;
}

.header-content {
  padding: 16px 24px;
  display: flex;
  align-items: center;
}

.header-content h2 {
  margin: 0;
}
</style>
