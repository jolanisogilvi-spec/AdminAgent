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
import { DeleteOutlined, EditOutlined, EyeOutlined, PlusOutlined, StockOutlined } from '@ant-design/icons';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useMemo, useState } from 'react';
import PageContainer from '@/components/PageContainer';
import { apiClient } from '@/services/api';
import type { Asset } from '@/types';

type AssetFormValues = {
  asset_code: string;
  name: string;
  category: Asset['category'];
  status: Asset['status'];
  owner_id?: number;
  current_stock: number;
  unit_price?: number;
  location?: string;
  description?: string;
};

const categoryOptions = [
  { value: 'it_equipment', label: 'IT设备' },
  { value: 'office_furniture', label: '办公家具' },
  { value: 'consumables', label: '耗材' },
  { value: 'other', label: '其他' },
];

const statusOptions = [
  { value: 'idle', label: '闲置' },
  { value: 'in_use', label: '使用中' },
  { value: 'maintenance', label: '维修中' },
  { value: 'scrapped', label: '已报废' },
];

const optionLabel = (options: { value: string; label: string }[], value?: string | null) =>
  options.find((item) => item.value === value)?.label || value || '-';

const statusColor: Record<Asset['status'], string> = {
  idle: 'green',
  in_use: 'blue',
  maintenance: 'orange',
  scrapped: 'red',
};

const AssetManagement = () => {
  const [open, setOpen] = useState(false);
  const [stockOpen, setStockOpen] = useState(false);
  const [editing, setEditing] = useState<Asset | null>(null);
  const [stockTarget, setStockTarget] = useState<Asset | null>(null);
  const [detail, setDetail] = useState<Asset | null>(null);
  const [keyword, setKeyword] = useState('');
  const [category, setCategory] = useState<Asset['category'] | 'all'>('all');
  const [status, setStatus] = useState<Asset['status'] | 'all'>('all');
  const [form] = Form.useForm<AssetFormValues>();
  const [stockForm] = Form.useForm<{ quantity: number }>();
  const queryClient = useQueryClient();

  const assets = useQuery({ queryKey: ['assets'], queryFn: () => apiClient.get<Asset[]>('/assets/') });

  const saveAsset = useMutation({
    mutationFn: (values: AssetFormValues) => {
      if (editing) {
        return apiClient.patch<Asset>(`/assets/${editing.id}`, values);
      }
      return apiClient.post<Asset>('/assets/', values);
    },
    onSuccess: () => {
      message.success(editing ? '资产已更新' : '资产已创建');
      setOpen(false);
      setEditing(null);
      form.resetFields();
      queryClient.invalidateQueries({ queryKey: ['assets'] });
    },
  });

  const updateStock = useMutation({
    mutationFn: ({ id, quantity }: { id: number; quantity: number }) => apiClient.post<Asset>(`/assets/${id}/stock?quantity=${quantity}`),
    onSuccess: () => {
      message.success('库存已更新');
      setStockOpen(false);
      setStockTarget(null);
      stockForm.resetFields();
      queryClient.invalidateQueries({ queryKey: ['assets'] });
    },
  });

  const deleteAsset = useMutation({
    mutationFn: (id: number) => apiClient.delete(`/assets/${id}`),
    onSuccess: () => {
      message.success('资产已删除');
      queryClient.invalidateQueries({ queryKey: ['assets'] });
    },
  });

  const dataSource = useMemo(() => {
    return (assets.data || []).filter((item) => {
      const text = `${item.asset_code} ${item.name} ${item.location || ''}`.toLowerCase();
      return (
        (!keyword || text.includes(keyword.toLowerCase())) &&
        (category === 'all' || item.category === category) &&
        (status === 'all' || item.status === status)
      );
    });
  }, [assets.data, category, keyword, status]);

  const stats = useMemo(() => {
    const items = assets.data || [];
    return {
      total: items.length,
      idle: items.filter((item) => item.status === 'idle').length,
      maintenance: items.filter((item) => item.status === 'maintenance').length,
      stock: items.reduce((sum, item) => sum + item.current_stock, 0),
    };
  }, [assets.data]);

  const openCreate = () => {
    setEditing(null);
    form.resetFields();
    form.setFieldsValue({ category: 'it_equipment', status: 'idle', current_stock: 1 });
    setOpen(true);
  };

  const openEdit = (record: Asset) => {
    setEditing(record);
    form.setFieldsValue({
      asset_code: record.asset_code,
      name: record.name,
      category: record.category,
      status: record.status,
      owner_id: record.owner_id || undefined,
      current_stock: record.current_stock,
      unit_price: record.unit_price || undefined,
      location: record.location || undefined,
      description: record.description || undefined,
    });
    setOpen(true);
  };

  return (
    <PageContainer
      title="资产管理"
      extra={
        <Button type="primary" icon={<PlusOutlined />} onClick={openCreate}>
          新增资产
        </Button>
      }
    >
      <Space direction="vertical" size={16} style={{ width: '100%' }}>
        <Space wrap size={24}>
          <Statistic title="资产总数" value={stats.total} />
          <Statistic title="闲置资产" value={stats.idle} />
          <Statistic title="维修中" value={stats.maintenance} />
          <Statistic title="库存总量" value={stats.stock} />
        </Space>

        <Space wrap>
          <Input.Search placeholder="搜索编号、名称、位置" allowClear onSearch={setKeyword} onChange={(e) => setKeyword(e.target.value)} />
          <Select style={{ width: 150 }} value={category} onChange={setCategory} options={[{ value: 'all', label: '全部分类' }, ...categoryOptions]} />
          <Select style={{ width: 140 }} value={status} onChange={setStatus} options={[{ value: 'all', label: '全部状态' }, ...statusOptions]} />
        </Space>

        <Table<Asset>
          rowKey="id"
          loading={assets.isLoading}
          dataSource={dataSource}
          pagination={{ pageSize: 8, showSizeChanger: false }}
          columns={[
            { title: '编号', dataIndex: 'asset_code', width: 140 },
            { title: '名称', dataIndex: 'name', ellipsis: true },
            { title: '分类', dataIndex: 'category', width: 120, render: (value) => optionLabel(categoryOptions, value) },
            { title: '状态', dataIndex: 'status', width: 110, render: (value: Asset['status']) => <Tag color={statusColor[value]}>{optionLabel(statusOptions, value)}</Tag> },
            { title: '库存', dataIndex: 'current_stock', width: 80 },
            { title: '位置', dataIndex: 'location', ellipsis: true },
            {
              title: '操作',
              width: 180,
              render: (_, record) => (
                <Space>
                  <Button size="small" icon={<EyeOutlined />} onClick={() => setDetail(record)} />
                  <Button size="small" icon={<EditOutlined />} onClick={() => openEdit(record)} />
                  <Button
                    size="small"
                    icon={<StockOutlined />}
                    onClick={() => {
                      setStockTarget(record);
                      stockForm.setFieldsValue({ quantity: 0 });
                      setStockOpen(true);
                    }}
                  />
                  <Popconfirm title="删除资产" description="确认删除这项资产？" onConfirm={() => deleteAsset.mutate(record.id)}>
                    <Button size="small" danger icon={<DeleteOutlined />} />
                  </Popconfirm>
                </Space>
              ),
            },
          ]}
        />
      </Space>

      <Modal
        title={editing ? '编辑资产' : '新增资产'}
        open={open}
        onCancel={() => {
          setOpen(false);
          setEditing(null);
        }}
        onOk={() => form.submit()}
        confirmLoading={saveAsset.isPending}
        destroyOnHidden
      >
        <Form form={form} layout="vertical" onFinish={(values) => saveAsset.mutate(values)}>
          <Form.Item name="asset_code" label="资产编号" rules={[{ required: true, message: '请输入资产编号' }]}>
            <Input disabled={!!editing} />
          </Form.Item>
          <Form.Item name="name" label="资产名称" rules={[{ required: true, message: '请输入资产名称' }]}>
            <Input />
          </Form.Item>
          <Space wrap style={{ width: '100%' }} align="start">
            <Form.Item name="category" label="分类">
              <Select style={{ width: 160 }} options={categoryOptions} />
            </Form.Item>
            <Form.Item name="status" label="状态">
              <Select style={{ width: 140 }} options={statusOptions} />
            </Form.Item>
            <Form.Item name="current_stock" label="库存">
              <InputNumber min={0} style={{ width: 120 }} />
            </Form.Item>
          </Space>
          <Space wrap style={{ width: '100%' }} align="start">
            <Form.Item name="owner_id" label="使用人ID">
              <InputNumber min={1} style={{ width: 140 }} />
            </Form.Item>
            <Form.Item name="unit_price" label="单价">
              <InputNumber min={0} style={{ width: 140 }} />
            </Form.Item>
          </Space>
          <Form.Item name="location" label="位置">
            <Input />
          </Form.Item>
          <Form.Item name="description" label="说明">
            <Input.TextArea rows={3} />
          </Form.Item>
        </Form>
      </Modal>

      <Modal
        title={stockTarget ? `调整库存：${stockTarget.name}` : '调整库存'}
        open={stockOpen}
        onCancel={() => setStockOpen(false)}
        onOk={() => stockForm.submit()}
        confirmLoading={updateStock.isPending}
        destroyOnHidden
      >
        <Form
          form={stockForm}
          layout="vertical"
          onFinish={(values) => stockTarget && updateStock.mutate({ id: stockTarget.id, quantity: values.quantity })}
        >
          <Form.Item name="quantity" label="库存变化量" rules={[{ required: true, message: '请输入变化量' }]}>
            <InputNumber style={{ width: '100%' }} placeholder="入库填正数，出库填负数" />
          </Form.Item>
        </Form>
      </Modal>

      <Drawer title="资产详情" open={!!detail} onClose={() => setDetail(null)} width={520}>
        {detail && (
          <Descriptions column={1} bordered size="small">
            <Descriptions.Item label="编号">{detail.asset_code}</Descriptions.Item>
            <Descriptions.Item label="名称">{detail.name}</Descriptions.Item>
            <Descriptions.Item label="分类">{optionLabel(categoryOptions, detail.category)}</Descriptions.Item>
            <Descriptions.Item label="状态">{optionLabel(statusOptions, detail.status)}</Descriptions.Item>
            <Descriptions.Item label="库存">{detail.current_stock}</Descriptions.Item>
            <Descriptions.Item label="使用人">{detail.owner_id || '-'}</Descriptions.Item>
            <Descriptions.Item label="单价">{detail.unit_price || '-'}</Descriptions.Item>
            <Descriptions.Item label="位置">{detail.location || '-'}</Descriptions.Item>
            <Descriptions.Item label="说明">{detail.description || '-'}</Descriptions.Item>
          </Descriptions>
        )}
      </Drawer>
    </PageContainer>
  );
};

export default AssetManagement;
