export type UserRole = 'employee' | 'admin_staff' | 'manager' | 'sys_admin';

export interface User {
  id: string;
  username?: string;
  name: string;
  role: UserRole;
  department: string;
  createdAt: string;
}

export interface ManagedUser {
  id: number;
  username: string;
  full_name: string;
  role: UserRole;
  department: string;
  email?: string | null;
  phone?: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  token: string;
  user: User;
}

export type TicketType = 'purchase' | 'repair' | 'requisition' | 'consultation';
export type ApprovalStatus =
  | 'no_approval'
  | 'pending_manager'
  | 'pending_finance'
  | 'approved'
  | 'rejected';
export type ProcessingStatus = 'pending' | 'in_progress' | 'completed' | 'closed';
export type UrgencyLevel = 'low' | 'normal' | 'high' | 'urgent';

export interface Ticket {
  id: number;
  requester_id: number;
  original_text: string;
  attachments?: string | null;
  ticket_type: TicketType;
  related_asset_id?: number | null;
  estimated_cost: number;
  approval_status: ApprovalStatus;
  processing_status: ProcessingStatus;
  assigned_to?: number | null;
  urgency: UrgencyLevel;
  created_at: string;
  updated_at: string;
  closed_at?: string | null;
}

export interface Asset {
  id: number;
  asset_code: string;
  name: string;
  category: 'it_equipment' | 'office_furniture' | 'consumables' | 'other';
  status: 'idle' | 'in_use' | 'maintenance' | 'scrapped';
  owner_id?: number | null;
  current_stock: number;
  unit_price?: number | null;
  location?: string | null;
  description?: string | null;
  created_at: string;
  updated_at: string;
}

export interface Task {
  id: number;
  title: string;
  description?: string | null;
  related_ticket_id?: number | null;
  assigned_to: number;
  status: 'todo' | 'in_progress' | 'completed' | 'cancelled';
  priority: number;
  due_date?: string | null;
  created_at: string;
  updated_at: string;
  completed_at?: string | null;
}

export interface SysConfig {
  id: number;
  config_key: string;
  config_value: string;
  description?: string | null;
  is_sensitive: boolean;
  updated_at: string;
}

export interface Knowledge {
  id: number;
  title: string;
  content: string;
  category: string;
  view_count: number;
  is_active: boolean;
  created_at: string;
}
