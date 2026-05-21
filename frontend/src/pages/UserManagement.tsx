import {
  Button,
  Form,
  Input,
  Modal,
  Popconfirm,
  Select,
  Space,
  Statistic,
  Switch,
  Table,
  Tag,
  message,
} from 'antd';
import { DeleteOutlined, EditOutlined, PlusOutlined } from '@ant-design/icons';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useMemo, useState } from 'react';
import PageContainer from '@/components/PageContainer';
import { apiClient } from '@/services/api';
import type { ManagedUser, UserRole } from '@/types';

type UserFormValues = {
  username: string;
  password?: string;
  full_name: string;
  role: UserRole;
  department: string;
  email?: string;
  phone?: string;
  is_active: boolean;
};

const roleOptions: { value: UserRole; label: string }[] = [
  { value: 'employee', label: '员工' },
  { value: 'admin_staff', label: '行政人员' },
  { value: 'manager', label: '部门主管' },
  { value: 'sys_admin', label: '系统管理员' },
];

const roleColor: Record<UserRole, string> = {
  employee: 'default',
  admin_staff: 'blue',
  manager: 'gold',
  sys_admin: 'red',
};

const roleLabel = (role: UserRole) => roleOptions.find((item) => item.value === role)?.label || role;

const UserManagement = () => {
  const [open, setOpen] = useState(false);
  const [editing, setEditing] = useState<ManagedUser | null>(null);
  const [keyword, setKeyword] = useState('');
  const [role, setRole] = useState<UserRole | 'all'>('all');
  const [form] = Form.useForm<UserFormValues>();
  const queryClient = useQueryClient();

  const users = useQuery({
    queryKey: ['users'],
    queryFn: () => apiClient.get<ManagedUser[]>('/users/'),
  });

  const saveUser = useMutation({
    mutationFn: (values: UserFormValues) => {
      const payload = { ...values };
      if (!payload.password) {
        delete payload.password;
      }
      if (editing) {
        return apiClient.patch<ManagedUser>(`/users/${editing.id}`, payload);
      }
      return apiClient.post<ManagedUser>('/users/', payload);
    },
    onSuccess: () => {
      message.success(editing ? '用户已更新' : '用户已添加');
      setOpen(false);
      setEditing(null);
      form.resetFields();
      queryClient.invalidateQueries({ queryKey: ['users'] });
    },
  });

  const toggleActive = useMutation({
    mutationFn: (user: ManagedUser) => apiClient.patch<ManagedUser>(`/users/${user.id}`, { is_active: !user.is_active }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] });
    },
  });

  const deleteUser = useMutation({
    mutationFn: (id: number) => apiClient.delete(`/users/${id}`),
    onSuccess: () => {
      message.success('用户已删除');
      queryClient.invalidateQueries({ queryKey: ['users'] });
    },
  });

  const dataSource = useMemo(() => {
    return (users.data || []).filter((item) => {
      const text = `${item.username} ${item.full_name} ${item.department}`.toLowerCase();
      return (!keyword || text.includes(keyword.toLowerCase())) && (role === 'all' || item.role === role);
    });
  }, [keyword, role, users.data]);

  const stats = useMemo(() => {
    const items = users.data || [];
    return {
      total: items.length,
      active: items.filter((item) => item.is_active).length,
      admins: items.filter((item) => item.role === 'sys_admin').length,
      staff: items.filter((item) => item.role === 'admin_staff').length,
    };
  }, [users.data]);

  const openCreate = () => {
    setEditing(null);
    form.resetFields();
    form.setFieldsValue({ role: 'employee', is_active: true, department: '默认部门' });
    setOpen(true);
  };

  const openEdit = (record: ManagedUser) => {
    setEditing(record);
    form.setFieldsValue({
      username: record.username,
      full_name: record.full_name,
      role: record.role,
      department: record.department,
      email: record.email || undefined,
      phone: record.phone || undefined,
      is_active: record.is_active,
    });
    setOpen(true);
  };

  return (
    <PageContainer
      title="用户管理"
      extra={
        <Button type="primary" icon={<PlusOutlined />} onClick={openCreate}>
          添加用户
        </Button>
      }
    >
      <Space direction="vertical" size={16} style={{ width: '100%' }}>
        <Space wrap size={24}>
          <Statistic title="用户总数" value={stats.total} />
          <Statistic title="启用用户" value={stats.active} />
          <Statistic title="行政人员" value={stats.staff} />
          <Statistic title="系统管理员" value={stats.admins} />
        </Space>

        <Space wrap>
          <Input.Search placeholder="搜索用户名、姓名、部门" allowClear onSearch={setKeyword} onChange={(event) => setKeyword(event.target.value)} />
          <Select style={{ width: 150 }} value={role} onChange={setRole} options={[{ value: 'all', label: '全部角色' }, ...roleOptions]} />
        </Space>

        <Table<ManagedUser>
          rowKey="id"
          loading={users.isLoading}
          dataSource={dataSource}
          pagination={{ pageSize: 8, showSizeChanger: false }}
          columns={[
            { title: '用户名', dataIndex: 'username', width: 120 },
            { title: '姓名', dataIndex: 'full_name', width: 120 },
            { title: '角色', dataIndex: 'role', width: 130, render: (value: UserRole) => <Tag color={roleColor[value]}>{roleLabel(value)}</Tag> },
            { title: '部门', dataIndex: 'department', width: 120 },
            {
              title: '启用',
              dataIndex: 'is_active',
              width: 90,
              render: (value: boolean, record) => <Switch checked={value} onChange={() => toggleActive.mutate(record)} />,
            },
            {
              title: '操作',
              width: 110,
              render: (_, record) => (
                <Space>
                  <Button size="small" icon={<EditOutlined />} onClick={() => openEdit(record)} />
                  <Popconfirm title="删除用户" description={`确认删除 ${record.full_name}？`} onConfirm={() => deleteUser.mutate(record.id)}>
                    <Button size="small" danger icon={<DeleteOutlined />} />
                  </Popconfirm>
                </Space>
              ),
            },
          ]}
        />
      </Space>

      <Modal
        title={editing ? '编辑用户' : '添加用户'}
        open={open}
        onCancel={() => {
          setOpen(false);
          setEditing(null);
        }}
        onOk={() => form.submit()}
        confirmLoading={saveUser.isPending}
        destroyOnHidden
      >
        <Form form={form} layout="vertical" onFinish={(values) => saveUser.mutate(values)}>
          <Form.Item name="username" label="用户名" rules={[{ required: true, message: '请输入用户名' }]}>
            <Input disabled={!!editing} />
          </Form.Item>
          <Form.Item
            name="password"
            label={editing ? '重置密码' : '登录密码'}
            rules={editing ? undefined : [{ required: true, message: '请输入登录密码' }]}
          >
            <Input.Password placeholder={editing ? '不填写则不修改密码' : '请输入登录密码'} />
          </Form.Item>
          <Form.Item name="full_name" label="姓名" rules={[{ required: true, message: '请输入姓名' }]}>
            <Input />
          </Form.Item>
          <Form.Item name="role" label="角色" rules={[{ required: true, message: '请选择角色' }]}>
            <Select options={roleOptions} />
          </Form.Item>
          <Form.Item name="department" label="部门" rules={[{ required: true, message: '请输入部门' }]}>
            <Input />
          </Form.Item>
          <Form.Item name="email" label="邮箱">
            <Input />
          </Form.Item>
          <Form.Item name="phone" label="电话">
            <Input />
          </Form.Item>
          <Form.Item name="is_active" label="启用账号" valuePropName="checked">
            <Switch checkedChildren="启用" unCheckedChildren="停用" />
          </Form.Item>
        </Form>
      </Modal>
    </PageContainer>
  );
};

export default UserManagement;
