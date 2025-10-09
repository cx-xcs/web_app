<template>
  <n-card>
    <n-grid :cols="2" :x-gap="12">
      <!-- 最新数据展示 -->
      <n-gi>
        <n-card title="实时数据">
          <template #header-extra>
            上次更新: {{ latestData?.timestamp || '-' }}
          </template>
          <n-statistic v-if="latestData"
            :value="latestData.value"
            :precision="2">
            <template #prefix>
              当前值：
            </template>
          </n-statistic>
          <n-empty v-else description="暂无数据" />
        </n-card>
      </n-gi>

      <!-- 图表展示 -->
      <n-gi>
        <n-card title="历史趋势">
          <div ref="chartRef" style="width: 100%; height: 300px;"></div>
        </n-card>
      </n-gi>
    </n-grid>
  </n-card>
</template>

<script src="./DataDisplay.js"></script>

<style scoped>
.echarts {
  width: 100%;
  height: 100%;
  min-height: 300px;
}
</style>
