import { createBrowserRouter, Navigate } from 'react-router-dom';
import MainLayout from '@/layouts/MainLayout';
import PrivateRoute from '@/components/PrivateRoute';
import Login from '@/pages/Login';
import Dashboard from '@/pages/Dashboard';
import ChatInterface from '@/pages/ChatInterface';
import TicketList from '@/pages/TicketList';
import TaskBoard from '@/pages/TaskBoard';
import ApprovalCenter from '@/pages/ApprovalCenter';
import AssetManagement from '@/pages/AssetManagement';
import KnowledgeBase from '@/pages/KnowledgeBase';
import SystemSettings from '@/pages/SystemSettings';
import UserManagement from '@/pages/UserManagement';

/**
 * 路由配置
 */
export const router = createBrowserRouter([
  {
    path: '/login',
    element: <Login />,
  },
  {
    path: '/',
    element: (
      <PrivateRoute>
        <MainLayout />
      </PrivateRoute>
    ),
    children: [
      {
        index: true,
        element: <Navigate to="/dashboard" replace />,
      },
      {
        path: 'dashboard',
        element: <Dashboard />,
      },
      {
        path: 'chat',
        element: <ChatInterface />,
      },
      {
        path: 'tickets',
        element: <TicketList />,
      },
      {
        path: 'tasks',
        element: <TaskBoard />,
      },
      {
        path: 'approvals',
        element: <ApprovalCenter />,
      },
      {
        path: 'assets',
        element: <AssetManagement />,
      },
      {
        path: 'knowledge',
        element: <KnowledgeBase />,
      },
      {
        path: 'users',
        element: <UserManagement />,
      },
      {
        path: 'settings',
        element: <SystemSettings />,
      },
    ],
  },
]);
