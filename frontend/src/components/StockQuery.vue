<template>
  <div class="stock-query">
    <el-card class="query-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>个股信息查询</span>
        </div>
      </template>

      <!-- 查询表单 -->
      <el-form :model="form" label-width="100px" @submit.prevent>
        <el-form-item label="股票代码">
          <el-input
            v-model="form.stockCode"
            placeholder="请输入股票代码，如：600000"
            clearable
            @keyup.enter="queryStock"
          >
            <template #append>
              <el-button
                type="primary"
                :icon="Search"
                @click="queryStock"
                :loading="loading"
              >
                查询
              </el-button>
            </template>
          </el-input>
        </el-form-item>

        <!-- 自动刷新控制 -->
        <el-form-item label="自动刷新" v-if="basicInfo">
          <el-switch
            v-model="autoRefresh"
            @change="toggleAutoRefresh"
            active-text="开启（每5分钟）"
            inactive-text="关闭"
          />
          <span v-if="autoRefresh" class="refresh-countdown">
            距离下次刷新：{{ countdown }}秒
          </span>
          <el-button
            type="success"
            :icon="Download"
            @click="downloadExcel(7)"
            style="margin-left: 20px"
          >
            下载近一周数据
          </el-button>
          <el-button type="primary" :icon="Download" @click="downloadExcel(30)">
            下载近一个月数据
          </el-button>
        </el-form-item>
      </el-form>

      <!-- 查询历史 -->
      <div v-if="queryHistory.length > 0" class="query-history-section">
        <div class="history-header">
          <div class="history-title">
            <el-icon class="clock-icon"><Clock /></el-icon>
            <span>最近查询</span>
          </div>
          <el-button
            type="danger"
            size="small"
            text
            @click="clearHistory"
            class="clear-btn"
          >
            <el-icon><Delete /></el-icon>
            清空
          </el-button>
        </div>
        <div class="history-list">
          <div
            v-for="item in queryHistory"
            :key="item.code"
            :class="['history-item', { active: form.stockCode === item.code }]"
            @click="selectFromHistory(item)"
          >
            <div class="stock-info-badge">
              <div class="stock-name">{{ item.name }}</div>
              <div class="stock-code">{{ item.code }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 加载骨架屏 -->
      <div v-if="loading" class="loading-skeleton">
        <el-skeleton :rows="8" animated />
      </div>

      <!-- 查询结果 - 基本信息 -->
      <div v-if="basicInfo && !loading" class="result-area">
        <el-divider content-position="left">
          <el-tag type="success" size="large">基本信息</el-tag>
        </el-divider>

        <div class="stock-info">
          <el-descriptions :column="2" border>
            <el-descriptions-item
              v-for="(value, key) in basicInfo"
              :key="key"
              :label="key"
            >
              {{ value }}
            </el-descriptions-item>
          </el-descriptions>
        </div>
      </div>

      <!-- 实时数据 -->
      <div v-if="realtimeData && !loading" class="result-area">
        <el-divider content-position="left">
          <el-tag type="warning" size="large">实时行情数据</el-tag>
        </el-divider>

        <!-- 查询时间显示 -->
        <div class="query-time-info" v-if="queryTime">
          <el-icon class="clock-icon"><Clock /></el-icon>
          <span>查询时间：{{ queryTime }}</span>
        </div>

        <div class="realtime-data">
          <!-- 核心指标卡片 -->
          <el-row :gutter="20" class="key-metrics">
            <el-col :span="6">
              <el-card shadow="hover" class="metric-card">
                <div class="metric-label">股票代码</div>
                <div class="metric-value">
                  {{ realtimeData["代码"] || "-" }}
                </div>
              </el-card>
            </el-col>
            <el-col :span="6">
              <el-card shadow="hover" class="metric-card">
                <div class="metric-label">股票名称</div>
                <div class="metric-value">
                  {{ realtimeData["名称"] || "-" }}
                </div>
              </el-card>
            </el-col>
            <el-col :span="6">
              <el-card shadow="hover" class="metric-card price-card">
                <div class="metric-label">最新价</div>
                <div
                  class="metric-value price"
                  :class="getPriceClass(realtimeData['涨跌幅'])"
                >
                  {{ realtimeData["最新价"] || "-" }}
                </div>
              </el-card>
            </el-col>
            <el-col :span="6">
              <el-card shadow="hover" class="metric-card">
                <div class="metric-label">涨跌幅</div>
                <div
                  class="metric-value"
                  :class="getPriceClass(realtimeData['涨跌幅'])"
                >
                  {{ realtimeData["涨跌幅"] }}%
                </div>
              </el-card>
            </el-col>
          </el-row>

          <!-- 详细数据表格 -->
          <el-descriptions :column="3" border class="realtime-details">
            <el-descriptions-item label="涨跌额">{{
              realtimeData["涨跌额"] || "-"
            }}</el-descriptions-item>
            <el-descriptions-item label="成交量">{{
              realtimeData["成交量"] || "-"
            }}</el-descriptions-item>
            <el-descriptions-item label="成交额">{{
              realtimeData["成交额"] || "-"
            }}</el-descriptions-item>
            <el-descriptions-item label="振幅"
              >{{ realtimeData["振幅"] || "-" }}%</el-descriptions-item
            >
            <el-descriptions-item label="换手率"
              >{{ realtimeData["换手率"] || "-" }}%</el-descriptions-item
            >
            <el-descriptions-item label="市盈率">{{
              realtimeData["市盈率-动态"] || "-"
            }}</el-descriptions-item>
            <el-descriptions-item label="最高">{{
              realtimeData["最高"] || "-"
            }}</el-descriptions-item>
            <el-descriptions-item label="最低">{{
              realtimeData["最低"] || "-"
            }}</el-descriptions-item>
            <el-descriptions-item label="今开">{{
              realtimeData["今开"] || "-"
            }}</el-descriptions-item>
            <el-descriptions-item label="昨收">{{
              realtimeData["昨收"] || "-"
            }}</el-descriptions-item>
            <el-descriptions-item label="量比">{{
              realtimeData["量比"] || "-"
            }}</el-descriptions-item>
            <el-descriptions-item label="市净率">{{
              realtimeData["市净率"] || "-"
            }}</el-descriptions-item>
            <el-descriptions-item label="总市值">{{
              realtimeData["总市值"] || "-"
            }}</el-descriptions-item>
            <el-descriptions-item label="流通市值">{{
              realtimeData["流通市值"] || "-"
            }}</el-descriptions-item>
            <el-descriptions-item label="60日涨跌幅"
              >{{ realtimeData["60日涨跌幅"] || "-" }}%</el-descriptions-item
            >
            <el-descriptions-item label="年初至今涨跌幅"
              >{{
                realtimeData["年初至今涨跌幅"] || "-"
              }}%</el-descriptions-item
            >
          </el-descriptions>
        </div>
      </div>

      <!-- 历史数据查询区域 -->
      <div v-if="basicInfo && !loading" class="history-query-area">
        <el-divider content-position="left">
          <el-tag type="info" size="large">历史数据查询</el-tag>
        </el-divider>

        <el-form :model="historyForm" label-width="100px" @submit.prevent>
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="开始日期">
                <el-date-picker
                  v-model="historyForm.startDate"
                  type="date"
                  placeholder="选择开始日期"
                  format="YYYY-MM-DD"
                  value-format="YYYYMMDD"
                  style="width: 100%"
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="结束日期">
                <el-date-picker
                  v-model="historyForm.endDate"
                  type="date"
                  placeholder="选择结束日期"
                  format="YYYY-MM-DD"
                  value-format="YYYYMMDD"
                  style="width: 100%"
                />
              </el-form-item>
            </el-col>
          </el-row>

          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="周期">
                <el-select
                  v-model="historyForm.period"
                  placeholder="选择周期"
                  style="width: 100%"
                >
                  <el-option label="日线" value="daily" />
                  <el-option label="周线" value="weekly" />
                  <el-option label="月线" value="monthly" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="复权类型">
                <el-select
                  v-model="historyForm.adjust"
                  placeholder="选择复权类型"
                  style="width: 100%"
                >
                  <el-option label="不复权" value="" />
                  <el-option label="前复权" value="qfq" />
                  <el-option label="后复权" value="hfq" />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>

          <el-form-item>
            <el-button
              type="primary"
              @click="queryHistoryData"
              :loading="historyLoading"
              :icon="Search"
            >
              查询历史数据
            </el-button>
          </el-form-item>
        </el-form>

        <!-- 历史数据表格 -->
        <div v-if="historyData && historyData.length > 0" class="history-table">
          <el-table
            :data="historyData"
            stripe
            border
            max-height="400"
            style="width: 100%"
          >
            <el-table-column prop="日期" label="日期" width="120" fixed />
            <el-table-column prop="开盘" label="开盘" width="100" />
            <el-table-column prop="收盘" label="收盘" width="100" />
            <el-table-column prop="最高" label="最高" width="100" />
            <el-table-column prop="最低" label="最低" width="100" />
            <el-table-column prop="成交量" label="成交量" width="120" />
            <el-table-column prop="成交额" label="成交额" width="120" />
            <el-table-column prop="振幅" label="振幅" width="100" />
            <el-table-column prop="涨跌幅" label="涨跌幅" width="100" />
            <el-table-column prop="涨跌额" label="涨跌额" width="100" />
            <el-table-column prop="换手率" label="换手率" width="100" />
          </el-table>

          <div class="table-footer">
            <el-tag>共 {{ historyData.length }} 条数据</el-tag>
          </div>
        </div>
      </div>

      <!-- 空状态 -->
      <el-empty
        v-if="!basicInfo && !loading"
        description="请输入股票代码进行查询"
        :image-size="150"
      />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onUnmounted, onMounted } from "vue";
import { ElMessage } from "element-plus";
import { Search, Download, Clock, Delete } from "@element-plus/icons-vue";
import axios from "axios";

const form = ref({
  stockCode: "",
});

const basicInfo = ref(null);
const realtimeData = ref(null);
const loading = ref(false);
const queryTime = ref(""); // 查询时间

// 查询历史记录
const queryHistory = ref([]);
const MAX_HISTORY = 10; // 最多保存10条历史记录

// 自动刷新相关
const autoRefresh = ref(false);
const countdown = ref(300); // 5分钟 = 300秒
let refreshTimer = null;
let countdownTimer = null;

// 历史数据相关
const historyForm = ref({
  startDate: "20240101",
  endDate: "20241231",
  period: "daily",
  adjust: "",
});

const historyData = ref(null);
const historyLoading = ref(false);

// 查询股票基本信息和实时数据
const queryStock = async () => {
  if (!form.value.stockCode) {
    ElMessage.warning("请输入股票代码");
    return;
  }

  loading.value = true;
  basicInfo.value = null;
  realtimeData.value = null;
  historyData.value = null;

  try {
    const response = await axios.get(`/api/stock/info/${form.value.stockCode}`);

    if (response.data.success) {
      basicInfo.value = response.data.data.basic_info;
      realtimeData.value = response.data.data.realtime_data;

      // 记录查询时间
      const now = new Date();
      queryTime.value = `${now.getFullYear()}年${String(
        now.getMonth() + 1
      ).padStart(2, "0")}月${String(now.getDate()).padStart(2, "0")}日 ${String(
        now.getHours()
      ).padStart(2, "0")}:${String(now.getMinutes()).padStart(2, "0")}:${String(
        now.getSeconds()
      ).padStart(2, "0")}`;

      // 保存到查询历史
      saveToHistory({
        code: form.value.stockCode,
        name:
          realtimeData.value?.名称 ||
          basicInfo.value?.股票简称 ||
          form.value.stockCode,
      });

      ElMessage.success("查询成功");

      // 设置默认的历史数据查询日期
      const today = new Date();
      const lastYear = new Date();
      lastYear.setFullYear(today.getFullYear() - 1);

      historyForm.value.endDate = formatDate(today);
      historyForm.value.startDate = formatDate(lastYear);
    } else {
      ElMessage.error(response.data.message || "查询失败");
    }
  } catch (error) {
    console.error("查询失败:", error);
    ElMessage.error(
      error.response?.data?.message || "查询失败，请检查股票代码是否正确"
    );
  } finally {
    loading.value = false;
  }
};

// 查询历史数据
const queryHistoryData = async () => {
  if (!form.value.stockCode) {
    ElMessage.warning("请先查询股票信息");
    return;
  }

  if (!historyForm.value.startDate || !historyForm.value.endDate) {
    ElMessage.warning("请选择开始和结束日期");
    return;
  }

  historyLoading.value = true;

  try {
    const response = await axios.get(
      `/api/stock/history/${form.value.stockCode}`,
      {
        params: {
          start_date: historyForm.value.startDate,
          end_date: historyForm.value.endDate,
          period: historyForm.value.period,
          adjust: historyForm.value.adjust,
        },
      }
    );

    if (response.data.success) {
      historyData.value = response.data.data;
      ElMessage.success(`查询成功，共 ${response.data.count} 条数据`);
    } else {
      ElMessage.error(response.data.message || "查询失败");
    }
  } catch (error) {
    console.error("历史数据查询失败:", error);
    ElMessage.error(error.response?.data?.message || "历史数据查询失败");
  } finally {
    historyLoading.value = false;
  }
};

// 格式化日期
const formatDate = (date) => {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return `${year}${month}${day}`;
};

// 判断涨跌颜色
const getPriceClass = (changePercent) => {
  if (!changePercent) return "";
  const value = parseFloat(changePercent);
  if (value > 0) return "price-up";
  if (value < 0) return "price-down";
  return "";
};

// 自动刷新功能
const toggleAutoRefresh = (value) => {
  if (value) {
    startAutoRefresh();
    ElMessage.success("已开启自动刷新（每5分钟）");
  } else {
    stopAutoRefresh();
    ElMessage.info("已关闭自动刷新");
  }
};

// 启动自动刷新
const startAutoRefresh = () => {
  countdown.value = 300;

  // 倒计时
  countdownTimer = setInterval(() => {
    countdown.value--;
    if (countdown.value <= 0) {
      countdown.value = 300;
    }
  }, 1000);

  // 定时刷新
  refreshTimer = setInterval(() => {
    if (form.value.stockCode) {
      refreshStockData();
    }
  }, 300000); // 5分钟 = 300000毫秒
};

// 停止自动刷新
const stopAutoRefresh = () => {
  if (refreshTimer) {
    clearInterval(refreshTimer);
    refreshTimer = null;
  }
  if (countdownTimer) {
    clearInterval(countdownTimer);
    countdownTimer = null;
  }
  countdown.value = 300;
};

// 刷新股票数据（不显示成功提示）
const refreshStockData = async () => {
  if (!form.value.stockCode) return;

  try {
    const response = await axios.get(`/api/stock/info/${form.value.stockCode}`);

    if (response.data.success) {
      basicInfo.value = response.data.data.basic_info;
      realtimeData.value = response.data.data.realtime_data;

      // 更新查询时间
      const now = new Date();
      queryTime.value = `${now.getFullYear()}年${String(
        now.getMonth() + 1
      ).padStart(2, "0")}月${String(now.getDate()).padStart(2, "0")}日 ${String(
        now.getHours()
      ).padStart(2, "0")}:${String(now.getMinutes()).padStart(2, "0")}:${String(
        now.getSeconds()
      ).padStart(2, "0")}`;

      console.log("数据已自动刷新", new Date().toLocaleTimeString());
    }
  } catch (error) {
    console.error("自动刷新失败:", error);
  }
};

// 从历史记录中选择
const selectFromHistory = (item) => {
  form.value.stockCode = item.code;
  queryStock();
};

// 保存到历史记录
const saveToHistory = (item) => {
  // 移除重复项
  const filtered = queryHistory.value.filter((h) => h.code !== item.code);
  // 添加到开头
  queryHistory.value = [item, ...filtered].slice(0, MAX_HISTORY);
  // 保存到 localStorage
  localStorage.setItem("stockQueryHistory", JSON.stringify(queryHistory.value));
};

// 清除历史记录
const clearHistory = () => {
  queryHistory.value = [];
  localStorage.removeItem("stockQueryHistory");
  ElMessage.success("历史记录已清除");
};

// 从 localStorage 加载历史记录
const loadHistory = () => {
  try {
    const saved = localStorage.getItem("stockQueryHistory");
    if (saved) {
      queryHistory.value = JSON.parse(saved);
    }
  } catch (error) {
    console.error("加载历史记录失败:", error);
  }
};

// 组件挂载时加载历史记录
onMounted(() => {
  loadHistory();
});

// 组件卸载时清理定时器
onUnmounted(() => {
  stopAutoRefresh();
});

// 下载Excel文件
const downloadExcel = async (days = 7) => {
  if (!form.value.stockCode) {
    ElMessage.warning("请先查询股票信息");
    return;
  }

  try {
    const periodText =
      days <= 31 ? `近${days}天` : `近${Math.floor(days / 30)}个月`;
    ElMessage.info(`正在生成${periodText}Excel文件...`);

    // 添加查询时间参数
    const response = await axios.get(
      `/api/stock/download/${form.value.stockCode}`,
      {
        params: {
          days,
          query_time: queryTime.value, // 传递查询时间
        },
        responseType: "blob",
      }
    );

    // 创建下载链接
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement("a");
    link.href = url;

    // 从响应头获取文件名，或使用默认文件名（包含股票名称）
    const stockName =
      realtimeData.value?.名称 || basicInfo.value?.股票简称 || "";
    const today = new Date().toISOString().split("T")[0].replace(/-/g, "");
    let filename = `${form.value.stockCode}_${stockName}_${periodText}数据_${today}.xlsx`;

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
</script>

<style scoped>
.stock-query {
  width: 100%;
  max-width: 1400px;
}

.query-card {
  background: linear-gradient(
    135deg,
    rgba(255, 255, 255, 0.98) 0%,
    rgba(255, 255, 255, 0.95) 100%
  );
  border-radius: 16px;
  overflow: hidden;
  border: 1px solid rgba(102, 126, 234, 0.1);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
}

.query-card:hover {
  box-shadow: 0 12px 48px rgba(102, 126, 234, 0.15);
  transform: translateY(-2px);
}

.card-header {
  font-size: 22px;
  font-weight: 700;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

/* 查询历史样式 */
.query-history-section {
  margin-top: 20px;
  margin-bottom: 25px;
  padding: 0;
  background: linear-gradient(
    135deg,
    rgba(255, 255, 255, 0.95) 0%,
    rgba(249, 250, 251, 0.95) 100%
  );
  border-radius: 16px;
  border: 1px solid rgba(102, 126, 234, 0.12);
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
  overflow: hidden;
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: linear-gradient(
    135deg,
    rgba(102, 126, 234, 0.08) 0%,
    rgba(118, 75, 162, 0.08) 100%
  );
  border-bottom: 2px solid rgba(102, 126, 234, 0.1);
}

.history-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
  font-weight: 700;
  color: #606266;
}

.clock-icon {
  font-size: 18px;
  color: #409eff;
}

/* 查询时间显示样式 */
.query-time-info {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  margin-bottom: 15px;
  background: linear-gradient(
    135deg,
    rgba(64, 158, 255, 0.08) 0%,
    rgba(64, 158, 255, 0.05) 100%
  );
  border-radius: 8px;
  border-left: 4px solid #409eff;
  font-size: 14px;
  color: #606266;
  font-weight: 500;
}

.query-time-info .clock-icon {
  color: #409eff;
  font-size: 16px;
}

.clear-btn {
  font-weight: 600;
  transition: all 0.3s ease;
}

.clear-btn:hover {
  transform: scale(1.05);
}

.history-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 12px;
  padding: 16px;
}

.history-item {
  position: relative;
  padding: 16px 14px;
  background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
  border: 2px solid rgba(102, 126, 234, 0.12);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.04);
}

.history-item:hover {
  transform: translateY(-4px);
  border-color: rgba(102, 126, 234, 0.4);
  box-shadow: 0 8px 20px rgba(102, 126, 234, 0.15);
  background: linear-gradient(135deg, #ffffff 0%, #ecf5ff 100%);
}

.history-item.active {
  border-color: #67c23a;
  background: linear-gradient(135deg, #f0f9ff 0%, #e1f3d8 100%);
  box-shadow: 0 4px 12px rgba(103, 194, 58, 0.2);
}

.history-item.active::before {
  content: "✓";
  position: absolute;
  top: 8px;
  right: 8px;
  width: 20px;
  height: 20px;
  background: #67c23a;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: bold;
}

.stock-info-badge {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.stock-name {
  font-size: 15px;
  font-weight: 700;
  color: #303133;
  line-height: 1.3;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.stock-code {
  font-size: 13px;
  font-weight: 600;
  color: #909399;
  font-family: "Courier New", monospace;
  letter-spacing: 0.5px;
}

.result-area {
  margin-top: 30px;
}

.stock-info {
  padding: 10px 0;
}

/* 加载骨架屏 */
.loading-skeleton {
  margin-top: 20px;
  padding: 20px;
}

/* 刷新倒计时 */
.refresh-countdown {
  margin-left: 15px;
  color: #67c23a;
  font-weight: 600;
  padding: 4px 12px;
  background: rgba(103, 194, 58, 0.1);
  border-radius: 20px;
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%,
  100% {
    opacity: 1;
  }
  50% {
    opacity: 0.7;
  }
}

/* 实时数据样式 */
.realtime-data {
  padding: 10px 0;
}

.key-metrics {
  margin-bottom: 20px;
}

.metric-card {
  text-align: center;
  padding: 15px 10px;
  transition: all 0.3s ease;
  border-radius: 12px;
}

.metric-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.15);
}

.metric-label {
  font-size: 14px;
  color: #909399;
  margin-bottom: 8px;
  font-weight: 500;
}

.metric-value {
  font-size: 22px;
  font-weight: 700;
  color: #303133;
}

.metric-value.price {
  font-size: 28px;
  font-weight: 800;
}

.price-up {
  color: #f56c6c !important;
  font-weight: 800 !important;
  text-shadow: 0 2px 4px rgba(245, 108, 108, 0.3);
}

.price-down {
  color: #67c23a !important;
  font-weight: 800 !important;
  text-shadow: 0 2px 4px rgba(103, 194, 58, 0.3);
}

.realtime-details {
  margin-top: 20px;
}

.history-query-area {
  margin-top: 30px;
  padding: 25px;
  background: linear-gradient(
    135deg,
    rgba(245, 247, 250, 0.6) 0%,
    rgba(236, 245, 255, 0.6) 100%
  );
  border-radius: 16px;
  border: 1px solid rgba(102, 126, 234, 0.1);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.04);
}

.history-table {
  margin-top: 20px;
}

.table-footer {
  margin-top: 10px;
  text-align: right;
}

:deep(.el-descriptions__label) {
  font-weight: 600;
  color: #606266;
  width: 150px;
}

:deep(.el-descriptions__content) {
  color: #303133;
}

:deep(.el-input-group__append) {
  background-color: #409eff;
  color: white;
  border: none;
}

:deep(.el-input-group__append .el-button) {
  color: white;
}

:deep(.el-table) {
  font-size: 14px;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
}

:deep(.el-table th) {
  background: linear-gradient(
    135deg,
    rgba(102, 126, 234, 0.08) 0%,
    rgba(118, 75, 162, 0.08) 100%
  );
  font-weight: 700;
  font-size: 15px;
  color: #606266;
  border-bottom: 2px solid rgba(102, 126, 234, 0.1);
}

:deep(.el-table .cell) {
  padding: 12px 0;
}

:deep(.el-table tr:hover > td) {
  background-color: rgba(102, 126, 234, 0.05) !important;
}

:deep(.el-input__wrapper) {
  border-radius: 8px;
  transition: all 0.3s ease;
}

:deep(.el-input__wrapper:hover) {
  box-shadow: 0 2px 12px rgba(102, 126, 234, 0.15);
}

:deep(.el-button) {
  border-radius: 8px;
  font-weight: 600;
  transition: all 0.3s ease;
}

:deep(.el-button:hover) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

:deep(.el-date-editor) {
  border-radius: 8px;
}

:deep(.metric-card .el-card__body) {
  padding: 15px 10px;
}
</style>
