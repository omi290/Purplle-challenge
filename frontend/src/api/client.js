import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  timeout: 15000,
});

// Zero-State Data fallback systems
const zeroDashboard = {
  metrics: {
    total_footfall: 0,
    unique_visitors: 0,
    conversion_rate: 0.0,
    average_dwell_time: 0.0,
    revenue_per_visitor: 0.0,
    actual_sales: 0.0
  },
  store_health: {
    overall_score: 0.0,
    grade: "N/A",
    components: {
      conversion_rate: { score: 0.0, weight: 0.25 },
      dwell_quality: { score: 0.0, weight: 0.20 },
      queue_efficiency: { score: 0.0, weight: 0.20 },
      zone_utilization: { score: 0.0, weight: 0.15 },
      anomaly_rate: { score: 0.0, weight: 0.10 },
      revenue_efficiency: { score: 0.0, weight: 0.10 }
    }
  },
  revenue_leakage: {
    leakage_rate: 0.0,
    estimated_leaked_revenue: 0.0,
    potential_total_revenue: 0.0,
    average_order_value: 0.0,
    leaked_visitors_count: 0
  },
  opportunity_loss: {
    total_opportunities_lost: 0,
    estimated_revenue_impact: 0.0,
    achievable_opportunities: 0,
    top_reasons: []
  },
  recent_anomalies: [],
  ai_suggestions: [],
  funnel_summary: {
    stages: [
      { name: "Entry", count: 0, percentage: 0.0, drop_off: 0.0 },
      { name: "Browse", count: 0, percentage: 0.0, drop_off: 0.0 },
      { name: "Billing Queue", count: 0, percentage: 0.0, drop_off: 0.0 },
      { name: "Purchase", count: 0, percentage: 0.0, drop_off: 0.0 }
    ]
  },
  zone_heatmap: [],
  staff_count: 0,
  hourly_trend: []
};

export const getDashboard = async () => {
  try {
    const res = await api.get('/dashboard');
    return res.data;
  } catch (err) {
    console.error("API Dashboard failed. Returning clean zero-state.", err);
    return zeroDashboard;
  }
};

export const getMetrics = async (params = {}) => {
  try {
    const res = await api.get('/metrics', { params });
    return res.data;
  } catch (err) {
    return zeroDashboard.metrics;
  }
};

export const getFunnel = async (params = {}) => {
  try {
    const res = await api.get('/funnel', { params });
    return res.data;
  } catch (err) {
    return {
      stages: zeroDashboard.funnel_summary.stages,
      overall_conversion: zeroDashboard.metrics.conversion_rate,
      confidence: 0.0
    };
  }
};

export const getHeatmap = async (params = {}) => {
  try {
    const res = await api.get('/heatmap', { params });
    return res.data;
  } catch (err) {
    return {
      zones: [],
      max_visitors: 0,
      total_zones: 0
    };
  }
};

export const getAnomalies = async (params = {}) => {
  try {
    const res = await api.get('/anomalies', { params });
    return res.data;
  } catch (err) {
    return zeroDashboard.recent_anomalies;
  }
};

export const getHealth = async () => {
  try {
    const res = await api.get('/health');
    return res.data;
  } catch (err) {
    return {
      status: "error",
      version: "1.0.0",
      uptime_seconds: 0,
      database: "disconnected",
      total_events: 0,
      store_health: zeroDashboard.store_health,
      revenue_leakage: zeroDashboard.revenue_leakage,
      opportunity_loss: zeroDashboard.opportunity_loss
    };
  }
};

export const uploadVideo = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  return api.post('/upload/video', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
};

export const uploadStoreLayout = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  return api.post('/upload/store-layout', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
};

export const uploadPosData = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  return api.post('/upload/pos-data', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
};

export const triggerProcessing = async () => {
  const res = await api.post('/upload/process');
  return res.data;
};

export const getRevenueLeakage = async () => {
  try {
    const res = await api.get('/revenue-leakage');
    return res.data;
  } catch (err) {
    return zeroDashboard.revenue_leakage;
  }
};

export const getOpportunityLoss = async () => {
  try {
    const res = await api.get('/opportunity-loss');
    return res.data;
  } catch (err) {
    return zeroDashboard.opportunity_loss;
  }
};
