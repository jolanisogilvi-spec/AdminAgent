import { Button, Form, Input, Modal, Space, Statistic, Table, Tag, message } from 'antd';
import { CheckOutlined, CloseOutlined } from '@ant-design/icons';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useMemo, useState } from 'react';
import PageContainer from '@/components/PageContainer';
import { apiClient } from '@/services/api';
import type { Ticket } from '@/types';

type ApprovalType = 'manager' | 'finance';
type ApprovalAction = 'approve' | 'reject';
type ApprovalRecord = Ticket & { approvalType: ApprovalType };

const approvalLabels: Record<ApprovalType, string> = {
  manager: '主管审批',
  finance: '财务审批',
};

const ApprovalCenter = () => {
  const [current, setCurrent] = useState<ApprovalRecord | null>(null);
  const [action, setAction] = useState<ApprovalAction>('approve');
  const [form] = Form.useForm<{ comment?: string }>();
  const queryClient = useQueryClient();

  const manager = useQuery({
    queryKey: ['approvals', 'manager'],
    queryFn: () => apiClient.get<Ticket[]>('/approvals/pending?approval_type=manager'),
  });
  const finance = useQuery({
    queryKey: ['approvals', 'finance'],
    queryFn: () => apiClient.get<Ticket[]>('/approvals/pending?approval_type=finance'),
  });

  const submitApproval = useMutation({
    mutationFn: ({ record, action, comment }: { record: ApprovalRecord; action: ApprovalAction; comment?: string }) => {
      if (action === 'approve') {
        return apiClient.post<Ticket>(`/approvals/tickets/${record.id}/approve?approval_type=${record.approvalType}`, {
          comment: comment || '同意',
        });
      }
      return apiClient.post<Ticket>(`/approvals/tickets/${record.id}/reject`, { comment: comment || '驳回' });
    },
    onSuccess: () => {
      message.success(action === 'approve' ? '审批已通过' : '工单已驳回');
      setCurrent(null);
      form.resetFields();
      queryClient.invalidateQueries({ queryKey: ['approvals'] });
      queryClient.invalidateQueries({ queryKey: ['tickets'] });
    },
  });

  const data = useMemo(
    () => [
      ...(manager.data || []).map((item) => ({ ...item, approvalType: 'manager' as const })),
      ...(finance.data || []).map((item) => ({ ...item, approvalType: 'finance' as const })),
    ],
    [finance.data, manager.data]
  );

  const openAction = (record: ApprovalRecord, nextAction: ApprovalAction) => {
    setCurrent(record);
    setAction(nextAction);
    form.setFieldsValue({ comment: nextAction === 'approve' ? '同意' : '' });
  };

  return (
    <PageContainer title="审批中心">
      <Space direction="vertical" size={16} style={{ width: '100%' }}>
        <Space wrap size={24}>
          <Statistic title="待主管审批" value={manager.data?.length || 0} />
          <Statistic title="待财务审批" value={finance.data?.length || 0} />
          <Statistic title="待审批总数" value={data.length} />
        </Space>

        <Table<ApprovalRecord>
          rowKey={(record) => `${record.approvalType}-${record.id}`}
          loading={manager.isLoading || finance.isLoading}
          dataSource={data}
          pagination={{ pageSize: 8, showSizeChanger: false }}
          columns={[
            { title: '工单ID', dataIndex: 'id', width: 90 },
            { title: '诉求内容', dataIndex: 'original_text', ellipsis: true },
            { title: '审批类型', dataIndex: 'approvalType', width: 120, render: (value: ApprovalType) => <Tag>{approvalLabels[value]}</Tag> },
            { title: '费用', dataIndex: 'estimated_cost', width: 100 },
            { title: '紧急度', dataIndex: 'urgency', width: 100 },
            {
              title: '操作',
              width: 170,
              render: (_, record) => (
                <Space>
                  <Button size="small" type="primary" icon={<CheckOutlined />} onClick={() => openAction(record, 'approve')}>
                    通过
                  </Button>
                  <Button size="small" danger icon={<CloseOutlined />} onClick={() => openAction(record, 'reject')}>
                    驳回
                  </Button>
                </Space>
              ),
            },
          ]}
        />
      </Space>

      <Modal
        title={action === 'approve' ? '审批通过' : '驳回工单'}
        open={!!current}
        onCancel={() => setCurrent(null)}
        onOk={() => form.submit()}
        okButtonProps={{ danger: action === 'reject' }}
        confirmLoading={submitApproval.isPending}
        destroyOnHidden
      >
        {current && (
          <Space direction="vertical" style={{ width: '100%' }} size={12}>
            <div>工单 #{current.id}：{current.original_text}</div>
            <Form
              form={form}
              layout="vertical"
              onFinish={(values) => submitApproval.mutate({ record: current, action, comment: values.comment })}
            >
              <Form.Item
                name="comment"
                label="审批意见"
                rules={action === 'reject' ? [{ required: true, message: '驳回时必须填写原因' }] : undefined}
              >
                <Input.TextArea rows={4} placeholder="填写审批意见" />
              </Form.Item>
            </Form>
          </Space>
        )}
      </Modal>
    </PageContainer>
  );
};

export default ApprovalCenter;
