import { Button, Card, Input, List, Space, Tag, Typography, message } from 'antd';
import { ClearOutlined, SendOutlined } from '@ant-design/icons';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useState } from 'react';
import PageContainer from '@/components/PageContainer';
import { apiClient } from '@/services/api';

interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  meta?: string;
}

interface ChatResponse {
  intent_type: string;
  response: string;
  ticket_id?: number;
  confidence: number;
}

const examples = ['会议室投影坏了，帮我报修', '我想领用一个鼠标', '采购一台显示器需要多少钱审批', '公司 WiFi 密码是什么'];

const ChatInterface = () => {
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState<ChatMessage[]>([
    { role: 'assistant', content: '你好，我可以回答行政问题，也可以帮你创建报修、采购、领用类工单。' },
  ]);
  const queryClient = useQueryClient();

  const chat = useMutation({
    mutationFn: (messageText: string) => apiClient.post<ChatResponse>('/ai/chat', { message: messageText }),
    onSuccess: (data) => {
      setMessages((items) => [
        ...items,
        {
          role: 'assistant',
          content: data.response,
          meta: `意图：${data.intent_type}，置信度：${Math.round(data.confidence * 100)}%${data.ticket_id ? `，工单 #${data.ticket_id}` : ''}`,
        },
      ]);
      if (data.ticket_id) {
        queryClient.invalidateQueries({ queryKey: ['tickets'] });
      }
    },
    onError: () => message.error('智能助手暂时不可用'),
  });

  const send = (text = input) => {
    const value = text.trim();
    if (!value) return;
    setMessages((items) => [...items, { role: 'user', content: value }]);
    setInput('');
    chat.mutate(value);
  };

  return (
    <PageContainer
      title="智能助手"
      extra={
        <Button icon={<ClearOutlined />} onClick={() => setMessages([])}>
          清空对话
        </Button>
      }
    >
      <Space direction="vertical" style={{ width: '100%' }} size={16}>
        <Space wrap>
          {examples.map((item) => (
            <Button key={item} onClick={() => send(item)}>
              {item}
            </Button>
          ))}
        </Space>

        <Card style={{ minHeight: 420 }}>
          <List
            dataSource={messages}
            locale={{ emptyText: '输入行政问题，或描述需要报修、采购、领用的事项。' }}
            renderItem={(item) => (
              <List.Item>
                <List.Item.Meta
                  title={
                    <Space>
                      <Tag color={item.role === 'user' ? 'blue' : 'green'}>{item.role === 'user' ? '我' : '智能助手'}</Tag>
                      {item.meta && <Typography.Text type="secondary">{item.meta}</Typography.Text>}
                    </Space>
                  }
                  description={<Typography.Text>{item.content}</Typography.Text>}
                />
              </List.Item>
            )}
          />
        </Card>

        <Space.Compact style={{ width: '100%' }}>
          <Input
            value={input}
            onChange={(event) => setInput(event.target.value)}
            onPressEnter={() => send()}
            placeholder="例如：会议室投影坏了，帮我报修"
          />
          <Button type="primary" icon={<SendOutlined />} loading={chat.isPending} onClick={() => send()}>
            发送
          </Button>
        </Space.Compact>
      </Space>
    </PageContainer>
  );
};

export default ChatInterface;
