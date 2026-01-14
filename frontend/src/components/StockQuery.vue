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

      <!-- 加载骨架屏 -->
      <div v-if="loading" class="loading-skeleton">
        <el-skeleton :rows="8" animated />
      </div>

      <!-- 实时数据和最近查询 -->
      <div v-if="realtimeData && !loading" class="result-area">
        <el-row :gutter="20" class="realtime-and-history">
          <!-- 左侧：最近查询 -->
          <el-col :span="8" v-if="queryHistory.length > 0">
            <div class="query-history-compact">
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
              <div class="history-grid">
                <div
                  v-for="(item, index) in displayHistory"
                  :key="item.code"
                  :class="[
                    'history-item-compact',
                    { active: form.stockCode === item.code },
                  ]"
                  @click="selectFromHistory(item)"
                >
                  <div class="stock-name-compact">{{ item.name }}</div>
                  <div class="stock-code-compact">{{ item.code }}</div>
                </div>
              </div>
            </div>
          </el-col>

          <!-- 右侧：实时行情数据 -->
          <el-col :span="queryHistory.length > 0 ? 16 : 24">
            <!-- 实时行情数据 -->
            <el-divider content-position="left">
              <el-tag type="warning" size="large">实时行情数据</el-tag>
            </el-divider>
            <!-- 昨日交易对比 -->
            <div v-if="realtimeData.昨日数据">
              <div class="yesterday-comparison">
                <div class="comparison-date" v-if="queryTime">
                  <el-icon><Calendar /></el-icon>
                  <span>查询时间：{{ queryTime }}</span>
                </div>

                <el-row :gutter="20">
                  <!-- 昨日开盘 -->
                  <el-col :span="4">
                    <el-card shadow="hover" class="comparison-card">
                      <div class="card-title">昨日开盘价</div>
                      <div class="card-value">
                        {{ realtimeData.昨日数据.昨日开盘 || "-" }}
                      </div>
                      <div
                        class="card-change"
                        :class="
                          getPriceClass(
                            realtimeData.昨日数据.相比昨日开盘涨跌幅
                          )
                        "
                        v-if="
                          realtimeData.昨日数据.相比昨日开盘涨跌幅 !== undefined
                        "
                      >
                        <el-icon
                          v-if="realtimeData.昨日数据.相比昨日开盘涨跌幅 > 0"
                          ><CaretTop
                        /></el-icon>
                        <el-icon
                          v-else-if="
                            realtimeData.昨日数据.相比昨日开盘涨跌幅 < 0
                          "
                          ><CaretBottom
                        /></el-icon>
                        <span
                          >{{ realtimeData.昨日数据.相比昨日开盘涨跌幅 }}%</span
                        >
                      </div>
                    </el-card>
                  </el-col>

                  <!-- 昨日最高 -->
                  <el-col :span="4">
                    <el-card shadow="hover" class="comparison-card">
                      <div class="card-title">昨日最高价</div>
                      <div class="card-value">
                        {{ realtimeData.昨日数据.昨日最高 || "-" }}
                      </div>
                      <div
                        class="card-change"
                        :class="
                          getPriceClass(
                            realtimeData.昨日数据.相比昨日最高涨跌幅
                          )
                        "
                        v-if="
                          realtimeData.昨日数据.相比昨日最高涨跌幅 !== undefined
                        "
                      >
                        <el-icon
                          v-if="realtimeData.昨日数据.相比昨日最高涨跌幅 > 0"
                          ><CaretTop
                        /></el-icon>
                        <el-icon
                          v-else-if="
                            realtimeData.昨日数据.相比昨日最高涨跌幅 < 0
                          "
                          ><CaretBottom
                        /></el-icon>
                        <span
                          >{{ realtimeData.昨日数据.相比昨日最高涨跌幅 }}%</span
                        >
                      </div>
                    </el-card>
                  </el-col>

                  <!-- 昨日最低 -->
                  <el-col :span="4">
                    <el-card shadow="hover" class="comparison-card">
                      <div class="card-title">昨日最低价</div>
                      <div class="card-value">
                        {{ realtimeData.昨日数据.昨日最低 || "-" }}
                      </div>
                      <div
                        class="card-change"
                        :class="
                          getPriceClass(
                            realtimeData.昨日数据.相比昨日最低涨跌幅
                          )
                        "
                        v-if="
                          realtimeData.昨日数据.相比昨日最低涨跌幅 !== undefined
                        "
                      >
                        <el-icon
                          v-if="realtimeData.昨日数据.相比昨日最低涨跌幅 > 0"
                          ><CaretTop
                        /></el-icon>
                        <el-icon
                          v-else-if="
                            realtimeData.昨日数据.相比昨日最低涨跌幅 < 0
                          "
                          ><CaretBottom
                        /></el-icon>
                        <span
                          >{{ realtimeData.昨日数据.相比昨日最低涨跌幅 }}%</span
                        >
                      </div>
                    </el-card>
                  </el-col>

                  <!-- 昨日收盘 -->
                  <el-col :span="4">
                    <el-card shadow="hover" class="comparison-card">
                      <div class="card-title">昨日收盘价</div>
                      <div class="card-value">
                        {{ realtimeData.昨日数据.昨日收盘 || "-" }}
                      </div>
                      <div
                        class="card-change"
                        :class="
                          getPriceClass(
                            realtimeData.昨日数据.相比昨日收盘涨跌幅
                          )
                        "
                        v-if="
                          realtimeData.昨日数据.相比昨日收盘涨跌幅 !== undefined
                        "
                      >
                        <el-icon
                          v-if="realtimeData.昨日数据.相比昨日收盘涨跌幅 > 0"
                          ><CaretTop
                        /></el-icon>
                        <el-icon
                          v-else-if="
                            realtimeData.昨日数据.相比昨日收盘涨跌幅 < 0
                          "
                          ><CaretBottom
                        /></el-icon>
                        <span
                          >{{ realtimeData.昨日数据.相比昨日收盘涨跌幅 }}%</span
                        >
                      </div>
                    </el-card>
                  </el-col>

                  <!-- 五日线 -->
                  <el-col :span="4">
                    <el-card shadow="hover" class="comparison-card ma-card">
                      <div class="card-title">五日线 (MA5)</div>
                      <div class="card-value">
                        {{ realtimeData.昨日数据.五日线 || "-" }}
                      </div>
                      <div
                        class="card-change"
                        :class="
                          getPriceClass(realtimeData.昨日数据.相比五日线涨跌幅)
                        "
                        v-if="
                          realtimeData.昨日数据.相比五日线涨跌幅 !== undefined
                        "
                      >
                        <el-icon
                          v-if="realtimeData.昨日数据.相比五日线涨跌幅 > 0"
                          ><CaretTop
                        /></el-icon>
                        <el-icon
                          v-else-if="realtimeData.昨日数据.相比五日线涨跌幅 < 0"
                          ><CaretBottom
                        /></el-icon>
                        <span
                          >{{ realtimeData.昨日数据.相比五日线涨跌幅 }}%</span
                        >
                      </div>
                    </el-card>
                  </el-col>

                  <!-- 十日线 -->
                  <el-col :span="4">
                    <el-card shadow="hover" class="comparison-card ma-card">
                      <div class="card-title">十日线 (MA10)</div>
                      <div class="card-value">
                        {{ realtimeData.昨日数据.十日线 || "-" }}
                      </div>
                      <div
                        class="card-change"
                        :class="
                          getPriceClass(realtimeData.昨日数据.相比十日线涨跌幅)
                        "
                        v-if="
                          realtimeData.昨日数据.相比十日线涨跌幅 !== undefined
                        "
                      >
                        <el-icon
                          v-if="realtimeData.昨日数据.相比十日线涨跌幅 > 0"
                          ><CaretTop
                        /></el-icon>
                        <el-icon
                          v-else-if="realtimeData.昨日数据.相比十日线涨跌幅 < 0"
                          ><CaretBottom
                        /></el-icon>
                        <span
                          >{{ realtimeData.昨日数据.相比十日线涨跌幅 }}%</span
                        >
                      </div>
                    </el-card>
                  </el-col>
                </el-row>
              </div>
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
                  >{{
                    realtimeData["60日涨跌幅"] || "-"
                  }}%</el-descriptions-item
                >
                <el-descriptions-item label="年初至今涨跌幅"
                  >{{
                    realtimeData["年初至今涨跌幅"] || "-"
                  }}%</el-descriptions-item
                >
              </el-descriptions>
            </div>
          </el-col>
        </el-row>
      </div>

      <!-- 历史数据查询区域 - 已隐藏 -->
      <div v-if="false" class="history-query-area">
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
import { ref, onUnmounted, onMounted, computed } from "vue";
import { ElMessage } from "element-plus";
import {
  Search,
  Download,
  Clock,
  Delete,
  Calendar,
  CaretTop,
  CaretBottom,
  InfoFilled,
} from "@element-plus/icons-vue";
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
const MAX_HISTORY = 20; // 最多保存20条历史记录

// 显示的历史记录（最多15个，5行×3列）
const displayHistory = computed(() => {
  return queryHistory.value.slice(0, 15);
});

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
    const response = await axios.get("/api/stock/info", {
      params: { code: form.value.stockCode },
    });

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
    const response = await axios.get("/api/stock/history", {
      params: {
        code: form.value.stockCode,
        start_date: historyForm.value.startDate,
        end_date: historyForm.value.endDate,
        period: historyForm.value.period,
        adjust: historyForm.value.adjust,
      },
    });

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
    const response = await axios.get("/api/stock/info", {
      params: { code: form.value.stockCode },
    });

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
    const response = await axios.get("/api/stock/download", {
      params: {
        code: form.value.stockCode,
        days,
        query_time: queryTime.value, // 传递查询时间
      },
      responseType: "blob",
    });

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
}

.query-card {
  background: rgba(255, 255, 255, 0.75);
  border-radius: 20px;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.5);
  box-shadow: 0 10px 40px rgba(102, 126, 234, 0.15);
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.query-card:hover {
  box-shadow: 0 15px 60px rgba(102, 126, 234, 0.18);
  transform: translateY(-4px);
}

.card-header {
  font-size: 26px;
  font-weight: 800;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: 0.5px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.card-header::before {
  content: "📊";
  font-size: 28px;
  filter: drop-shadow(0 2px 4px rgba(102, 126, 234, 0.3));
}

/* 实时数据和最近查询并排布局 */
.realtime-and-history {
  margin-top: 20px;
}

/* 最近查询紧凑布局 */
.query-history-compact {
  background: linear-gradient(
    135deg,
    rgba(236, 245, 255, 0.95) 0%,
    rgba(245, 247, 250, 0.95) 100%
  );
  border-radius: 18px;
  border: 2px solid rgba(102, 126, 234, 0.15);
  box-shadow: 0 6px 24px rgba(102, 126, 234, 0.08);
  overflow: hidden;
  height: 100%;
  display: flex;
  flex-direction: column;
  backdrop-filter: blur(10px);
}

.history-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
  padding: 15px;
  background: white;
  overflow-y: auto;
  flex: 1;
  max-height: 600px;
}

.history-item-compact {
  padding: 12px 10px;
  background: white;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border: 2px solid rgba(102, 126, 234, 0.08);
  position: relative;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.06);
  text-align: center;
}

.history-item-compact:hover {
  border-color: rgba(102, 126, 234, 0.5);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.2);
  transform: translateY(-3px) scale(1.02);
  background: linear-gradient(135deg, #ecf5ff 0%, #f5f7fa 100%);
}

.history-item-compact.active {
  border-color: #409eff;
  background: linear-gradient(
    135deg,
    rgba(102, 126, 234, 0.15) 0%,
    rgba(118, 75, 162, 0.15) 100%
  );
  box-shadow: 0 6px 24px rgba(102, 126, 234, 0.35);
  transform: scale(1.03);
}

.history-item-compact.active::after {
  content: "✓";
  position: absolute;
  top: 4px;
  right: 4px;
  width: 16px;
  height: 16px;
  background: #67c23a;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 10px;
  font-weight: bold;
}

.stock-name-compact {
  font-size: 13px;
  font-weight: 600;
  color: #303133;
  line-height: 1.3;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  margin-bottom: 4px;
}

.stock-code-compact {
  font-size: 11px;
  font-weight: 500;
  color: #909399;
  font-family: "Courier New", monospace;
  letter-spacing: 0.3px;
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

.yesterday-comparison {
  padding: 20px 0 10px 0;
}

.comparison-date {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  margin-bottom: 20px;
  background: linear-gradient(
    135deg,
    rgba(103, 194, 58, 0.08) 0%,
    rgba(103, 194, 58, 0.05) 100%
  );
  border-radius: 8px;
  border-left: 4px solid #67c23a;
  font-size: 14px;
  color: #606266;
  font-weight: 600;
}

.comparison-cards {
  margin-bottom: 20px;
}

.comparison-card {
  text-align: center;
  padding: 24px 18px;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  border-radius: 16px;
  border: 2px solid rgba(103, 194, 58, 0.2);
  background: linear-gradient(
    135deg,
    #ffffff 0%,
    rgba(240, 249, 235, 0.8) 100%
  );
  box-shadow: 0 4px 12px rgba(103, 194, 58, 0.08);
}

.comparison-card:hover {
  transform: translateY(-6px) scale(1.02);
  box-shadow: 0 12px 32px rgba(103, 194, 58, 0.25);
  border-color: rgba(103, 194, 58, 0.5);
}

.comparison-card.ma-card {
  border-color: rgba(64, 158, 255, 0.2);
  background: linear-gradient(
    135deg,
    #ffffff 0%,
    rgba(236, 245, 255, 0.8) 100%
  );
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.08);
}

.comparison-card.ma-card:hover {
  border-color: rgba(64, 158, 255, 0.5);
  box-shadow: 0 12px 32px rgba(64, 158, 255, 0.25);
}

.comparison-card .card-title {
  font-size: 14px;
  color: #606266;
  margin-bottom: 12px;
  font-weight: 600;
}

.comparison-card .card-value {
  font-size: 24px;
  font-weight: 700;
  color: #303133;
  margin-bottom: 10px;
}

.comparison-card .card-change {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  font-size: 16px;
  font-weight: 600;
}

.comparison-card .card-change .el-icon {
  font-size: 18px;
}

.comparison-note {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px;
  background: linear-gradient(
    135deg,
    rgba(64, 158, 255, 0.08) 0%,
    rgba(64, 158, 255, 0.05) 100%
  );
  border-radius: 8px;
  font-size: 14px;
  color: #409eff;
  font-weight: 500;
}

.no-yesterday-data {
  padding: 20px 0;
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
  padding: 20px 15px;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  border-radius: 16px;
  background: linear-gradient(135deg, #ffffff 0%, #f8f9ff 100%);
  border: 2px solid rgba(102, 126, 234, 0.1);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.08);
}

.metric-card:hover {
  transform: translateY(-5px) scale(1.02);
  box-shadow: 0 10px 30px rgba(102, 126, 234, 0.2);
  border-color: rgba(102, 126, 234, 0.3);
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
  border-radius: 12px;
  transition: all 0.3s ease;
  border: 2px solid rgba(102, 126, 234, 0.1);
}

:deep(.el-input__wrapper:hover) {
  box-shadow: 0 4px 16px rgba(102, 126, 234, 0.15);
  border-color: rgba(102, 126, 234, 0.3);
}

:deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 4px 20px rgba(102, 126, 234, 0.25);
  border-color: #409eff;
}

:deep(.el-button) {
  border-radius: 12px;
  font-weight: 600;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  padding: 10px 20px;
}

:deep(.el-button:hover) {
  transform: translateY(-2px) scale(1.02);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.3);
}

:deep(.el-button--primary) {
  background: linear-gradient(135deg, #409eff 0%, #667eea 100%);
  border: none;
}

:deep(.el-button--success) {
  background: linear-gradient(135deg, #67c23a 0%, #85ce61 100%);
  border: none;
}

:deep(.el-date-editor) {
  border-radius: 8px;
}

:deep(.metric-card .el-card__body) {
  padding: 15px 10px;
}

/* 移动端适配 */
@media screen and (max-width: 768px) {
  .query-card {
    border-radius: 8px;
    margin: 0;
  }

  .card-header {
    font-size: 18px;
  }

  /* 表单适配 */
  :deep(.el-form-item__label) {
    font-size: 13px;
  }

  /* 昨日对比卡片改为2列 */
  .comparison-cards :deep(.el-col) {
    width: 33.33% !important;
    max-width: 33.33% !important;
    flex: 0 0 33.33% !important;
    margin-bottom: 12px;
  }

  .comparison-card {
    padding: 15px 10px;
  }

  .comparison-card .card-title {
    font-size: 11px;
  }

  .comparison-card .card-value {
    font-size: 18px;
  }

  .comparison-card .card-change {
    font-size: 13px;
  }

  .comparison-date {
    font-size: 13px;
    padding: 10px 12px;
  }

  .comparison-note {
    font-size: 13px;
    padding: 10px;
  }

  :deep(.el-input__inner) {
    font-size: 14px;
  }

  :deep(.el-button) {
    padding: 8px 12px;
    font-size: 13px;
  }

  /* 查询历史网格适配 - 紧凑布局 */
  .history-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 6px;
    padding: 10px;
  }

  .history-item-compact {
    padding: 8px 6px;
  }

  .stock-name-compact {
    font-size: 12px;
  }

  .stock-code-compact {
    font-size: 10px;
  }

  /* 实时和历史并排布局在移动端改为堆叠 */
  .realtime-and-history :deep(.el-col) {
    width: 100% !important;
    max-width: 100% !important;
    flex: 0 0 100% !important;
    margin-bottom: 15px;
  }

  .query-history-compact {
    margin-bottom: 20px;
  }

  /* 查询历史网格适配 */
  .history-list {
    grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
    gap: 8px;
    padding: 12px;
  }

  .history-item {
    padding: 12px 10px;
  }

  .stock-name {
    font-size: 13px;
  }

  .stock-code {
    font-size: 12px;
  }

  /* 查询时间信息 */
  .query-time-info {
    font-size: 12px;
    padding: 10px 12px;
  }

  /* 核心指标卡片 - 改为2列 */
  .key-metrics :deep(.el-col) {
    width: 50% !important;
    max-width: 50% !important;
    flex: 0 0 50% !important;
    margin-bottom: 12px;
  }

  .metric-card {
    padding: 10px 8px;
  }

  .metric-label {
    font-size: 12px;
  }

  .metric-value {
    font-size: 18px;
  }

  .metric-value.price {
    font-size: 22px;
  }

  /* 描述列表适配 */
  :deep(.el-descriptions) {
    font-size: 12px;
  }

  :deep(.el-descriptions__label) {
    width: 80px;
    font-size: 12px;
    padding: 8px 10px;
  }

  :deep(.el-descriptions__content) {
    font-size: 12px;
    padding: 8px 10px;
  }

  :deep(.realtime-details) {
    font-size: 12px;
  }

  :deep(.realtime-details .el-descriptions__label) {
    width: 70px;
  }

  /* 历史查询区域 */
  .history-query-area {
    padding: 15px;
  }

  :deep(.el-col) {
    margin-bottom: 0;
  }

  /* 表格适配 */
  :deep(.el-table) {
    font-size: 12px;
  }

  :deep(.el-table th) {
    font-size: 12px;
    padding: 8px 0;
  }

  :deep(.el-table .cell) {
    padding: 8px 5px;
    line-height: 1.4;
  }

  :deep(.el-table__body-wrapper) {
    overflow-x: auto;
  }

  /* 下载按钮适配 */
  :deep(.el-form-item .el-button) {
    margin-left: 0 !important;
    margin-top: 8px;
    width: 100%;
  }
}

@media screen and (max-width: 480px) {
  .card-header {
    font-size: 16px;
  }

  /* 紧凑历史网格改为单列 */
  .history-grid {
    grid-template-columns: 1fr;
    gap: 5px;
    padding: 8px;
  }

  .history-item-compact {
    padding: 8px 6px;
  }

  .stock-name-compact {
    font-size: 11px;
  }

  .stock-code-compact {
    font-size: 9px;
  }

  /* 查询历史改为单列 */
  .history-list {
    grid-template-columns: 1fr;
    gap: 6px;
    padding: 10px;
  }

  .history-header {
    padding: 12px 15px;
  }

  .history-title {
    font-size: 14px;
  }

  /* 昨日对比卡片改为单列 */
  .comparison-cards :deep(.el-col) {
    width: 50% !important;
    max-width: 50% !important;
    flex: 0 0 50% !important;
    margin-bottom: 10px;
  }

  .comparison-card .card-title {
    font-size: 12px;
  }

  .comparison-card .card-value {
    font-size: 20px;
  }

  .comparison-card .card-change {
    font-size: 14px;
  }

  /* 核心指标卡片 - 小屏单列 */
  .key-metrics :deep(.el-col) {
    width: 100% !important;
    max-width: 100% !important;
    flex: 0 0 100% !important;
    margin-bottom: 10px;
  }

  .metric-label {
    font-size: 13px;
  }

  .metric-value {
    font-size: 20px;
  }

  .metric-value.price {
    font-size: 24px;
  }

  /* 描述列表改为单列 */
  :deep(.el-descriptions) {
    font-size: 11px;
  }

  :deep(.el-descriptions__label) {
    width: 90px;
    font-size: 11px;
  }

  :deep(.el-descriptions__content) {
    font-size: 11px;
  }

  /* 历史查询表单改为单列 */
  :deep(.el-form .el-col) {
    width: 100% !important;
    max-width: 100% !important;
  }

  /* 按钮全宽 */
  :deep(.el-button) {
    width: 100%;
    margin-left: 0 !important;
    margin-bottom: 8px;
  }

  .refresh-countdown {
    display: block;
    margin-left: 0 !important;
    margin-top: 8px;
    text-align: center;
  }

  /* 表格字体更小 */
  :deep(.el-table) {
    font-size: 11px;
  }

  :deep(.el-table th) {
    font-size: 11px;
  }

  :deep(.el-table .cell) {
    padding: 6px 3px;
  }
}
</style>
