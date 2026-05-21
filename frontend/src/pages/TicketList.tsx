import {
  Button,
  Descriptions,
  Drawer,
  Form,
  Input,
  InputNumber,
  Modal,
  Popconfirm,
  Select,
  Space,
  Statistic,
  Table,
  Tag,
  message,
} from 'antd';
import { DeleteOutlined, EditOutlined, EyeOutlined, PlusOutlined } from '@ant-design/icons';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useMemo, useState } from 'react';
import PageContainer from '@/components/PageContainer';
import { apiClient } from '@/services/api';
import type { ApprovalStatus, ProcessingStatus, Ticket, TicketType, UrgencyLevel } from '@/types';

type TicketFormValues = {
  original_text: string;
  attachments?: string;
  ticket_type: TicketType;
  related_asset_id?: number;
  estimated_cost: number;
  urgency: UrgencyLevel;
  approval_status?: ApprovalStatus;
  processing_status?: ProcessingStatus;
  assigned_to?: number;
};

const ticketTypeOptions = [
  { value: 'purchase', label: '采购' },
  { value: 'repair', label: '报修' },
  { value: 'requisition', label: '领用' },
  { value: 'consultation', label: '咨询' },
];

const urgencyOptions = [
  { value: 'low', label: '低' },
  { value: 'normal', label: '普通' },
  { value: 'high', label: '高' },
  { value: 'urgent', label: '紧急' },
];

const approvalOptions = [
  { value: 'no_approval', label: '无需审批' },
  { value: 'pending_manager', label: '待主管审批' },
  { value: 'pending_finance', label: '待财务审批' },
  { value: 'approved', label: '已通过' },
  { value: 'rejected', label: '已驳回' },
];

const processingOptions = [
  { value: 'pending', label: '待处理' },
  { value: 'in_progress', label: '处理中' },
  { value: 'completed', label: '已完成' },
  { value: 'closed', label: '已关闭' },
];

const optionLabel = (options: { value: string; label: string }[], value?: string | null) =>
  options.find((item) => item.value === value)?.label || value || '-';

const approvalColor: Record<ApprovalStatus, string> = {
  no_approval: 'default',
  pending_manager: 'gold',
  pending_finance: 'orange',
  approved: 'green',
  rejected: 'red',
};

const statusColor: Record<ProcessingStatus, string> = {
  pending: 'default',
  in_progress: 'blue',
  completed: 'green',
  closed: 'purple',
};

const TicketList = () => {
  const [open, setOpen] = useState(false);
  const [editing, setEditing] = useState<Ticket | null>(null);
  const [detail, setDetail] = useState<Ticket | null>(null);
  const [keyword, setKeyword] = useState('');
  const [statusFilter, setStatusFilter] = useState<ProcessingStatus | 'all'>('all');
  const [typeFilter, setTypeFilter] = useState<TicketType | 'all'>('all');
  const [form] = Form.useForm<TicketFormValues>();
  const queryClient = useQueryClient();

  const tickets = useQuery({ queryKey: ['tickets'], queryFn: () => apiClient.get<Ticket[]>('/tickets/') });

  const saveTicket = useMutation({
    mutationFn: (values: TicketFormValues) => {
      if (editing) {
        return apiClient.patch<Ticket>(`/tickets/${editing.id}`, values);
      }
      return apiClient.post<Ticket>('/tickets/', values);
    },
    onSuccess: () => {
      message.success(editing ? '工单已更新' : '工单已创建');
      setOpen(false);
      setEditing(null);
      form.resetFields();
      queryClient.invalidateQueries({ queryKey: ['tickets'] });
    },
  });

  const deleteTicket = useMutation({
    mutationFn: (id: number) => apiClient.delete(`/tickets/${id}`),
    onSuccess: () => {
      message.success('工单已删除');
      queryClient.invalidateQueries({ queryKey: ['tickets'] });
    },
  });

  const dataSource = useMemo(() => {
    return (tickets.data || []).filter((item) => {
      const matchesKeyword = !keyword || item.original_text.toLowerCase().includes(keyword.toLowerCase());
      const matchesStatus = statusFilter === 'all' || item.processing_status === statusFilter;
      const matchesType = typeFilter === 'all' || item.ticket_type === typeFilter;
      return matchesKeyword && matchesStatus && matchesType;
    });
  }, [keyword, statusFilter, tickets.data, typeFilter]);

  const stats = useMemo(() => {
    const items = tickets.data || [];
    return {
      total: items.length,
      pending: items.filter((item) => item.processing_status === 'pending').length,
      inProgress: items.filter((item) => item.processing_status === 'in_progress').length,
      approval: items.filter((item) => item.approval_status.startsWith('pending')).length,
    };
  }, [tickets.data]);

  const openCreate = () => {
    setEditing(null);
    form.resetFields();
    form.setFieldsValue({
      ticket_type: 'repair',
      urgency: 'normal',
      estimated_cost: 0,
      processing_status: 'pending',
    });
    setOpen(true);
  };

  const openEdit = (record: Ticket) => {
    setEditing(record);
    form.setFieldsValue({
      original_text: record.original_text,
      attachments: record.attachments || undefined,
      ticket_type: record.ticket_type,
      related_asset_id: record.related_asset_id || undefined,
      estimated_cost: Number(record.estimated_cost || 0),
      urgency: record.urgency,
      approval_status: record.approval_status,
      processing_status: record.processing_status,
      assigned_to: record.assigned_to || undefined,
    });
    setOpen(true);
  };

  return (
    <PageContainer
      title="工单管理"
      extra={
        <Button type="primary" icon={<PlusOutlined />} onClick={openCreate}>
          新建工单
        </Button>
      }
    >
      <Space direction="vertical" size={16} style={{ width: '100%' }}>
        <Space wrap size={24}>
          <Statistic title="工单总数" value={stats.total} />
          <Statistic title="待处理" value={stats.pending} />
          <Statistic title="处理中" value={stats.inProgress} />
          <Statistic title="待审批" value={stats.approval} />
        </Space>

        <Space wrap>
          <Input.Search placeholder="搜索诉求内容" allowClear onSearch={setKeyword} onChange={(e) => setKeyword(e.target.value)} />
          <Select style={{ width: 140 }} value={typeFilter} onChange={setTypeFilter} options={[{ value: 'all', label: '全部类型' }, ...ticketTypeOptions]} />
          <Select
            style={{ width: 140 }}
            value={statusFilter}
            onChange={setStatusFilter}
            options={[{ value: 'all', label: '全部状态' }, ...processingOptions]}
          />
        </Space>

        <Table<Ticket>
          rowKey="id"
          loading={tickets.isLoading}
          dataSource={dataSource}
          pagination={{ pageSize: 8, showSizeChanger: false }}
          columns={[
            { title: 'ID', dataIndex: 'id', width: 70 },
            { title: '诉求内容', dataIndex: 'original_text', ellipsis: true },
            { title: '类型', dataIndex: 'ticket_type', width: 100, render: (value) => optionLabel(ticketTypeOptions, value) },
            { title: '紧急度', dataIndex: 'urgency', width: 90, render: (value) => optionLabel(urgencyOptions, value) },
            { title: '预估费用', dataIndex: 'estimated_cost', width: 110 },
            {
              title: '审批',
              dataIndex: 'approval_status',
              width: 130,
              render: (value: ApprovalStatus) => <Tag color={approvalColor[value]}>{optionLabel(approvalOptions, value)}</Tag>,
            },
            {
              title: '处理状态',
              dataIndex: 'processing_status',
              width: 120,
              render: (value: ProcessingStatus) => <Tag color={statusColor[value]}>{optionLabel(processingOptions, value)}</Tag>,
            },
            {
              title: '操作',
              width: 150,
              render: (_, record) => (
                <Space>
                  <Button size="small" icon={<EyeOutlined />} onClick={() => setDetail(record)} />
                  <Button size="small" icon={<EditOutlined />} onClick={() => openEdit(record)} />
                  <Popconfirm title="删除工单" description="确认删除这条工单？" onConfirm={() => deleteTicket.mutate(record.id)}>
                    <Button size="small" danger icon={<DeleteOutlined />} />
                  </Popconfirm>
                </Space>
              ),
            },
          ]}
        />
      </Space>

      <Modal
        title={editing ? '编辑工单' : '新建工单'}
        open={open}
        onCancel={() => {
          setOpen(false);
          setEditing(null);
        }}
        onOk={() => form.submit()}
        confirmLoading={saveTicket.isPending}
        width={720}
        destroyOnHidden
      >
        <Form form={form} layout="vertical" onFinish={(values) => saveTicket.mutate(values)}>
          <Form.Item name="original_text" label="诉求内容" rules={[{ required: true, message: '请输入诉求内容' }]}>
            <Input.TextArea rows={4} />
          </Form.Item>
          <Space wrap style={{ width: '100%' }} align="start">
            <Form.Item name="ticket_type" label="类型" rules={[{ required: true }]}>
              <Select style={{ width: 140 }} options={ticketTypeOptions} />
            </Form.Item>
            <Form.Item name="urgency" label="紧急度">
              <Select style={{ width: 120 }} options={urgencyOptions} />
            </Form.Item>
            <Form.Item name="estimated_cost" label="预估费用">
              <InputNumber min={0} style={{ width: 130 }} />
            </Form.Item>
            <Form.Item name="related_asset_id" label="关联资产ID">
              <InputNumber min={1} style={{ width: 130 }} />
            </Form.Item>
          </Space>
          <Form.Item name="attachments" label="附件地址">
            <Input placeholder="多个附件可用逗号分隔" />
          </Form.Item>
          {editing && (
            <Space wrap style={{ width: '100%' }} align="start">
              <Form.Item name="approval_status" label="审批状态">
                <Select style={{ width: 160 }} options={approvalOptions} />
              </Form.Item>
              <Form.Item name="processing_status" label="处理状态">
                <Select style={{ width: 140 }} options={processingOptions} />
              </Form.Item>
              <Form.Item name="assigned_to" label="负责人ID">
                <InputNumber min={1} style={{ width: 120 }} />
              </Form.Item>
            </Space>
          )}
        </Form>
      </Modal>

      <Drawer title="工单详情" open={!!detail} onClose={() => setDetail(null)} width={520}>
        {detail && (
          <Descriptions column={1} bordered size="small">
            <Descriptions.Item label="工单ID">{detail.id}</Descriptions.Item>
            <Descriptions.Item label="诉求内容">{detail.original_text}</Descriptions.Item>
            <Descriptions.Item label="类型">{optionLabel(ticketTypeOptions, detail.ticket_type)}</Descriptions.Item>
            <Descriptions.Item label="紧急度">{optionLabel(urgencyOptions, detail.urgency)}</Descriptions.Item>
            <Descriptions.Item label="预估费用">{detail.estimated_cost}</Descriptions.Item>
            <Descriptions.Item label="关联资产">{detail.related_asset_id || '-'}</Descriptions.Item>
            <Descriptions.Item label="负责人">{detail.assigned_to || '-'}</Descriptions.Item>
            <Descriptions.Item label="审批状态">{optionLabel(approvalOptions, detail.approval_status)}</Descriptions.Item>
            <Descriptions.Item label="处理状态">{optionLabel(processingOptions, detail.processing_status)}</Descriptions.Item>
            <Descriptions.Item label="创建时间">{new Date(detail.created_at).toLocaleString()}</Descriptions.Item>
            <Descriptions.Item label="更新时间">{new Date(detail.updated_at).toLocaleString()}</Descriptions.Item>
          </Descriptions>
        )}
      </Drawer>
    </PageContainer>
  );
};

export default TicketList;
