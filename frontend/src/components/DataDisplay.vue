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

<script>
import { defineComponent, ref, onMounted, onUnmounted } from 'vue'
import { api } from '../api'
import { useMessage } from 'naive-ui'
import * as echarts from 'echarts'

export default defineComponent({
    name: 'DataDisplay',
    setup() {
        const latestData = ref(null)
        const chartRef = ref(null)
        const message = useMessage()
        let chart = null
        let updateTimer = null

        // 获取最新数据
        const fetchLatestData = async () => {
            try {
                const data = await api.getLatestData()
                latestData.value = data
            } catch (error) {
                message.error('获取最新数据失败')
            }
        }

        // 初始化图表
        const initChart = () => {
            if (chartRef.value) {
                chart = echarts.init(chartRef.value)
            }
        }

        // 更新历史数据图表
        const updateHistoricalChart = async () => {
            try {
                const data = await api.getHistoricalData()
                if (chart) {
                    // 假设数据格式为 [{ timestamp: string, value: number }]
                    const option = {
                        title: {
                            text: '历史数据 (最近3天)'
                        },
                        tooltip: {
                            trigger: 'axis'
                        },
                        xAxis: {
                            type: 'time',
                            axisLabel: {
                                formatter: '{yyyy-MM-dd HH:mm}'
                            }
                        },
                        yAxis: {
                            type: 'value'
                        },
                        series: [{
                            name: '传感器数据',
                            type: 'line',
                            data: data.map(item => ([
                                item.timestamp,
                                item.value
                            ]))
                        }]
                    }
                    chart.setOption(option)
                }
            } catch (error) {
                message.error('获取历史数据失败')
            }
        }

        // 组件挂载时
        onMounted(() => {
            initChart()
            fetchLatestData()
            updateHistoricalChart()
            // 每30秒更新一次最新数据
            updateTimer = setInterval(() => {
                fetchLatestData()
            }, 30000)
        })

        // 组件卸载时
        onUnmounted(() => {
            if (updateTimer) {
                clearInterval(updateTimer)
            }
            if (chart) {
                chart.dispose()
            }
        })

        return {
            latestData,
            chartRef
        }
    }
})
</script>

<style scoped>
.echarts {
  width: 100%;
  height: 100%;
  min-height: 300px;
}
</style>