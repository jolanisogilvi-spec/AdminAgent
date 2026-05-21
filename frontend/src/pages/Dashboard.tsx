import { Card, Col, Progress, Row, Space, Statistic, Table, Tag } from 'antd';
import { useQuery } from '@tanstack/react-query';
import PageContainer from '@/components/PageContainer';
import { apiClient } from '@/services/api';
import type { Asset, Task, Ticket } from '@/types';

const Dashboard = () => {
  const tickets = useQuery({ queryKey: ['tickets'], queryFn: () => apiClient.get<Ticket[]>('/tickets/') });
  const assets = useQuery({ queryKey: ['assets'], queryFn: () => apiClient.get<Asset[]>('/assets/') });
  const tasks = useQuery({ queryKey: ['tasks'], queryFn: () => apiClient.get<Task[]>('/tasks/') });

  const ticketItems = tickets.data || [];
  const assetItems = assets.data || [];
  const taskItems = tasks.data || [];

  const pendingTickets = ticketItems.filter((item) => item.processing_status === 'pending').length;
  const inProgressTickets = ticketItems.filter((item) => item.processing_status === 'in_progress').length;
  const pendingTasks = taskItems.filter((item) => item.status === 'todo').length;
  const doneTasks = taskItems.filter((item) => item.status === 'completed').length;
  const pendingApprovals = ticketItems.filter((item) => item.approval_status.includes('pending')).length;
  const idleAssets = assetItems.filter((item) => item.status === 'idle').length;
  const totalCost = ticketItems.reduce((sum, item) => sum + Number(item.estimated_cost || 0), 0);
  const taskCompletion = taskItems.length ? Math.round((doneTasks / taskItems.length) * 100) : 0;

  return (
    <PageContainer title="数据看板">
      <Space direction="vertical" size={16} style={{ width: '100%' }}>
        <Row gutter={[16, 16]}>
          <Col xs={24} md={6}>
            <Card>
              <Statistic title="工单总数" value={ticketItems.length} />
            </Card>
          </Col>
          <Col xs={24} md={6}>
            <Card>
              <Statistic title="待处理工单" value={pendingTickets} />
            </Card>
          </Col>
          <Col xs={24} md={6}>
            <Card>
              <Statistic title="待审批" value={pendingApprovals} />
            </Card>
          </Col>
          <Col xs={24} md={6}>
            <Card>
              <Statistic title="预估费用" value={totalCost} precision={2} prefix="¥" />
            </Card>
          </Col>
        </Row>

        <Row gutter={[16, 16]}>
          <Col xs={24} lg={8}>
            <Card title="处理进度">
              <Space direction="vertical" style={{ width: '100%' }}>
                <div>处理中工单：{inProgressTickets}</div>
                <div>任务完成率</div>
                <Progress percent={taskCompletion} />
                <div>待办任务：{pendingTasks}</div>
              </Space>
            </Card>
          </Col>
          <Col xs={24} lg={8}>
            <Card title="资产概况">
              <Space direction="vertical" style={{ width: '100%' }}>
                <Statistic title="资产总数" value={assetItems.length} />
                <Statistic title="闲置资产" value={idleAssets} />
                <Statistic title="库存总量" value={assetItems.reduce((sum, item) => sum + item.current_stock, 0)} />
              </Space>
            </Card>
          </Col>
          <Col xs={24} lg={8}>
            <Card title="任务概况">
              <Space direction="vertical" style={{ width: '100%' }}>
                <Statistic title="任务总数" value={taskItems.length} />
                <Statistic title="待办" value={pendingTasks} />
                <Statistic title="已完成" value={doneTasks} />
              </Space>
            </Card>
          </Col>
        </Row>

        <Row gutter={[16, 16]}>
          <Col xs={24} lg={12}>
            <Card title="最新工单" loading={tickets.isLoading}>
              <Table<Ticket>
                rowKey="id"
                pagination={false}
                dataSource={ticketItems.slice(0, 5)}
                columns={[
                  { title: '内容', dataIndex: 'original_text', ellipsis: true },
                  { title: '类型', dataIndex: 'ticket_type', width: 110 },
                  { title: '状态', dataIndex: 'processing_status', width: 110, render: (value) => <Tag>{value}</Tag> },
                ]}
              />
            </Card>
          </Col>
          <Col xs={24} lg={12}>
            <Card title="最近任务" loading={tasks.isLoading}>
              <Table<Task>
                rowKey="id"
                pagination={false}
                dataSource={taskItems.slice(0, 5)}
                columns={[
                  { title: '任务', dataIndex: 'title', ellipsis: true },
                  { title: '负责人', dataIndex: 'assigned_to', width: 90 },
                  { title: '状态', dataIndex: 'status', width: 110, render: (value) => <Tag>{value}</Tag> },
                ]}
              />
            </Card>
          </Col>
        </Row>
      </Space>
    </PageContainer>
  );
};

export default Dashboard;
