import type { ThemeConfig } from 'antd';

export const theme: ThemeConfig = {
  token: {
    colorPrimary: '#0891b2',
    colorSuccess: '#10b981',
    colorWarning: '#f59e0b',
    colorError: '#ef4444',
    colorInfo: '#2563eb',
    colorBgLayout: '#eef4f8',
    colorBgContainer: '#ffffff',
    colorBorder: '#d8e2ea',
    colorText: '#0f172a',
    colorTextSecondary: '#64748b',
    borderRadius: 8,
    controlHeight: 36,
    fontSize: 14,
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
    boxShadow: '0 12px 30px rgba(15, 23, 42, 0.08)',
  },
  components: {
    Layout: {
      headerBg: 'rgba(255, 255, 255, 0.82)',
      headerHeight: 64,
      headerPadding: '0 24px',
      siderBg: '#07111f',
      bodyBg: '#eef4f8',
    },
    Menu: {
      darkItemBg: '#07111f',
      darkItemHoverBg: 'rgba(255, 255, 255, 0.08)',
      darkItemSelectedBg: 'rgba(8, 145, 178, 0.24)',
      darkItemSelectedColor: '#67e8f9',
    },
    Button: {
      controlHeight: 36,
      borderRadius: 7,
    },
    Card: {
      borderRadiusLG: 8,
      boxShadowTertiary: '0 12px 28px rgba(15, 23, 42, 0.08)',
    },
    Table: {
      headerBg: '#f5f9fc',
      headerColor: '#334155',
      borderColor: '#e2e8f0',
    },
    Modal: {
      borderRadiusLG: 8,
    },
    Drawer: {
      borderRadiusLG: 8,
    },
  },
};
