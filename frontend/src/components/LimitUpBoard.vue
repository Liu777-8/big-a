<template>
  <div class="limit-up-board">
    <el-card class="board-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span class="header-title">涨跌停股票池</span>
          <div class="header-controls">
            <el-date-picker
              v-model="selectedDate"
              type="date"
              placeholder="选择日期"
              format="YYYY-MM-DD"
              value-format="YYYYMMDD"
              size="default"
              style="width: 180px; margin-right: 12px"
              @change="fetchData"
            />
            <el-button
              type="primary"
              :icon="Refresh"
              @click="fetchData"
              :loading="loading"
              size="default"
            >
              刷新数据
            </el-button>
            <el-button
              type="success"
              :icon="Download"
              @click="downloadData"
              :loading="loading"
              size="default"
              style="margin-left: 12px"
            >
              下载数据
            </el-button>
          </div>
        </div>
      </template>

      <!-- Tab切换 -->
      <el-tabs v-model="activeTab" @tab-change="handleTabChange">
        <!-- 涨停股票池 -->
        <el-tab-pane label="涨停股票池" name="limitUp">
          <!-- 加载状态 -->
          <div v-if="loading" class="loading-container">
            <el-skeleton :rows="10" animated />
          </div>

          <!-- 数据统计 -->
          <div v-if="!loading && limitUpData.length > 0" class="stats-bar">
            <div class="stats-left">
              <el-tag type="success" size="large">
                共 {{ filteredLimitUpData.length }} 只股票涨停
              </el-tag>
              <el-checkbox
                v-model="filter30"
                label="过滤30开头股票"
                size="large"
                style="margin-left: 15px"
              />
            </div>
            <div class="time-info">
              <span class="trade-date">交易日期：{{ tradeDate }}</span>
              <span class="update-time">更新时间：{{ updateTime }}</span>
            </div>
          </div>

          <!-- 涨停股票表格 -->
          <el-table
            v-if="!loading && limitUpData.length > 0"
            :data="filteredLimitUpData"
            stripe
            border
            height="600"
            style="width: 100%; margin-top: 20px"
          >
            <el-table-column type="index" label="序号" width="60" fixed />
            <el-table-column prop="代码" label="股票代码" width="100" fixed />
            <el-table-column prop="名称" label="股票名称" width="100" fixed />
            <el-table-column
              prop="涨跌幅"
              label="涨跌幅(%)"
              width="100"
              sortable
            >
              <template #default="{ row }">
                <span :class="getPriceClass(row.涨跌幅)">
                  {{ row.涨跌幅 }}%
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="最新价" label="最新价" width="100" />
            <el-table-column prop="涨停价" label="涨停价" width="100" />
            <el-table-column prop="成交额" label="成交额" width="120" />
            <el-table-column prop="流通市值" label="流通市值" width="120" />
            <el-table-column prop="总市值" label="总市值" width="120" />
            <el-table-column prop="换手率" label="换手率(%)" width="100" />
            <el-table-column prop="涨停统计" label="涨停统计" width="120">
              <template #default="{ row }">
                {{ row.涨停统计 ? row.涨停统计 + "次" : "-" }}
              </template>
            </el-table-column>
            <el-table-column prop="连板数" label="连板数" width="100" />
            <el-table-column
              prop="首次封板时间"
              label="首次封板时间"
              width="120"
            />
            <el-table-column
              prop="最后封板时间"
              label="最后封板时间"
              width="120"
            />
            <el-table-column prop="炸板次数" label="炸板次数" width="100" />
            <el-table-column prop="涨停开板" label="涨停开板" width="100" />
            <el-table-column prop="所属行业" label="所属行业" width="120" />
          </el-table>

          <!-- 空状态 -->
          <el-empty
            v-if="!loading && limitUpData.length === 0"
            description="暂无涨停数据"
            :image-size="150"
          />
        </el-tab-pane>

        <!-- 跌停股票池 -->
        <el-tab-pane label="跌停股票池" name="limitDown">
          <!-- 加载状态 -->
          <div v-if="loading" class="loading-container">
            <el-skeleton :rows="10" animated />
          </div>

          <!-- 数据统计 -->
          <div v-if="!loading && limitDownData.length > 0" class="stats-bar">
            <div class="stats-left">
              <el-tag type="danger" size="large">
                共 {{ filteredLimitDownData.length }} 只股票跌停
              </el-tag>
              <el-checkbox
                v-model="filter30LimitDown"
                label="过滤30开头股票"
                size="large"
                style="margin-left: 15px"
              />
            </div>
            <div class="time-info">
              <span class="trade-date">交易日期：{{ tradeDateLimitDown }}</span>
              <span class="update-time"
                >更新时间：{{ updateTimeLimitDown }}</span
              >
            </div>
          </div>

          <!-- 跌停股票表格 -->
          <el-table
            v-if="!loading && limitDownData.length > 0"
            :data="filteredLimitDownData"
            stripe
            border
            height="600"
            style="width: 100%; margin-top: 20px"
          >
            <el-table-column type="index" label="序号" width="60" fixed />
            <el-table-column prop="代码" label="股票代码" width="100" fixed />
            <el-table-column prop="名称" label="股票名称" width="100" fixed />
            <el-table-column
              prop="涨跌幅"
              label="涨跌幅(%)"
              width="100"
              sortable
            >
              <template #default="{ row }">
                <span :class="getPriceClass(row.涨跌幅)">
                  {{ row.涨跌幅 }}%
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="最新价" label="最新价" width="100" />
            <el-table-column prop="跌停价" label="跌停价" width="100" />
            <el-table-column prop="成交额" label="成交额" width="120" />
            <el-table-column prop="流通市值" label="流通市值" width="120" />
            <el-table-column prop="总市值" label="总市值" width="120" />
            <el-table-column prop="换手率" label="换手率(%)" width="100" />
            <el-table-column prop="所属行业" label="所属行业" width="120" />
          </el-table>

          <!-- 空状态 -->
          <el-empty
            v-if="!loading && limitDownData.length === 0"
            description="暂无跌停数据"
            :image-size="150"
          />
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed } from "vue";
import { ElMessage } from "element-plus";
import { Refresh, Download } from "@element-plus/icons-vue";
import axios from "axios";

const activeTab = ref("limitUp"); // 当前激活的tab
const limitUpData = ref([]);
const limitDownData = ref([]);
const loading = ref(false);
const updateTime = ref("");
const tradeDate = ref("");
const updateTimeLimitDown = ref("");
const tradeDateLimitDown = ref("");
const filter30 = ref(false); // 过滤30开头股票的开关（涨停）
const filter30LimitDown = ref(false); // 过滤30开头股票的开关（跌停）

// 日期选择器，默认今天
const selectedDate = ref(
  new Date().toISOString().split("T")[0].replace(/-/g, "")
);

// 过滤后的涨停数据
const filteredLimitUpData = computed(() => {
  if (!filter30.value) {
    return limitUpData.value;
  }
  return limitUpData.value.filter((item) => {
    const code = String(item.代码 || "");
    return !code.startsWith("30");
  });
});

// 过滤后的跌停数据
const filteredLimitDownData = computed(() => {
  if (!filter30LimitDown.value) {
    return limitDownData.value;
  }
  return limitDownData.value.filter((item) => {
    const code = String(item.代码 || "");
    return !code.startsWith("30");
  });
});

// Tab切换处理
const handleTabChange = (tabName) => {
  fetchData();
};

// 获取数据
const fetchData = async () => {
  loading.value = true;

  try {
    const params = selectedDate.value ? { date: selectedDate.value } : {};

    if (activeTab.value === "limitUp") {
      // 获取涨停数据
      const response = await axios.get("/api/stock/limit-up/previous", {
        params,
      });

      if (response.data.success) {
        limitUpData.value = response.data.data;
        updateTime.value = response.data.timestamp;
        tradeDate.value = response.data.display_date || response.data.date;
        ElMessage.success(`加载成功，共 ${response.data.count} 只涨停股票`);
      } else {
        ElMessage.error(response.data.message || "加载失败");
      }
    } else {
      // 获取跌停数据
      const response = await axios.get("/api/stock/limit-down", {
        params,
      });

      if (response.data.success) {
        limitDownData.value = response.data.data;
        updateTimeLimitDown.value = response.data.timestamp;
        tradeDateLimitDown.value =
          response.data.display_date || response.data.date;
        ElMessage.success(`加载成功，共 ${response.data.count} 只跌停股票`);
      } else {
        ElMessage.error(response.data.message || "加载失败");
      }
    }
  } catch (error) {
    console.error("获取数据失败:", error);
    ElMessage.error(
      error.response?.data?.message || "获取数据失败，请稍后重试"
    );
  } finally {
    loading.value = false;
  }
};

// 下载数据
const downloadData = async () => {
  try {
    const params = selectedDate.value ? { date: selectedDate.value } : {};
    const endpoint =
      activeTab.value === "limitUp"
        ? "/api/stock/download-limit-up"
        : "/api/stock/download-limit-down";
    const type = activeTab.value === "limitUp" ? "涨停" : "跌停";

    ElMessage.info(`正在生成${type}股票池Excel文件...`);

    const response = await axios.get(endpoint, {
      params,
      responseType: "blob",
    });

    // 创建下载链接
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement("a");
    link.href = url;

    const today = new Date().toISOString().split("T")[0].replace(/-/g, "");
    const dateStr = selectedDate.value || today;
    let filename = `${type}股票池_${dateStr}.xlsx`;

    link.setAttribute("download", filename);
    document.body.appendChild(link);
    link.click();

    // 清理
    link.remove();
    window.URL.revokeObjectURL(url);

    ElMessage.success("Excel文件下载成功");
  } catch (error) {
    console.error("下载失败:", error);
    ElMessage.error(error.response?.data?.message || "下载失败，请稍后重试");
  }
};

// 判断涨跌颜色
const getPriceClass = (changePercent) => {
  if (!changePercent) return "";
  const value = parseFloat(changePercent);
  if (value > 0) return "price-up";
  if (value < 0) return "price-down";
  return "";
};

// 暴露fetchData方法给父组件调用
defineExpose({
  fetchData,
});
</script>

<style scoped>
.limit-up-board {
  width: 100%;
  max-width: 1600px;
}

.board-card {
  background: linear-gradient(
    135deg,
    rgba(255, 255, 255, 0.98) 0%,
    rgba(255, 255, 255, 0.95) 100%
  );
  border-radius: 16px;
  border: 1px solid rgba(102, 126, 234, 0.1);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
}

.board-card:hover {
  box-shadow: 0 12px 48px rgba(102, 126, 234, 0.15);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
}

.header-title {
  font-size: 22px;
  font-weight: 700;
  background: linear-gradient(135deg, #67c23a 0%, #409eff 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.header-controls {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-controls .el-button {
  font-size: 14px;
  font-weight: 600;
  padding: 10px 20px;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.header-controls .el-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.header-controls .el-date-picker {
  font-size: 14px;
}

:deep(.header-controls .el-input__wrapper) {
  padding: 8px 12px;
  font-size: 14px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

:deep(.header-controls .el-input__inner) {
  font-size: 14px;
  color: #303133;
  font-weight: 500;
}

.loading-container {
  padding: 20px;
}

.stats-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
}

.stats-left {
  display: flex;
  align-items: center;
}

.time-info {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.trade-date {
  color: #409eff;
  font-size: 15px;
  font-weight: 600;
  margin-bottom: 5px;
}

.update-time {
  color: #909399;
  font-size: 13px;
}

.price-up {
  color: #f56c6c;
  font-weight: 600;
}

.price-down {
  color: #67c23a;
  font-weight: 600;
}

:deep(.el-table) {
  font-size: 13px;
}

:deep(.el-table th) {
  background-color: #f5f7fa;
  font-weight: 600;
}

:deep(.el-table .cell) {
  padding: 8px 0;
}
</style>
