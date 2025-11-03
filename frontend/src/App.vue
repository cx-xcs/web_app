<template>
  <n-message-provider>
    <n-config-provider>
      <n-layout has-sider style="height: 100vh;">
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
          <div class="logo" :class="{ collapsed }">
            <h3 v-if="!collapsed">物联网监控</h3>
            <span v-else>IoT</span>
          </div>
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
          <n-layout-header bordered style="height: 64px; padding: 0 24px; display: flex; align-items: center;">
            <h2 style="margin: 0;">LoRaWAN 数据监控平台</h2>
          </n-layout-header>

          <n-layout-content content-style="padding: 24px; overflow: auto;">
            <router-view></router-view>
          </n-layout-content>
        </n-layout>
      </n-layout>
    </n-config-provider>
  </n-message-provider>
</template>

<script setup>
import { ref, h } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { 
  NConfigProvider, 
  NMessageProvider,
  NLayout, 
  NLayoutSider, 
  NLayoutHeader, 
  NLayoutContent, 
  NMenu,
  NIcon
} from 'naive-ui'
import { 
  DashboardOutlined, 
  AppstoreOutlined 
} from '@vicons/antd'

const router = useRouter()
const collapsed = ref(false)
const activeKey = ref('dashboard')

const renderIcon = (icon) => {
  return () => h(NIcon, null, { default: () => h(icon) })
}

const menuOptions = [
  {
    label: () => h(
      RouterLink,
      { to: '/' },
      { default: () => '设备监控' }
    ),
    key: 'dashboard',
    icon: renderIcon(DashboardOutlined)
  }
]
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body {
  height: 100%;
  width: 100%;
}

#app {
  height: 100%;
}

.logo {
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-bottom: 1px solid #e8e8e8;
  font-weight: bold;
  transition: all 0.3s;
}

.logo.collapsed {
  font-size: 18px;
}

.logo h3 {
  margin: 0;
  font-size: 18px;
}
</style>
