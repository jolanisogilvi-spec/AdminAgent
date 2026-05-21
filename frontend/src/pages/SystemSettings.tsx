import { Alert, Button, Card, Col, Form, Input, InputNumber, Row, Space, Switch, Tabs, message } from 'antd';
import { ReloadOutlined, SaveOutlined } from '@ant-design/icons';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useEffect, useMemo } from 'react';
import PageContainer from '@/components/PageContainer';
import { apiClient } from '@/services/api';
import type { SysConfig } from '@/types';

type SettingValue = string | number | boolean | null | undefined;
type SettingsFormValues = Record<string, SettingValue>;

type SettingDefinition = {
  key: string;
  label: string;
  description: string;
  category: 'basic' | 'ai' | 'approval' | 'knowledge';
  defaultValue: string;
  sensitive?: boolean;
  input: 'text' | 'password' | 'number' | 'switch';
  min?: number;
  max?: number;
  step?: number;
};

const settings: SettingDefinition[] = [
  {
    key: 'SYSTEM_NAME',
    label: '系统名称',
    description: '显示在系统页面和浏览器标题中的名称。',
    category: 'basic',
    defaultValue: 'Admin Agent',
    input: 'text',
  },
  {
    key: 'SESSION_TIMEOUT',
    label: '登录有效期',
    description: '用户登录后保持在线的时间，单位为分钟。',
    category: 'basic',
    defaultValue: '10080',
    input: 'number',
    min: 1,
  },
  {
    key: 'MAX_UPLOAD_SIZE',
    label: '附件上传上限',
    description: '单个附件允许上传的最大大小，单位为 MB。',
    category: 'basic',
    defaultValue: '10',
    input: 'number',
    min: 1,
  },
  {
    key: 'AUTO_ASSIGN_ADMIN',
    label: '自动分派工单',
    description: '开启后，新工单可自动进入行政处理流程。',
    category: 'basic',
    defaultValue: 'true',
    input: 'switch',
  },
  {
    key: 'LLM_BASE_URL',
    label: '模型服务地址',
    description: '兼容 OpenAI 协议的接口地址。',
    category: 'ai',
    defaultValue: 'https://api.openai.com/v1',
    input: 'text',
  },
  {
    key: 'LLM_API_KEY',
    label: '模型 API 密钥',
    description: '调用模型服务使用的密钥，页面会按敏感信息处理。',
    category: 'ai',
    defaultValue: 'sk-your-api-key',
    input: 'password',
    sensitive: true,
  },
  {
    key: 'LLM_MODEL',
    label: '模型名称',
    description: '智能助手和工单解析使用的模型。',
    category: 'ai',
    defaultValue: 'gpt-4o',
    input: 'text',
  },
  {
    key: 'LLM_TEMPERATURE',
    label: '回复随机性',
    description: '数值越低越稳定，越高越发散。',
    category: 'ai',
    defaultValue: '0.2',
    input: 'number',
    min: 0,
    max: 2,
    step: 0.1,
  },
  {
    key: 'LLM_MAX_TOKENS',
    label: '最大回复长度',
    description: '单次模型回复允许使用的最大 token 数。',
    category: 'ai',
    defaultValue: '2000',
    input: 'number',
    min: 1,
  },
  {
    key: 'APPROVAL_THRESHOLD',
    label: '主管审批金额',
    description: '工单预估费用达到该金额后进入主管审批。',
    category: 'approval',
    defaultValue: '1000',
    input: 'number',
    min: 0,
  },
  {
    key: 'FINANCE_APPROVAL_THRESHOLD',
    label: '财务审批金额',
    description: '工单预估费用达到该金额后进入财务审批。',
    category: 'approval',
    defaultValue: '5000',
    input: 'number',
    min: 0,
  },
  {
    key: 'EMBEDDING_BASE_URL',
    label: '向量服务地址',
    description: '知识库向量化使用的接口地址，可与聊天模型服务地址不同。',
    category: 'knowledge',
    defaultValue: 'https://api.openai.com/v1',
    input: 'text',
  },
  {
    key: 'EMBEDDING_MODEL',
    label: '知识向量模型',
    description: '知识库同步和语义检索使用的向量模型。',
    category: 'knowledge',
    defaultValue: 'text-embedding-3-small',
    input: 'text',
  },
  {
    key: 'VECTOR_DB_PATH',
    label: '知识库索引目录',
    description: '本地向量索引保存目录。',
    category: 'knowledge',
    defaultValue: './chroma_data',
    input: 'text',
  },
];

const categoryTitles = {
  basic: '基础设置',
  ai: 'AI 模型',
  approval: '审批规则',
  knowledge: '知识库',
};

const parseValue = (definition: SettingDefinition, value?: string) => {
  const rawValue = value ?? definition.defaultValue;
  if (definition.input === 'switch') return rawValue === 'true';
  if (definition.input === 'number') return Number(rawValue);
  return rawValue;
};

const serializeValue = (definition: SettingDefinition, value: SettingValue) => {
  if (definition.input === 'switch') return value ? 'true' : 'false';
  if (value === null || value === undefined) return '';
  return String(value);
};

const SystemSettings = () => {
  const [form] = Form.useForm<SettingsFormValues>();
  const queryClient = useQueryClient();

  const configs = useQuery({
    queryKey: ['configs'],
    queryFn: () => apiClient.get<SysConfig[]>('/configs/?include_sensitive=true'),
  });

  const configMap = useMemo(() => {
    return new Map((configs.data || []).map((item) => [item.config_key, item]));
  }, [configs.data]);

  useEffect(() => {
    const values: SettingsFormValues = {};
    settings.forEach((definition) => {
      values[definition.key] = parseValue(definition, configMap.get(definition.key)?.config_value);
    });
    form.setFieldsValue(values);
  }, [configMap, form]);

  const initDefaults = useMutation({
    mutationFn: () => apiClient.post('/configs/init'),
    onSuccess: () => {
      message.success('默认设置已补齐');
      queryClient.invalidateQueries({ queryKey: ['configs'] });
    },
  });

  const saveSettings = useMutation({
    mutationFn: async (values: SettingsFormValues) => {
      await Promise.all(
        settings.map((definition) => {
          const payload = {
            config_key: definition.key,
            config_value: serializeValue(definition, values[definition.key]),
            description: definition.description,
            is_sensitive: !!definition.sensitive,
          };
          if (configMap.has(definition.key)) {
            return apiClient.put(`/configs/${definition.key}`, payload);
          }
          return apiClient.post('/configs/', payload);
        })
      );
    },
    onSuccess: () => {
      message.success('系统设置已保存');
      queryClient.invalidateQueries({ queryKey: ['configs'] });
    },
  });

  const renderInput = (definition: SettingDefinition) => {
    if (definition.input === 'password') {
      return <Input.Password placeholder="请输入密钥" autoComplete="new-password" />;
    }
    if (definition.input === 'number') {
      return <InputNumber min={definition.min} max={definition.max} step={definition.step} style={{ width: '100%' }} />;
    }
    if (definition.input === 'switch') {
      return <Switch checkedChildren="开启" unCheckedChildren="关闭" />;
    }
    return <Input />;
  };

  const renderSection = (category: SettingDefinition['category']) => (
    <Row gutter={[16, 16]}>
      {settings
        .filter((definition) => definition.category === category)
        .map((definition) => (
          <Col xs={24} lg={12} key={definition.key}>
            <Card size="small" title={definition.label}>
              <Form.Item
                name={definition.key}
                valuePropName={definition.input === 'switch' ? 'checked' : 'value'}
                rules={[{ required: definition.input !== 'switch', message: `请填写${definition.label}` }]}
                style={{ marginBottom: 8 }}
              >
                {renderInput(definition)}
              </Form.Item>
              <div style={{ color: '#667085', fontSize: 13 }}>{definition.description}</div>
            </Card>
          </Col>
        ))}
    </Row>
  );

  return (
    <PageContainer
      title="系统设置"
      extra={
        <Space>
          <Button icon={<ReloadOutlined />} loading={initDefaults.isPending} onClick={() => initDefaults.mutate()}>
            补齐默认设置
          </Button>
          <Button type="primary" icon={<SaveOutlined />} loading={saveSettings.isPending} onClick={() => form.submit()}>
            保存设置
          </Button>
        </Space>
      }
    >
      <Space direction="vertical" size={16} style={{ width: '100%' }}>
        <Alert
          type="info"
          showIcon
          message="这里维护系统运行参数"
          description="这些设置会保存到底层配置表中，但页面只展示业务字段。修改 AI 密钥、审批金额等设置后，后续功能会读取新的配置。"
        />

        <Form form={form} layout="vertical" onFinish={(values) => saveSettings.mutate(values)}>
          <Tabs
            items={[
              { key: 'basic', label: categoryTitles.basic, children: renderSection('basic') },
              { key: 'ai', label: categoryTitles.ai, children: renderSection('ai') },
              { key: 'approval', label: categoryTitles.approval, children: renderSection('approval') },
              { key: 'knowledge', label: categoryTitles.knowledge, children: renderSection('knowledge') },
            ]}
          />
        </Form>
      </Space>
    </PageContainer>
  );
};

export default SystemSettings;
