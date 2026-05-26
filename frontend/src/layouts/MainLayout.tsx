import { useState } from 'react';
import { Layout, Menu, Avatar, Dropdown, Badge, Button } from 'antd';
import {
  DashboardOutlined,
  MessageOutlined,
  FileTextOutlined,
  ProjectOutlined,
  CheckCircleOutlined,
  DatabaseOutlined,
  ReadOutlined,
  SettingOutlined,
  TeamOutlined,
  LogoutOutlined,
  UserOutlined,
  BellOutlined,
  ApiOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined,
} from '@ant-design/icons';
import { Outlet, useLocation, useNavigate } from 'react-router-dom';
import { useAuthStore } from '@/stores';
import type { MenuProps } from 'antd';

const { Header, Sider, Content } = Layout;

const MainLayout = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, clearAuth } = useAuthStore();
  const [collapsed, setCollapsed] = useState(false);

  const menuItems: MenuProps['items'] = [
    { key: '/dashboard', icon: <DashboardOutlined />, label: '数据看板' },
    { key: '/chat', icon: <MessageOutlined />, label: '智能助手' },
    { key: '/tickets', icon: <FileTextOutlined />, label: '工单管理' },
    { key: '/tasks', icon: <ProjectOutlined />, label: '任务看板' },
    { key: '/approvals', icon: <CheckCircleOutlined />, label: '审批中心' },
    { key: '/assets', icon: <DatabaseOutlined />, label: '资产管理' },
    { key: '/knowledge', icon: <ReadOutlined />, label: '知识库' },
    { key: '/users', icon: <TeamOutlined />, label: '用户管理' },
    { key: '/settings', icon: <SettingOutlined />, label: '系统设置' },
  ];

  const userMenuItems: MenuProps['items'] = [
    { key: 'profile', icon: <UserOutlined />, label: user?.name || '个人信息' },
    { type: 'divider' },
    { key: 'logout', icon: <LogoutOutlined />, label: '退出登录', danger: true },
  ];

  const handleUserMenuClick = ({ key }: { key: string }) => {
    if (key === 'logout') {
      clearAuth();
      navigate('/login');
    }
  };

  return (
    <Layout className="app-shell" style={{ minHeight: '100vh' }}>
      <Sider
        className="app-sider"
        trigger={null}
        collapsible
        collapsed={collapsed}
        theme="dark"
        style={{ overflow: 'auto', height: '100vh', position: 'fixed', left: 0, top: 0, bottom: 0 }}
      >
        <div
          className="app-logo"
          style={{
            height: 64,
            display: 'flex',
            alignItems: 'center',
            justifyContent: collapsed ? 'center' : 'flex-start',
            fontSize: collapsed ? 16 : 20,
            fontWeight: 700,
            color: '#fff',
          }}
        >
          <span className="app-logo-mark" aria-hidden="true">
            <img src="https://www.thingo.com.cn/logo.svg" alt="" />
          </span>
          {!collapsed && <span className="app-logo-text">Thingo 行政智能体</span>}
        </div>
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[location.pathname]}
          items={menuItems}
          onClick={({ key }) => navigate(key)}
        />
      </Sider>

      <Layout style={{ marginLeft: collapsed ? 80 : 200, transition: 'all 0.2s' }}>
        <Header
          className="app-header"
          style={{
            padding: '0 24px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
          }}
        >
          <div className="app-header-trigger" onClick={() => setCollapsed(!collapsed)} style={{ fontSize: 18, cursor: 'pointer' }}>
            {collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
          </div>

          <div className="app-header-actions" style={{ display: 'flex', alignItems: 'center', gap: 24 }}>
            <Button className="docs-link-button" icon={<ApiOutlined />} onClick={() => { window.location.href = '/docs'; }}>
              接口文档
            </Button>
            <Badge count={0} size="small">
              <BellOutlined style={{ fontSize: 18 }} />
            </Badge>
            <Dropdown menu={{ items: userMenuItems, onClick: handleUserMenuClick }} placement="bottomRight">
              <div className="app-user" style={{ cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 8 }}>
                <Avatar icon={<UserOutlined />} style={{ backgroundColor: '#1677ff' }} />
                <span style={{ fontWeight: 500 }}>{user?.name || '用户'}</span>
              </div>
            </Dropdown>
          </div>
        </Header>

        <Content className="app-content" style={{ margin: '24px 16px', minHeight: 280 }}>
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  );
};

export default MainLayout;
