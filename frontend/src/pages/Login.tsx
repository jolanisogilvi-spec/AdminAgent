import { Button, Card, Form, Input, message } from 'antd';
import { LockOutlined, UserOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { authApi } from '@/services/auth';
import { useAuthStore } from '@/stores';
import type { LoginRequest } from '@/types';
import './Login.css';

const Login = () => {
  const navigate = useNavigate();
  const { setAuth } = useAuthStore();
  const [form] = Form.useForm<LoginRequest>();

  const handleLogin = async (values: LoginRequest) => {
    try {
      const response = await authApi.login(values);
      setAuth(response.user, response.token);
      message.success('登录成功');
      navigate('/dashboard');
    } catch {
      message.error('登录失败，请检查用户名和密码');
    }
  };

  return (
    <div className="login-container">
      <Card className="login-card" title={<div className="login-title">行政智能体</div>}>
        <Form form={form} onFinish={handleLogin} size="large" initialValues={{ username: 'admin', password: 'admin123' }}>
          <Form.Item name="username" rules={[{ required: true, message: '请输入用户名' }]}>
            <Input prefix={<UserOutlined />} placeholder="用户名" />
          </Form.Item>
          <Form.Item name="password" rules={[{ required: true, message: '请输入密码' }]}>
            <Input.Password prefix={<LockOutlined />} placeholder="密码" />
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit" block>
              登录
            </Button>
          </Form.Item>
        </Form>
      </Card>
    </div>
  );
};

export default Login;
