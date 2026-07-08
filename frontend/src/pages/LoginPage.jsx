import { LockOutlined, UserOutlined } from '@ant-design/icons';
import { Button, Form, Input, Typography, message } from 'antd';
import { Link, useNavigate } from 'react-router-dom';
import { api, getErrorMessage } from '../api.js';

const { Title, Text } = Typography;

export default function LoginPage() {
  const navigate = useNavigate();
  const [messageApi, contextHolder] = message.useMessage();

  async function handleSubmit(values) {
    try {
      await api.post('/api/login', values);
      messageApi.success('登录成功');
      navigate('/home');
    } catch (error) {
      messageApi.error(getErrorMessage(error));
    }
  }

  return (
    <main className="auth-page">
      {contextHolder}
      <section className="auth-panel" aria-label="登录">
        <div className="brand-block">
          <Text className="eyebrow">AI TestFlow</Text>
          <Title level={1}>登录 Demo 系统</Title>
          <Text className="subtle-text">用于验证 PRD 到测试报告和 Bug 单的最小闭环。</Text>
        </div>

        <Form layout="vertical" size="large" onFinish={handleSubmit} requiredMark={false}>
          <Form.Item
            label="用户名"
            name="username"
            rules={[{ required: true, message: '用户名不能为空' }]}
          >
            <Input prefix={<UserOutlined />} placeholder="请输入用户名" autoComplete="username" />
          </Form.Item>

          <Form.Item
            label="密码"
            name="password"
            rules={[{ required: true, message: '密码不能为空' }]}
          >
            <Input.Password prefix={<LockOutlined />} placeholder="请输入密码" autoComplete="current-password" />
          </Form.Item>

          <Button type="primary" htmlType="submit" block>
            登录
          </Button>
        </Form>

        <div className="auth-footer">
          <Text>还没有账号？</Text>
          <Link to="/register">去注册</Link>
        </div>
      </section>
    </main>
  );
}

