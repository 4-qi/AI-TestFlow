import { LockOutlined, UserOutlined } from '@ant-design/icons';
import { Button, Form, Input, Typography, message } from 'antd';
import { Link, useNavigate } from 'react-router-dom';
import { api, getErrorMessage } from '../api.js';

const { Title, Text } = Typography;

export default function RegisterPage() {
  const navigate = useNavigate();
  const [messageApi, contextHolder] = message.useMessage();

  async function handleSubmit(values) {
    try {
      await api.post('/api/register', values);
      messageApi.success('注册成功');
      navigate('/login');
    } catch (error) {
      messageApi.error(getErrorMessage(error));
    }
  }

  return (
    <main className="auth-page">
      {contextHolder}
      <section className="auth-panel" aria-label="注册">
        <div className="brand-block">
          <Text className="eyebrow">AI TestFlow</Text>
          <Title level={1}>注册测试账号</Title>
          <Text className="subtle-text">用户名规则来自 PRD：长度必须大于等于 6 位。</Text>
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
            <Input.Password prefix={<LockOutlined />} placeholder="请输入密码" autoComplete="new-password" />
          </Form.Item>

          <Form.Item
            label="确认密码"
            name="confirm_password"
            dependencies={['password']}
            rules={[
              { required: true, message: '请再次输入密码' },
              ({ getFieldValue }) => ({
                validator(_, value) {
                  if (!value || getFieldValue('password') === value) {
                    return Promise.resolve();
                  }
                  return Promise.reject(new Error('两次输入的密码不一致'));
                },
              }),
            ]}
          >
            <Input.Password prefix={<LockOutlined />} placeholder="请再次输入密码" autoComplete="new-password" />
          </Form.Item>

          <Button type="primary" htmlType="submit" block>
            注册
          </Button>
        </Form>

        <div className="auth-footer">
          <Text>已有账号？</Text>
          <Link to="/login">去登录</Link>
        </div>
      </section>
    </main>
  );
}

