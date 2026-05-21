import { Button, Form, Input, Modal, Popconfirm, Select, Space, Statistic, Table, Tag, message } from 'antd';
import { DeleteOutlined, EditOutlined, PlusOutlined, SearchOutlined, SyncOutlined } from '@ant-design/icons';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useMemo, useState } from 'react';
import PageContainer from '@/components/PageContainer';
import { apiClient } from '@/services/api';
import type { Knowledge } from '@/types';

type KnowledgeFormValues = {
  title: string;
  content: string;
  category: string;
};

const defaultCategories = ['制度流程', '办公支持', '资产设备', '报销采购', '其他'];

const KnowledgeBase = () => {
  const [open, setOpen] = useState(false);
  const [editing, setEditing] = useState<Knowledge | null>(null);
  const [keyword, setKeyword] = useState('');
  const [category, setCategory] = useState<string>('all');
  const [searchResult, setSearchResult] = useState<string>('');
  const [form] = Form.useForm<KnowledgeFormValues>();
  const queryClient = useQueryClient();

  const knowledge = useQuery({
    queryKey: ['knowledge'],
    queryFn: () => apiClient.get<Knowledge[]>('/knowledge/?limit=100'),
  });

  const saveKnowledge = useMutation({
    mutationFn: (values: KnowledgeFormValues) => {
      if (editing) {
        return apiClient.put<Knowledge>(`/knowledge/${editing.id}`, values);
      }
      return apiClient.post<Knowledge>('/knowledge/', values);
    },
    onSuccess: () => {
      message.success(editing ? '知识已更新' : '知识已创建');
      setOpen(false);
      setEditing(null);
      form.resetFields();
      queryClient.invalidateQueries({ queryKey: ['knowledge'] });
    },
  });

  const deleteKnowledge = useMutation({
    mutationFn: (id: number) => apiClient.delete(`/knowledge/${id}`),
    onSuccess: () => {
      message.success('知识已删除');
      queryClient.invalidateQueries({ queryKey: ['knowledge'] });
    },
  });

  const syncKnowledge = useMutation({
    mutationFn: () => apiClient.post('/ai/knowledge/sync'),
    onSuccess: () => message.success('知识库已同步'),
  });

  const searchKnowledge = useMutation({
    mutationFn: (query: string) => apiClient.post<{ results: unknown[] }>('/knowledge/search', { query, n_results: 5 }),
    onSuccess: (data) => {
      setSearchResult(JSON.stringify(data.results || [], null, 2));
    },
  });

  const categories = useMemo(() => {
    const values = new Set(defaultCategories);
    (knowledge.data || []).forEach((item) => values.add(item.category));
    return Array.from(values);
  }, [knowledge.data]);

  const dataSource = useMemo(() => {
    return (knowledge.data || []).filter((item) => {
      const text = `${item.title} ${item.content}`.toLowerCase();
      return (!keyword || text.includes(keyword.toLowerCase())) && (category === 'all' || item.category === category);
    });
  }, [category, keyword, knowledge.data]);

  const openCreate = () => {
    setEditing(null);
    form.resetFields();
    form.setFieldsValue({ category: '制度流程' });
    setOpen(true);
  };

  const openEdit = (record: Knowledge) => {
    setEditing(record);
    form.setFieldsValue({
      title: record.title,
      content: record.content,
      category: record.category,
    });
    setOpen(true);
  };

  return (
    <PageContainer
      title="知识库"
      extra={
        <Space>
          <Button icon={<SyncOutlined />} loading={syncKnowledge.isPending} onClick={() => syncKnowledge.mutate()}>
            同步知识
          </Button>
          <Button type="primary" icon={<PlusOutlined />} onClick={openCreate}>
            新增知识
          </Button>
        </Space>
      }
    >
      <Space direction="vertical" size={16} style={{ width: '100%' }}>
        <Space wrap size={24}>
          <Statistic title="知识条目" value={knowledge.data?.length || 0} />
          <Statistic title="分类数量" value={categories.length} />
          <Statistic title="当前筛选" value={dataSource.length} />
        </Space>

        <Space wrap>
          <Input.Search placeholder="搜索标题或内容" allowClear onSearch={setKeyword} onChange={(e) => setKeyword(e.target.value)} />
          <Select
            style={{ width: 160 }}
            value={category}
            onChange={setCategory}
            options={[{ value: 'all', label: '全部分类' }, ...categories.map((item) => ({ value: item, label: item }))]}
          />
          <Button icon={<SearchOutlined />} loading={searchKnowledge.isPending} onClick={() => searchKnowledge.mutate(keyword || '行政流程')}>
            检索测试
          </Button>
        </Space>

        {searchResult && <Input.TextArea rows={4} value={searchResult} readOnly />}

        <Table<Knowledge>
          rowKey="id"
          loading={knowledge.isLoading}
          dataSource={dataSource}
          pagination={{ pageSize: 8, showSizeChanger: false }}
          columns={[
            { title: '标题', dataIndex: 'title', ellipsis: true },
            { title: '分类', dataIndex: 'category', width: 120, render: (value) => <Tag>{value}</Tag> },
            { title: '内容', dataIndex: 'content', ellipsis: true },
            { title: '浏览', dataIndex: 'view_count', width: 80 },
            {
              title: '操作',
              width: 110,
              render: (_, record) => (
                <Space>
                  <Button size="small" icon={<EditOutlined />} onClick={() => openEdit(record)} />
                  <Popconfirm title="删除知识" description="确认删除这条知识？" onConfirm={() => deleteKnowledge.mutate(record.id)}>
                    <Button size="small" danger icon={<DeleteOutlined />} />
                  </Popconfirm>
                </Space>
              ),
            },
          ]}
        />
      </Space>

      <Modal
        title={editing ? '编辑知识' : '新增知识'}
        open={open}
        onCancel={() => {
          setOpen(false);
          setEditing(null);
        }}
        onOk={() => form.submit()}
        confirmLoading={saveKnowledge.isPending}
        width={720}
        destroyOnHidden
      >
        <Form form={form} layout="vertical" onFinish={(values) => saveKnowledge.mutate(values)}>
          <Form.Item name="title" label="标题" rules={[{ required: true, message: '请输入标题' }]}>
            <Input />
          </Form.Item>
          <Form.Item name="category" label="分类" rules={[{ required: true, message: '请选择分类' }]}>
            <Select options={categories.map((item) => ({ value: item, label: item }))} />
          </Form.Item>
          <Form.Item name="content" label="内容" rules={[{ required: true, message: '请输入内容' }]}>
            <Input.TextArea rows={8} />
          </Form.Item>
        </Form>
      </Modal>
    </PageContainer>
  );
};

export default KnowledgeBase;
