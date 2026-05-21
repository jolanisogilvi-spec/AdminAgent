import { Button, Form, Input, InputNumber, Modal, Popconfirm, Select, Space, Statistic, Table, Tag, message } from 'antd';
import { DeleteOutlined, EditOutlined, PlusOutlined } from '@ant-design/icons';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useMemo, useState } from 'react';
import PageContainer from '@/components/PageContainer';
import { apiClient } from '@/services/api';
import type { Task } from '@/types';

type TaskFormValues = {
  title: string;
  description?: string;
  related_ticket_id?: number;
  assigned_to: number;
  status: Task['status'];
  priority: number;
  due_date?: string;
};

const statusOptions = [
  { value: 'todo', label: '待办' },
  { value: 'in_progress', label: '进行中' },
  { value: 'completed', label: '已完成' },
  { value: 'cancelled', label: '已取消' },
];

const statusColor: Record<Task['status'], string> = {
  todo: 'default',
  in_progress: 'blue',
  completed: 'green',
  cancelled: 'red',
};

const statusLabel = (value: string) => statusOptions.find((item) => item.value === value)?.label || value;

const TaskBoard = () => {
  const [open, setOpen] = useState(false);
  const [editing, setEditing] = useState<Task | null>(null);
  const [statusFilter, setStatusFilter] = useState<Task['status'] | 'all'>('all');
  const [keyword, setKeyword] = useState('');
  const [form] = Form.useForm<TaskFormValues>();
  const queryClient = useQueryClient();

  const tasks = useQuery({ queryKey: ['tasks'], queryFn: () => apiClient.get<Task[]>('/tasks/') });

  const saveTask = useMutation({
    mutationFn: (values: TaskFormValues) => {
      const payload = {
        ...values,
        due_date: values.due_date || null,
      };
      if (editing) {
        return apiClient.patch<Task>(`/tasks/${editing.id}`, payload);
      }
      return apiClient.post<Task>('/tasks/', payload);
    },
    onSuccess: () => {
      message.success(editing ? '任务已更新' : '任务已创建');
      setOpen(false);
      setEditing(null);
      form.resetFields();
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
    },
  });

  const deleteTask = useMutation({
    mutationFn: (id: number) => apiClient.delete(`/tasks/${id}`),
    onSuccess: () => {
      message.success('任务已删除');
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
    },
  });

  const quickStatus = useMutation({
    mutationFn: ({ id, status }: { id: number; status: Task['status'] }) => apiClient.patch<Task>(`/tasks/${id}`, { status }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
    },
  });

  const dataSource = useMemo(() => {
    return (tasks.data || []).filter((item) => {
      const matchesKeyword = !keyword || `${item.title} ${item.description || ''}`.toLowerCase().includes(keyword.toLowerCase());
      const matchesStatus = statusFilter === 'all' || item.status === statusFilter;
      return matchesKeyword && matchesStatus;
    });
  }, [keyword, statusFilter, tasks.data]);

  const stats = useMemo(() => {
    const items = tasks.data || [];
    return {
      total: items.length,
      todo: items.filter((item) => item.status === 'todo').length,
      progress: items.filter((item) => item.status === 'in_progress').length,
      done: items.filter((item) => item.status === 'completed').length,
    };
  }, [tasks.data]);

  const openCreate = () => {
    setEditing(null);
    form.resetFields();
    form.setFieldsValue({ assigned_to: 1, priority: 0, status: 'todo' });
    setOpen(true);
  };

  const openEdit = (record: Task) => {
    setEditing(record);
    form.setFieldsValue({
      title: record.title,
      description: record.description || undefined,
      related_ticket_id: record.related_ticket_id || undefined,
      assigned_to: record.assigned_to,
      status: record.status,
      priority: record.priority,
      due_date: record.due_date || undefined,
    });
    setOpen(true);
  };

  return (
    <PageContainer
      title="任务看板"
      extra={
        <Button type="primary" icon={<PlusOutlined />} onClick={openCreate}>
          新增任务
        </Button>
      }
    >
      <Space direction="vertical" size={16} style={{ width: '100%' }}>
        <Space wrap size={24}>
          <Statistic title="任务总数" value={stats.total} />
          <Statistic title="待办" value={stats.todo} />
          <Statistic title="进行中" value={stats.progress} />
          <Statistic title="已完成" value={stats.done} />
        </Space>

        <Space wrap>
          <Input.Search placeholder="搜索任务" allowClear onSearch={setKeyword} onChange={(e) => setKeyword(e.target.value)} />
          <Select style={{ width: 140 }} value={statusFilter} onChange={setStatusFilter} options={[{ value: 'all', label: '全部状态' }, ...statusOptions]} />
        </Space>

        <Table<Task>
          rowKey="id"
          loading={tasks.isLoading}
          dataSource={dataSource}
          pagination={{ pageSize: 8, showSizeChanger: false }}
          columns={[
            { title: 'ID', dataIndex: 'id', width: 70 },
            { title: '任务', dataIndex: 'title', ellipsis: true },
            { title: '关联工单', dataIndex: 'related_ticket_id', width: 100, render: (value) => value || '-' },
            { title: '负责人ID', dataIndex: 'assigned_to', width: 100 },
            { title: '优先级', dataIndex: 'priority', width: 90 },
            {
              title: '状态',
              dataIndex: 'status',
              width: 130,
              render: (value: Task['status']) => <Tag color={statusColor[value]}>{statusLabel(value)}</Tag>,
            },
            {
              title: '快捷流转',
              width: 180,
              render: (_, record) => (
                <Space>
                  <Button size="small" disabled={record.status === 'in_progress'} onClick={() => quickStatus.mutate({ id: record.id, status: 'in_progress' })}>
                    开始
                  </Button>
                  <Button size="small" disabled={record.status === 'completed'} onClick={() => quickStatus.mutate({ id: record.id, status: 'completed' })}>
                    完成
                  </Button>
                </Space>
              ),
            },
            {
              title: '操作',
              width: 110,
              render: (_, record) => (
                <Space>
                  <Button size="small" icon={<EditOutlined />} onClick={() => openEdit(record)} />
                  <Popconfirm title="删除任务" description="确认删除这条任务？" onConfirm={() => deleteTask.mutate(record.id)}>
                    <Button size="small" danger icon={<DeleteOutlined />} />
                  </Popconfirm>
                </Space>
              ),
            },
          ]}
        />
      </Space>

      <Modal
        title={editing ? '编辑任务' : '新增任务'}
        open={open}
        onCancel={() => {
          setOpen(false);
          setEditing(null);
        }}
        onOk={() => form.submit()}
        confirmLoading={saveTask.isPending}
        destroyOnHidden
      >
        <Form form={form} layout="vertical" onFinish={(values) => saveTask.mutate(values)}>
          <Form.Item name="title" label="任务名称" rules={[{ required: true, message: '请输入任务名称' }]}>
            <Input />
          </Form.Item>
          <Form.Item name="description" label="描述">
            <Input.TextArea rows={3} />
          </Form.Item>
          <Space wrap style={{ width: '100%' }} align="start">
            <Form.Item name="related_ticket_id" label="关联工单ID">
              <InputNumber min={1} style={{ width: 130 }} />
            </Form.Item>
            <Form.Item name="assigned_to" label="负责人ID" rules={[{ required: true }]}>
              <InputNumber min={1} style={{ width: 130 }} />
            </Form.Item>
            <Form.Item name="priority" label="优先级">
              <InputNumber style={{ width: 110 }} />
            </Form.Item>
          </Space>
          <Form.Item name="status" label="状态">
            <Select options={statusOptions} />
          </Form.Item>
          <Form.Item name="due_date" label="截止时间">
            <Input placeholder="例如 2026-05-20T18:00:00" />
          </Form.Item>
        </Form>
      </Modal>
    </PageContainer>
  );
};

export default TaskBoard;
