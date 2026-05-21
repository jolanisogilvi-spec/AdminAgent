import type { ReactNode } from 'react';
import { Breadcrumb } from 'antd';
import { HomeOutlined } from '@ant-design/icons';
import { Link, useLocation } from 'react-router-dom';

interface PageContainerProps {
  title?: string;
  children: ReactNode;
  extra?: ReactNode;
  breadcrumb?: boolean;
}

const PageContainer = ({ title, children, extra, breadcrumb = true }: PageContainerProps) => {
  const location = useLocation();
  const pathSnippets = location.pathname.split('/').filter(Boolean);
  const nameMap: Record<string, string> = {
    dashboard: '数据看板',
    chat: '智能助手',
    tickets: '工单管理',
    tasks: '任务看板',
    approvals: '审批中心',
    assets: '资产管理',
    knowledge: '知识库',
    users: '用户管理',
    settings: '系统设置',
  };

  const breadcrumbItems = [
    { title: <Link to="/"><HomeOutlined /></Link> },
    ...pathSnippets.map((snippet, index) => {
      const url = `/${pathSnippets.slice(0, index + 1).join('/')}`;
      const isLast = index === pathSnippets.length - 1;
      return {
        title: isLast ? nameMap[snippet] || snippet : <Link to={url}>{nameMap[snippet] || snippet}</Link>,
      };
    }),
  ];

  return (
    <div className="page-container" style={{ paddingBottom: 24 }}>
      {breadcrumb && <Breadcrumb className="page-breadcrumb" items={breadcrumbItems} style={{ marginBottom: 16 }} />}
      {title && (
        <div className="page-heading" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
          <div>
            <div className="page-kicker">运营工作台</div>
            <h2 style={{ margin: 0, fontSize: 20, fontWeight: 600 }}>{title}</h2>
          </div>
          {extra && <div className="page-heading-extra">{extra}</div>}
        </div>
      )}
      <div className="page-surface" style={{ minHeight: 'calc(100vh - 200px)' }}>
        {children}
      </div>
    </div>
  );
};

export default PageContainer;
