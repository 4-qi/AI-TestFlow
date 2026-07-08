import { LogoutOutlined, UserOutlined } from '@ant-design/icons';
import { Button, Result, Spin, Typography, message } from 'antd';
import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { api, getErrorMessage } from '../api.js';

const { Text, Title } = Typography;

export default function HomePage() {
  const navigate = useNavigate();
  const [messageApi, contextHolder] = message.useMessage();
  const [loading, setLoading] = useState(true);
  const [username, setUsername] = useState('');

  useEffect(() => {
    async function fetchCurrentUser() {
      try {
        const response = await api.get('/api/me');
        setUsername(response.data.data.username);
      } catch (error) {
        messageApi.error(getErrorMessage(error));
        navigate('/login');
      } finally {
        setLoading(false);
      }
    }

    fetchCurrentUser();
  }, [messageApi, navigate]);

  async function handleLogout() {
    try {
      await api.post('/api/logout');
      messageApi.success('退出登录成功');
      navigate('/login');
    } catch (error) {
      messageApi.error(getErrorMessage(error));
    }
  }

  if (loading) {
    return (
      <main className="home-page">
        {contextHolder}
        <Spin size="large" />
      </main>
    );
  }

  return (
    <main className="home-page">
      {contextHolder}
      <Result
        icon={<UserOutlined />}
        title={<Title level={1}>欢迎，{username}</Title>}
        subTitle={<Text>你已登录登录注册 Demo 系统。</Text>}
        extra={
          <Button type="primary" icon={<LogoutOutlined />} onClick={handleLogout}>
            退出登录
          </Button>
        }
      />
    </main>
  );
}

